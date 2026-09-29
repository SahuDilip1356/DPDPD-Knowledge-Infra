#!/usr/bin/env python3
"""
DPDPA Knowledge Base Seed Script
==================================
Creates and publishes 22 structured Knowledge Objects covering the core
Digital Personal Data Protection Act, 2023 corpus into Supabase + Pinecone.

Usage:
  python seed_knowledge_base.py             # Live mode: Supabase + Pinecone
  python seed_knowledge_base.py --dry-run   # Validate only, no writes
  python seed_knowledge_base.py --skip-vectors  # Supabase only, skip Pinecone
"""

import os, sys, hashlib, argparse, subprocess
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from dotenv import load_dotenv
from src.schemas.validate_schema import validate_ko
from src.storage.db_client import DatabaseClient

load_dotenv()

ACT_URN  = "urn:ki:in:dpdp:act:dpdpa-2023"
ACT_SRC  = {
    "name": "Digital Personal Data Protection Act, 2023 — Gazette of India",
    "layer": 1,
    "url": "https://www.meity.gov.in/writereaddata/files/Digital%20Personal%20Data%20Protection%20Act%202023.pdf",
    "hash": "a" * 64
}
DATE = "2023-08-11"
STIME = "2023-08-11T00:00:00Z"

def h(text): return hashlib.sha256(text.encode()).hexdigest()
def hist(msg): return [{"version":1,"system_time":STIME,"commit_message":msg,"author_id":"seed_v1"}]
def evid(sec, cit): return [{"source_urn":ACT_URN,"citation_text":cit,"coordinates":{"section":sec,"hash":h(cit)}}]

