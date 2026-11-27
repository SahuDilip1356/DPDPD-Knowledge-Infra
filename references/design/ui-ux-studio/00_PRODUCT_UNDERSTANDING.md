# Product Understanding: Regulatory Knowledge Infrastructure

## Purpose of this folder

This folder is a separate workspace for discussing and designing the application's UI and UX. It does not alter the existing architecture, source code, schemas, tests, or frontend.

This first note captures my current understanding after reading:

- The supplied founding discussion
- All authored architecture and planning documents in the repository
- The Knowledge Object schema
- The Python storage, factory, reasoning, API, and test code
- The existing React frontend and its components

It is a foundation for discussion, not a final UI specification.

---

## 1. My understanding in one sentence

This product is a continuously updated, evidence-first operating system for regulatory knowledge: it converts changes in law into versioned, connected, explainable knowledge and then turns that knowledge into decisions and actions for different users and downstream applications.

---

## 2. What the product is—and is not

### It is

- A permanent regulatory memory
- A canonical, versioned knowledge graph
- An evidence and citation system
- A change-detection and impact-analysis engine
- A decision-intelligence layer
- A reusable infrastructure platform for many applications
- An institutional workflow represented by specialized departments/agents

### It is not

- Merely a DPDPA information website
- Merely a document repository
- Merely a legal search engine
- Merely an AI chatbot
- Merely a SaralPrivacy feature
- A system in which an LLM's memory is treated as legal truth

SaralPrivacy is best understood as one downstream consumer. The infrastructure should remain product-neutral enough to serve compliance applications, researchers, developers, regulators, auditors, legal teams, and future AI systems.

---

## 3. The central product promise

The user should be able to move from:

> Something changed in the regulatory world

to:

> Here is exactly what changed, the evidence for it, how it relates to existing law, where uncertainty or conflict exists, who is affected, what must be done, and what downstream controls or products need to change.

That end-to-end transformation is the real product.

The graph is the underlying product, but the user's experienced value is trustworthy movement from **change to decision to action**.

---

## 4. The three-layer model

### Layer 1: Knowledge Infrastructure

This is the permanent system of record—the "Library of Alexandria."

It contains:

- Knowledge Objects
- Source documents and evidence chunks
- Citation coordinates and cryptographic hashes
- Entities and ontology
- Graph relationships
- Confidence and trust metadata
- Current and historical versions
- Legal time and system time
- Source, entity, and citation registries

Its governing principle is preservation. Knowledge is appended, versioned, superseded, or made obsolete, but history is not erased.

### Layer 2: Reasoning

This is the replaceable intelligence layer.

It retrieves relevant knowledge and asks:

- What changed?
- Why does it matter?
- Who is affected?
- What conflicts exist?
- How confident are we?
- What recommendations, controls, templates, or applications must change?

The model is not the source of truth. It reasons over retrieved, cited knowledge. A future model can replace the current one without replacing the knowledge core.

### Layer 3: Applications

These are user-facing experiences and integrations:

- SaralPrivacy
- Compliance assessments
- Regulatory change monitoring
- Consent and notice products
- DSAR tooling
- Industry playbooks
- Research interfaces
- Developer APIs
- Enterprise risk and control systems

The infrastructure therefore needs both an internal operating interface and external application experiences.

---

## 5. The operating model: an institution, not a feature set

The Research Factory is organized as departments with defined responsibilities:

1. **Research / Scout** discovers signals and source material.
2. **Verification / Citation** validates sources, extracts evidence, and creates hashes and coordinates.
3. **Knowledge Engineering / Parsing** converts evidence into structured Knowledge Objects.
4. **Ontology** normalizes vocabulary and prevents duplicate concepts.
5. **Relationship Engineering** connects objects using approved relationship types.
6. **Reasoning** detects conflicts, supersessions, gaps, and emerging patterns.
7. **Business Translation** turns legal meaning into role-specific actions.
8. **Publishing** validates and commits knowledge to the ledger and indexes.

Deduplication is an important supporting capability: multiple reports about the same real-world change should converge around one event instead of becoming disconnected copies.

From a UX perspective, this creates two complementary ways to understand the system:

- **Pipeline view:** Where is this item in the institutional workflow?
- **Knowledge view:** What does this object mean and how is it connected?

Both are needed, but they serve different mental tasks and should not be collapsed into one screen.

---

## 6. The core domain object

The Knowledge Object is the fundamental unit of the system. It is more than a content card. It is a typed, traceable, temporal, operational package.

Its important dimensions are:

