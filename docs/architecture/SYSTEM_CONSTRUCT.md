# System Construct and Agentic Layer Design

This document details the end-to-end structural construct, database schemas, directory layouts, and agentic handshakes that compile the Regulatory Knowledge Infrastructure into a single, cohesive machine.

---

## 1. Physical Storage & Schema Construct

The storage system is bi-temporal, versioned, and split into two physical stores: the **Cold Git Ledger** (Open JSON files) and the **Hot Index Store** (PostgreSQL/Spanner Database).

### I. The Cold Git Ledger Directory Structure
Every Knowledge Object (KO) is written as an immutable JSON file inside an structured directory tree within the Git repository.

```
/knowledge-infra-core/ (Git Repository)
├── domain.json                 # Domain metadata (e.g., Privacy, Tax)
├── schema.json                 # JSON schema of Knowledge Objects
└── objects/
    └── in/                     # Jurisdiction: India
        └── dpdp/               # Sub-domain: DPDP Act
            ├── authority/
            │   └── urn_ki_in_dpdp_auth_dpbi/
            │       ├── v1.json
            │       └── v2.json
            ├── source_document/
            │   └── urn_ki_in_dpdp_source_gazette_2026_1/
            │       └── v1.json
            ├── event/
            │   └── urn_ki_in_dpdp_event_rules_notified/
            │       └── v1.json
            └── normative_statement/
                └── urn_ki_in_dpdp_norm_consent_notice/
                    ├── v1.json
                    └── v2.json
```

---

### II. The Hot Index Database Schema (PostgreSQL/Spanner)
To support multi-hop graph queries and bi-temporal query compilation, the Git Ledger JSON files are mirrored into a relational schema:

```sql
-- 1. Knowledge Objects Master Table
CREATE TABLE knowledge_objects (
    urn VARCHAR(255) NOT NULL,
    version INT NOT NULL,
    type VARCHAR(50) NOT NULL,
    title VARCHAR(512) NOT NULL,
    summary TEXT NOT NULL,
    confidence_score NUMERIC(3, 2) NOT NULL,
    system_time_start TIMESTAMP NOT NULL, -- Transaction Commit Time
    system_time_end TIMESTAMP,           -- Null indicates current active version
    legal_time_start TIMESTAMP NOT NULL,  -- Law effective date
    legal_time_end TIMESTAMP,             -- Law superseded date
    body JSONB NOT NULL,                  -- Entity specific parameters
    business_impact JSONB NOT NULL,       -- Actionable instructions
    evidence JSONB NOT NULL,              -- Citation coordinates and hashes
    PRIMARY KEY (urn, version)
);

-- 2. Graph Edges Table (The Network)
CREATE TABLE graph_edges (
    source_urn VARCHAR(255) NOT NULL,
    source_version INT NOT NULL,
    target_urn VARCHAR(255) NOT NULL,
    edge_type VARCHAR(50) NOT NULL,       -- AMENDS, SUPERSEDES, INTERPRETS, etc.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (source_urn, source_version, target_urn, edge_type),
    FOREIGN KEY (source_urn, source_version) REFERENCES knowledge_objects(urn, version)
);

-- 3. Vector Embeddings Table (Semantic Search)
CREATE TABLE vector_citations (
    id SERIAL PRIMARY KEY,
    ko_urn VARCHAR(255) NOT NULL,
    ko_version INT NOT NULL,
    coordinate_hash VARCHAR(64) NOT NULL,
    chunk_text TEXT NOT NULL,
    embedding VECTOR(1536),               -- PGVector field for Gemini embeddings
    FOREIGN KEY (ko_urn, ko_version) REFERENCES knowledge_objects(urn, version)
);
```

---

## 2. The Agentic Pipeline & Handshake Protocol

The 8 departments coordinate sequentially through a **State Envelope Handshake**. Each agent receives a state payload, executes its logic, appends its modifications, and forwards it to the next queue.

