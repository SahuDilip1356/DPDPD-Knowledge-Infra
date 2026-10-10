# Founding Memo: The Regulatory Knowledge Infrastructure

**To:** The Core Build Team  
**From:** The Architecture Office  
**Date:** July 23, 2026  
**Subject:** Bedrock Philosophy, Mental Model, and Invariants for the AWS of Regulatory Knowledge

---

## 1. The One-Sentence Vision

> **Build India’s canonical Knowledge Infrastructure for Digital Personal Data Protection—an evidence-first, continuously learning, event-centric knowledge graph that transforms regulatory change into structured knowledge, trusted reasoning, and operational decisions for businesses, developers, researchers, and future AI systems.**

We are not trying to build a DPDPA application. We are trying to build a **Knowledge Infrastructure**. 

Google did not start by building Gmail, Amazon did not start by building Prime, and GitHub did not start by building Copilot. They first built infrastructure. Everything else became applications on top. This project is completely separate from SaralPrivacy; SaralPrivacy is merely the first consumer application of this infrastructure.

---

## 2. The Mental Model: AWS of Regulatory Knowledge

We are building the **AWS of Regulatory Knowledge**. Not another website, not another AI chatbot, and not another search engine. We are building the foundational infrastructure that every future compliance, risk, and legal product can consume. 

This model changes every design decision:
* **Infrastructure first, application second.**
* **Scale for decades, not release cycles.**
* **Treat vocabulary (ontology) as the ultimate contract.**

---

## 3. First Principles & The Four Truths

Our design is grounded in four fundamental truths:

```
+-----------------------------------------------------------------------------------+
|                                  THE FOUR TRUTHS                                  |
|                                                                                   |
|  [ Truth 1: Continuous Change ]  --------->  System must continuously learn.      |
|  [ Truth 2: Multi-Evidence Truth ]  ------>  Store evidence, not opinions.        |
|  [ Truth 3: Decisions over Documents ]  -->  Output is Decision Intelligence.     |
|  [ Truth 4: Connected Universe ]  -------->  The Knowledge Graph is the product.  |
+-----------------------------------------------------------------------------------+
```

1. **Truth 1: Knowledge continuously changes.** Therefore, the system must continuously learn. It cannot be static or frozen.
2. **Truth 2: No single document represents truth.** Truth emerges from multiple evidence sources. Therefore, we store raw evidence, not opinions.
3. **Truth 3: People don't want documents; they want decisions.** Therefore, our output is **Decision Intelligence**, not raw PDFs or summaries.
4. **Truth 4: Every piece of knowledge is connected.** Acts connect to Rules $\rightarrow$ Notifications $\rightarrow$ Cases $\rightarrow$ Expert Opinions $\rightarrow$ Business Processes $\rightarrow$ Templates $\rightarrow$ Controls $\rightarrow$ Software $\rightarrow$ Business Decisions. The knowledge graph is the product.

---

## 4. The Three Layers

Everything we build fits into three decoupled layers:

```
+-------------------------------------------------------------------------+
|                              APPLICATIONS                               |
|        (SaralPrivacy, Assessment, Discovery, DSAR, APIs, Playbooks)     |
+-------------------------------------------------------------------------+
                                    │
                                    ▼ (Consumes Layer 2)
+-------------------------------------------------------------------------+
|                            REASONING LAYER                              |
|   (Disposable AI; asks: What changed? Why? Who is affected? Conflicts?) |
+-------------------------------------------------------------------------+
                                    │
                                    ▼ (Retrieves from Layer 1)
+-------------------------------------------------------------------------+
|                        KNOWLEDGE INFRASTRUCTURE                          |
| (Alexandria: Objects, Evidence, History, Ontology, Registries. Permanent) |
+-------------------------------------------------------------------------+
```

* **Layer 1: Knowledge Infrastructure (The Library of Alexandria):** This never changes. It only grows. Everything enters here; nothing is lost. It houses Knowledge Objects, Evidence, Relationships, Ontology, registries (Entity, Source, Citation), taxonomies, and version history. *Nothing intelligent happens here. It simply remembers forever.*
* **Layer 2: Reasoning (Disposable AI):** The AI layer never memorizes. It queries Layer 1 to answer: *What changed? Why? Who is affected? What conflicts exist? How certain are we? What recommendations change?* Reasoning is disposable; knowledge is permanent. **We do not train the model; we train the knowledge.**
* **Layer 3: Applications (Consumer Products):** Where applications like SaralPrivacy, assessments, risk mapping, consent managers, and compliance portals live. Every app consumes Layer 2.

---

## 5. The Founding Principle (The Flywheel)

Every morning, the system wakes up and asks: **"Has the world changed?"** If yes, it executes the following cycle:

```
[Acquire] ──> [Compare] ──> [Understand] ──> [Update] ──> [Republish] ──> [Notify] ──> [Repeat]
```

This flywheel never ends.

---

## 6. The 20-Year Design Invariants

These are the ten principles we commit to and will rarely change:

1. **Knowledge over content:** Treat every regulatory insight as structured knowledge, not as a page, note, or article.
2. **Evidence before opinion:** Every assertion must be traceable directly to authoritative sources.
3. **Events over documents:** Model changes in the real world (events), not individual publications or news articles.
4. **Graphs over folders:** Relational connections matter more than storage hierarchies.
5. **Version everything:** Knowledge should evolve without losing history. Users should be able to travel through time like Git.
6. **AI reasons; it does not remember:** The intelligence layer retrieves and synthesizes from the knowledge layer; it does not speak from model weights.
7. **Infrastructure before applications:** Build reusable, neutral capabilities first; products are downstream consumers.
8. **Open knowledge, proprietary intelligence:** Grow the ecosystem through open canonical graphs while preserving competitive advantage in reasoning APIs.
9. **Ontology before implementation:** Invest heavily in the language, nouns, and verbs of the system before writing application logic.
10. **Build an institution, not a product:** Design for decades, not release cycles. Settle the constitution first.
