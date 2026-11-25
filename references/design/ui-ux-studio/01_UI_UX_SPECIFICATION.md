# UI/UX Specification

## Regulatory Knowledge Infrastructure

**Document status:** Draft for discussion  
**Version:** 0.1  
**Date:** 25 July 2026  
**Companion document:** `00_PRODUCT_UNDERSTANDING.md`

---

## 1. Purpose

This document defines the product-level UI and UX specification for the Regulatory Knowledge Infrastructure.

It is intended to guide:

- Product decisions
- Information architecture
- User-flow design
- Wireframes and prototypes
- Frontend implementation
- Backend contract design
- Usability testing
- Accessibility and quality assurance

This specification does not modify or prescribe changes to the current implementation. It describes the target experience from which an MVP and later releases can be designed.

---

## 2. Product definition

The product is an evidence-first regulatory knowledge operating system. It continuously discovers regulatory changes, converts evidence into structured and versioned knowledge, maps relationships and conflicts, determines business impact, and distributes grounded decisions and actions.

The primary user promise is:

> Understand what changed, verify why it is true, determine what it affects, and take the right action.

The interface must make five things consistently visible:

1. **Change** — what happened?
2. **Evidence** — what authoritative material supports it?
3. **Meaning** — how does it affect the existing regulatory position?
4. **Impact** — who, what process, and what control are affected?
5. **Action** — what should happen next, by whom, and by when?

---

## 3. Product boundaries

### 3.1 The interface includes

- Regulatory change monitoring
- Event-centered change workspaces
- Knowledge Object search and exploration
- Evidence and citation inspection
- Graph relationship exploration
- Conflict and supersession analysis
- Business-impact translation
- Action assignment and tracking
- Human review and publishing workflows
- Version and audit history
- Grounded question answering
- Developer integration visibility

### 3.2 The interface does not present

- AI output as unquestionable legal truth
- Unsupported legal advice
- A document feed without synthesis
- A generic chatbot as the primary product
- Raw infrastructure complexity on every screen
- A single confidence score without explanation
- Private organizational context as public knowledge

### 3.3 Product relationship to SaralPrivacy

The infrastructure is an independent platform. SaralPrivacy may consume its APIs and knowledge, but the infrastructure must not be architected as a SaralPrivacy-only admin panel.

The initial visual language may share SaralPrivacy's trust-oriented foundation, but navigation, product naming, permissions, and workflows belong to the Knowledge Infrastructure.

---

## 4. UX principles

### 4.1 Lead with change and consequence

The most prominent content should explain what changed and what it affects. Source documents and system metadata remain one step away.

### 4.2 Evidence is always reachable

Every important claim, conclusion, conflict, and action must provide a path back to:

- Knowledge Object
- Source
- Exact citation
- Location or coordinate
- Verification state
- Relevant version

### 4.3 Separate knowledge states

The UI must distinguish:

- Authoritative fact
- Interpretation
- System inference
- Business recommendation
- Human decision
- Assigned action

These must not appear as visually equivalent statements.

### 4.4 Display uncertainty honestly

The interface must support:

- Insufficient evidence
- Conflicting authorities
- Unverified extraction
- Low-confidence inference
- Pending human review
- Unknown applicability

Uncertainty is a normal product state, not an error to hide.

### 4.5 Preserve context during action

An operational task must retain its connection to the underlying obligation, event, evidence, and review decision.

### 4.6 Use progressive disclosure

The first level answers the user's immediate question. Technical detail—URNs, hashes, graph properties, pipeline logs—appears when requested.

### 4.7 Make time understandable

The product must clearly distinguish:

- Publication date
- Legal effective date
- Date detected by the system
- Date verified
- Date published to the graph
- Historical version

### 4.8 Design for institutional continuity

The interface should support queues, ownership, review, approval, audit, and handoffs. It should not feel like a one-time content viewer.

---

## 5. User roles

One person may have multiple roles. Permissions and default views should be role-aware.

### 5.1 Regulatory observer

Examples:

- Compliance leader
- Privacy officer
- Legal counsel
- Policy researcher

Primary needs:

- Monitor important changes
- Understand legal meaning
- Inspect evidence
- Compare interpretations
- Track effective dates

### 5.2 Business action owner

Examples:

- HR leader
- Product manager
- Security lead
- Marketing lead
- Procurement manager

Primary needs:

- Know what applies to their function
- Understand required action in plain language
- See priority, owner, deadline, and supporting rationale
- Record progress and completion evidence

