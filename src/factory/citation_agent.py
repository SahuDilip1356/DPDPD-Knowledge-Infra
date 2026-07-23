import hashlib
from typing import List, Dict

class CitationAgent:
    def __init__(self):
        pass

    def compute_sha256(self, text: str) -> str:
        """
        Computes the SHA-256 checksum of a clean text block.
        """
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def generate_evidence_packet(
        self, 
        source_urn: str, 
        source_layer: int,
        parsed_pages: List[Dict]
    ) -> Dict:
        """
        Constructs a verified evidence packet with exact paragraph chunk hashes and coordinate URNs.
        """
        chunks = []
        chunk_counter = 1
        
        for page in parsed_pages:
            page_num = page["page_num"]
            for p_text in page["paragraphs"]:
                p_hash = self.compute_sha256(p_text)
                
                # Deterministic URN coordinate for this chunk
                chunk_urn = f"{source_urn}:page-{page_num}:chunk-{chunk_counter}"
                
                chunks.append({
                    "urn": chunk_urn,
                    "text": p_text,
                    "coordinates": {
                        "page": page_num,
                        "section": f"Paragraph {chunk_counter}",
                        "hash": p_hash
                    }
                })
                chunk_counter += 1

        return {
            "source_urn": source_urn,
            "layer": source_layer,
            "chunks": chunks
        }
