"""Shared OpenAI JSON-mode caller for the claim pipeline."""
import json
import os
import time

import requests
from dotenv import load_dotenv

from fetch import REPO_ROOT

def _env_path() -> str:
    """A git worktree has no .env of its own; fall back to the main checkout's."""
    local = os.path.join(REPO_ROOT, ".env")
    if os.path.exists(local):
        return local
    marker = os.sep + os.path.join(".claude", "worktrees") + os.sep
    if marker in REPO_ROOT + os.sep:
        return os.path.join(REPO_ROOT.split(marker)[0], ".env")
    return local


load_dotenv(_env_path())

# CI_PROVIDER=openrouter routes the same OpenAI models through OpenRouter (separate billing,
# no 10k-requests/day cap). Model names gain the "openai/" prefix OpenRouter expects.
PROVIDER = (os.getenv("CI_PROVIDER") or "openai").lower()
if PROVIDER == "openrouter":
    API_BASE = "https://openrouter.ai/api/v1"
    API_KEY_VAR = "OPENROUTER_API_KEY"
else:
    API_BASE = "https://api.openai.com/v1"
    API_KEY_VAR = "OPENAI_API_KEY"
ENDPOINT = f"{API_BASE}/chat/completions"
EMBED_ENDPOINT = f"{API_BASE}/embeddings"
MODEL = os.getenv("CI_MODEL") or "gpt-4o-mini"
PRICE_PER_MTOK = {"gpt-4o-mini": (0.15, 0.60), "gpt-4o": (2.50, 10.00)}


def provider_model(name: str) -> str:
    """The model id as this provider names it."""
    if PROVIDER == "openrouter" and "/" not in name:
        return f"openai/{name}"
    return name


def api_key() -> str:
    key = os.getenv(API_KEY_VAR)
    if not key:
        raise SystemExit(f"{API_KEY_VAR} is not set")
    return key


class Usage:
    """Running token/cost tally across a run."""

    def __init__(self, model: str = None):
        self.model = model or MODEL
        self.calls = self.prompt = self.completion = 0

    def add(self, usage: dict):
        self.calls += 1
        self.prompt += usage.get("prompt_tokens", 0)
        self.completion += usage.get("completion_tokens", 0)

    @property
    def cost_usd(self) -> float:
        rate_in, rate_out = PRICE_PER_MTOK.get(self.model.split("/")[-1], (0.0, 0.0))
        return self.prompt / 1e6 * rate_in + self.completion / 1e6 * rate_out

    def __str__(self):
        return (f"{self.calls} calls · {self.prompt:,} in + {self.completion:,} out tokens "
                f"· ${self.cost_usd:.2f} at {self.model} list price")


def ask_json(system: str, user: str, usage: Usage, max_tokens: int = 2000, retries: int = 7,
             model: str = None):
    """One JSON-mode completion. Returns the parsed object, or None if it never succeeds."""
    key = api_key()

    body = {
        "model": provider_model(model or MODEL),
        "temperature": 0,
        "max_tokens": max_tokens,
        "response_format": {"type": "json_object"},
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
    }
    for attempt in range(retries):
        try:
            resp = requests.post(ENDPOINT, timeout=180, json=body,
                                 headers={"Authorization": f"Bearer {key}"})
            if resp.status_code in (429, 500, 502, 503, 529):
                # The account's tokens-per-minute ceiling is the usual cause; wait it out
                # rather than dropping the item, and honour Retry-After when given.
                wait = float(resp.headers.get("retry-after") or min(60, 2 ** attempt * 2))
                time.sleep(wait)
                continue
            resp.raise_for_status()
            payload = resp.json()
            usage.add(payload.get("usage", {}))
            return json.loads(payload["choices"][0]["message"]["content"])
        except (requests.RequestException, ValueError, KeyError):
            if attempt == retries - 1:
                return None
            time.sleep(min(60, 2 ** attempt * 2))
    return None
