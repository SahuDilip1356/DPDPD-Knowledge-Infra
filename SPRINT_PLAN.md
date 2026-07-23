# Sprint Plan & Build Sequence: Regulatory Knowledge Infrastructure

This document outlines the detailed build sequence, sprint tasks, milestones, and verification criteria to implement the 3-Layer Knowledge Infrastructure from first principles.

---

## The Build Sequence Model

We build bottom-up, starting with validation and storage rules (Layer 1) before introducing AI agents (Layer 2) and final client connections (Layer 3).

```
[ Sprint 6: API & Downstream Gate ] ──> Layer 3: API Gateway & Webhooks
               ▲
[ Sprint 5: Orchestration & Synth ] ──> Layer 2: Reasoning & Translation
               ▲
[ Sprint 4: Graph Engineering     ] ──> Layer 1: Relations & Deduplication
               ▲
[ Sprint 3: Ingestion Pipeline    ] ──> Layer 1: Ingestion, OCR & Parsing
               ▲
[ Sprint 2: Versioned Ledger DB   ] ──> Layer 1: Git Ledger & SQL Indexes
               ▲
[ Sprint 1: Ontology & Schemas    ] ──> Layer 1: Schema Validation Rules
```

---

## Sprint 1: Schema & Constitution Validation (Bootstrap Phase)
* **Objective:** Define the physical schemas and validation rules of the Knowledge Constitution.
* **Duration:** 1 Sprint (2 Weeks)
* **Tasks:**
  * Define the JSON schemas for Authority, SourceDocument, Event, NormativeStatement, CaseLaw, and ComplianceControl.
  * Code `validate_schema.py` utilizing the `jsonschema` library.
  * Create mock Knowledge Objects (JSON files) representing DPDPA Section 6, the Consent Rules Gazette, and a Supreme Court privacy ruling.
* **Deliverables:**
  * `src/schemas/validate_schema.py`
  * `src/schemas/knowledge_object.json`
* **Verification Checkpoint:** Run unit tests proving that schema-conforming KOs pass validation, while KOs lacking citations, URNs, or confidence scores are rejected.

---

## Sprint 2: Versioned Git Ledger & Database Index Store
* **Objective:** Build the temporal database storage and Git-based change tracking system.
* **Duration:** 1 Sprint (2 Weeks)
* **Tasks:**
  * Set up local Git repository storage routines (`git_ledger.py`) to manage append-only JSON version files.
  * Define SQLAlchemy models matching the `knowledge_objects` and `graph_edges` tables.
  * Implement the bi-temporal query compiler (`db_client.py`) allowing state lookups by transaction time and validity time.
* **Deliverables:**
  * `src/storage/git_ledger.py`
  * `src/storage/db_client.py`
  * `src/storage/models.py`
* **Verification Checkpoint:** Query the DB client using historical legal timestamps and verify that superseded rules revert to their historical states.

---

## Sprint 3: Ingestion & Parsing Pipeline (Departments 1, 2, and 3)
* **Objective:** Construct the OCR layout parser and scrapers to pull and normalise Layer 1-8 sources.
* **Duration:** 1 Sprint (2 Weeks)
* **Tasks:**
  * Build the **Research Agent (Scout)** to poll e-Gazette and ministry RSS directories.
  * Build the **Collection Agent** to safely download PDFs to storage.
  * Build the **Parsing Agent** (using Gemini Layout Vision APIs) to extract text, OCR coordinates, and annotate page/byte coordinates.
  * Implement coordinate-hashing (SHA-256) inside the **Citation Agent**.
* **Deliverables:**
  * `src/factory/scout_agent.py`
  * `src/factory/parsing_agent.py`
  * `src/factory/citation_agent.py`
* **Verification Checkpoint:** Feed a multi-page Gazette PDF to the pipeline and verify that it outputs layout-aware Markdown with valid block hashes and page coordinate references.

---

## Sprint 4: Graph Engineering & Vocabulary Alignment (Departments 4 and 5)
* **Objective:** Implement ontology mapping and connect nodes using graph edges.
* **Duration:** 1 Sprint (2 Weeks)
* **Tasks:**
  * Build the **Ontology Agent** to normalize entity tags against the 23 constitutional nouns.
  * Build the **Relationship Engineering Agent** to resolve node dependencies using the 14 constitutional verbs.
  * Build the **Deduplication Agent** to cluster redundant articles and opinions around Event nodes.
* **Deliverables:**
  * `src/factory/ontology_agent.py`
  * `src/factory/relationship_agent.py`
  * `src/factory/deduplication_agent.py`
* **Verification Checkpoint:** Input 5 mock articles and 1 Gazette notifying a rule change. Confirm they cluster around a single Event node, and correct `SUPERSEDES` and `Depends On` edges are created.

---

## Sprint 5: Orchestration, Contradictions, & Translation (Departments 6, 7, and 8)
* **Objective:** Wire the entire 8-department pipeline and implement compliance logic analysis.
* **Duration:** 1 Sprint (2 Weeks)
* **Tasks:**
  * Develop the **Reasoning Agent** to cross-reference transactions and generate conflict warnings.
  * Develop the **Business Translation Agent** to append operational recommendations and update control indexes.
  * Develop the **Publishing Agent** to commit changes to Git and database.
  * Code `factory_orchestrator.py` to run the state pipeline envelope from start to finish.
* **Deliverables:**
  * `src/factory/reasoning_agent.py`
  * `src/factory/business_translation_agent.py`
  * `src/factory/publishing_agent.py`
  * `src/factory/factory_orchestrator.py`
* **Verification Checkpoint:** Run the complete orchestrator pipeline on a new rule change. Verify that the Git Ledger commits a new JSON file, Postgres matches the state changes, and conflict logs are populated.

---

## Sprint 6: API Gateway & Grounded Reasoning Engine
* **Objective:** Expose the reasoning engine to downstream consumer applications (such as SaralPrivacy) via API.
* **Duration:** 1 Sprint (2 Weeks)
* **Tasks:**
  * Setup a FastAPI server exposing `/knowledge/query`, `/knowledge/objects/{urn}`, and `/knowledge/graph/diff` paths.
  * Build the grounded prompt compiler inside `reasoning_engine.py` (which fetches Graph and Vector contexts first, then passes them to the Gemini model).
  * Build the Webhook/PubSub dispatcher to alert subscribing applications.
* **Deliverables:**
  * `src/api/api_service.py`
  * `src/reasoning/reasoning_engine.py`
* **Verification Checkpoint:** Query the API endpoint for "Notice languages requirements" and inspect the JSON response. Verify that the answer lists specific citations, hashes, and graph version numbers, and is strictly grounded in the database evidence.
