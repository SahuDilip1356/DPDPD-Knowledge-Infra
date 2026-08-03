import os
import shutil
import pytest
from src.factory.scout_agent import ScoutAgent
from src.factory.parsing_agent import ParsingAgent
from src.factory.citation_agent import CitationAgent

TEMP_STAGING_DIR = os.path.abspath("src/tests/temp_staging")

@pytest.fixture
def clean_staging():
    if os.path.exists(TEMP_STAGING_DIR):
        shutil.rmtree(TEMP_STAGING_DIR)
    yield ScoutAgent(TEMP_STAGING_DIR)
    if os.path.exists(TEMP_STAGING_DIR):
        shutil.rmtree(TEMP_STAGING_DIR)

def test_ingestion_pipeline(clean_staging):
    # 1. Scout/Collection Department: Download mock PDF
    url = "mock://gazette-rules.pdf"
    local_path = clean_staging.download_document(url)
    assert os.path.exists(local_path)
    assert local_path.endswith("gazette-rules.pdf")

    # 2. Parsing Department: Extract pages and paragraphs
    parser = ParsingAgent()
    parsed_pages = parser.parse_pdf(local_path)
    assert len(parsed_pages) == 1
    assert parsed_pages[0]["page_num"] == 1
    assert len(parsed_pages[0]["paragraphs"]) == 1
    assert "Gazette Rule 4.1 Notice is bilingual." in parsed_pages[0]["paragraphs"][0]

    # 3. Citation Department: Generate verified evidence packet
    citation = CitationAgent()
    source_urn = "urn:ki:in:dpdp:source:gazette-2026-rules"
    packet = citation.generate_evidence_packet(
        source_urn=source_urn,
        source_layer=1,
        parsed_pages=parsed_pages
    )

    # 4. Verify evidence envelope structure
    assert packet["source_urn"] == source_urn
    assert packet["layer"] == 1
    assert len(packet["chunks"]) == 1
    
    chunk = packet["chunks"][0]
    assert chunk["urn"] == f"{source_urn}:page-1:chunk-1"
    assert chunk["text"] == "Mock PDF Content - Gazette Rule 4.1 Notice is bilingual."
    
    # 5. Verify cryptographic hashes
    assert len(chunk["coordinates"]["hash"]) == 64
    # The hash should be correct for the text
    expected_hash = citation.compute_sha256(chunk["text"])
    assert chunk["coordinates"]["hash"] == expected_hash

def test_scanned_pdf_vision_ocr(tmp_path):
    """
    Verifies that ParsingAgent triggers visual OCR via ModelClient
    when standard text extraction returns no content.
    """
    # 1. Create a dummy scanned PDF with binary header but no extractable text
    dummy_pdf = tmp_path / "scanned.pdf"
    with open(dummy_pdf, "wb") as f:
        f.write(b"%PDF-1.4\n%scanned_images_only_no_text_bytes\n")

    # 2. Mock ModelClient to return structured layout OCR JSON
    class MockModelClient:
        def __init__(self):
            self.calls = []

        def generate_vision(self, prompt: str, mime_type: str, file_bytes: bytes) -> str:
            self.calls.append({
                "prompt": prompt,
                "mime_type": mime_type,
                "file_bytes": file_bytes
            })
            return """
            [
              {
                "page_num": 1,
                "paragraphs": [
                  "Visual Page 1 Paragraph 1",
                  "Visual Page 1 Paragraph 2"
                ]
              },
              {
                "page_num": 2,
                "paragraphs": [
                  "Visual Page 2 Paragraph 1"
                ]
              }
            ]
            """

    mock_client = MockModelClient()
    parser = ParsingAgent(model_client=mock_client)

    # 3. Execute visual parsing
    results = parser.parse_pdf(str(dummy_pdf))

    # 4. Verify OCR pipeline triggered
    assert len(mock_client.calls) == 1
    assert mock_client.calls[0]["mime_type"] == "application/pdf"
    
    # 5. Verify results structured correctly
    assert len(results) == 2
    assert results[0]["page_num"] == 1
    assert results[0]["paragraphs"][0] == "Visual Page 1 Paragraph 1"
    assert results[1]["page_num"] == 2
    assert results[1]["paragraphs"][0] == "Visual Page 2 Paragraph 1"

