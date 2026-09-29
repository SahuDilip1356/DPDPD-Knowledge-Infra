import os
import requests
import json
import base64
from typing import Dict
from dotenv import load_dotenv

load_dotenv()

class ModelClient:
    """
    Provider chain for grounded generation (the cook):
        GPT-OSS (OpenAI-compatible local/remote) -> Gemini -> OpenAI -> OpenRouter.

    GPT-OSS is retrieval-only. It never trains on harvested competitor text.
    Vision OCR and embeddings stay on Gemini/OpenAI-compatible providers;
    gpt-oss weights are not an embedding model.
    """

    def __init__(self):
        self.gemini_key = (
            (os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or "").strip()
            or None
        )
        self.openai_key = (os.getenv("OPENAI_API_KEY") or "").strip() or None
        self.openrouter_key = (os.getenv("OPENROUTER_API_KEY") or "").strip() or None

        # NOTE: use `os.getenv(X) or default`, never `os.getenv(X, default)`.
        # A key present-but-blank in .env (e.g. "EMBED_MODEL=") returns "" from
        # the two-arg form, which would send an empty model name to the API.
        def cfg(name, default):
            return (os.getenv(name) or "").strip() or default

        reasoning_provider = cfg("REASONING_PROVIDER", "").lower()
        gpt_oss_base = (os.getenv("GPT_OSS_BASE_URL") or "").strip()
        gpt_oss_model = (os.getenv("GPT_OSS_MODEL") or "").strip()
        self.gpt_oss_enabled = (
            reasoning_provider == "gpt-oss" or bool(gpt_oss_base or gpt_oss_model)
        )
        if self.gpt_oss_enabled:
            self.gpt_oss_base = gpt_oss_base or "http://127.0.0.1:11434/v1"
            self.gpt_oss_model = gpt_oss_model or "gpt-oss:20b"
            self.gpt_oss_key = (os.getenv("GPT_OSS_API_KEY") or "ollama").strip() or "ollama"
            print(
                "[ModelClient] Active: GPT-OSS cook "
                f"({self.gpt_oss_model} @ {self.gpt_oss_base}). Retrieval only."
            )
        else:
            self.gpt_oss_base = None
            self.gpt_oss_model = None
            self.gpt_oss_key = None

        # Resolve the OpenAI-compatible transport (direct OpenAI, else OpenRouter).
        if self.openai_key:
            self.oai_key = self.openai_key
            self.oai_base = cfg("OPENAI_BASE_URL", "https://api.openai.com/v1")
            self.oai_chat_model = cfg("CHAT_MODEL", "gpt-4o-mini")
            self.oai_embed_model = cfg("EMBED_MODEL", "text-embedding-3-small")
            self.oai_provider = "OpenAI"
        elif self.openrouter_key:
            self.oai_key = self.openrouter_key
            self.oai_base = cfg("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
            # OpenRouter namespaces models by vendor. text-embedding-3-small is
            # 1536-dimensional either way, so the vector index stays compatible
            # when switching between OpenAI and OpenRouter.
            self.oai_chat_model = cfg("CHAT_MODEL", "openai/gpt-4o-mini")
            self.oai_embed_model = cfg("EMBED_MODEL", "openai/text-embedding-3-small")
            self.oai_provider = "OpenRouter"
        else:
            self.oai_key = None
            self.oai_base = None
            self.oai_chat_model = None
            self.oai_embed_model = None
            self.oai_provider = None

        if self.gpt_oss_enabled:
            pass  # Already announced as the cook.
        elif self.gemini_key:
            print("[ModelClient] Active: Gemini API client initialized.")
        elif self.oai_key:
            print(f"[ModelClient] Active: {self.oai_provider} client initialized (Gemini key missing).")
        else:
            print("[ModelClient] Warning: No model API keys found. Model-backed queries will fail closed.")

    @property
    def is_configured(self) -> bool:
        return bool(self.gpt_oss_enabled or self.gemini_key or self.oai_key)

    def _oai_headers(self) -> dict:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.oai_key}"
        }
        if self.oai_provider == "OpenRouter":
            # Optional attribution headers OpenRouter uses for usage dashboards.
            headers["HTTP-Referer"] = os.getenv("OPENROUTER_SITE_URL", "https://dpdpa.wiki")
            headers["X-Title"] = os.getenv("OPENROUTER_SITE_NAME", "DPDPA Knowledge Infra")
        return headers

    def generate(self, prompt: str) -> str:
        """
        Sends the prompt to the configured LLM endpoint and returns the generated text response.
        """
        if self.gpt_oss_enabled:
            return self._generate_gpt_oss(prompt)
        if self.gemini_key:
            return self._generate_gemini(prompt)
        elif self.oai_key:
            return self._generate_openai(prompt)
        else:
            raise ValueError(
                "No API key found. Add GPT_OSS_MODEL / GPT_OSS_BASE_URL, "
                "GEMINI_API_KEY, OPENAI_API_KEY or OPENROUTER_API_KEY."
            )

    def generate_json(self, prompt: str) -> Dict:
        """Generate a structured response and fail closed after one retry."""
        raw = ""
        last_error = "MALFORMED_JSON"

        for _attempt in range(2):
            try:
                if self.gpt_oss_enabled:
                    raw = self._generate_json_gpt_oss(prompt)
                elif self.gemini_key:
                    raw = self._generate_json_gemini(prompt)
                elif self.oai_key:
                    raw = self._generate_json_openai(prompt)
                else:
                    raise ValueError(
                        "No model API key configured for structured generation."
                    )

                parsed = json.loads(self._strip_json_fence(raw))
                if not isinstance(parsed, dict):
                    raise ValueError("Structured model response must be a JSON object.")
                return parsed
            except Exception as exc:
                last_error = f"MALFORMED_JSON: {exc}"

        return {
            "answer": (
                "INSUFFICIENT_EVIDENCE: The model did not return a valid "
                "structured answer."
            ),
            "cited_urns": [],
            "sufficient_evidence": False,
            "error": last_error,
            "raw_output": raw,
        }

    @staticmethod
    def _strip_json_fence(raw: str) -> str:
        clean_raw = raw.strip()
        if clean_raw.startswith("```json"):
            clean_raw = clean_raw[7:]
        elif clean_raw.startswith("```"):
            clean_raw = clean_raw[3:]
        if clean_raw.endswith("```"):
            clean_raw = clean_raw[:-3]
        return clean_raw.strip()

    def generate_vision(self, prompt: str, mime_type: str, file_bytes: bytes) -> str:
        """
        Sends a visual document/image alongside a prompt to the configured LLM endpoint.
        """
        if self.gemini_key:
            return self._generate_vision_gemini(prompt, mime_type, file_bytes)
        elif self.oai_key:
            return self._generate_vision_openai(prompt, mime_type, file_bytes)
        else:
            raise ValueError(
                "No API key found. Add GEMINI_API_KEY, OPENAI_API_KEY or "
                "OPENROUTER_API_KEY to the service environment."
            )

    def _generate_vision_gemini(self, prompt: str, mime_type: str, file_bytes: bytes) -> str:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={self.gemini_key}"
        headers = {"Content-Type": "application/json"}
        base64_data = base64.b64encode(file_bytes).decode("utf-8")
        
        payload = {
            "contents": [{
                "parts": [
                    {
                        "inlineData": {
                            "mimeType": mime_type,
                            "data": base64_data
                        }
                    },
                    {
                        "text": prompt
                    }
                ]
            }],
            "generationConfig": {
                "temperature": 0.1,
                "maxOutputTokens": 2048
            }
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            result = response.json()
            
            candidates = result.get("candidates", [])
            if not candidates:
                return "ERROR: No response candidates returned from Gemini Vision API."
            
            parts = candidates[0].get("content", {}).get("parts", [])
            if not parts:
                return "ERROR: Empty content parts returned from Gemini Vision API."
                
            return parts[0].get("text", "")
        except Exception as e:
            return f"ERROR: Gemini Vision API execution failed: {str(e)}"

    def _generate_vision_openai(self, prompt: str, mime_type: str, file_bytes: bytes) -> str:
        if mime_type == "application/pdf":
            # OpenAI does not support raw PDF files in the chat completions API directly
            print("[ModelClient] Warning: OpenAI does not support direct PDF visual uploads in completions. Falling back to text extraction.")
            return "ERROR: OpenAI does not support raw PDF Vision OCR."
            
        url = f"{self.oai_base}/chat/completions"
        headers = self._oai_headers()
        base64_data = base64.b64encode(file_bytes).decode("utf-8")

        payload = {
            "model": self.oai_chat_model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime_type};base64,{base64_data}"
                            }
                        }
                    ]
                }
            ],
            "temperature": 0.1,
            "max_tokens": 2048
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            result = response.json()
            
            choices = result.get("choices", [])
            if not choices:
                return "ERROR: No choices returned from OpenAI Vision API."
                
            return choices[0].get("message", {}).get("content", "")
        except Exception as e:
            return f"ERROR: OpenAI Vision API execution failed: {str(e)}"

    def _generate_gemini(self, prompt: str) -> str:
        # We use the gemini-2.5-flash model for fast, cost-efficient, and accurate reasoning
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={self.gemini_key}"
        headers = {
            "Content-Type": "application/json"
        }
        payload = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }],
            "generationConfig": {
                "temperature": 0.1,  # Keep temperature low for precise, grounded extraction
                "maxOutputTokens": 2048
            }
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            result = response.json()
            
            # Parse Gemini response schema
            candidates = result.get("candidates", [])
            if not candidates:
                return "ERROR: No response candidates returned from Gemini API."
            
            parts = candidates[0].get("content", {}).get("parts", [])
            if not parts:
                return "ERROR: Empty content parts returned from Gemini API."
                
            return parts[0].get("text", "")
            
        except Exception as e:
            return f"ERROR: Gemini API execution failed: {str(e)}"

    def _generate_openai(self, prompt: str) -> str:
        url = f"{self.oai_base}/chat/completions"
        headers = self._oai_headers()
        payload = {
            "model": self.oai_chat_model,
            "messages": [
                {"role": "system", "content": "You are a precise legal reasoning assistant."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.1,
            "max_tokens": 2048
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            result = response.json()
            
            choices = result.get("choices", [])
            if not choices:
                return "ERROR: No choices returned from OpenAI API."
                
            return choices[0].get("message", {}).get("content", "")
            
        except Exception as e:
            return f"ERROR: {self.oai_provider} API execution failed: {str(e)}"

    def _gpt_oss_headers(self) -> dict:
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.gpt_oss_key}",
        }

    def _generate_gpt_oss(self, prompt: str) -> str:
        payload = {
            "model": self.gpt_oss_model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a grounded legal cook. Answer only from the "
                        "supplied knowledge-graph evidence. Never invent law."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.1,
            "max_tokens": 2048,
        }
        try:
            response = requests.post(
                f"{self.gpt_oss_base}/chat/completions",
                headers=self._gpt_oss_headers(),
                json=payload,
                timeout=120,
            )
            response.raise_for_status()
            choices = response.json().get("choices", [])
            if not choices:
                return "ERROR: No choices returned from GPT-OSS."
            return choices[0].get("message", {}).get("content", "")
        except Exception as e:
            return f"ERROR: GPT-OSS execution failed: {str(e)}"

    def _generate_json_gpt_oss(self, prompt: str) -> str:
        messages = [
            {
                "role": "system",
                "content": "Return only a JSON object matching the schema in the user request.",
            },
            {"role": "user", "content": prompt},
        ]
        payload = {
            "model": self.gpt_oss_model,
            "messages": messages,
            "temperature": 0.0,
            "max_tokens": 2048,
            "response_format": {"type": "json_object"},
        }
        response = requests.post(
            f"{self.gpt_oss_base}/chat/completions",
            headers=self._gpt_oss_headers(),
            json=payload,
            timeout=120,
        )
        if response.status_code >= 400:
            payload.pop("response_format", None)
            response = requests.post(
                f"{self.gpt_oss_base}/chat/completions",
                headers=self._gpt_oss_headers(),
                json=payload,
                timeout=120,
            )
        response.raise_for_status()
        choices = response.json().get("choices", [])
        if not choices:
            raise RuntimeError("No choices returned from GPT-OSS.")
        return choices[0].get("message", {}).get("content", "")

    def _generate_json_gemini(self, prompt: str) -> str:
        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"gemini-2.5-flash:generateContent?key={self.gemini_key}"
        )
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.0,
                "responseMimeType": "application/json",
                "maxOutputTokens": 2048,
            },
        }
        response = requests.post(
            url,
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=60,
        )
        response.raise_for_status()
        result = response.json()
        candidates = result.get("candidates", [])
        if not candidates:
            raise RuntimeError("No response candidates returned from Gemini API.")
        parts = candidates[0].get("content", {}).get("parts", [])
        if not parts:
            raise RuntimeError("Empty content returned from Gemini API.")
        return parts[0].get("text", "")

    def _generate_json_openai(self, prompt: str) -> str:
        payload = {
            "model": self.oai_chat_model,
            "response_format": {"type": "json_object"},
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Return only a JSON object matching the schema in the "
                        "user request."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.0,
            "max_tokens": 2048,
        }
        response = requests.post(
            f"{self.oai_base}/chat/completions",
            headers=self._oai_headers(),
            json=payload,
            timeout=60,
        )
        response.raise_for_status()
        choices = response.json().get("choices", [])
        if not choices:
            raise RuntimeError(f"No choices returned from {self.oai_provider} API.")
        return choices[0].get("message", {}).get("content", "")

    def embed(self, text: str) -> list:
        """
        Generates vector embedding for the input text.
        """
        if self.gemini_key:
            return self._embed_gemini(text)
        elif self.oai_key:
            return self._embed_openai(text)
        else:
            raise ValueError(
                "No API Key found. Add GEMINI_API_KEY, OPENAI_API_KEY or "
                "OPENROUTER_API_KEY to your .env file."
            )

    def _embed_gemini(self, text: str) -> list:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/text-embedding-004:embedContent?key={self.gemini_key}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "model": "models/text-embedding-004",
            "content": {
                "parts": [{"text": text}]
            }
        }
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=20)
            response.raise_for_status()
            result = response.json()
            return result["embedding"]["values"]
        except Exception as e:
            raise RuntimeError(f"Gemini embedding failed: {str(e)}")

    def _embed_openai(self, text: str) -> list:
        url = f"{self.oai_base}/embeddings"
        headers = self._oai_headers()
        payload = {
            "input": text,
            "model": self.oai_embed_model
        }
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=20)
            response.raise_for_status()
            result = response.json()
            return result["data"][0]["embedding"]
        except Exception as e:
            raise RuntimeError(f"{self.oai_provider} embedding failed: {str(e)}")