### 5.3 Knowledge operator

Examples:

- Research analyst
- Knowledge engineer
- Legal editor
- Ontology steward

Primary needs:

- Review pipeline items
- Validate evidence
- Correct extracted fields
- approve concepts and relationships
- Resolve duplicates
- Escalate conflicts
- Publish knowledge

### 5.4 Reviewer or approver

Examples:

- Senior counsel
- Editorial lead
- Compliance authority

Primary needs:

- Review proposed changes
- Compare evidence and reasoning
- Accept, reject, return, or qualify a proposal
- Leave an auditable rationale

### 5.5 Auditor

Primary needs:

- Reconstruct what was known at a given time
- Inspect versions and approvals
- Trace a decision to supporting evidence
- Export audit records

### 5.6 Developer

Primary needs:

- Understand schemas
- Test endpoints
- inspect graph versions and diffs
- Manage webhooks and subscriptions
- Verify integration health

### 5.7 Executive

Primary needs:

- See material regulatory changes
- Understand business exposure and readiness
- Identify unresolved high-risk issues
- Know which teams own the response

---

## 6. Platform model

The UX consists of three connected workspaces.

### 6.1 Intelligence workspace

For observing, investigating, and understanding regulatory knowledge.

Includes:

- Command Center
- Change Intelligence
- Knowledge Explorer
- Ask Intelligence

### 6.2 Operations workspace

For translating knowledge into organizational response.

Includes:

- Decisions
- Actions
- Controls and affected assets
- Organizational applicability

### 6.3 Factory workspace

For producing and governing canonical knowledge.

Includes:

- Research Factory
- Review queues
- Ontology governance
- Publication and audit
- Developer platform

Permissions determine which workspaces are visible.

---

## 7. Information architecture

### 7.1 Primary navigation

Desktop navigation:

1. **Today**
2. **Changes**
3. **Knowledge**
4. **Decisions & Actions**
5. **Factory**
6. **Ask**
7. **Developer**

Utility navigation:

- Global search
- Notifications
- Saved items
- Organization selector
- Help
- User and workspace settings

### 7.2 Role-based navigation

The system should not show irrelevant sections.

Example:

- Business action owners may see Today, Changes, Decisions & Actions, and Ask.
- Knowledge operators may see Today, Changes, Knowledge, Factory, and Ask.
- Developers may see Knowledge, Ask, and Developer.
- Auditors receive read-only access across permitted areas.

### 7.3 Mobile navigation

Mobile uses:

- Bottom navigation for the four most relevant role-based destinations
- “More” sheet for remaining destinations
- Persistent search access
- Context actions within a bottom sheet

---

## 8. Global page framework

### 8.1 Desktop shell

- Collapsible left navigation: 240 px expanded, 72 px collapsed
- Top utility bar: 64 px
- Main content maximum width: 1600 px
- Reading views maximum text width: 760–880 px
- Optional right context panel: 360–440 px

### 8.2 Page header

Every primary page should provide:

- Page title
- One-sentence purpose or current scope
- Relevant scope controls
- Primary action, if any
- Last updated state where freshness matters

### 8.3 Context preservation

When moving between event, object, evidence, action, or graph views:

- Preserve filters
- Preserve selected time
- Preserve organization scope
- Offer a visible back path
- Avoid losing investigation state

### 8.4 Density modes

Operational lists should support:

- Comfortable
- Compact

Default:

- Comfortable for general users
- Compact for Factory and audit users

---

## 9. Global search

### 9.1 Search scope

Search should find:

- Regulatory events
- Knowledge Objects
- Acts, rules, notifications, cases, and judgments
- Authorities and organizations
- Controls and business processes
- Sources and citations
- Actions
- URNs

### 9.2 Search interaction

The search overlay should provide:

- Recent searches
- Saved searches
- Suggested filters
- Results grouped by type
- Keyboard navigation
- Exact-URN lookup

### 9.3 Search filters

- Jurisdiction
- Regulatory domain
- Object type
- Authority
- Source layer
- Effective date
- Publication date
- Status
- Confidence dimension
- Industry
- Business function
- Relationship type

### 9.4 Result presentation

Each result displays:

- Type
- Title
- Short context
- Current status
- Effective date
- Authority/source
- Evidence or relationship count
- Relevant matched text

Search must explain whether the match came from title, summary, entity, evidence, or semantic similarity.

---

## 10. Screen specification: Today / Command Center

### 10.1 Purpose