- **Identity:** deterministic URN
- **Meaning:** title, type, summary, entities
- **Provenance:** source, evidence, coordinates, hashes
- **Authority:** source layer and confidence
- **Time:** legal date, version, system history
- **Context:** relations and linked objects
- **Impact:** business meaning, affected actors, required action
- **State:** current, superseded, obsolete, conflicted, or under review

A useful UI should not expose all fields with equal visual weight. It should progressively reveal them according to the user's question:

1. What is it?
2. Is it trustworthy and current?
3. What changed?
4. What is it connected to?
5. What does it require me to do?
6. Can I inspect the original evidence?

---

## 7. The constitutional vocabulary

The system deliberately constrains knowledge into a shared language.

### Nouns

Act, Rule, Notification, Circular, Case, Judgement, Opinion, Organization, Person, Template, Risk, Control, Purpose, Consent, Legal Basis, Penalty, Data Category, Industry, Business Process, Software, Vendor, Country, and Authority.

### Verbs

Amends, Supersedes, Interprets, Depends On, Overrides, Conflicts With, Supports, Implements, References, Requires, Applies To, Violates, Explains, and Replaces.

This is more than backend validation. It should shape the interface:

- Object types can provide consistent visual and interaction patterns.
- Relationship verbs should be readable as meaningful sentences, not merely graph labels.
- Users should be able to filter and traverse by noun and verb.
- Unknown or disputed mappings should appear as governance work, not be silently normalized.

---

## 8. Events are more important than documents

The strongest product idea is event-centricity.

A Gazette, article, podcast, judgment, post, or expert opinion is evidence or interpretation around something that happened. The system should center the event and connect:

- The authoritative source
- Supporting or conflicting interpretations
- Affected obligations
- Superseded knowledge
- Business processes and controls
- Templates and product modules
- Required actions and notifications

This suggests that the most valuable high-level UI is not a document feed. It is a **regulatory change/event feed** in which each event explains its evidence, impact radius, status, and downstream consequences.

---

## 9. Truth, confidence, and conflict

The system does not define truth as a single confident AI answer.

Its model is:

- Primary authority establishes or changes norms.
- Lower-tier material may interpret, explain, or support.
- Every assertion needs traceable evidence.
- Confidence is derived from source trust and verification.
- Contradictions are preserved and connected.
- The interface must not hide unresolved conflict.

This has major UX consequences:

- Confidence must not be reduced to a decorative percentage.
- Users need to understand why a confidence score exists.
- "Verified" must identify what was verified: source integrity, citation coordinates, authority, or interpretation.
- Conflicting nodes should be compared side-by-side.
- A grounded answer should clearly distinguish law, interpretation, inference, and recommended action.
- Absence of evidence must be shown honestly as insufficient evidence, not filled with fluent text.

Trust is not a visual style. It is the product's inspectable behavior.

---

## 10. Time and versioning are first-class

The system is bi-temporal:

- **Legal time:** when a rule is or was legally effective
- **System time:** when the infrastructure learned or recorded it

It also maintains immutable object versions.

Therefore users need to be able to answer:

- What is effective today?
- What was effective on a historical date?
- When did the system learn of the change?
- Which version changed?
- What was added, removed, or superseded?
- Which downstream controls changed because of it?

The existing Git timeline communicates auditability, but the eventual UX should make temporal comparison a primary workflow rather than only showing a list of commits.

---

## 11. Likely user groups

The repository does not yet define formal personas, but the product structure implies several distinct user groups.

### A. Compliance and privacy leaders

Need to know what changed, organizational exposure, deadlines, owners, and evidence.

### B. Legal researchers and counsel

Need precise sources, citations, authority, conflicts, interpretations, temporal state, and graph context.

### C. Business and control owners

Need plain-language obligations, affected processes, concrete actions, priority, and completion state.

### D. Knowledge operators

Need to supervise ingestion, verification, ontology alignment, relationships, conflicts, exceptions, and publication.

### E. Auditors and reviewers

Need provenance, version history, approvals, evidence integrity, and an explanation of how a conclusion was reached.

### F. Developers and product teams

Need stable APIs, object schemas, graph queries, webhooks, versions, and impact signals for downstream applications.

### G. Executives

Need a concise view of major regulatory events, organizational impact, risk, readiness, and unresolved decisions.

One universal dashboard will not serve these groups well. The information architecture should share a common knowledge core while offering role-oriented entry points.

---

## 12. Core jobs the interface should support

### Monitor

- See significant new regulatory events
- Understand freshness, source coverage, and pipeline status
- Detect items needing human review

### Investigate

- Open a Knowledge Object
- Trace it to exact evidence
- Explore its graph neighborhood
- Compare competing interpretations
- Inspect historical versions

