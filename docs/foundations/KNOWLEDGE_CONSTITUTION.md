# The Knowledge Constitution

This document defines the formal ontology, object schemas, and core vocabulary of the Regulatory Knowledge Infrastructure. It serves as the constitutional contract for all processing departments, storage engines, and applications.

---

## 1. Constitutional Definitions

This Constitution establishes the core principles that define how knowledge is captured, validated, and versioned in the infrastructure.

### I. What is Truth?
* **Definition:** Truth in this system is not a static assertion; it is the current consensus of primary legal authorities. 
* **The Rule:** The system itself holds no opinions. "Truth" is represented by active, un-superseded **Normative Statements** and **Judicial Interpretations** published by established Authorities, backed by cryptographic evidence. If two authorities contradict each other, both are stored as competing active nodes in the graph; the system does not pick a winner but explicitly exposes the contradiction.

### II. What is Evidence?
* **Definition:** Evidence is the raw material from which knowledge is synthesized.
* **The Rule:** An assertion cannot exist in the knowledge graph without an explicit link to a Source Document chunk. Each piece of evidence must contain:
  1. A coordinate pointer (page, line, section, or time offset).
  2. A cryptographic hash (SHA-256) of the original text/media chunk.
  3. The Source Registry identifier of the originating document.

### III. How is Confidence Measured?
* **Definition:** Every Knowledge Object is assigned a `confidence_score` between `0.0` and `1.0`.
* **The Rule:** The score is calculated mathematically by the Verification Department based on the source layers:
  $$\text{Confidence Score} = \text{Layer Trust Weight} \times \text{Verification Coefficient}$$
  * *Layer Trust Weights:* Layer 1 (Primary Government Gazette) = 1.0; Layer 2 (Courts) = 0.9; Layer 3 (Regulators) = 0.7; Layer 4 (Expert Opinions) = 0.5; Layer 5 (Industry Guidance) = 0.3; Layer 6 (Discussions) = 0.2; Layer 7 (Operational Checklists) = 0.6; Layer 8 (Community Signals) = 0.1.
  * *Verification Coefficient:* Set to `1.0` if the cryptographic chunk hash matches the source document, and `0.5` if the source is unverified or lacks direct coordinates.

### IV. How are Conflicts Resolved?
* **Definition:** A conflict occurs when two active Knowledge Objects make contradictory assertions (e.g., MeitY guidance conflicts with a High Court ruling).
* **The Rule:** We do not overwrite or delete. The Contradiction Department creates a `Conflicts With` edge between the two objects. Downstream applications are forced to display both nodes with their respective confidence scores, letting the user see the exact point of tension and its citations.

### V. How is Knowledge Versioned?
* **Definition:** Knowledge is versioned using an immutable, append-only commit ledger.
* **The Rule:** Every Knowledge Object is versioned sequentially (`v1`, `v2`, `v3`). When a change occurs, the existing object's status transitions to `superseded`, its `successor_urn` is set, and a new object is created with an incremented version. The database retains the entire historical state, enabling users to travel back in time to see what the regulations were at any historical date.

### VI. When is Knowledge Obsolete?
* **Definition:** A Knowledge Object becomes obsolete when it is explicitly repealed or superseded by a primary authority.
* **The Rule:** Its status is updated to `superseded` or `obsolete`, but it is never deleted from the Git Ledger or the Graph database. It remains in the system to preserve history and to resolve past compliance states.

### VII. What Makes a Source Authoritative?
* **Definition:** Authority is determined by legal jurisdiction and constitutional power.
* **The Rule:** Only entities of Layer 1 (Parliament, Ministries, Gazettes) and Layer 2 (Appellate Tribunals, High Courts, Supreme Court) can establish, amend, or repeal a Normative Statement. Lower-tier sources (expert opinions, industry posts) can interpret or explain, but they can never overwrite primary authority nodes.