Give each user an actionable overview of what changed and what requires attention.

### 10.2 Header

Display:

- Greeting or workspace name
- Current jurisdiction and domain
- “Updated X minutes ago”
- Date-range selector
- Customize button

### 10.3 Primary sections

#### A. Material changes

Show the highest-impact regulatory events.

Each row contains:

- Event title
- Event type
- Authority
- Detected date
- Effective date
- Impact level
- Change status
- Affected industries/functions
- Unresolved conflict indicator

#### B. Attention required

Shows:

- Pending review
- Unresolved conflicts
- Low-confidence critical items
- Approaching effective dates
- Overdue organizational actions

#### C. Impact overview

Compact metrics:

- New authoritative changes
- Obligations changed
- Controls affected
- Actions due
- Conflicts open

Metrics must link to the underlying filtered list.

#### D. Factory health

Visible only to permitted roles.

Show:

- Items in pipeline
- Failed extraction
- Review backlog
- Publishing latency
- Source freshness

### 10.4 Empty state

Use:

> No material changes in the selected period.

Then show:

- Last successful source scan
- Current monitoring coverage
- Link to browse all knowledge

Do not imply that “no changes detected” guarantees no external change occurred.

---

## 11. Screen specification: Changes

### 11.1 Purpose

Provide an event-centric view of regulatory change.

### 11.2 Default presentation

A structured change feed, not a news feed.

Each event card or row contains:

- Event name
- Plain-English change summary
- Legal authority
- Jurisdiction
- Publication and effective dates
- Event status
- Evidence count by source tier
- Number of affected Knowledge Objects
- Number of affected organizational assets
- Conflict state
- Review state

### 11.3 Views

- List
- Timeline
- Impact matrix
- Saved watchlist

### 11.4 Filters

- Date
- Authority
- Jurisdiction
- Domain
- Event type
- Legal status
- Review status
- Impact
- Conflict
- Industry
- Business function

### 11.5 Sorting

- Materiality
- Most recent
- Effective soonest
- Most affected assets
- Lowest confidence
- Highest unresolved risk

---

## 12. Screen specification: Regulatory Change Workspace

This is the flagship product experience.

### 12.1 Purpose

Bring evidence, legal change, graph impact, organizational applicability, and action into one coherent workspace.

### 12.2 Header

Display:

- Event title
- Status badge
- Authority
- Jurisdiction
- Published date
- Effective date
- Last verified
- Watch/save control
- Share/export
- Review or approve action when permitted

### 12.3 Summary panel

Answer:

- What happened?
- What changed from the previous position?
- Why does it matter?
- Who is likely affected?

Content labels must identify:

- Verified fact
- System-generated analysis
- Human-reviewed conclusion

### 12.4 Workspace tabs

#### Overview

- Executive summary
- Change severity
- Effective date countdown
- Affected object count
- Affected business areas
- Open conflicts
- Recommended immediate actions

#### Evidence

- Primary authoritative sources first
- Supporting sources grouped by trust tier
- Citation-level viewer
- Extraction verification status
- Source file hash and citation hash on demand

#### What changed

- Previous versus current comparison
- Added, removed, modified, or superseded obligations
- Legal-time comparison
- Version selector

#### Impact

- Impact graph
- Affected Knowledge Objects
- Industries
- Roles
- Processes
- Controls
- Templates
- Software and vendors

#### Conflicts

- Competing claims
- Source authority comparison
- Exact contradiction
- Current resolution state
- Human reviewer notes

#### Decisions & actions

- Applicability decision
- Required actions
- Owners
- Deadlines
- Related controls
- Completion status

#### History

- Detection
- Verification
- Knowledge creation
- Review
- Publication
- Subsequent version changes

### 12.5 Sticky context

On desktop, a right panel may show:

- Current status
- Effective-date countdown
- Confidence breakdown
- Review owner
- Primary next action

### 12.6 Primary actions by role

Observer:

- Follow event
- Save view
- Export brief

Knowledge operator:

- Edit proposal
- Request review
- Link object
- Flag issue

Reviewer:

- Approve
- Approve with qualification
- Return for revision
- Reject

Business owner:

- Assess applicability
- Accept assigned action
- Add implementation evidence

---

## 13. Screen specification: Knowledge Explorer

### 13.1 Purpose

Let users search, inspect, and traverse canonical regulatory knowledge.

### 13.2 Layout

Desktop:

- Left: filters and object list
- Center: selected object
- Right: contextual relationships or evidence