KOS = [
  {
    "urn": ACT_URN,
    "title": "Digital Personal Data Protection Act, 2023",
    "source": ACT_SRC, "date": DATE, "version": 1,
    "summary": "The Digital Personal Data Protection Act, 2023 (DPDPA) is the primary Indian statute governing the processing of digital personal data. Enacted 11 August 2023, it establishes rights for Data Principals, obligations for Data Fiduciaries, and the Data Protection Board of India (DPBI) as the regulatory authority. Penalties range from Rs 10,000 to Rs 250 crore.",
    "entities": ["Act","Authority","Penalty"],
    "evidence": evid("Preamble","An Act to provide for the processing of digital personal data in a manner that recognises both the right of individuals to protect their personal data and the need to process personal data for lawful purposes."),
    "business_impact": {"impact_summary":"Every entity processing digital personal data of individuals in India must comply with this Act.","affected_actors":["Data Fiduciary","Significant Data Fiduciary","Data Processor","Consent Manager"],"action_required":"Map data flows, implement consent mechanisms, appoint grievance officers, and establish breach notification playbooks."},
    "confidence_score": 1.0,
    "relations": [],
    "linked_objects": ["urn:ki:in:dpdp:act:2023:sec:6","urn:ki:in:dpdp:act:2023:sec:8","urn:ki:in:dpdp:act:2023:sec:9","urn:ki:in:dpdp:act:2023:sec:10","urn:ki:in:dpdp:act:2023:sec:16","urn:ki:in:dpdp:act:2023:sec:33"],
    "history": hist("Initial seed: DPDPA 2023 Act parent KO")
  },
  {
    "urn": "urn:ki:in:dpdp:act:2023:sec:2",
    "title": "Section 2 — Definitions",
    "source": ACT_SRC, "date": DATE, "version": 1,
    "summary": "Section 2 defines key terms: 'Personal data' means data about an identifiable individual. 'Data Fiduciary' determines the purpose and means of processing. 'Data Principal' is the individual to whom data relates. 'Processing' means wholly or partly automated operations on personal data. 'Consent Manager' enables a Data Principal to manage consents through an interoperable platform.",
    "entities": ["Act","Data Category","Organization"],
    "evidence": evid("Section 2","'Data Fiduciary' means any person who alone or in conjunction with other persons determines the purpose and means of processing of personal data; 'Data Principal' means the individual to whom the personal data relates; 'personal data' means any data about an individual who is identifiable by or in relation to such data."),
    "business_impact": {"impact_summary":"Definitions determine who is regulated and what data is in scope. Misclassification shifts compliance obligations entirely.","affected_actors":["Data Fiduciary","Data Processor","Consent Manager"],"action_required":"Classify every data-handling entity within your organisation as Data Fiduciary, Data Processor, or Consent Manager based on Section 2."},
    "confidence_score": 1.0,
    "relations": [{"target_urn":ACT_URN,"edge_type":"Depends On"}],
    "linked_objects": [ACT_URN],
    "history": hist("Initial seed: Section 2 Definitions")
  },
  {
    "urn": "urn:ki:in:dpdp:act:2023:sec:3",
    "title": "Section 3 — Territorial Scope",
    "source": ACT_SRC, "date": DATE, "version": 1,
    "summary": "Section 3 establishes that the Act applies to processing of digital personal data within India collected online or offline and subsequently digitised. It also applies to processing outside India if in connection with offering goods or services to Data Principals within India.",
    "entities": ["Act","Country"],
    "evidence": evid("Section 3","This Act applies to the processing of digital personal data within the territory of India where the personal data is collected in digital form or in non-digital form and digitised subsequently. This Act also applies to processing outside India if such processing is in connection with any activity related to offering of goods or services to Data Principals within India."),
    "business_impact": {"impact_summary":"Any company targeting Indian users must comply, regardless of server location.","affected_actors":["Data Fiduciary","Foreign Data Fiduciary"],"action_required":"Assess whether your product targets Indian users. If yes, full DPDPA obligations apply even if servers are offshore."},
    "confidence_score": 1.0,
    "relations": [{"target_urn":ACT_URN,"edge_type":"Depends On"}],
    "linked_objects": [ACT_URN],
    "history": hist("Initial seed: Section 3 Territorial Scope")
  },
  {
    "urn": "urn:ki:in:dpdp:act:2023:sec:4",
    "title": "Section 4 — Grounds for Processing Personal Data",
    "source": ACT_SRC, "date": DATE, "version": 1,
    "summary": "Section 4 permits processing of personal data only for a lawful purpose: either (a) with the Data Principal's consent, or (b) for certain legitimate uses specified in Section 7. The purpose must be clearly stated and processing must not exceed that purpose.",
    "entities": ["Legal Basis","Consent","Purpose"],
    "evidence": evid("Section 4","A person may process the personal data of a Data Principal only in accordance with the provisions of this Act and for a lawful purpose — (a) for which the Data Principal has given her consent; or (b) for certain legitimate uses."),
    "business_impact": {"impact_summary":"No personal data processing is permitted without a legal basis.","affected_actors":["Data Fiduciary"],"action_required":"Document the legal basis for every data processing activity in your Register of Processing Activities."},
    "confidence_score": 1.0,
    "relations": [{"target_urn":ACT_URN,"edge_type":"Depends On"},{"target_urn":"urn:ki:in:dpdp:act:2023:sec:6","edge_type":"References"},{"target_urn":"urn:ki:in:dpdp:act:2023:sec:7","edge_type":"References"}],
    "linked_objects": [ACT_URN,"urn:ki:in:dpdp:act:2023:sec:6","urn:ki:in:dpdp:act:2023:sec:7"],
    "history": hist("Initial seed: Section 4 Grounds for Processing")
  },
  {
    "urn": "urn:ki:in:dpdp:act:2023:sec:5",
    "title": "Section 5 — Notice",
    "source": ACT_SRC, "date": DATE, "version": 1,
    "summary": "Section 5 requires that before seeking consent, a Data Fiduciary must provide the Data Principal a notice in clear and plain language stating: (i) the personal data to be processed and the purpose; (ii) how the Data Principal may exercise rights under the Act including withdrawal of consent; (iii) how to make a complaint to the Board. Notice must be in English or a language in the Eighth Schedule to the Constitution.",
    "entities": ["Consent","Legal Basis","Data Category"],
    "evidence": evid("Section 5","Every request for consent shall be accompanied or preceded by a notice given by the Data Fiduciary to the Data Principal, informing her — (a) the personal data and the purpose for which the same is proposed to be processed; (b) the manner in which she may exercise her rights under the provisions of this Act; and (c) the manner in which she may make a complaint to the Board."),
    "business_impact": {"impact_summary":"Missing or deficient consent notices invalidate all downstream consent-based processing.","affected_actors":["Data Fiduciary"],"action_required":"Draft multilingual consent notice templates identifying data categories, processing purpose, and Data Principal rights before any data collection."},
    "confidence_score": 1.0,
    "relations": [{"target_urn":ACT_URN,"edge_type":"Depends On"},{"target_urn":"urn:ki:in:dpdp:act:2023:sec:6","edge_type":"References"}],
    "linked_objects": [ACT_URN,"urn:ki:in:dpdp:act:2023:sec:6"],
    "history": hist("Initial seed: Section 5 Notice")
  },
  {
    "urn": "urn:ki:in:dpdp:act:2023:sec:6",
    "title": "Section 6 — Consent",
    "source": ACT_SRC, "date": DATE, "version": 1,
    "summary": "Section 6 specifies that valid consent must be free, specific, informed, unconditional, and unambiguous, indicated through a clear affirmative action. Consent may be withdrawn at any time and withdrawal must be as easy as giving it. Consent obtained through deceptive means is invalid. Data Principals may manage consent through a registered Consent Manager.",
    "entities": ["Consent","Legal Basis"],
    "evidence": evid("Section 6","Consent given by the Data Principal shall be free, specific, informed, unconditional and unambiguous with a clear affirmative action, and shall signify an agreement to the processing of her personal data for the specified purpose. The Data Principal shall have the right to withdraw her consent at any time and such withdrawal shall be as easy to withdraw as it was to give consent."),
    "business_impact": {"impact_summary":"Bundled, pre-ticked, or coerced consent is unlawful. Withdrawal must be honoured immediately.","affected_actors":["Data Fiduciary"],"action_required":"Implement granular per-purpose consent UI. Integrate consent withdrawal flow. Log all consent events with timestamps."},
    "confidence_score": 1.0,
    "relations": [{"target_urn":ACT_URN,"edge_type":"Depends On"},{"target_urn":"urn:ki:in:dpdp:act:2023:sec:5","edge_type":"Depends On"}],
    "linked_objects": [ACT_URN,"urn:ki:in:dpdp:act:2023:sec:5"],
    "history": hist("Initial seed: Section 6 Consent")
  },
  {
    "urn": "urn:ki:in:dpdp:act:2023:sec:7",
    "title": "Section 7 — Legitimate Uses",
    "source": ACT_SRC, "date": DATE, "version": 1,
    "summary": "Section 7 enumerates situations where personal data may be processed without explicit consent: (a) voluntary provision by the Data Principal for a specified purpose; (b) State instrumentalities for subsidies, licences, permits, or services; (c) medical emergency or epidemic threat; (d) employment-related processing; (e) judicial or quasi-judicial proceedings; (f) breakdown of public order. Legitimate uses do not override data minimisation.",
    "entities": ["Legal Basis","Purpose","Organization"],
    "evidence": evid("Section 7","Personal data of a Data Principal may be processed by a person for a legitimate use, including — (a) if a Data Principal voluntarily provides her personal data and has not indicated that she does not consent; (b) by the State or any of its instrumentalities for performing any function under law; (c) for responding to a medical emergency involving a threat to life; (d) for the performance of any function related to employment."),
    "business_impact": {"impact_summary":"Employers may process employee data under legitimate use but must still comply with data minimisation and purpose limitation.","affected_actors":["Data Fiduciary","Employer","State Instrumentality"],"action_required":"Identify which activities qualify as legitimate uses. Document the specific subsection justification in the Record of Processing Activities."},
    "confidence_score": 1.0,
    "relations": [{"target_urn":ACT_URN,"edge_type":"Depends On"},{"target_urn":"urn:ki:in:dpdp:act:2023:sec:4","edge_type":"Supports"}],
    "linked_objects": [ACT_URN],
    "history": hist("Initial seed: Section 7 Legitimate Uses")
  },
  {
    "urn": "urn:ki:in:dpdp:act:2023:sec:8",
    "title": "Section 8 — General Obligations of Data Fiduciary",
    "source": ACT_SRC, "date": DATE, "version": 1,
    "summary": "Section 8 imposes general obligations: (a) data quality — ensure accuracy and completeness; (b) security — implement reasonable technical and organisational safeguards to prevent personal data breach; (c) breach notification — notify the Board and each affected Data Principal promptly upon a breach; (d) erasure — erase personal data when consent is withdrawn or purpose is no longer served, unless retention is required by law. Penalty for security failure: up to Rs 250 crore. Penalty for breach notification failure: up to Rs 200 crore.",
    "entities": ["Control","Risk","Penalty"],
    "evidence": evid("Section 8","Every Data Fiduciary shall — (b) implement appropriate technical and organisational measures; (c) protect personal data including by taking reasonable security safeguards to prevent personal data breach; (d) in the event of a personal data breach, give the Board and each affected Data Principal notice of such breach in the manner as may be prescribed; (e) erase personal data upon withdrawal of consent or when the Data Principal exercises her right under section 12."),
    "business_impact": {"impact_summary":"Failure to implement security controls or notify breaches carries the highest penalties. Erasure must be an automated workflow.","affected_actors":["Data Fiduciary","Data Processor","CISO"],"action_required":"Deploy 72-hour breach notification SOC playbook. Implement automated erasure pipeline triggered on consent withdrawal. Document security controls."},
    "confidence_score": 1.0,
    "relations": [{"target_urn":ACT_URN,"edge_type":"Depends On"},{"target_urn":"urn:ki:in:dpdp:act:2023:sec:33","edge_type":"References"},{"target_urn":"urn:ki:in:dpdp:penalty:security-safeguards","edge_type":"References"},{"target_urn":"urn:ki:in:dpdp:penalty:notify-breach","edge_type":"References"}],
    "linked_objects": [ACT_URN,"urn:ki:in:dpdp:act:2023:sec:33"],
    "history": hist("Initial seed: Section 8 General Obligations")
  },
  {
    "urn": "urn:ki:in:dpdp:act:2023:sec:9",
    "title": "Section 9 — Processing of Personal Data of Children",
    "source": ACT_SRC, "date": DATE, "version": 1,
    "summary": "Section 9 imposes heightened obligations for processing personal data of children (under 18). A Data Fiduciary must obtain verifiable consent from the child's parent or lawful guardian before processing. Section 9(3) categorically prohibits: (i) tracking or behavioural monitoring of children; (ii) targeted advertising directed at children; (iii) any processing likely to cause detrimental effect on the wellbeing of a child. Penalty for violation: up to Rs 200 crore.",
    "entities": ["Consent","Data Category","Penalty","Risk"],
    "evidence": evid("Section 9","A Data Fiduciary shall, before processing any personal data of a child, obtain verifiable consent of the parent or the lawful guardian of such child. A Data Fiduciary shall not undertake processing of personal data of a child that is likely to cause any detrimental effect on the wellbeing of a child, including — (a) tracking or behavioural monitoring of children; or (b) targeted advertising directed at children."),
    "business_impact": {"impact_summary":"Any product accessible to children must implement age-gate mechanisms and parental consent flows. Behavioural advertising to children is absolutely prohibited.","affected_actors":["Data Fiduciary","EdTech","Gaming Platforms","Social Media"],"action_required":"Implement verified parental consent workflows. Disable behavioural advertising and tracking for users under 18. Apply data minimisation strictly."},
    "confidence_score": 1.0,
    "relations": [{"target_urn":ACT_URN,"edge_type":"Depends On"},{"target_urn":"urn:ki:in:dpdp:penalty:children-obligations","edge_type":"References"},{"target_urn":"urn:ki:in:dpdp:act:2023:sec:6","edge_type":"Depends On"}],
    "linked_objects": [ACT_URN,"urn:ki:in:dpdp:act:2023:sec:6"],
    "history": hist("Initial seed: Section 9 Children's Data Processing")
  },
  {
    "urn": "urn:ki:in:dpdp:act:2023:sec:10",
    "title": "Section 10 — Significant Data Fiduciaries",
    "source": ACT_SRC, "date": DATE, "version": 1,
    "summary": "Section 10 empowers the Central Government to notify certain Data Fiduciaries as Significant Data Fiduciaries (SDFs) based on: volume and sensitivity of data, risk to rights of Data Principals, potential impact on sovereignty, electoral democracy, or public order. SDFs must: (a) appoint an India-based Data Protection Officer (DPO) accountable to the Board of Directors; (b) appoint an independent data auditor; (c) conduct periodic Data Protection Impact Assessments (DPIAs). Penalty for non-compliance: up to Rs 150 crore.",
    "entities": ["Organization","Risk","Control","Authority"],
    "evidence": evid("Section 10","The Central Government may notify any Data Fiduciary or class of Data Fiduciaries as Significant Data Fiduciary. Every Significant Data Fiduciary shall — (a) appoint a Data Protection Officer who shall be based in India and responsible to the Board of Directors; (b) appoint an independent data auditor to carry out data audit; (c) undertake such other measures including Data Protection Impact Assessment as may be prescribed."),
    "business_impact": {"impact_summary":"SDF designation triggers the highest compliance burden. DPO appointment, independent audits, and DPIAs are mandatory. Penalty for SDF obligation breach: up to Rs 150 crore.","affected_actors":["Significant Data Fiduciary","Board of Directors","DPO"],"action_required":"Monitor Central Government SDF notifications. If designated, appoint India-based DPO, commission independent audit, and schedule annual DPIA."},
    "confidence_score": 1.0,
    "relations": [{"target_urn":ACT_URN,"edge_type":"Depends On"},{"target_urn":"urn:ki:in:dpdp:penalty:sdf-obligations","edge_type":"References"}],
    "linked_objects": [ACT_URN],
    "history": hist("Initial seed: Section 10 Significant Data Fiduciaries")
  },
  {
    "urn": "urn:ki:in:dpdp:act:2023:sec:11",
    "title": "Section 11 — Right to Access Information About Personal Data",
    "source": ACT_SRC, "date": DATE, "version": 1,
    "summary": "Section 11 grants the Data Principal the right to obtain from the Data Fiduciary: (a) a summary of personal data being processed and the processing activities; (b) the identities of all other Data Fiduciaries and Data Processors with whom the data has been shared. The Data Fiduciary must respond within the prescribed time limit.",
    "entities": ["Data Category","Organization"],
    "evidence": evid("Section 11","A Data Principal shall have the right to obtain from the Data Fiduciary a summary of personal data being processed and the processing activities undertaken by that Data Fiduciary; the identities of all other Data Fiduciaries and Data Processors with whom the personal data has been shared, along with a description of the personal data so shared."),
    "business_impact": {"impact_summary":"Organisations must build a subject access request fulfilment workflow that can respond within prescribed timelines.","affected_actors":["Data Fiduciary"],"action_required":"Build a Data Principal access portal capable of returning a processing summary and third-party sharing log within the statutory window."},
    "confidence_score": 1.0,
    "relations": [{"target_urn":ACT_URN,"edge_type":"Depends On"}],
    "linked_objects": [ACT_URN],
    "history": hist("Initial seed: Section 11 Right to Access")
  },
  {
    "urn": "urn:ki:in:dpdp:act:2023:sec:12",
    "title": "Section 12 — Right to Correction, Completion, Update, and Erasure",
    "source": ACT_SRC, "date": DATE, "version": 1,
    "summary": "Section 12 grants the Data Principal the right to: (a) correction of inaccurate or misleading personal data; (b) completion of incomplete personal data; (c) update of personal data; (d) erasure of personal data no longer necessary for the purpose for which it was collected. The Data Fiduciary must act on valid requests and instruct Data Processors accordingly.",
    "entities": ["Data Category","Control"],
    "evidence": evid("Section 12","A Data Principal shall have the right to correction, completion, updating and erasure of her personal data — (a) correction of inaccurate or misleading personal data; (b) completion of incomplete personal data; (c) update of personal data; (d) erasure of personal data which is no longer necessary for the purpose for which it was processed."),
    "business_impact": {"impact_summary":"Erasure requests must cascade from the Data Fiduciary to every downstream Data Processor. Automated erasure pipelines are essential.","affected_actors":["Data Fiduciary","Data Processor"],"action_required":"Implement correction and erasure workflows that propagate deletion to all downstream processors and third-party sharing partners."},
    "confidence_score": 1.0,
    "relations": [{"target_urn":ACT_URN,"edge_type":"Depends On"},{"target_urn":"urn:ki:in:dpdp:act:2023:sec:8","edge_type":"References"}],
    "linked_objects": [ACT_URN,"urn:ki:in:dpdp:act:2023:sec:8"],
    "history": hist("Initial seed: Section 12 Correction and Erasure")
  },
  {
    "urn": "urn:ki:in:dpdp:act:2023:sec:13",
    "title": "Section 13 — Right to Grievance Redressal",
    "source": ACT_SRC, "date": DATE, "version": 1,
    "summary": "Section 13 gives every Data Principal the right to have her grievance expeditiously redressed by the Data Fiduciary. Every Data Fiduciary must establish an effective mechanism to redress grievances. If not resolved within the prescribed time or if the Data Principal is unsatisfied, she may approach the Data Protection Board of India (DPBI).",
    "entities": ["Authority","Organization"],
    "evidence": evid("Section 13","A Data Principal shall have the right to have readily available means of grievance redressal provided by the Data Fiduciary in respect of any act or omission of the Data Fiduciary or any Data Processor acting on behalf of such Data Fiduciary. Every Data Fiduciary shall establish an effective mechanism to redress the grievances of Data Principals."),
    "business_impact": {"impact_summary":"A grievance officer with a defined escalation path is a mandatory compliance control.","affected_actors":["Data Fiduciary"],"action_required":"Appoint a Grievance Officer, publish contact details, and implement a ticketed grievance system with SLA-driven escalation and audit trail."},
    "confidence_score": 1.0,
    "relations": [{"target_urn":ACT_URN,"edge_type":"Depends On"}],
    "linked_objects": [ACT_URN],
    "history": hist("Initial seed: Section 13 Grievance Redressal")
  },
  {
    "urn": "urn:ki:in:dpdp:act:2023:sec:14",
    "title": "Section 14 — Right to Nominate",
    "source": ACT_SRC, "date": DATE, "version": 1,
    "summary": "Section 14 grants a Data Principal the right to nominate any individual to exercise her rights under the Act in the event of her death or incapacity. The nominee shall exercise the Data Principal's rights on her behalf.",
    "entities": ["Person"],
    "evidence": evid("Section 14","A Data Principal shall have the right to nominate, in such manner as may be prescribed, any other individual, who shall, in the event of death or incapacity of the Data Principal, exercise the rights of the Data Principal in accordance with the provisions of this Act."),
    "business_impact": {"impact_summary":"Organisations must implement nomination registration workflows and honour nominee-initiated data requests.","affected_actors":["Data Fiduciary"],"action_required":"Build a nomination registry and test nominee-triggered access, correction, and erasure workflows."},
    "confidence_score": 1.0,
    "relations": [{"target_urn":ACT_URN,"edge_type":"Depends On"}],
    "linked_objects": [ACT_URN],
    "history": hist("Initial seed: Section 14 Right to Nominate")
  },
  {
    "urn": "urn:ki:in:dpdp:act:2023:sec:15",
    "title": "Section 15 — Duties of Data Principal",
    "source": ACT_SRC, "date": DATE, "version": 1,
    "summary": "Section 15 imposes duties on Data Principals. A Data Principal must not: (a) impersonate another person while providing personal data; (b) suppress material information when applying for documents, licences, services, or benefits; (c) register a false or frivolous grievance or complaint with the Data Fiduciary or the Board. Penalty for filing a frivolous complaint: up to Rs 10,000.",
    "entities": ["Person","Penalty"],
    "evidence": evid("Section 15","Every Data Principal shall — comply with the provisions of all applicable laws while exercising her rights; not register a false or frivolous complaint or grievance with the Data Fiduciary or the Board; furnish only such information as is verifiably authentic while exercising rights or making a complaint."),
    "business_impact": {"impact_summary":"Data Principals bear responsibilities in the ecosystem. Frivolous complaints can be penalised.","affected_actors":["Data Principal"],"action_required":"Include Data Principal duties in consent notices and terms of service. Implement complaint screening to flag frivolous submissions."},
    "confidence_score": 1.0,
    "relations": [{"target_urn":ACT_URN,"edge_type":"Depends On"}],
    "linked_objects": [ACT_URN],
    "history": hist("Initial seed: Section 15 Duties of Data Principal")
  },
  {
    "urn": "urn:ki:in:dpdp:act:2023:sec:16",
    "title": "Section 16 — Transfer of Personal Data Outside India",
    "source": ACT_SRC, "date": DATE, "version": 1,
    "summary": "Section 16 permits a Data Fiduciary to transfer personal data of a Data Principal to any country or territory outside India, EXCEPT to countries or territories blacklisted by the Central Government by notification. Until a country is specifically blacklisted, transfers are permitted. There is no whitelist or adequacy-decision mechanism analogous to GDPR. Additional conditions may be imposed by the Central Government by notification.",
    "entities": ["Country","Legal Basis","Control"],
    "evidence": evid("Section 16","A Data Fiduciary may transfer personal data of a Data Principal to a country or territory outside India, except to such countries or territories as may be notified by the Central Government. The Central Government may, subject to such conditions as may be prescribed, restrict the transfer of personal data by a Data Fiduciary to a country or territory outside India."),
    "business_impact": {"impact_summary":"Cross-border data transfer is generally permitted until a country is specifically blacklisted. Monitor Central Government notifications for restricted destinations.","affected_actors":["Data Fiduciary","Multinational Organisation"],"action_required":"Subscribe to Central Government DPDPA notifications. Maintain a live blacklist registry. Update data transfer agreements upon any new notification."},
    "confidence_score": 1.0,
    "relations": [{"target_urn":ACT_URN,"edge_type":"Depends On"},{"target_urn":"urn:ki:in:dpdp:act:2023:sec:4","edge_type":"Depends On"}],
    "linked_objects": [ACT_URN],
    "history": hist("Initial seed: Section 16 Cross-Border Transfers")
  },
  {
    "urn": "urn:ki:in:dpdp:act:2023:sec:17",
    "title": "Section 17 — Exemptions",
    "source": ACT_SRC, "date": DATE, "version": 1,
    "summary": "Section 17 grants exemptions from certain Act provisions: (a) State instrumentalities for national security, public order, sovereignty, preventing incitement to offences; (b) research, archiving, or statistical purposes with prescribed safeguards; (c) startups and small entities as notified by the Central Government. Exempted entities must still implement reasonable security safeguards.",
    "entities": ["Organization","Legal Basis","Authority"],
    "evidence": evid("Section 17","Nothing contained in this Act shall apply to — (a) personal data processed by an instrumentality of State for interests of sovereignty and integrity of India, security of the State, friendly relations with foreign States, maintenance of public order, or preventing incitement to any cognisable offence; (b) personal data processed for the purpose of research, archiving or statistical purposes in accordance with prescribed standards."),
    "business_impact": {"impact_summary":"Startups granted exemptions still face residual security obligations. State agencies enjoy wider but not absolute exemptions.","affected_actors":["State Instrumentality","Research Organisation","Startup"],"action_required":"Check if your organisation qualifies for an exemption class. Maintain security safeguards regardless, as these are not exempted."},
    "confidence_score": 1.0,
    "relations": [{"target_urn":ACT_URN,"edge_type":"Depends On"}],
    "linked_objects": [ACT_URN],
    "history": hist("Initial seed: Section 17 Exemptions")
  },
  {
    "urn": "urn:ki:in:dpdp:act:2023:sec:18",
    "title": "Section 18 — Establishment of Data Protection Board of India",
    "source": ACT_SRC, "date": DATE, "version": 1,
    "summary": "Section 18 establishes the Data Protection Board of India (DPBI) as a body corporate with perpetual succession. The DPBI is empowered to: (a) determine non-compliance; (b) impose penalties; (c) direct remedial action. The Board operates on digital-first principles and Data Principals may file complaints electronically.",
    "entities": ["Authority","Organization"],
    "evidence": evid("Section 18","The Central Government shall, by notification, establish a Board to be known as the Data Protection Board of India to exercise the powers conferred on, and to perform the functions assigned to it under this Act. The Board shall be a body corporate by the name aforesaid, having perpetual succession and a common seal."),
    "business_impact": {"impact_summary":"The DPBI is the enforcement authority. Investigations are initiated on complaints or suo motu. Cooperation with Board inquiries is mandatory.","affected_actors":["Data Fiduciary","Significant Data Fiduciary"],"action_required":"Designate a DPBI liaison. Establish an internal rapid-response team for Board inquiry notices. Maintain evidence-ready documentation of compliance controls."},
    "confidence_score": 1.0,
    "relations": [{"target_urn":ACT_URN,"edge_type":"Depends On"}],
    "linked_objects": [ACT_URN],
    "history": hist("Initial seed: Section 18 DPBI Setup")
  },
  {
    "urn": "urn:ki:in:dpdp:act:2023:sec:33",
    "title": "Section 33 — Penalties and Schedule of Fines",
    "source": ACT_SRC, "date": DATE, "version": 1,
    "summary": "Section 33 and the Schedule specify monetary penalties: Item 1 — Failure to implement security safeguards (S.8): up to Rs 250 crore. Item 2 — Failure to notify Board and affected persons of a breach (S.8): up to Rs 200 crore. Item 3 — Failure to fulfil children's data obligations (S.9): up to Rs 200 crore. Item 4 — Failure to fulfil SDF obligations (S.10): up to Rs 150 crore. Item 5 — Breach of any other provision: up to Rs 50 crore. Item 6 — Data Principal filing a frivolous complaint: up to Rs 10,000. Penalties do not bar civil or criminal action.",
    "entities": ["Penalty","Risk","Authority"],
    "evidence": evid("Section 33 / Schedule","Item 1: Failure to take reasonable security safeguards to prevent personal data breach: up to Rs 250,00,00,000. Item 2: Failure to notify the Board or affected Data Principals of personal data breach: up to Rs 200,00,00,000. Item 3: Non-fulfilment of obligations for processing children's personal data: up to Rs 200,00,00,000. Item 4: Non-fulfilment of additional obligations of Significant Data Fiduciary: up to Rs 150,00,00,000. Item 5: Breach of any provision: up to Rs 50,00,00,000. Item 6: Data Principal filing a false or frivolous complaint: up to Rs 10,000."),
    "business_impact": {"impact_summary":"The penalty schedule creates a clear risk-ranked compliance priority. Security safeguards and breach notification carry the largest financial exposure.","affected_actors":["Data Fiduciary","Significant Data Fiduciary","Data Principal"],"action_required":"Use the Schedule as a risk-prioritisation matrix. Allocate compliance investment proportionally: security controls first, then breach notification, then children's data, then SDF obligations."},
    "confidence_score": 1.0,
    "relations": [{"target_urn":ACT_URN,"edge_type":"Depends On"},{"target_urn":"urn:ki:in:dpdp:act:2023:sec:8","edge_type":"Applies To"},{"target_urn":"urn:ki:in:dpdp:act:2023:sec:9","edge_type":"Applies To"},{"target_urn":"urn:ki:in:dpdp:act:2023:sec:10","edge_type":"Applies To"}],
    "linked_objects": [ACT_URN],
    "history": hist("Initial seed: Section 33 Penalties and Schedule")
  },
  {
    "urn": "urn:ki:in:dpdp:penalty:security-safeguards",
    "title": "Penalty — Failure to Implement Security Safeguards (Schedule Item 1)",
    "source": ACT_SRC, "date": DATE, "version": 1,
    "summary": "Schedule Item 1 imposes a monetary penalty of up to Rs 250 crore (Rs 2.5 billion) on a Data Fiduciary that fails to take reasonable technical and organisational security safeguards to prevent a personal data breach, as required under Section 8. This is the highest single penalty in the Act.",
    "entities": ["Penalty","Control","Risk"],
    "evidence": evid("Schedule — Item 1","For failure by a Data Fiduciary to take reasonable security safeguards to prevent personal data breach under sub-section (5) of section 8: Penalty up to Rs 250,00,00,000."),
    "business_impact": {"impact_summary":"Rs 250 crore penalty. Highest financial exposure in the Act. Security controls are the single highest compliance priority.","affected_actors":["Data Fiduciary","CISO","Board of Directors"],"action_required":"Conduct security gap assessment. Implement encryption, access controls, vulnerability management, and annual penetration testing."},
    "confidence_score": 1.0,
    "relations": [{"target_urn":"urn:ki:in:dpdp:act:2023:sec:33","edge_type":"Depends On"},{"target_urn":"urn:ki:in:dpdp:act:2023:sec:8","edge_type":"Applies To"}],
    "linked_objects": ["urn:ki:in:dpdp:act:2023:sec:8","urn:ki:in:dpdp:act:2023:sec:33"],
    "history": hist("Initial seed: Penalty — Security Safeguards")
  },
  {
    "urn": "urn:ki:in:dpdp:penalty:notify-breach",
    "title": "Penalty — Failure to Notify Board of Breach (Schedule Item 2)",
    "source": ACT_SRC, "date": DATE, "version": 1,
    "summary": "Schedule Item 2 imposes a penalty of up to Rs 200 crore on a Data Fiduciary that fails to notify the Data Protection Board of India and each affected Data Principal of a personal data breach, as required under Section 8. This obligation is triggered immediately upon the fiduciary becoming aware of a breach.",
    "entities": ["Penalty","Risk","Authority"],
    "evidence": evid("Schedule — Item 2","For failure by a Data Fiduciary to notify the Board and each affected Data Principal in the event of a personal data breach under sub-section (6) of section 8: Penalty up to Rs 200,00,00,000."),
    "business_impact": {"impact_summary":"Rs 200 crore penalty. Breach notification is time-critical. Absence of a tested SOC playbook is a material compliance risk.","affected_actors":["Data Fiduciary","CISO","Legal Counsel"],"action_required":"Draft and test a 72-hour breach notification playbook with defined roles. Pre-draft notification templates for Board submission and affected Data Principal communication."},
    "confidence_score": 1.0,
    "relations": [{"target_urn":"urn:ki:in:dpdp:act:2023:sec:33","edge_type":"Depends On"},{"target_urn":"urn:ki:in:dpdp:act:2023:sec:8","edge_type":"Applies To"}],
    "linked_objects": ["urn:ki:in:dpdp:act:2023:sec:8","urn:ki:in:dpdp:act:2023:sec:33"],
    "history": hist("Initial seed: Penalty — Breach Notification Failure")
  },
  {
    "urn": "urn:ki:in:dpdp:penalty:children-obligations",
    "title": "Penalty — Non-Fulfilment of Children's Data Obligations (Schedule Item 3)",
    "source": ACT_SRC, "date": DATE, "version": 1,
    "summary": "Schedule Item 3 imposes a penalty of up to Rs 200 crore on a Data Fiduciary that fails to comply with Section 9 obligations for processing children's personal data. Violations include: processing without verified parental consent, behavioural tracking or monitoring of children, or directing targeted advertising at children.",
    "entities": ["Penalty","Consent","Data Category"],
    "evidence": evid("Schedule — Item 3","For non-fulfilment of obligations in relation to processing of personal data of children under section 9: Penalty up to Rs 200,00,00,000."),
    "business_impact": {"impact_summary":"Rs 200 crore penalty. Zero-tolerance rule for targeted advertising to children. Verifiable parental consent is mandatory before any processing.","affected_actors":["Data Fiduciary","EdTech","Social Media","Gaming"],"action_required":"Implement age verification and parental consent collection. Disable all behavioural advertising segments for users under 18. Audit recommendation engines for child exposure."},
    "confidence_score": 1.0,
    "relations": [{"target_urn":"urn:ki:in:dpdp:act:2023:sec:33","edge_type":"Depends On"},{"target_urn":"urn:ki:in:dpdp:act:2023:sec:9","edge_type":"Applies To"}],
    "linked_objects": ["urn:ki:in:dpdp:act:2023:sec:9","urn:ki:in:dpdp:act:2023:sec:33"],
    "history": hist("Initial seed: Penalty — Children's Data Obligations")
  },
  {
    "urn": "urn:ki:in:dpdp:penalty:sdf-obligations",
    "title": "Penalty — Non-Fulfilment of SDF Obligations (Schedule Item 4)",
    "source": ACT_SRC, "date": DATE, "version": 1,
    "summary": "Schedule Item 4 imposes a penalty of up to Rs 150 crore on a Significant Data Fiduciary that fails to comply with Section 10 obligations. These include: failure to appoint an India-based DPO, failure to commission an independent data audit, or failure to conduct a Data Protection Impact Assessment (DPIA).",
    "entities": ["Penalty","Organization","Risk"],
    "evidence": evid("Schedule — Item 4","For non-fulfilment of additional obligations by a Significant Data Fiduciary under section 10: Penalty up to Rs 150,00,00,000."),
    "business_impact": {"impact_summary":"Rs 150 crore penalty for SDF non-compliance. DPO appointment and DPIA are not optional once SDF designation is received.","affected_actors":["Significant Data Fiduciary","DPO","Board of Directors"],"action_required":"Upon SDF notification, immediately appoint India-based DPO. Engage an independent auditor. Schedule DPIA within 6 months."},
    "confidence_score": 1.0,
    "relations": [{"target_urn":"urn:ki:in:dpdp:act:2023:sec:33","edge_type":"Depends On"},{"target_urn":"urn:ki:in:dpdp:act:2023:sec:10","edge_type":"Applies To"}],
    "linked_objects": ["urn:ki:in:dpdp:act:2023:sec:10","urn:ki:in:dpdp:act:2023:sec:33"],
    "history": hist("Initial seed: Penalty — SDF Obligations")
  },
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--skip-vectors", action="store_true")
    args = parser.parse_args()

    print(f"\n{'='*60}")
    print(f"  DPDPA Knowledge Base Seeder")
    print(f"  Mode: {'DRY RUN (validate only)' if args.dry_run else 'LIVE'}")
    print(f"  KOs to process: {len(KOS)}")
    print(f"{'='*60}\n")

    # Phase 1: Validate
    print("── Phase 1: Schema Validation ──")
    errors = []
    for ko in KOS:
        try:
            validate_ko(ko)
            print(f"  ✅  {ko['urn']}")
        except Exception as e:
            print(f"  ❌  {ko['urn']} — {e}")
            errors.append((ko["urn"], str(e)))

    if errors:
        print(f"\n[!] {len(errors)} validation error(s). Fix before proceeding.")
        sys.exit(1)

    print(f"\n  All {len(KOS)} KOs passed schema validation.\n")

    if args.dry_run:
        print("── Dry-run complete. No writes performed. ──")
        return

    # Phase 2: Publish to Supabase
    # DATABASE_URL may be blank ("") — os.getenv default only fires on absent keys,
    # not empty strings. Use `or` to catch both None and "".
    db_url = os.getenv("DATABASE_URL") or "sqlite:///:memory:"


    print("── Phase 2: Publishing to Supabase ──")
    db_client = DatabaseClient(db_url)

    published, failed = 0, 0
    for ko in KOS:
        try:
            db_client.publish_ko(ko)
            print(f"  ✅  {ko['urn']}")
            published += 1
        except Exception as e:
            print(f"  ❌  {ko['urn']} — {e}")
            failed += 1

    print(f"\n  Published: {published} | Failed: {failed}\n")
    if failed > 0:
        print("[!] Some KOs failed. Review errors before indexing vectors.")
        sys.exit(1)

    # Phase 3: Pinecone
    if args.skip_vectors:
        print("── Phase 3: Skipped (--skip-vectors) ──")
        return

    print("── Phase 3: Indexing Vectors in Pinecone ──")
    result = subprocess.run(
        [sys.executable, "src/reasoning/index_vectors.py"],
        cwd=os.path.dirname(os.path.abspath(__file__))
    )
    if result.returncode != 0:
        print("[!] Pinecone indexing failed. Check output above.")
        sys.exit(1)

    print(f"\n{'='*60}")
    print(f"  ✅  Knowledge base seeding complete!")
    print(f"  {published} KOs in Supabase | Vectors in: {os.getenv('PINECONE_INDEX_NAME', 'dpdpa-knowledge')}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