### Decide

- Understand what changed and why
- Evaluate confidence and conflict
- Determine applicability to an organization, industry, process, or role
- Record a reviewed conclusion where human governance is required

### Act

- Convert obligations into tasks
- Assign owners, priorities, and deadlines
- Connect actions to controls, templates, systems, and business processes
- Track completion without losing the legal rationale

### Govern

- Review ontology exceptions
- Confirm or reject proposed relationships
- Resolve duplicates
- Approve publication
- Audit every transformation and decision

### Integrate

- Discover APIs and schemas
- Subscribe to graph changes
- Inspect graph versions
- Test grounded queries

---

## 13. The existing frontend

The React/Vite frontend is a useful proof of concept. It currently presents four top-level views:

1. **Ask Intelligence** — a chat interface with citations and grounded/ungrounded states
2. **Knowledge Graph** — a searchable object list and object-detail inspector
3. **Business Actions** — a role- and priority-filtered checklist
4. **Version History** — a Git-style ledger timeline

It also includes:

- Mock Knowledge Objects
- Mock business actions and commit events
- A live/offline API mode
- Confidence scores
- Evidence coordinates and hashes
- Object relations
- Constitutional entity tags
- Business-impact summaries

### What this prototype gets right

- It exposes more than chat.
- It keeps evidence visible.
- It connects legal knowledge to business action.
- It acknowledges version history.
- It demonstrates the system's four major output surfaces.

### What it does not yet express

- The event-centric model
- The Research Factory workflow
- Human review and governance queues
- Real graph visualization and path exploration
- Conflict comparison
- Supersession and before/after differences
- Legal time versus system time
- Applicability to a particular organization
- Source authority hierarchy
- The relationship between a regulatory event and its full downstream impact radius
- Role-specific workspaces
- Operational ownership, assignment, and durable completion

The current interface is therefore best treated as an exploratory console, not yet as the final product information architecture.

---

## 14. What the implementation currently demonstrates

The backend is a functional skeleton rather than only architecture prose.

It includes:

- JSON Schema validation for Knowledge Objects
- An append-oriented Git ledger abstraction
- SQLAlchemy models and a database client
- Bi-temporal retrieval
- PDF/text parsing and citation hashing
- Ontology normalization
- Relationship proposal and orphan detection
- Deduplication and merge proposals
- Conflict, supersession, gap, and pattern detection
- Business obligation and action generation
- Publishing validation and audit logs
- A factory orchestrator
- A grounded reasoning engine with insufficient-evidence fallback
- FastAPI endpoints for health, query, object lookup, and graph differences
- Tests for schemas, storage, graph engineering, reasoning, publishing, orchestration, and APIs

The system currently relies heavily on deterministic/local logic and mocks. This is appropriate for validating contracts and flows, but the UI must distinguish:

- Implemented and verified behavior
- Demonstration/mock data
- Proposed future AI capability
- Human-reviewed versus machine-proposed knowledge

Without these distinctions, the interface could overstate maturity or certainty.

---

## 15. Important architectural tensions to resolve before detailed UI design

These are not necessarily flaws; they are decisions that the product needs to make explicit.

### Storage direction

Some documents describe Git plus PostgreSQL/Spanner, while another proposes Firestore as the hot graph/vector store. The UI can remain storage-agnostic, but developer tooling and real-time behavior will depend on the chosen architecture.

### Department naming and count

The conceptual model describes eight departments, while the implementation distributes verification across Scout, Parsing, and Citation and adds Deduplication as a supporting agent. The user-facing operational model should use stable department names even if internal services differ.

### Immutable history versus mutable active indexes

The permanent ledger is append-only, but active database records and statuses must change. The UI should explain the distinction between immutable historical truth and the current active projection.

### Confidence semantics

The Constitution proposes a simple trust-weight formula, while actual legal confidence may require separate dimensions: source authority, extraction integrity, interpretation certainty, freshness, and human review status. A single number may conceal rather than communicate trust.

### Open core versus sensitive enterprise context

Canonical law and citations may be public, while an organization's systems, controls, gaps, assignments, and decisions may be private. The UX and permission model should visibly separate public knowledge from proprietary organizational overlays.

### Automated action versus human accountability

The system can propose relationships, conflicts, and actions, but high-impact legal conclusions may require review. The product must decide where human approval is mandatory and make responsibility visible.

---

## 16. Proposed UI/UX design principles

These follow from the product rather than from visual taste.