Allow panels to collapse.

### 13.3 Object-list row

- Object type
- Title
- Current/superseded/conflicted status
- Version
- Effective date
- Authority
- Confidence summary
- Relationship count

### 13.4 Knowledge Object detail

#### Identity

- Human-readable title
- Object type
- URN
- Version
- Status

#### Meaning

- Summary
- Legal statement
- Plain-English explanation
- Relevant entities

#### Authority and trust

- Source authority
- Source layer
- Verification status
- Interpretation review state
- Freshness

#### Evidence

- Primary citations
- Exact passages
- Page/section
- Open source action

#### Relationships

Present initially as readable statements:

> Consent Notice Rule implements Section 6 of the DPDPA.

Allow switching to graph representation.

#### Business impact

- Impact summary
- Affected actors
- Required action
- Related controls and templates

#### Time

- Effective period
- Detected date
- System publication date
- Version history

### 13.5 Object actions

- Copy stable link
- Follow
- Compare version
- Open graph
- View source
- Export
- Report an issue

Editing actions are permission-gated.

---

## 14. Evidence viewer

### 14.1 Purpose

Allow a user to verify a claim without leaving the product context.

### 14.2 Layout

Desktop split view:

- Left: source document
- Right: citation metadata and linked claims

Mobile:

- Document and metadata as separate tabs

### 14.3 Required functions

- Navigate to page or section
- Highlight exact cited passage
- Show surrounding context
- Copy citation
- Open original source
- Display source authority and trust tier
- Show file checksum
- Show citation checksum
- Show extraction and verification status
- List Knowledge Objects using the citation

### 14.4 Evidence states

- Source verified; citation verified
- Source verified; citation pending review
- Source available; extraction incomplete
- Source inaccessible
- Citation mismatch

Mismatch is a critical integrity state and must be visually prominent.

---

## 15. Graph Explorer

### 15.1 Purpose

Explain relationships and impact paths, not merely display a visually impressive network.

### 15.2 Default graph behavior

- Start with a selected node and one-hop neighborhood
- Group nodes by object type
- Label relationship direction
- Provide legend
- Prevent label overlap
- Allow expansion on demand
- Preserve a breadcrumb of the exploration path

### 15.3 Controls

- Depth: 1–3 hops
- Relationship types
- Object types
- Time state
- Active versus historical
- Authority
- Confidence/review status
- Organizational overlay on/off

### 15.4 Alternative representations

Every graph result should also offer:

- Relationship list
- Dependency tree
- Impact path

This ensures accessibility and makes complex connections readable.

### 15.5 Path explanation

When a user selects a path, translate it into plain language:

> The new rule implements Section 6, changes the consent-notice obligation, and affects the onboarding consent control.

---

## 16. Conflict Workspace

### 16.1 Purpose

Present disagreement or legal tension transparently.

### 16.2 Comparison layout

Two-column comparison:

- Claim A
- Claim B

For each:

- Exact statement
- Object type
- Authority
- Jurisdiction
- Effective date
- Citation
- Trust dimensions
- Current status

Center or top:

- System explanation of the contradiction
- Relationship type
- Scope of conflict
- Affected downstream conclusions

### 16.3 Resolution states

- Newly detected
- Under review
- Accepted as unresolved
- Resolved by authority
- Superseded
- False positive

### 16.4 Reviewer actions

- Confirm conflict
- Reject conflict
- Narrow the conflict scope
- Add qualification
- Link resolving authority
- Escalate

Every decision requires a rationale and becomes part of the audit history.

---

## 17. Decisions & Actions

### 17.1 Purpose

Convert regulatory knowledge into accountable organizational response.

### 17.2 Views

- My actions
- Team actions
- Decisions required
- By regulatory event
- By control
- Calendar/deadline
- Completed

### 17.3 Action item structure

Each action includes:

- Action title
- Plain-language description
- Source obligation
- Triggering event
- Applicability scope
- Priority
- Owner
- Reviewer
- Due date
- Status
- Related process
- Related control
- Related software/vendor/template
- Completion evidence

### 17.4 Action states

- Proposed
- Applicability review
- Accepted
- In progress
- Blocked
- Ready for review
- Completed
- Not applicable
- Superseded

### 17.5 Applicability decision

The user must be able to record:

- Applies
- Partially applies
- Does not apply
- Unknown / more information required

Required fields:

- Scope
- Rationale
- Decision owner
- Decision date
- Supporting organizational evidence

### 17.6 Completion