```
                    STATE ENVELOPE PIPELINE FLOW
                    
[Signal] ──> [Research] ──> [Verification] ──> [Knowledge Eng] ──> [Ontology]
                                                                        │
[Ledger] <── [Publishing] <── [Business Trans] <── [Reasoning] <── [Relations]
```

### The Processing Envelope Schema
The data envelope passed between agents is defined as follows:

```json
{
  "pipeline_id": "uuid-v4-transaction-id",
  "current_state": "inbox | evidence | drafts | validated | actionable | active",
  "last_updated": "2026-07-23T21:05:00Z",
  "history": [
    { "department": "research", "agent_id": "scout_01", "timestamp": "2026-07-23T21:03:00Z" }
  ],
  "payload": {
    "raw_signal": {},
    "source_file": {},
    "markdown_evidence": {},
    "draft_ko": {},
    "aligned_ko": {},
    "relations_transaction": {},
    "conflict_report": {},
    "final_ko": {}
  }
}
```

---

### Agent Handshake Execution Code (Orchestrator Logic)
The `factory_orchestrator.py` script manages execution state transitions:

```python
class FactoryOrchestrator:
    def __init__(self, agent_instances: dict, storage_client):
        self.agents = agent_instances
        self.storage = storage_client

    async def process_pipeline_step(self, envelope: dict) -> dict:
        state = envelope["current_state"]
        
        if state == "inbox":
            # 1. Verification Handover
            output = await self.agents["verification"].chat(envelope["payload"]["raw_signal"])
            envelope["payload"]["markdown_evidence"] = output.json()
            envelope["current_state"] = "evidence"
            
        elif state == "evidence":
            # 2. Knowledge Engineering Handover
            output = await self.agents["knowledge_engineering"].chat(envelope["payload"]["markdown_evidence"])
            envelope["payload"]["draft_ko"] = output.json()
            envelope["current_state"] = "drafts"

        elif state == "drafts":
            # 3. Ontology & Vocabulary Normalization
            output = await self.agents["ontology"].chat(envelope["payload"]["draft_ko"])
            envelope["payload"]["aligned_ko"] = output.json()
            
            # 4. Relationship Edges Mapping
            output = await self.agents["relationship_engineering"].chat(envelope["payload"]["aligned_ko"])
            envelope["payload"]["relations_transaction"] = output.json()
            envelope["current_state"] = "validated"

        elif state == "validated":
            # 5. Reasoning & Contradiction Detection
            output = await self.agents["reasoning"].chat(envelope["payload"]["relations_transaction"])
            envelope["payload"]["conflict_report"] = output.json()
            
            # 6. Business Impact Translation
            output = await self.agents["business_translation"].chat(envelope["payload"]["relations_transaction"])
            envelope["payload"]["final_ko"] = output.json()
            envelope["current_state"] = "actionable"

        elif state == "actionable":
            # 7. Publishing Commit
            commit_result = await self.agents["publishing"].chat(envelope["payload"]["final_ko"])
            envelope["current_state"] = "active"
            envelope["pipeline_result"] = commit_result.json()

        envelope["last_updated"] = self.current_timestamp()
        return envelope
```

---

## 3. End-to-End Walkthrough: Processing a Gazette Notification

To demonstrate how the system works coherently, we trace the workflow of a real-world event: **The notification of new consent notice rules by the government.**

### Step 1: Ingestion & Verification (The Scout & Gatekeeper)
1. **Research Agent** (Scout) scans the e-Gazette RSS feed and flags Gazette No. 456 containing the newly notified "DPDP Consent Notice Rules 2026." It posts a `RawSignal` to the `/inbox/` directory.
2. **Verification Agent** downloads the PDF, extracts layout-aware Markdown, splits it into paragraph blocks, and assigns SHA-256 hashes to each. It writes the result to `/evidence/`:
   ```json
   {
     "coordinate_hash": "e3b0c442...",
     "text": "Rule 4.1: Notice shall be provided in English and all regional languages listed in Schedule 8..."
   }
   ```