def test_scout_poll_meity(monkeypatch):
    """
    Verifies that ScoutAgent.poll_meity_notifications extracts matching
    data protection/privacy PDFs from MeitY page HTML.
    """
    scout = ScoutAgent()

    # Mock HTML source simulating the MeitY notifications page
    mock_html = """
    <html>
      <body>
        <table>
          <tr>
            <td>
              <a href="/writereaddata/files/dpdp_rules_notification_2026.pdf"><b>Notification for Digital Personal Data Protection Rules 2026</b></a>
            </td>
          </tr>
          <tr>
            <td>
              <a href="/writereaddata/files/quantum_computing_advisory.pdf">Advisory on Quantum Technology Standards</a>
            </td>
          </tr>
          <tr>
            <td>
              <a href="https://www.meity.gov.in/writereaddata/files/consent_manager_specification_v1.pdf">Consent Manager Specifications</a>
            </td>
          </tr>
        </table>
      </body>
    </html>
    """

    class MockResponse:
        def __init__(self):
            self.text = mock_html
            self.status_code = 200
        def raise_for_status(self):
            pass

    # Monkeypatch requests.get to return our mock page instead of hit MeitY
    import requests
    monkeypatch.setattr(requests, "get", lambda *args, **kwargs: MockResponse())

    signals = scout.poll_meity_notifications()
    
    # Check that we extracted the 2 notifications matching privacy keywords:
    # 1. dpdp_rules_notification_2026.pdf (matches "dpdp" and "rules")
    # 2. consent_manager_specification_v1.pdf (matches "consent")
    # And we filtered out quantum_computing_advisory.pdf
    assert len(signals) == 2
    
    assert signals[0]["source_url"] == "https://www.meity.gov.in/writereaddata/files/dpdp_rules_notification_2026.pdf"
    assert "Digital Personal Data Protection Rules 2026" in signals[0]["scraped_title"]
    assert signals[0]["layer"] == 3
    
    assert signals[1]["source_url"] == "https://www.meity.gov.in/writereaddata/files/consent_manager_specification_v1.pdf"
    assert "Consent Manager Specifications" in signals[1]["scraped_title"]

def test_publishing_webhook(monkeypatch):
    """
    Verifies that PublishingAgent triggers a webhook POST alert
    when a new Knowledge Object is successfully published.
    """
    from src.factory.publishing_agent import PublishingAgent
    from src.tests.test_reasoning_pipeline import make_ko

    webhook_url = "http://mock-webhook.org/alert"
    monkeypatch.setenv("SUBSCRIBER_WEBHOOK_URL", webhook_url)

    post_calls = []

    class MockResponse:
        def raise_for_status(self):
            pass

    import requests
    def mock_post(url, json=None, timeout=None):
        post_calls.append({"url": url, "json": json, "timeout": timeout})
        return MockResponse()

    monkeypatch.setattr(requests, "post", mock_post)

    publishing = PublishingAgent()
    ko_data = {
        "urn": "urn:ki:in:dpdp:rule:new-notification",
        "title": "Consent Notice Rules 2026",
        "source": {
            "name": "DPDP Rules 2026 Gazette",
            "layer": 1
        },
        "date": "2026-07-27",
        "version": 1,
        "summary": "Detailed consent forms must specify all target categories.",
        "entities": ["Rule", "Consent"],
        "evidence": [{
            "source_urn": "urn:ki:in:dpdp:source:rules-2026",
            "citation_text": "Detailed consent forms must specify all target categories.",
            "coordinates": {
                "page": 1,
                "section": "Paragraph 1",
                "hash": "a" * 64
            }
        }],
        "business_impact": {
            "impact_summary": "Requires update to data consent templates.",
            "action_required": "Redesign UI screens to capture detailed consent categories."
        },
        "confidence_score": 0.9,
        "relations": [{
            "target_urn": "urn:ki:in:dpdp:act:sec-6",
            "edge_type": "Implements"
        }],
        "linked_objects": ["urn:ki:in:dpdp:act:sec-6"],
        "history": [{
            "version": 1,
            "system_time": "2026-07-27T12:00:00Z",
            "commit_message": "initial rules notification"
        }]
    }
 
    receipt = publishing.publish(ko_data)
 
    assert receipt["status"] == "PUBLISHED"
    assert len(post_calls) == 1
    assert post_calls[0]["url"] == webhook_url
    assert post_calls[0]["json"]["urn"] == "urn:ki:in:dpdp:rule:new-notification"