### VIII. What Constitutes a Knowledge Object?
* **Definition:** A Knowledge Object (KO) is a self-contained, typed, versioned, and cited package of regulatory reality.
* **The Rule:** Every KO must contain:
  * **ID (URN):** A deterministic, unique URN (e.g., `urn:ki:in:dpdp:act:2023:sec:6`).
  * **Title & Type:** The name and ontology class of the object.
  * **Summary:** A concise synthesis of the regulatory concept.
  * **Evidence:** Citations linking directly to source documents and coordinate hashes.
  * **Entities:** Ontology nouns referenced within the object.
  * **Relationships:** Typed verbs linking this object to other objects.
  * **Confidence:** The verified evidence confidence score (0.0 to 1.0).
  * **Version & History:** Git-like commit ledger and lineage track.
  * **Last Verified:** Time of last department verification.
  * **Business Impact & Recommendations:** Actionable compliance directives and operational controls.

---

## 2. Ontology First: The Nouns and Verbs of Privacy

We build vocabulary before we build software. The system models the privacy universe using 23 specific Nouns (Entities) and 14 Verbs (Relationships).

### The Nouns (Entities)
1. **Act:** Primary legislation (e.g., DPDPA 2023).
2. **Rule:** Delegated legislation (e.g., DPDP Rules 2026).
3. **Notification:** Government announcements or orders.
4. **Circular:** Clarifications published by ministries or boards.
5. **Case:** A legal dispute filed in court.
6. **Judgement:** A final court decision.
7. **Opinion:** Expert commentary, academic paper, or advisory.
8. **Organization:** Corporate entity, Ministry, or NGO.
9. **Person:** Individual citizen, judge, expert, or data principal.
10. **Template:** Legal draft, clause, or policy template.
11. **Risk:** Compliance risk or threat category.
12. **Control:** Operational counter-measure (technical or organizational).
13. **Purpose:** Reason for data processing (e.g., Billing, Marketing).
14. **Consent:** Consent mechanism or requirements details.
15. **Legal Basis:** Lawful ground for processing (e.g., Consent, Legitimate Use).
16. **Penalty:** Fines or enforcement actions.
17. **Data Category:** Classification of data (e.g., Biometric, Financial).
18. **Industry:** Specific commercial vertical (e.g., Fintech, Healthcare).
19. **Business Process:** Internal operational workflow (e.g., User Onboarding).
20. **Software:** System or application processing data.
21. **Vendor:** Third-party data processor.
22. **Country:** Jurisdiction boundaries.
23. **Authority:** Regulatory body (e.g., DPBI, MeitY).

### The Verbs (Relationships)
1. **Amends:** Modifies the text/scope of another node.
2. **Supersedes:** Replaces another node entirely, making it obsolete.
3. **Interprets:** Clarifies or defines the legal meaning of a node.
4. **Depends On:** Indicates a structural or execution dependency.
5. **Overrides:** Takes legal precedence under specific conditions.
6. **Conflicts With:** Highlights a direct contradiction between two nodes.
7. **Supports:** Provides supporting evidence or commentary.
8. **Implements:** Realizes a normative rule via a control or template.
9. **References:** Mentions another node without modifying it.
10. **Requires:** Outlines a mandatory prerequisite or obligation.
11. **Applies To:** Limits the scope to specific industries, categories, or processes.
12. **Violates:** Documents an action or process that breaks a control.
13. **Explains:** Provides layperson commentary or expert translation.
14. **Replaces:** Directly swaps one tool or process for another.

---

## 3. Event-Centric Graph Architecture

We do not build around documents; we build around **Events**. 

A document is merely evidence of an event. When a change happens in the world (e.g., "DPDP Rules Published"), the system captures the event as the central node and links all incoming files and subsequent updates to it:

```
                  [ Government Notification ] (Gazette PDF)
                               │
                               ▼ (Evidence For)
  [ 20 News Articles ] ──> [ Event: DPDP Rules Published ] <── [ 5 Expert Opinions ]
                               │
                               ├──────────────────────────────────────┐
                               ▼ (Triggers Updates To)                ▼ (Updates)
                   [ Normative Statement: Notice URN ]       [ Compliance Templates ]
                               │                                      │
                               ▼ (Modifies)                           ▼ (Requires)
                   [ Business Process Onboarding ] ───────────> [ Operational Control ]
```

By placing the **Event** at the center:
* Ten different articles or opinions are collapsed into **one synthesized Event node** linked to all evidence sources.
* Downstream impact is computed from the Event outwards: when the Event node is committed, the Relationship Engineering department traces all affected Normative Statements, updating the status of downstream controls, templates, and application modules automatically.
