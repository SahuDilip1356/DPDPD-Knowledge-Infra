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
        Extracts structured titles and publication dates from HTML table rows or text context.
        """
        pdf_pattern = r'href=["\'](https?://[^"\']+\.pdf)["\']'
        urls = re.findall(pdf_pattern, html_source, re.IGNORECASE)
        
        signals = []
        for url in set(urls):
            filename = os.path.basename(url)
            
            # Extract date if present in URL (e.g. G.S.R_811_E_13_11_2025.pdf -> 2025-11-13)
            date_match = re.search(r'(\d{1,2})[-_](\d{1,2})[-_](\d{4})', url)
            if date_match:
                day, month, year = date_match.groups()
                date_str = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
            else:
                date_str = datetime_today_str()

            # Clean title from filename
            clean_title = filename.replace(".pdf", "").replace("-", " ").replace("_", " ").title()
            
            signals.append({
                "source_url": url,
                "scraped_title": clean_title,
                "scraped_date": date_str,
                "layer": source_layer
            })
        return signals

    def poll_meity_notifications(self) -> List[Dict]:
        """
        Polls the official MeitY notifications index page and extracts matching DPDPA / Privacy notifications.
        """
        url = "https://www.meity.gov.in/notifications"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        
        print(f"[*] ScoutAgent: Polling MeitY Notifications at '{url}'...")
        try:
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            html = response.text
        except Exception as e:
            print(f"[!] ScoutAgent: Failed to connect to MeitY Notifications page: {e}")
            return []

        # Find all PDF links alongside their text
        link_pattern = r'<a[^>]+href=["\']([^"\']+\.pdf)["\'][^>]*>(.*?)</a>'
        matches = re.findall(link_pattern, html, re.IGNORECASE | re.DOTALL)

        signals = []
        keywords = ["personal data", "privacy", "dpdp", "protection", "consent", "rules", "gazette"]
        
        for href, anchor_text in matches:
            # Strip inner HTML tags from anchor text
            clean_text = re.sub(r'<[^>]+>', '', anchor_text).strip()
            clean_text = " ".join(clean_text.split())
            
            # Combine href and title to check keywords
            combined = f"{href} {clean_text}".lower()
            if any(kw in combined for kw in keywords):
                # Build absolute URL if relative
                absolute_url = href
                if href.startswith("/"):
                    absolute_url = "https://www.meity.gov.in" + href
                
                # Clean up title if empty
                title = clean_text if clean_text else "MeitY Notification " + os.path.basename(href).replace(".pdf", "")
                
                if not any(s["source_url"] == absolute_url for s in signals):
                    signals.append({
                        "source_url": absolute_url,
                        "scraped_title": title,
                        "scraped_date": datetime_today_str(),
                        "layer": 3  # Trust Layer 3 = Regulator/MeitY Circulars
                    })
                    
        print(f"[+] ScoutAgent: Found {len(signals)} matching notifications.")
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
        if "mock" in url or url.startswith("mock://"):
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
