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