Completion must not be a checkbox alone.

For high-impact actions, require:

- Completion note
- Evidence or linked artifact
- Reviewer
- Review outcome

---

## 18. Research Factory

### 18.1 Purpose

Provide an operational console for producing and governing knowledge.

### 18.2 Pipeline board

Columns:

1. Detected
2. Evidence processing
3. Knowledge drafting
4. Ontology review
5. Relationship review
6. Reasoning and conflict review
7. Business translation
8. Publication review
9. Published

Internal service names may differ, but the visible stages must remain stable.

### 18.3 Pipeline item

Display:

- Signal or proposed event
- Source and authority
- Current stage
- Time in stage
- Assigned operator
- Automated checks
- Blocking issue
- Priority
- SLA status

### 18.4 Work queues

- New authoritative sources
- Failed downloads
- Extraction failures
- Citation mismatches
- Unknown ontology terms
- Proposed relationships
- Orphan objects
- Duplicate clusters
- Conflicts
- Publication approvals

### 18.5 Review panel

The panel should combine:

- Original evidence
- Extracted fields
- Proposed object
- Validation issues
- Relationship proposals
- Audit log
- Approve, edit, return, reject actions

Avoid requiring operators to switch across many screens for one review.

---

## 19. Ontology governance

### 19.1 Purpose

Maintain the shared vocabulary without hiding ambiguity.

### 19.2 Views

- Constitutional nouns
- Relationship verbs
- Registered concepts
- Synonyms
- Unresolved terms
- Merge candidates
- Change history

### 19.3 Concept detail

- Canonical term
- Definition
- Type
- Synonyms
- Usage count
- Connected objects
- Similar concepts
- Steward
- Status
- Version history

### 19.4 Governance actions

- Approve synonym
- Reject mapping
- Merge concept
- Propose new constitutional type
- Deprecate term

High-impact ontology changes require review and impact preview.

---

## 20. Ask Intelligence

### 20.1 Purpose

Provide grounded exploration of the knowledge core. It is an investigation tool, not an oracle.

### 20.2 Query composer

Support:

- Natural-language question
- Jurisdiction scope
- Time scope
- Regulatory domain
- Organization context on/off
- Evidence-tier restriction

### 20.3 Answer structure

Every answer should contain:

1. Direct answer
2. Key qualification or uncertainty
3. Supporting claims
4. Citations
5. Relevant conflicts
6. Effective date
7. Suggested next investigation or action

### 20.4 Claim-level citation

Citations should attach to the claim they support. A citation drawer may show full details.

### 20.5 Answer labels

Use:

- Grounded in authoritative evidence
- Grounded with qualifications
- Conflicting evidence
- Insufficient evidence
- Uses private organizational context

### 20.6 Conversation functions

- Follow-up question
- Save investigation
- Add answer to event workspace
- Export cited brief
- Report unsupported claim

### 20.7 Insufficient-evidence response

The interface should state:

- What could not be answered
- What sources were searched
- What evidence is missing
- Which filters may have limited the answer

Do not provide a speculative substitute by default.

---

## 21. Version history and time travel

### 21.1 Object history

Display a chronological sequence of:

- Version created
- Fields changed
- Evidence changed
- Relations changed
- Status changed
- Reviewer and rationale

### 21.2 Compare versions

Support:

- Side-by-side
- Inline diff
- Structured-field diff

Differentiate:

- Legal content changes
- Metadata corrections
- Evidence corrections
- Business-impact changes

### 21.3 Historical state

Provide a global “View as of” control with:

- Legal date
- System-known date

The interface must visibly indicate when historical mode is active.

---

## 22. Developer platform

### 22.1 Pages

- Overview
- API explorer
- Schemas
- Webhooks
- Graph versions
- Changelog
- Integration health

### 22.2 API explorer

For each endpoint:

- Method and path
- Purpose
- Parameters
- Example request
- Example response
- Error states
- Authentication requirement
- Graph version behavior

### 22.3 Webhooks

Display:

- Subscription event
- Destination
- Status
- Last delivery
- Failure count
- Replay action

Secret values must never be shown after creation.

---

## 23. Notifications

### 23.1 Notification types

- New followed regulatory event
- Material update
- Effective date approaching
- Conflict detected
- Review assigned
- Review returned
- Action assigned
- Action overdue
- Publication completed
- Integration failure

### 23.2 Notification controls

Users can configure:

- In-product
- Email
- Webhook for system events
- Frequency
- Jurisdiction
- Domain
- Authority
- Impact threshold

