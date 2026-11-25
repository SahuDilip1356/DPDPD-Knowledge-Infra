# Firebase Firestore Database Design

This document outlines the schema, collection structures, and vector search configurations to implement the Regulatory Knowledge Infrastructure on **Firebase / Cloud Firestore**.

---

## 1. Why Firebase Firestore is an Excellent Fit

Firebase Firestore aligns perfectly with our Open Core vs. Proprietary architecture:

1. **Document-Native Design:** Knowledge Objects (KOs) are defined as self-contained JSON records. Firestore stores these as structured document maps out-of-the-box.
2. **Real-Time Synchronisation:** Downstream applications (like SaralPrivacy) can subscribe to Firestore listeners. When a new Gazette rules update is published to Firestore, compliance dashboard controls update in real-time.
3. **Open Access Control (Public Reads):** Using Firebase Security Rules, we can make the `/knowledge_objects` and `/graph_edges` collections read-only public, serving the "Open Knowledge Core" principle. Writing is restricted to the authenticated Research Factory Publishing Agent service account.
4. **Native Vector Search:** Firestore supports vector embeddings and semantic search (using the `Vector32` data type and `createVectorIndex` API). This allows us to perform semantic retrieval (semantic search) and metadata queries directly in Firestore, removing the need for a separate vector database.

---

## 2. Collection and Document Structures

We map the relational model into four core Firestore collections:

```
/source_documents (Collection)
    └── [source_urn_hash] (Document)
        └── chunks (Subcollection)
            └── [chunk_id] (Document: contains text & embedding)

/knowledge_objects (Collection)
    └── [ko_urn_hash] (Document: holds active version metadata & payload)
        └── versions (Subcollection)
            └── [version_number] (Document: bi-temporal history logs)

/graph_edges (Collection)
    └── [edge_id] (Document: represents source-target relations)
```

---

### Collection 1: `/source_documents`
Stores details of ingested Gazette PDFs, Court Cases, and expert articles.

* **Document Path:** `/source_documents/{source_urn_hash}`
* **Fields:**
  ```json
  {
    "urn": "urn:ki:in:dpdp:source:gazette-2026-123456",
    "name": "Notice Rules Gazette Notification No. F. 1/2026",
    "layer": 1,
    "url": "https://egazette.gov.in/WriteReadData/2026/123456.pdf",
    "file_hash": "sha256_file_hash...",
    "ingested_at": "2026-07-23T21:03:00Z"
  }
  ```

#### Subcollection: `/source_documents/{source_urn_hash}/chunks`
Contains block-level text parsed by the Extraction department, complete with vectors.

* **Document Path:** `/source_documents/{source_urn_hash}/chunks/{chunk_index}`
* **Fields:**
  ```json
  {
    "chunk_index": 0,
    "page": 2,
    "section": "Rule 4.1",
    "chunk_hash": "sha256_paragraph_hash...",
    "text": "Data fiduciaries shall provide a notice to the data principal...",
    "embedding": [0.012, -0.045, 0.98, "..."] // Native Firestore Vector32 field
  }
  ```

---

### Collection 2: `/knowledge_objects`
Stores active Knowledge Objects. The parent document represents the **current active version** for fast querying.

* **Document Path:** `/knowledge_objects/{ko_urn_hash}`
* **Fields:**
  ```json
  {
    "urn": "urn:ki:in:dpdp:rule:consent-notice",
    "title": "DPDP Rules 2026 - Notice Requirements",
    "type": "rule",
    "version": 2,
    "summary": "Mandates notice display in English and 22 scheduled languages.",
    "date": "2026-07-23",
    "confidence_score": 1.0,
    "entities": ["Rule", "Organization", "Consent", "Language"],
    "evidence": [
      {
        "source_urn": "urn:ki:in:dpdp:source:gazette-2026-123456",
        "citation_text": "Gazette No. F. 1/2026, Page 2, Rule 4.1",
        "coordinate_hash": "sha256_paragraph_hash..."
      }
    ],
    "business_impact": {
      "impact_summary": "Organizations must support translation of consent notices into 22 scheduled languages.",
      "affected_actors": ["Data Fiduciary", "Consent Manager"],
      "action_required": "Deploy multilingual notice prompts on user onboarding screens."
    },
    "linked_objects": [
      "urn:ki:in:dpdp:act:2023:sec:6",
      "urn:ki:in:dpdp:control:consent-widget"
    ],
    "system_time_start": "2026-07-23T21:05:00Z",
    "legal_time_start": "2026-08-01T00:00:00Z"
  }
  ```

#### Subcollection: `/knowledge_objects/{ko_urn_hash}/versions`
Houses bi-temporal history logs.

* **Document Path:** `/knowledge_objects/{ko_urn_hash}/versions/{version_number}`
* **Fields:** Identical to parent KO fields, documenting historical states (e.g., `v1` prior to modification).

---

### Collection 3: `/graph_edges`
Maps the directional relationships between URNs.

* **Document Path:** `/graph_edges/{edge_id}` (where `edge_id` is a hash of `source_urn` + `target_urn` + `edge_type`)
* **Fields:**
  ```json
  {
    "source_urn": "urn:ki:in:dpdp:rule:consent-notice",
    "target_urn": "urn:ki:in:dpdp:act:2023:sec:6",
    "edge_type": "IMPLEMENTS",
    "created_at": "2026-07-23T21:05:00Z"
  }
  ```

---

## 3. Database Security Rules

To enforce the Open Core strategy, the Firebase Security Rules (`firestore.rules`) allow anyone to view the knowledge graph but only permit authorized agent writes:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Open Core: Allow read access to anyone
    match /source_documents/{document=**} {
      allow read: if true;
      allow write: if request.auth != null && request.auth.token.role == 'factory_publisher';
    }
    match /knowledge_objects/{document=**} {
      allow read: if true;
      allow write: if request.auth != null && request.auth.token.role == 'factory_publisher';
    }
    match /graph_edges/{document=**} {
      allow read: if true;
      allow write: if request.auth != null && request.auth.token.role == 'factory_publisher';
    }
  }
}
```

---

## 4. Query & Vector Routing (Vercel Integration)

 Downstream apps query this infrastructure via the **Reasoning Layer API** hosted on **Vercel Serverless Functions**.

```
[ Downstream App ] ──> [ Vercel Serverless Function ] ──> [ Firebase Firestore Vector Query ]
```

### Serverless Hybrid Query Function (Python / Vercel API)
Below is how a Vercel Serverless Function retrieves and reasons over Firestore vector data:

```python
from google.cloud import firestore
from google.cloud.firestore_v1.vector import Vector

db = firestore.Client()

async def find_grounded_norms(question_embedding: list):
    # Query Firestore using native vector cosine distance search
    collection_ref = db.collection_group("chunks")
    vector_query = collection_ref.find_nearest(
        vector_field="embedding",
        query_vector=Vector(question_embedding),
        distance_measure=firestore.Query.DistanceMeasure.COSINE,
        limit=5
    )
    
    results = []
    docs = vector_query.stream()
    for doc in docs:
        chunk_data = doc.to_dict()
        # Retrieve the parent source document URN
        parent_source_ref = doc.reference.parent.parent
        source_data = parent_source_ref.get().to_dict()
        
        results.append({
            "text": chunk_data["text"],
            "coordinates": {
                "page": chunk_data["page"],
                "section": chunk_data["section"],
                "hash": chunk_data["chunk_hash"]
            },
            "source_name": source_data["name"],
            "source_urn": source_data["urn"]
        })
        
    return results
```
