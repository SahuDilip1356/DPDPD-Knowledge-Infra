import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

class ModelClient:
    def __init__(self):
        self.gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        self.openai_key = os.getenv("OPENAI_API_KEY")
        
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
        if self.gemini_key:
            return self._generate_gemini(prompt)
        elif self.openai_key:
            return self._generate_openai(prompt)
        else:
            raise ValueError(
                "No API Key found. Please add GEMINI_API_KEY or OPENAI_API_KEY to your .env file."
            )

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