### 23.3 Digest

Support a daily or weekly digest organized by:

- Material changes
- Decisions required
- Actions due
- Factory exceptions

---

## 24. Status system

Statuses must use text plus shape/icon, not color alone.

### 24.1 Knowledge status

- Draft
- Under review
- Active
- Qualified
- Conflicted
- Superseded
- Obsolete
- Rejected

### 24.2 Evidence status

- Verified
- Pending verification
- Extraction incomplete
- Source unavailable
- Integrity mismatch

### 24.3 Review status

- Unassigned
- Assigned
- In review
- Changes requested
- Approved
- Approved with qualification
- Rejected

### 24.4 Severity

- Informational
- Low
- Medium
- High
- Critical

Critical is reserved for real, time-sensitive impact—not general visual emphasis.

---

## 25. Confidence and trust presentation

Do not rely on one percentage.

### 25.1 Trust dimensions

Where data is available, show:

- Source authority
- Source integrity
- Citation integrity
- Extraction quality
- Interpretation confidence
- Human review status
- Freshness

### 25.2 Summary label

Examples:

- High-authority, verified evidence
- Authoritative source; interpretation pending review
- Lower-tier interpretation
- Conflicting authority
- Incomplete evidence

### 25.3 Detail popover

Explain:

- How each dimension was calculated
- What lowers trust
- Who reviewed it
- When it was last verified

---

## 26. Public and private data separation

### 26.1 Public canonical layer

May contain:

- Public source material
- Knowledge Objects
- Citations
- Ontology
- Public graph relationships

### 26.2 Private organizational overlay

May contain:

- Applicability decisions
- Business systems
- Vendors
- Controls
- Assignments
- Internal evidence
- Completion records

### 26.3 UX rules

- Always show current workspace/organization
- Mark private content
- Warn before exporting private context
- Do not include private context in public links
- Allow the user to disable private context in Ask Intelligence

---

## 27. Visual design system

The interface should feel calm, authoritative, operational, and readable.

### 27.1 Core colors

- Trust Navy: `#121A2E`
- Verification Green: `#07B981`
- Assurance Teal: `#35B6AE`
- Signal Gold: `#E8AB42`
- Cloud background: `#F7F9FC`
- White surface: `#FFFFFF`
- Primary text: `#121A2E`
- Body text: `#334155`
- Muted text: `#64748B`
- Border: `#E2E8F0`
- Error: `#B42318`
- Error surface: `#FEF3F2`

### 27.2 Usage

- Navy anchors navigation, headings, and high-trust contexts.
- Green is used for primary actions and verified/approved states.
- Teal is used for links, selected filters, and supportive visualization.
- Gold is used sparingly for approaching deadlines or items requiring attention.
- Red is reserved for actual integrity errors, rejection, destructive action, and critical failure.

### 27.3 Typography

Use:

`Inter, system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif`

Recommended scale:

- Display: 32/40, semibold
- H1: 28/36, semibold
- H2: 22/30, semibold
- H3: 18/26, semibold
- Body: 15/24, regular
- Small: 13/20, regular
- Metadata: 12/18, medium
- Code/URN: a legible monospace stack

### 27.4 Spacing

Use a 4 px base.

Common values:

- 4
- 8
- 12
- 16
- 24
- 32
- 48
- 64

### 27.5 Radius

- Inputs/buttons: 8 px
- Cards/panels: 10–12 px
- Pills: fully rounded

### 27.6 Elevation

Use subtle borders before shadows. Reserve elevation for:

- Menus
- Dialogs
- Sticky context panels
- Dragged items

Avoid decorative glass effects in core operational screens.

---

## 28. Core components

### 28.1 Buttons

Types:

- Primary
- Secondary
- Tertiary/text
- Destructive
- Icon

Every button must have:

- Default
- Hover
- Focus
- Active
- Disabled
- Loading

### 28.2 Badges

Use for:

- Status
- Object type
- Authority tier
- Review state
- Severity

Do not combine more than three badges on a compact row. Move secondary metadata into detail views.

### 28.3 Data table

Must support:

- Sort
- Filter
- Column visibility
- Pagination or virtualization
- Row selection where required
- Keyboard navigation
- Empty and error states

### 28.4 Filter bar

- Common filters visible
- Advanced filters in drawer
- Active-filter count
- Clear all
- Save view
- Share view when permitted

### 28.5 Citation

Compact form:

- Source
- Page/section
- Verification indicator

