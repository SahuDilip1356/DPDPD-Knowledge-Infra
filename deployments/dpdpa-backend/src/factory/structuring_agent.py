import json
from typing import List, Dict
from src.reasoning.model_client import ModelClient

class StructuringAgent:
    def __init__(self, model_client: ModelClient):
        self.model_client = model_client

    def structure_document(self, filename: str, source_urn: str, source_layer: int, evidence_packet: Dict) -> List[Dict]:
        """
        Uses the ModelClient to read the evidence chunks, extract regulatory rules,
        and generate structured Knowledge Objects conforming to the constitution schema.
        """
        # Formulate chunks description for LLM context
        chunks_str = ""
        for chunk in evidence_packet.get("chunks", []):
            coords = chunk["coordinates"]
            chunks_str += f"CHUNK_URN: {chunk['urn']}\n"
            chunks_str += f"Page: {coords['page']}, Section: {coords['section']}, Hash: {coords['hash']}\n"
            chunks_str += f"Text: \"{chunk['text']}\"\n\n"

        prompt = f"""You are the Structuring Agent of the Regulatory Knowledge Ingestion Factory.
Your job is to read raw parsed document chunks from a regulatory filing/act/rule, extract distinct regulatory rules, obligations, or definitions, and structure them as a list of valid JSON Knowledge Objects (KOs).

Here is the document context:
Source URN: {source_urn}
Source Layer: {source_layer}
Filename: {filename}

Parsed Chunks:
{chunks_str}

CRITICAL SCHEMA GUIDELINES:
Return a JSON array of objects. Each object in the array MUST conform to this exact schema:
{{
  "urn": "urn:ki:in:dpdp:..." (Generate a deterministic, unique URN matching the pattern, e.g. urn:ki:in:dpdp:act:2023:sec:x or urn:ki:in:dpdp:rule:2025:r:x),
  "version": 1,
  "type": "Act" | "Rule" | "Notification" | "Circular" | "Opinion" | "Judgement" | "Penalty",
  "title": "Clear concise title of the section/rule",
  "summary": "Precise summary of the obligation or rule",
  "confidence_score": 1.0 (1.0 for primary source like Acts/Rules, 0.9 for judgements, 0.7 for circulars/notifications),
  "source_credibility": "primary" | "secondary" | "tertiary",
  "legal_time_start": "YYYY-MM-DDT00:00:00Z" (use the legal date of the document),
  "business_impact": {{
    "impact_summary": "Actionable business summary of how this affects enterprises",
    "action_required": "Concrete compliance steps required by the company"
  }},
  "evidence": [
    {{
      "id": "ev-001",
      "source_urn": "{source_urn}",
      "source_name": "{filename}",
      "source_tier": "primary",
      "citation_text": "Exact text from the chunk backing this rule",
      "coordinates": {{
        "page": 1,
        "section": "Paragraph coordinates"
      }},
      "hash": "The exact Hash value of the chunk from which the citation text was drawn",
      "verification_status": "verified"
    }}
  ],
  "linked_objects": [],
  "entities": ["list of entities mentioned, e.g. Data Fiduciary, Data Principal"],
  "relations": []
}}

Return ONLY a valid JSON list. Do not include markdown wraps like ```json or any other text before/after. Return a raw JSON array.
"""

        print(f"[*] Sending {len(evidence_packet.get('chunks', []))} chunks to LLM for structuring...")
        response = self.model_client.generate(prompt)
        
        # Clean response if LLM accidentally wrapped it in code blocks
        response = response.strip()
        if response.startswith("```json"):
            response = response[7:]
        if response.endswith("```"):
            response = response[:-3]
        response = response.strip()
        
        try:
            structured_kos = json.loads(response)
            if not isinstance(structured_kos, list):
                structured_kos = [structured_kos]
            print(f"[+] Structured {len(structured_kos)} Knowledge Objects from document.")
            return structured_kos
        except Exception as e:
            print(f"[!] Error parsing LLM response as JSON: {e}")
            print(f"--- LLM Output Start ---\n{response}\n--- LLM Output End ---")
            return []
