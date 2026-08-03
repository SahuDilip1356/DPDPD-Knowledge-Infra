import os
import requests
import json
import base64
from dotenv import load_dotenv

load_dotenv()

class ModelClient:
    """
    Provider chain: Gemini -> OpenAI -> OpenRouter.

    OpenRouter speaks the OpenAI wire format for both /chat/completions and
    /embeddings, so it reuses the same transport — only the base URL, key and
    model identifiers differ. That keeps one code path for two providers.
    """

    def __init__(self):
        self.gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.openrouter_key = os.getenv("OPENROUTER_API_KEY")

        # NOTE: use `os.getenv(X) or default`, never `os.getenv(X, default)`.
        # A key present-but-blank in .env (e.g. "EMBED_MODEL=") returns "" from
        # the two-arg form, which would send an empty model name to the API.
        def cfg(name, default):
            return (os.getenv(name) or "").strip() or default

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

        if self.gemini_key:
            print("[ModelClient] Active: Gemini API client initialized.")
        elif self.oai_key:
            print(f"[ModelClient] Active: {self.oai_provider} client initialized (Gemini key missing).")
        else:
            print("[ModelClient] Warning: No API keys found in environment. Grounded queries will fall back to mock solver.")

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
        if self.gemini_key:
            return self._generate_gemini(prompt)
        elif self.openai_key:
            return self._generate_openai(prompt)
        else:
            raise ValueError(
                "No API Key found. Please add GEMINI_API_KEY or OPENAI_API_KEY to your .env file."
            )

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
            return f"ERROR: OpenAI API execution failed: {str(e)}"

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
