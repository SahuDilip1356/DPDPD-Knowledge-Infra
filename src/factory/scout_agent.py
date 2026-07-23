import os
import requests
import re
from typing import List, Dict

class ScoutAgent:
    def __init__(self, download_dir: str = "staging/inbox"):
        """
        Initializes the Scout & Collection Agent. Downloads are saved in the inbox directory.
        """
        self.download_dir = os.path.abspath(download_dir)
        os.makedirs(self.download_dir, exist_ok=True)

    def scout_feed(self, html_source: str, source_layer: int) -> List[Dict]:
        """
        Scans a raw HTML string or feed index for links to Gazette or rule notifications (PDFs).
        Returns a list of identified signals.
        """
        # Look for PDF links
        pdf_pattern = r'href=["\'](https?://[^"\']+\.pdf)["\']'
        urls = re.findall(pdf_pattern, html_source, re.IGNORECASE)
        
        signals = []
        for url in set(urls):
            filename = os.path.basename(url)
            title = filename.replace(".pdf", "").replace("-", " ").title()
            signals.append({
                "source_url": url,
                "scraped_title": title,
                "scraped_date": datetime_today_str(),
                "layer": source_layer
            })
        return signals

    def download_document(self, url: str) -> str:
        """
        Downloads a document URL to the inbox directory. Returns the local file path.
        Supports mock downloads if the URL is a test trigger.
        """
        filename = os.path.basename(url)
        if not filename.endswith(".pdf"):
            filename += ".pdf"
            
        dest_path = os.path.join(self.download_dir, filename)
        
        # Test Mock Handler
        if url.startswith("mock://"):
            with open(dest_path, "w") as f:
                f.write("Mock PDF Content - Gazette Rule 4.1 Notice is bilingual.")
            return dest_path

        # Real Network Handler
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        with open(dest_path, "wb") as f:
            f.write(response.content)
            
        return dest_path

def datetime_today_str() -> str:
    from datetime import datetime
    return datetime.utcnow().strftime("%Y-%m-%d")
