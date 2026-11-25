# Research Factory Design: Block-Wise Multi-Agent Architecture

This document details the concrete, block-wise implementation of the Research Factory. It defines the coding constructs, agent configuration classes, schemas, and pipelines required to build the 8-department agent ecosystem using the Google Antigravity SDK.

---

## 1. High-Level Orchestration Pattern (Google Antigravity SDK)

The Research Factory is managed by a central supervisor script, `factory_orchestrator.py`. This script registers the 8 departments as independent agent instances, handles pipeline state transitions, and manages errors.

```
                              [ Factory Orchestrator ]
                                         │
        ┌──────────────┬─────────────────┼──────────────┬──────────────┐
        ▼              ▼                 ▼              ▼              ▼
   [ Research ]   [ Verification ]   [ Knowledge ]   [ Ontology ]   [ Relations ] ...
```

### Agent Configuration Bootstrap (Python)
Every agent in the factory is instantiated with a customized `LocalAgentConfig`, binding specific system instructions, tool capabilities, and safety policies:

```python
from google.antigravity import Agent, LocalAgentConfig, types

# Shared config blueprint for processing departments
def create_department_config(
    name: str, 
    system_instruction: str, 
    tools: list
) -> LocalAgentConfig:
    return LocalAgentConfig(
        capabilities=types.CapabilitiesConfig(
            enable_subagents=True,
            allowed_commands=["git"], # Allowed commands for the Publisher
        ),
        persona=types.PersonaConfig(
            name=name,
            system_instruction=system_instruction,
        ),
        tools=tools,
        model="gemini-2.5-pro", # Target reasoning model
    )
```

---

## 2. Department-by-Department Specifications

---

### Department 1: Research Agent (The Scout)
* **Core Role:** Periodically monitors the external environment (Layers 1-8) for new regulatory artifacts, judicial updates, blog posts, and community discussions.

```
[ Sources List ] ──> [ Research Agent ] ──> [ Signals Output Folder ]
```

* **System Persona & Prompt:**
  ```
  You are the Head of Research. Your role is to monitor Indian regulatory feeds for updates regarding the Digital Personal Data Protection Act (DPDPA). Do not analyze the legal content; your sole objective is to discover and flag new documents, URL links, and metadata. Focus on finding new Gazettes, MeitY circulars, HC/SC privacy cases, NASSCOM commentary, and expert opinions.
  ```
* **Tools:**
  * `fetch_rss_feeds(feed_urls: list)`: Reads external RSS updates.
  * `web_search_query(query: str)`: Searches target legal blogs and notifications using search APIs.
  * `scrape_page_url(url: str)`: Scrapes HTML elements from identified targets.
* **Input Schema:**
  ```json
  {
    "monitored_sources": [
      { "name": "MeitY Notifications", "url": "https://www.meity.gov.in/notifications", "frequency_minutes": 60 }
    ]
  }
  ```
* **Output Schema (`RawSignal`):**
  ```json
  {
    "source_url": "https://egazette.gov.in/WriteReadData/2026/123456.pdf",
    "scraped_title": "DPDP Notice Rules 2026",
    "scraped_date": "2026-07-23",
    "layer": 1,
    "ingested_at": "2026-07-23T21:03:00Z"
  }
  ```
* **Guardrails:** Verify that the extracted `source_url` resolves with a successful HTTP 200 before publishing.

---

### Department 2: Verification Agent (The Gatekeeper)
* **Core Role:** Evaluates the signal list, downloads the raw files, removes duplicate noise, and generates immutable text coordinates with SHA-256 hashes.

```
[ RawSignal ] ──> [ Verification Agent ] ──> [ VerifiedEvidencePacket ]
```

* **System Persona & Prompt:**
  ```
  You are the Head of Verification. Your role is to validate incoming regulatory files. Check that the file download is complete and uncontaminated. Clean the text, extract standard Markdown, and segment the file into paragraphs. For each paragraph, compute an absolute coordinate mapping (page, section) and a cryptographic hash to serve as the evidence foundation.
  ```
* **Tools:**
  * `download_asset(url: str)`: Downloads PDF/HTML to the local scratch directory.
  * `convert_to_markdown(filepath: str)`: Normalizes layouts and transcribes non-text assets.
  * `compute_block_hashes(markdown_content: str)`: Splits text into paragraphs and hashes each individually.