### Step 2: Knowledge Extraction & Ontology (The Architect & Lexicographer)
3. **Knowledge Engineering Agent** reviews the evidence and constructs a draft KO representing the obligation.
4. **Ontology Agent** validates the nouns. It notices the text refers to "Company obligations" and normalizes the entity tags:
   * Maps "Company" $\rightarrow$ `Organization`
   * Maps "DPBI Board" $\rightarrow$ `Authority`
   * Maps "Fines" $\rightarrow$ `Penalty`

### Step 3: Graph Wiring (The Weaver)
5. **Relationship Engineering Agent** queries the database and maps edges between the new KO URN (`urn:ki:in:dpdp:rule:consent-notice`) and the existing ecosystem:
   * `urn:ki:in:dpdp:rule:consent-notice` $\xrightarrow{\text{Depends On}}$ `urn:ki:in:dpdp:act:2023:sec:6` (The primary Act Section authorizing notice rules).
   * `urn:ki:in:dpdp:rule:consent-notice` $\xrightarrow{\text{Supercedes}}$ `urn:ki:in:dpdp:opinion:meity-faq:consent-notice` (Supersedes the old informal MeitY FAQ advice).

### Step 4: Reasoning & Impact Assessment (The Analyst & Translator)
6. **Reasoning Agent** checks the new nodes against active expert opinions. It flags a conflict:
   * *The Conflict:* The newly notified Rule 4.1 mandates notice in *all* regional languages, whereas a prevailing Appellate Court Judgment (`urn:ki:in:dpdp:case:appellate-xyz`) ruled that "bilingual consent notice is sufficient."
   * It creates a `Conflicts With` edge linking the two nodes, marking the conflict.
7. **Business Translation Agent** computes the corporate impact:
   * *Business Action:* Organizations must update their signup screens to support translation into 22 scheduled languages instead of just two.
   * *Affected Controls:* Maps this obligation to Control URN `urn:ki:in:dpdp:control:consent-widget` (The consent frontend checkbox UI).
   * *SOP Update:* Triggers update flag for `urn:ki:in:dpdp:template:notice-format-checklist`.

### Step 5: Publishing & Application Notification (The Registrar)
8. **Publishing Agent** acts:
   * Commits the finalized JSON object to the local Git Ledger.
   * Runs database insertions updating `knowledge_objects` and `graph_edges`.
   * Invokes the Vector Embeddings API to save semantic chunks.
   * Dispatches a webhook notification to **SaralPrivacy**:
     ```json
     {
       "event": "graph_updated",
       "urn": "urn:ki:in:dpdp:rule:consent-notice",
       "affected_controls": ["urn:ki:in:dpdp:control:consent-widget"]
     }
     ```

---

## 4. Grounded Reasoning Layer APIs

Downstream applications execute grounded retrieval over the open infrastructure layer. The API gateway exposes the reasoning layer through FastAPI:

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class QueryRequest(BaseModel):
    question: str
    context_filters: dict = {}

@app.post("/knowledge/query")
async def query_knowledge_base(request: QueryRequest):
    # 1. Fetch relevant subgraph nodes and cited markdown chunks
    subgraph = await graph_store.retrieve_neighborhood(request.question)
    citations = await vector_store.semantic_search(request.question)
    
    # 2. Package context with coordinates
    grounding_context = compile_llm_context(subgraph, citations)
    
    # 3. Invoke Reasoning agent (stateless chip)
    response = await reasoning_agent.generate_response(
        prompt=request.question,
        context=grounding_context
    )
    
    # 4. Return answer backed by verified citation hashes
    return {
        "grounded_answer": response.text,
        "citations": [c.metadata for c in citations],
        "graph_version": ledger.get_latest_hash()
    }
```

This API structure ensures that when SaralPrivacy displays notice compliance guidelines to a business, it displays the **exact text, confidence scores, and legal conflicts** mapped directly to the e-Gazette, ensuring zero hallucinations.
