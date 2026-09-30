import os
import requests
import json
import base64
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv

load_dotenv()

class ModelClient:
    """Grounded cook chain: GPT-OSS (retrieval only) -> Gemini -> OpenAI."""

    def __init__(self):
        self.gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        self.openai_key = os.getenv("OPENAI_API_KEY")
        reasoning_provider = (os.getenv("REASONING_PROVIDER") or "").strip().lower()
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
            if self.gemini_key:
                print("[ModelClient] Active: Gemini API client initialized.")
            elif self.openai_key:
                print("[ModelClient] Active: OpenAI API client initialized (Gemini Key missing).")
            else:
                print("[ModelClient] Warning: No API keys found in environment. Grounded queries will fall back to mock solver.")

    def generate(self, prompt: str) -> str:
        """
        Sends the prompt to the configured LLM endpoint and returns the generated text response.
        """
        if self.gpt_oss_enabled:
            return self._generate_gpt_oss(prompt)
        if self.gemini_key:
            return self._generate_gemini(prompt)
        elif self.openai_key:
            return self._generate_openai(prompt)
        else:
            raise ValueError(
                "No API Key found. Please add GPT_OSS_MODEL / GPT_OSS_BASE_URL, "
                "GEMINI_API_KEY or OPENAI_API_KEY to your .env file."
            )

    def generate_json(self, prompt: str) -> Dict:
        """
        Sends the prompt to the configured LLM endpoint demanding structured JSON.
        Implements single retry on malformed JSON and fails closed with raw text preserved.
        """
        for attempt in range(2):
            raw = ""
            try:
                if self.gpt_oss_enabled:
                    raw = self._generate_json_gpt_oss(prompt)
                elif self.gemini_key:
                    raw = self._generate_json_gemini(prompt)
                elif self.openai_key:
                    raw = self._generate_json_openai(prompt)
                else:
                    raise ValueError("No API Key found.")
                
                # Attempt to parse json
                # Handle possible markdown backticks from lenient models
                clean_raw = raw.strip()
                if clean_raw.startswith("```json"):
                    clean_raw = clean_raw[7:]
                if clean_raw.startswith("```"):
                    clean_raw = clean_raw[3:]
                if clean_raw.endswith("```"):
                    clean_raw = clean_raw[:-3]
                clean_raw = clean_raw.strip()

                parsed = json.loads(clean_raw)
                if isinstance(parsed, dict):
                    return parsed
            except Exception as e:
                if attempt == 1:
                    print(f"[ModelClient] JSON parse failed after retry: {e}. Raw: {raw[:150]}")
                    return {
                        "answer": raw,
                        "cited_urns": [],
                        "sufficient_evidence": False,
                        "error": f"MALFORMED_JSON: {str(e)}",
                        "raw_output": raw
                    }
        return {
            "answer": raw,
            "cited_urns": [],
            "sufficient_evidence": False,
            "error": "MALFORMED_JSON",
            "raw_output": raw
        }

    def generate_vision(self, prompt: str, mime_type: str, file_bytes: bytes) -> str:
        """
        Sends a visual document/image alongside a prompt to the configured LLM endpoint.
        """
        if self.gemini_key:
            return self._generate_vision_gemini(prompt, mime_type, file_bytes)
        elif self.openai_key:
            return self._generate_vision_openai(prompt, mime_type, file_bytes)
        else:
            raise ValueError(
                "No API Key found. Please add GEMINI_API_KEY or OPENAI_API_KEY to your .env file."
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
            
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.openai_key}"
        }
        base64_data = base64.b64encode(file_bytes).decode("utf-8")
        
        payload = {
            "model": "gpt-4o-mini",
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
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.openai_key}"
        }
        payload = {
            "model": "gpt-4o-mini",
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
            return f"ERROR: OpenAI API execution failed: {str(e)}"

    def embed(self, text: str) -> list:
        """
        Generates vector embedding for the input text.
        """
        if self.gemini_key:
            return self._embed_gemini(text)
        elif self.openai_key:
            return self._embed_openai(text)
        else:
            raise ValueError(
                "No API Key found. Please add GEMINI_API_KEY or OPENAI_API_KEY to your .env file."
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
        url = "https://api.openai.com/v1/embeddings"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.openai_key}"
        }
        payload = {
            "input": text,
            "model": "text-embedding-3-small"
        }
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=20)
            response.raise_for_status()
            result = response.json()
            return result["data"][0]["embedding"]
        except Exception as e:
            raise RuntimeError(f"OpenAI embedding failed: {str(e)}")

    def _generate_json_gemini(self, prompt: str) -> str:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={self.gemini_key}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.0,
                "responseMimeType": "application/json",
                "maxOutputTokens": 2048
            }
        }
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        result = response.json()
        candidates = result.get("candidates", [])
        if not candidates:
            raise RuntimeError("No response candidates returned from Gemini API.")
        parts = candidates[0].get("content", {}).get("parts", [])
        if not parts:
            raise RuntimeError("Empty content parts returned from Gemini API.")
        return parts[0].get("text", "")

    def _generate_json_openai(self, prompt: str) -> str:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.openai_key}"
        }
        payload = {
            "model": "gpt-4o-mini",
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": "You are a precise legal reasoning assistant. You must always return valid JSON adhering strictly to the requested schema."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.0,
            "max_tokens": 2048
        }
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        result = response.json()
        choices = result.get("choices", [])
        if not choices:
            raise RuntimeError("No choices returned from OpenAI API.")
        return choices[0].get("message", {}).get("content", "")

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


class MockModelClient(ModelClient):
    """
    Deterministic offline model client for testing and zero-cost evals.
    Does not make any network requests or require API keys.
    """
    def __init__(self, canned_responses=None):
        self.gemini_key = None
        self.openai_key = None
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
                if isinstance(response, dict):
                    return json.dumps(response)
                return str(response)
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
                    pass
                    
        # If context contains KOs, return structured grounded answer citing the first URN
        if "Context:" in prompt and "urn:ki:" in prompt:
            import re
            urns = re.findall(r"urn:ki:[a-zA-Z0-9_\-:]+", prompt)
            first_urn = urns[0] if urns else "urn:ki:in:dpdp:act:dpdpa-2023"
            return {
                "answer": f"Based on the canonical regulatory core, the mandate is specified in [{first_urn} (Page 1, Section 1, Hash: aaaaaaaa)].",
                "cited_urns": [first_urn],
                "sufficient_evidence": True
            }
        else:
            return {
                "answer": "INSUFFICIENT_EVIDENCE: The query cannot be answered using the canonical knowledge core.",
                "cited_urns": [],
                "sufficient_evidence": False
            }

    def embed(self, text: str) -> list:
        return [0.01] * 1536