* **Input Schema:** `RawSignal` object.
* **Output Schema (`VerifiedEvidencePacket`):**
  ```json
  {
    "source_urn": "urn:ki:in:dpdp:source:gazette-2026-123456",
    "checksum": "sha256_file_hash...",
    "layer": 1,
    "chunks": [
      {
        "id": 1,
        "text": "Data fiduciaries shall provide a notice to the data principal...",
        "coordinates": { "page": 2, "section": "Rule 4.1", "hash": "sha256_paragraph_hash..." }
      }
    ]
  }
  ```
* **Guardrails:** Cryptographic hash checks are mandatory. Any block that fails coordinates parsing is redirected to a manual formatting queue.

---

### Department 3: Knowledge Engineering Agent (The Architect)
* **Core Role:** Transforms verified text fragments into draft Knowledge Objects conforming to the JSON schema in the constitution.

```
[ VerifiedEvidencePacket ] ──> [ Knowledge Engineering Agent ] ──> [ DraftKnowledgeObject ]
```

* **System Persona & Prompt:**
  ```
  You are the Head of Knowledge Engineering. Your role is to convert raw legal text fragments into structured compliance objects. Extract the core legal concept, summarize it, and populate the metadata fields. Maintain absolute traceability; align each block to its coordinate hashes.
  ```
* **Tools:**
  * `generate_draft_ko(payload: dict)`: Schema constructor.
* **Input Schema:** `VerifiedEvidencePacket`.
* **Output Schema:** Draft `KnowledgeObject` JSON matching the Schema in the Constitution.
* **Guardrails:** The agent must output JSON containing 100% of the required schema fields, or the orchestrator rejects the turn.

---

### Department 4: Ontology Agent (The Lexicographer)
* **Core Role:** Ensures all terms and referenced entities map strictly to the 23 constitutional nouns (e.g. mapping "Company" to "Organization", "penalty clause" to "Penalty").

```
[ DraftKnowledgeObject ] ──> [ Ontology Agent ] ──> [ VocabularyAlignedKO ]
```

* **System Persona & Prompt:**
  ```
  You are the Head of Ontology. Your role is to enforce vocabulary discipline. Review the entities referenced in the draft Knowledge Object. You must normalize all entities into the 23 defined constitutional Nouns (Act, Rule, Notification, Circular, Case, Judgement, Opinion, Organization, Person, Template, Risk, Control, Purpose, Consent, Legal Basis, Penalty, Data Category, Industry, Business Process, Software, Vendor, Country, Authority). If a noun is outside this vocabulary, map it to the closest match or raise a structural alert.
  ```
* **Tools:**
  * `get_ontology_schema()`: Returns the list of 23 approved nouns.
  * `resolve_synonyms(word: str)`: Looks up approved vocabulary matches.
* **Input Schema:** Draft `KnowledgeObject`.
* **Output Schema:** `VocabularyAlignedKO` (where the `entities` array contains only constitutional nouns).
* **Guardrails:** Rejects the KO if it contains any entity type not registered in the schema.

---

### Department 5: Relationship Engineering Agent (The Weaver)
* **Core Role:** Scans the active graph to connect the new KO to existing nodes using the 14 constitutional verbs.

```
[ VocabularyAlignedKO ] ──> [ Relationship Engineering Agent ] ──> [ RelationalGraphTransaction ]
```

* **System Persona & Prompt:**
  ```
  You are the Head of Relationship Engineering. Your role is to construct the edges of the Knowledge Graph. Review the aligned Knowledge Object and locate related active nodes in the database. Map edges using only the 14 approved verbs (Amends, Supersedes, Interprets, Depends On, Overrides, Conflicts With, Supports, Implements, References, Requires, Applies To, Violates, Explains, Replaces).
  ```
* **Tools:**
  * `query_graph_nodes(filters: dict)`: Searches the graph DB.
  * `validate_relation(source: str, target: str, verb: str)`: Checks relationship sanity.
* **Input Schema:** `VocabularyAlignedKO`.
* **Output Schema (`RelationalGraphTransaction`):**
  ```json
  {
    "ko_urn": "urn:ki:in:dpdp:rule:consent-notice",
    "new_relations": [
      { "target_urn": "urn:ki:in:dpdp:act:sec-6", "edge_type": "IMPLEMENTS" }
    ]
  }
  ```
* **Guardrails:** Validate target existence. Edges pointing to orphaned or non-existent URNs are rejected.

---