class MockModelClient(ModelClient):
    """Deterministic model client for explicitly offline tests and evals."""

    def __init__(self, canned_responses=None):
        self.gemini_key = None
        self.openai_key = None
        self.openrouter_key = None
        self.oai_key = None
        self.oai_base = None
        self.oai_chat_model = None
        self.oai_embed_model = None
        self.oai_provider = None
        self.gpt_oss_enabled = False
        self.gpt_oss_base = None
        self.gpt_oss_model = None
        self.gpt_oss_key = None
        self.canned_responses = canned_responses or {}
        self.call_history = []

    def generate(self, prompt: str) -> str:
        self.call_history.append({"type": "generate", "prompt": prompt})
        for pattern, response in self.canned_responses.items():
            if pattern.lower() in prompt.lower():
                return json.dumps(response) if isinstance(response, dict) else str(response)
        return "Deterministic mock text response."

    def generate_json(self, prompt: str) -> Dict:
        self.call_history.append({"type": "generate_json", "prompt": prompt})
        for pattern, response in self.canned_responses.items():
            if pattern.lower() in prompt.lower():
                if isinstance(response, dict):
                    return response
                try:
                    return json.loads(response)
                except Exception:
                    break

        if "Context:" in prompt and "urn:ki:" in prompt:
            import re

            urns = re.findall(r"urn:ki:[a-zA-Z0-9_:\-]+", prompt)
            first_urn = urns[0] if urns else "urn:ki:in:dpdp:act:dpdpa-2023"
            return {
                "answer": (
                    "Based on the canonical regulatory core, the mandate is "
                    f"specified in [{first_urn} (Page 1, Section 1, Hash: aaaaaaaa)]."
                ),
                "cited_urns": [first_urn],
                "sufficient_evidence": True,
            }

        return {
            "answer": (
                "INSUFFICIENT_EVIDENCE: The query cannot be answered using "
                "the canonical knowledge core."
            ),
            "cited_urns": [],
            "sufficient_evidence": False,
        }

    def embed(self, text: str) -> list:
        return [0.01] * 1536