1. **Lead with change and impact.** Start with what happened and who/what is affected.
2. **Make every conclusion inspectable.** Evidence, reasoning, versions, and graph paths must be reachable.
3. **Use progressive disclosure.** Provide clarity first and forensic detail on demand.
4. **Separate fact, interpretation, inference, and action.** Never visually blend them.
5. **Design conflicts as first-class objects.** Do not bury disagreement in warning text.
6. **Make time navigable.** Current state, effective dates, learned dates, and historical state should be clear.
7. **Keep legal context attached to operational work.** A task should always retain its source obligation and evidence.
8. **Support role-specific entry points.** Shared truth does not require identical screens.
9. **Show machine and human agency.** Users should know what was extracted, inferred, reviewed, approved, or published—and by whom.
10. **Prefer meaningful language over infrastructure jargon.** URNs, hashes, and graph terminology remain available, but the primary interface should speak in events, obligations, impacts, and actions.
11. **Treat insufficient evidence as a valid outcome.** Honest uncertainty is a trust feature.
12. **Design the product as an institutional console.** The interface should convey responsibility, queues, governance, and continuity—not only content consumption.

---

## 17. A likely future information architecture

This is an initial hypothesis for discussion, not a committed design.

### Today / Command Center

- Important regulatory events
- Changes since last visit
- High-impact obligations
- Unresolved conflicts
- Items awaiting review
- Organizational actions at risk

### Change Intelligence

- Event feed
- Event detail
- Change comparison
- Impact radius
- Notifications and subscriptions

### Knowledge Explorer

- Search
- Object detail
- Evidence viewer
- Graph traversal
- Source registry
- Historical state

### Decisions and Actions

- Role-specific action queue
- Applicability decisions
- Owners and deadlines
- Controls, templates, systems, and processes
- Completion evidence

### Research Factory

- Pipeline states
- Review queues
- Failed or ambiguous items
- Ontology exceptions
- Proposed relationships
- Duplicate clusters
- Publication approvals

### Intelligence

- Grounded question answering
- Saved investigations
- Cited reports
- Query scope and evidence coverage

### Developer Platform

- API explorer
- Schemas
- Webhooks
- Graph versions and diffs
- Integration health

### Governance

- Knowledge Constitution
- Vocabulary management
- Trust tiers
- Audit history
- Access and review policies

---

## 18. The most important end-to-end experience

The flagship experience should likely be a Regulatory Change Workspace:

1. A new event is detected.
2. The authoritative evidence and lower-tier commentary are grouped around it.
3. The system explains what changed compared with the previous legal state.
4. Conflicts and uncertainties are shown.
5. The graph reveals affected obligations, controls, templates, processes, vendors, and software.
6. The system proposes role-specific actions and deadlines.
7. A qualified user reviews applicability and recommendations.
8. Actions are assigned and tracked.
9. Publication updates downstream applications and APIs.
10. The entire chain remains auditable from action back to evidence.

If this experience is clear, the product's large architectural vision becomes tangible to a user.

---

## 19. Questions for our next UI/UX discussion

These questions should be resolved collaboratively before high-fidelity design:

1. Who is the first paying or primary user of this interface?
2. Is the first interface an internal Knowledge Factory console, an enterprise compliance workspace, or both?
3. What decisions may the machine make automatically, and which require human approval?
4. What organizational context will be stored as a private overlay?
5. Which event/change workflow should be the first complete demonstration?
6. Should the product initially focus only on India's DPDPA or visibly support multiple regulatory domains from the beginning?
7. What is the canonical department naming model presented to users?
8. What does "confidence" need to mean in the UI?
9. Which role owns a final applicability decision?
10. What must be auditable for legal defensibility?

---

## 20. Recommended next design sequence

1. Agree on the first user and first end-to-end job.
2. Define public knowledge versus private organizational overlays.
3. Map the Regulatory Change Workspace journey.
4. Define object, event, conflict, evidence, action, and review states.
5. Create the information architecture and navigation model.
6. Produce low-fidelity wireframes.
7. Test the wireframes against three scenarios:
   - A new authoritative rule supersedes earlier guidance.
   - A court interpretation conflicts with regulator guidance.
   - A change affects multiple business controls and applications.
8. Only then define the visual system and high-fidelity screens.

---

## Closing understanding

The deepest idea in this project is not "AI for privacy." It is the separation of permanent, evidence-backed knowledge from replaceable reasoning and downstream products.

The corresponding UI/UX opportunity is to make a complex regulatory knowledge institution feel understandable and actionable without hiding its evidence, uncertainty, conflicts, or history.

The ideal experience should let an executive understand the impact in one minute, a compliance owner act on it in ten minutes, and a legal researcher verify every conclusion down to the source coordinate.