### Department 6: Reasoning Agent (The Analyst)
* **Core Role:** Evaluates the transaction against the active graph to spot direct logical conflicts or contradictions.

```
[ RelationalGraphTransaction ] ──> [ Reasoning Agent ] ──> [ EvaluatedGraphTransaction ]
```

* **System Persona & Prompt:**
  ```
  You are the Head of Reasoning. Analyze this proposed graph transaction. Search the surrounding graph nodes for contradictions. If MeitY guidance, expert opinions, or court judgments make claims that conflict with this object, write a Conflict Report. Do not summarize; analyze the soundness of the claims based on source trust weights.
  ```
* **Tools:**
  * `fetch_neighborhood_subgraph(urn: str, depth: int)`: Returns surrounding nodes/edges.
  * `evaluate_contradictions(node_a_data: dict, node_b_data: dict)`: Logic evaluator.
* **Input Schema:** `RelationalGraphTransaction`.
* **Output Schema (`EvaluatedGraphTransaction`):**
  ```json
  {
    "transaction": {},
    "conflicts_detected": [
      { "target_urn": "urn:ki:in:dpdp:opinion:expert-a", "conflict_type": "contradiction", "rationale": "Expert asserts notice can be in regional language only, but Notification 123 requires bilingual." }
    ]
  }
  ```
* **Guardrails:** If a conflict is discovered, automatically generate a `Conflicts With` edge to be added to the transaction.

---

### Department 7: Business Translation Agent (The Translator)
* **Core Role:** Translates legal terminology into practical, actionable business recommendations and maps them to operational controls.

```
[ EvaluatedGraphTransaction ] ──> [ Business Translation Agent ] ──> [ ActionableKO ]
```

* **System Persona & Prompt:**
  ```
  You are the Head of Business Translation. Legal text is useless to an operations team unless translated. Your job is to define exactly what changes for businesses. Explain the actions required, which roles (CISO, Privacy Officer, Developer) are affected, and what controls/checklists must be updated.
  ```
* **Tools:**
  * `search_control_index(query: str)`: Searches corporate control repositories.
  * `get_compliance_playbook(industry: str)`: Fetches playbook templates.
* **Input Schema:** `EvaluatedGraphTransaction`.
* **Output Schema:** Fully populated `KnowledgeObject` including `business_impact` properties.
* **Guardrails:** Rejects translations that are vague (e.g. "comply with rules"). Instructions must detail concrete changes (e.g. "Update consent page to show notice before checkbox").

---

### Department 8: Publishing Agent (The Registrar)
* **Core Role:** Commits the validated, translated object to the Git Ledger, updates index databases, and fires webhooks.

```
[ ActionableKO ] ──> [ Publishing Agent ] ──> [ Commits to Git & Graph Database ]
```

* **System Persona & Prompt:**
  ```
  You are the Head of Publishing. Your role is to write the finalized transaction to the immutable Git Ledger and index stores. Run git commands to commit the JSON file, execute writes to the Postgres/Spanner database, and notify downstream applications via webhook.
  ```
* **Tools:**
  * `write_json_to_ledger(urn: str, data: dict)`: Saves to the file system.
  * `git_commit_push(commit_message: str)`: Executes git commands.
  * `notify_subscribers(event_data: dict)`: Dispatches webhooks.
* **Input Schema:** Finalized `KnowledgeObject`.
* **Output Schema:** Transaction confirmation (ledger hash).
* **Guardrails:** Transaction must be atomic. If the Git write succeeds but the database write fails, the agent must perform a rollback.

---

## 3. Data Flow and Queueing Mechanics

To ensure reliable, decoupled processing, the pipeline runs via **Staged Folders** representing processing queues:

```
[Scout API] ──> /inbox/ ──> [Verification] ──> /evidence/ ──> [Knowledge Eng] ──> /drafts/ ──> [Ontology & Relationship] ──> /validated/ ──> [Reasoning & Translation] ──> /actionable/ ──> [Publishing] ──> /ledger/ (Active)
```

1. **Inbox State:** Raw files downloaded by Collection.
2. **Evidence State:** Markdown conversions with verified coordinate hashes.
3. **Draft State:** Schema-conforming JSON objects.
4. **Validated State:** Ontology-aligned and relationship-linked transactions.
5. **Actionable State:** Inspected for conflicts and appended with business impact details.
6. **Active State:** Committed to Git and searchable in the Graph.
