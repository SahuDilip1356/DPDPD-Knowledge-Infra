# Question sources — what each one adds

Matching: semantic (text-embedding-3-small, cosine ≥ 0.86).

Unified registry: `staging/competitive_intel/questions/unified_questions.jsonl` (1779 canonical questions, each tagged with the sources that ask it).

## Sources

| Source | Items | What it is | Unique contribution |
|---|---|---|---|
| Canonical graph | 1779 | Questions competitors and SaralPrivacy write, deduplicated and mapped to provisions | The taxonomy, the provision mapping, 252 law-only answers |
| Google street (JV) | 186 | People Also Ask + related searches, with hit counts | **Search demand.** 98 not in the graph, 66 near-matches |
| Google organic titles (JV) | 1 question-form titles of 223 | What already ranks | 1 not in the graph |
| Harvest (19 Sep) | 1648 pages | Classified competitor pages, trust layers 4–5 | 195 URLs our crawl did not fetch; no questions |

## Street questions the graph doesn't have

98 of 186 street questions have no match in the canonical graph. By kind:

| Kind | Count | What to do |
|---|---|---|
| question | 26 | Add to the graph and answer from the law |
| navigational | 44 | Not questions — people want the law itself, dates, an official home. Served by the /act, /rules and "Applies from" pages |
| shopping | 8 | Certificates, courses, tools. One "there is no DPDPA certificate" page answers most of it |
| noise | 20 | GDPR-only, UPSC exam prep, drifted searches — ignore |

### Real questions to add

| Hits | Question |
|---|---|
| 4 | Data principal can withdraw consent |
| 4 | Data Protection Bill, 2025 |
| 4 | Personal Data Protection Act 2025 |
| 3 | Is there a GDPR equivalent in India? |
| 2 | Before collecting personal data the data fiduciary must provide |
| 2 | Data processing Agreement template |
| 2 | Data Processing Agreement template India |
| 2 | DPDP Rules, 2025 implementation date |
| 2 | India Digital personal data Protection Act effective date |
| 2 | Personal data Protection Bill |
| 2 | The right to grievance redressal is provided under |
| 2 | WhatsApp Business Terms of Service |
| 2 | WhatsApp Data Processing agreement |
| 2 | Which activity is restricted for children data processing |
| 2 | Who is responsible for data protection in a company |
| 1 | How do I know if I was a victim of a data breach? |
| 1 | How much compensation can you get for a data protection breach? |
| 1 | Is a DPO a high ranking officer? |
| 1 | Is a DPO role full time? |
| 1 | Is GDPR mandatory in India? |
| 1 | Is WhatsApp API safe? |
| 1 | Is WhatsApp Business legal? |
| 1 | What are the 7 data protections? |
| 1 | What are the three types of consent? |
| 1 | What are the top 5 CA firms in India? |
| 1 | What is GDPR in India? |

### Navigational and shopping intents (page ideas, not questions)

| Hits | Kind | Intent |
|---|---|---|
| 18 | shopping | DPDPA certification |
| 10 | navigational | DPDPA news |
| 8 | navigational | DPDP Rules |
| 8 | navigational | DPDPA checklist |
| 8 | navigational | DPDPA website |
| 6 | navigational | DPDP portal |
| 6 | navigational | DPDPA effective date |
| 6 | navigational | Latest news on dpdpa |
| 4 | navigational | Data Protection Act India |
| 4 | navigational | Data Rules |
| 4 | navigational | DPDP Act, 2023 PDF |
| 4 | navigational | DPDP Rules pdf |
| 4 | navigational | DPDPA 2025 |
| 4 | shopping | DPDPA course |
| 4 | navigational | Dpdpa in |
| 4 | navigational | Draft digital personal data protection rules 2025 pdf |
| 2 | shopping | Certificate in data protection Law |
| 2 | shopping | Courses on data protection law |
| 2 | navigational | Data consent form |
| 2 | navigational | Data Protection Rules |
| 2 | navigational | DDPA |
| 2 | navigational | DPBI portal |
| 2 | navigational | DPDP Act |
| 2 | navigational | DPDP Act summary PDF |
| 2 | navigational | DPDP Bare Act |
| 2 | navigational | DPDP full form |
| 2 | shopping | DPDP Rules 2025 pdf free download |
| 2 | navigational | Dpdp rules public consultation |
| 2 | navigational | DPDP Rules, 2025 MeitY |
| 2 | navigational | DPDP Rules, 2025 notification |
| 2 | navigational | DPDP Rules, 2025 pdf |
| 2 | navigational | DPDP website |
| 2 | navigational | DPDPA 2023 |
| 2 | shopping | Dpdpa 2023 certificate |
| 2 | navigational | DPDPA 2023 compliance |
| 2 | navigational | Dpdpa 2023 website |
| 2 | navigational | Dpdpa breach investigation |
| 2 | navigational | Dpdpa breach list |
| 2 | navigational | Dpdpa data processor pdf |
| 2 | shopping | DPDPA free certification course |

## Graph questions with the most Google demand

Canonical questions that street searches match, ranked by hits. These should lead the course modules.

| Street hits | Sites asking | Question | Provisions |
|---|---|---|---|
| 8 | 10 | What is a Data Fiduciary under the DPDP Act? | — |
| 6 | 11 | What is cross-border data transfer under the DPDP Act? | S16, S15 |
| 5 | 7 | What are the DPDP Rules 2025? | — |
| 2 | 18 | What is a Consent Manager under the DPDP Act? | R4, S6 |
| 2 | 18 | Who needs to comply with the DPDP Act? | S15, S16, S17 |
| 2 | 16 | What is a Significant Data Fiduciary under the DPDP Act? | S10 |
| 2 | 9 | Who is a Data Principal under the DPDP Act? | S2, S15 |
| 2 | 7 | What is the difference between a Data Fiduciary and a Data Processor under the DPDP Act? | — |
| 2 | 5 | How is the DPDP Act different from GDPR? | — |
| 2 | 4 | What are the principles of data protection under the DPDP Act? | — |
| 1 | 19 | What are the penalties for non-compliance with the DPDP Act? | S33 |
| 1 | 18 | What are the rights of Data Principals under the DPDP Act? | S14, S11, S12 |
| 1 | 8 | What is the maximum penalty under the DPDP Act? | S33 |
| 1 | 3 | What is a Data Processing Agreement (DPA)? | — |

## Harvest pages our crawl missed

195 URLs, across: gotrust-tech (84), redacto-ai (80), privybyidfy-com (80), dpdpindia-in (80), consently-in (80), comply-askmeidentity-com (80), dpo-india-com (80), consentos-in (80)

Sample:

- https://cadp.in/events
- https://complynz.com/dpdp/software
- https://consent.in/blog/cookie-consent
- https://consent.in/blog/dpdp-exemptions
- https://consent.in/blog/dpdp-telemarketing-regulations
- https://consent.in/blog/e-commerce
- https://consent.in/blog/penalties
- https://consent.in/legal-explainers
- https://dpdpa.com/dpdpa2023/chapter-3/section14.html
- https://dpdpa.com/dpdpa2023/chapter-3/section15.html
- https://dpdpa.com/dpdpa2023/chapter-4/section16.html
- https://dpdpashield.in/partners
- https://dpdpashield.in/pii-scanner
- https://dpdpashield.in/products/cloud-security
- https://dpdpashield.in/products/data-inventory

## Organic result titles not in the graph

- DPDPA Penalties Can Reach ₹250 Crore: Are You Ready?