Expanded form:

- Passage
- Source authority
- Hash
- Linked claims
- Open evidence

### 28.6 Change diff

Use:

- Added
- Removed
- Modified
- Superseded

Never rely on red/green color alone.

### 28.7 Empty states

An empty state should explain:

- What is absent
- Why it may be absent
- What the user can do

### 28.8 Skeletons

Use skeleton loading for known layouts. Use a progress state for long-running reasoning or document extraction.

---

## 29. Interaction patterns

### 29.1 Destructive and high-impact actions

Require confirmation for:

- Rejecting publication
- Superseding a Knowledge Object
- Removing a relationship
- Marking a critical action not applicable
- Revoking access

The dialog must explain consequence and reversibility.

### 29.2 Autosave

Draft reviews and notes may autosave.

Show:

- Saving
- Saved
- Save failed

Approval and publication are always explicit actions.

### 29.3 Bulk actions

Allow only where meaning remains clear:

- Assign reviewer
- Follow/unfollow
- Export
- Change low-risk queue priority

Do not allow bulk legal approval by default.

### 29.4 Keyboard support

Provide:

- `/` focus search
- `Esc` close overlay
- Arrow-key navigation in results
- Clear tab order
- Optional command palette for expert users

---

## 30. Content design

### 30.1 Voice

- Plain English
- Specific
- Non-alarmist
- Evidence-aware
- Action-oriented

### 30.2 Labels

Prefer:

- What changed
- Why it matters
- Evidence
- Affected areas
- Action required
- Needs review

Avoid as primary labels:

- Relational graph transaction
- State envelope
- Vector citations
- Reasoning chip

Technical terms remain available in developer and audit contexts.

### 30.3 Legal posture

Where appropriate:

> This information is evidence-backed regulatory guidance and does not replace advice from qualified legal counsel.

Avoid:

- Guaranteed compliance
- Legally certified
- Zero hallucination
- Definitive language where conflicts or uncertainty exist

---

## 31. Responsive behavior

### 31.1 Breakpoints

- Mobile: under 640 px
- Tablet: 640–1023 px
- Desktop: 1024 px and above
- Wide desktop: 1440 px and above

### 31.2 Mobile priorities

Mobile should support:

- Monitoring changes
- Reading summaries
- Reviewing notifications
- Inspecting actions
- Adding comments or evidence
- Approving simple review steps

Dense graph editing and complex ontology governance may use a desktop-recommended message while retaining read-only access.

### 31.3 Responsive transformations

- Tables become prioritized cards or horizontally scroll with pinned first column.
- Split views become tabs.
- Right panels become bottom sheets.
- Filter sidebars become drawers.
- Graph controls collapse into a toolbar sheet.
- Sticky action bars remain reachable above mobile browser controls.

---

## 32. Accessibility requirements

Target WCAG 2.2 AA.

### 32.1 Required

- Full keyboard navigation
- Visible focus
- Semantic landmarks
- Correct heading hierarchy
- Form labels and error associations
- Screen-reader names for icon buttons
- Status announced through text
- Contrast-compliant text and controls
- Reduced-motion support
- 44 × 44 px touch targets where practical
- Zoom support to 200%

### 32.2 Graph accessibility

Graph data must also be available as:

- A relationship list
- A tree
- A textual path explanation

### 32.3 Diff accessibility

Added, removed, and modified states require:

- Text labels
- Icons or patterns
- Screen-reader announcements

---

## 33. Performance requirements

Initial targets:

- Primary shell interactive within 2.5 seconds on a typical business connection
- Filter response within 300 ms after local data is available
- Search suggestions within 500 ms
- Large table virtualization above 200 visible records
- Graph progressively loads from one-hop neighborhood
- Long reasoning tasks show meaningful progress and can be cancelled

Do not load full graph datasets by default.

---

## 34. Error handling

### 34.1 Error message structure

Explain:

- What failed
- What the system preserved
- What the user can do
- Whether retry is safe

### 34.2 Important errors

- Source unavailable
- Citation integrity mismatch
- Object validation failure
- Graph relationship target missing
- Version conflict
- Publication partial failure
- Reasoning service unavailable
- Insufficient permissions
- Private-context export restriction

### 34.3 Offline or degraded reasoning

If reasoning is unavailable:

- Keep canonical knowledge browsing available
- State that synthesized answers are unavailable
- Do not silently replace live answers with mock output in production

---

## 35. Auditability

Every high-impact state change should record:

- Actor
- Role
- Timestamp
- Previous state
- New state
- Rationale
- Related evidence
- Graph/object version

Audit logs are read-only and filterable.

Export formats:

- PDF brief
- CSV for structured lists
- JSON for machine-readable history

---

## 36. MVP scope

### 36.1 MVP objective

Demonstrate the complete path from one regulatory event to verified evidence, changed knowledge, business impact, and accountable action.

### 36.2 MVP screens

1. Today
2. Changes list
3. Regulatory Change Workspace
4. Knowledge Explorer
5. Evidence viewer
6. Decisions & Actions
7. Factory review queue
8. Ask Intelligence

### 36.3 MVP capabilities

- Browse mock or real regulatory events
- Inspect linked Knowledge Objects
- Inspect exact evidence
- Compare two object versions
- See relationship paths
- Display conflict state
- Generate grounded answer with claim-level citations
- Record applicability
- Create and assign an action
- Review and publish a proposed object
- View audit history

### 36.4 Deferred after MVP

- Full ontology editing
- Advanced developer portal
- Multi-jurisdiction authoring
- Complex organization permissions
- Automated webhook administration
- Advanced graph analytics
- Mobile Factory authoring

---

## 37. Recommended MVP scenario

Use one coherent demonstration:

> A new authoritative consent-notice rule is published, changes the previous interpretation, affects onboarding controls, and requires a multilingual notice update.

The scenario should demonstrate:

1. Event detected
2. Source verified
3. Citation extracted
4. Knowledge Object created
5. Previous guidance superseded or conflicted
6. Affected control identified
7. Business action proposed
8. Human review completed
9. Knowledge published
10. Action assigned
11. Grounded question answered
12. Audit trail inspected

---

## 38. Key success measures

### 38.1 Understanding

- Users can correctly explain what changed after viewing the event.
- Users can distinguish legal fact from system recommendation.

### 38.2 Trust

- Users can reach supporting evidence in no more than two interactions.
- Users can identify authority, effective date, and review status.

### 38.3 Actionability

- Users can determine whether an obligation applies.
- Users can create or accept an action without losing legal context.

### 38.4 Operational efficiency

- Operators can review one pipeline item without unnecessary screen switching.
- Reviewers can understand validation issues and evidence before approval.

### 38.5 Safety

- Unsupported answers are visibly identified.
- Conflicts and insufficient evidence are not hidden.

---

## 39. Usability-test tasks

### Task 1: Understand a change

> Tell us what the new consent-notice rule changes and when it becomes effective.

### Task 2: Verify a claim

> Find the exact authoritative passage supporting the multilingual notice requirement.

### Task 3: Investigate a conflict

> Explain why the new rule conflicts with the earlier interpretation.

### Task 4: Determine impact

> Identify which business process and control are affected.

### Task 5: Record applicability

> Record that the rule applies to your organization and explain why.

### Task 6: Take action

> Assign the required product update to an owner and add a due date.

### Task 7: Factory review

> Review the proposed Knowledge Object and decide whether it is ready to publish.

### Task 8: Ask a question

> Ask what languages a consent notice must support and verify the answer's citations.

---

## 40. Acceptance criteria for design

The first complete design is acceptable when:

- The event is clearly the central unit of change.
- Evidence is reachable from every important conclusion.
- Users can distinguish fact, interpretation, inference, decision, and action.
- Legal time and system time are not confused.
- Conflict is a first-class workflow.
- Organizational actions remain linked to regulatory knowledge.
- Factory review and approval responsibilities are visible.
- The interface works without requiring users to understand URNs or graph terminology.
- Expert users can still access URNs, hashes, versions, and audit metadata.
- Core workflows meet WCAG 2.2 AA requirements.
- Desktop and mobile behavior is specified for every MVP screen.

---

## 41. Design deliverables to create next

1. Sitemap and role-permission matrix
2. Event and Knowledge Object state diagrams
3. Regulatory Change Workspace user journey
4. Low-fidelity desktop wireframes
5. Mobile wireframes for monitoring and actions
6. Component inventory
7. Interactive prototype
8. Usability-test script
9. Revised specification based on findings
10. High-fidelity visual design

---

## 42. Final product experience

The interface should enable three levels of understanding at the same time:

- An executive understands the impact in one minute.
- A compliance owner understands and assigns the response in ten minutes.
- A legal researcher can verify every conclusion down to its precise source and historical version.

That balance—clarity without loss of evidence—is the defining UX requirement of the product.
