#!/usr/bin/env python3
"""
DPDPA Full Knowledge Base Seeder
=================================
Seeds the COMPLETE DPDPA knowledge base (~73 Knowledge Objects) into Supabase,
covering all 5 trust layers defined in the Knowledge Constitution.

Layer 1 (Primary Authority, Confidence=1.0): Act sections, Rules, Penalty Schedule
Layer 2 (Judicial Authority, Confidence=0.9): Puttaswamy + SC challenges
Layer 3 (Regulatory, Confidence=0.7): MeitY notifications, Sector overlaps
Layer 4 (Expert Opinions, Confidence=0.5): Law firm advisories
Layer 5 (Industry Guidance, Confidence=0.3): NASSCOM, DSCI, ICSI

Requires:
  SUPABASE_URL, SUPABASE_SERVICE_KEY in environment or .env
"""

import os
import sys
from dotenv import load_dotenv
load_dotenv()
from supabase import create_client, Client

# ═══════════════════════════════════════════════════════════════════════════════
# LAYER 1: PRIMARY AUTHORITY — THE ACT (Confidence = 1.0)
# ═══════════════════════════════════════════════════════════════════════════════

ACT_PARENT = {
    "urn": "urn:ki:in:dpdp:act:dpdpa-2023",
    "title": "Digital Personal Data Protection Act 2023",
    "type": "Act",
    "version": 1,
    "summary": "The foundational privacy legislation passed by the Parliament of India on August 11, 2023. Establishes rights of data principals, duties of data fiduciaries, security mandates, the Data Protection Board of India (DPBI), and a penalty framework reaching ₹250 crore. Organized into 9 chapters and 44 sections.",
    "confidence_score": 1.00,
    "legal_time_start": "2023-08-11T00:00:00Z",
    "entities": ["Act", "Data Principal", "Data Fiduciary", "Consent", "DPBI", "Penalty", "Authority"],
    "business_impact": {
        "impact_summary": "Establishes a completely new digital personal data compliance regime in India.",
        "action_required": "Map all digital personal data processing flows across the enterprise and implement reasonable security safeguards."
    },
    "evidence": [{
        "id": "ev-001", "source_urn": "urn:ki:in:dpdp:source:gazette-dpdpa-2023",
        "source_name": "Gazette of India Extraordinary Part II Section 1",
        "source_tier": "primary",
        "citation_text": "An Act to provide for the processing of digital personal data in a manner that recognises both the right of individuals to protect their personal data and the need to process such personal data for lawful purposes.",
        "coordinates": {"page": 1, "section": "Preamble"},
        "hash": "da8cf9105432a9e8751db432ef5012a4b8cd9a77efca1357db5c6c99ef412e87",
        "verification_status": "verified"
    }],
    "linked_objects": ["urn:ki:in:dpdp:rule:dpdp-rules-2025"],
    "relations": [{"target_urn": "urn:ki:in:dpdp:rule:dpdp-rules-2025", "edge_type": "Depends On"}]
}

ACT_SECTIONS = [
    {
        "urn": "urn:ki:in:dpdp:act:2023:sec:2",
        "title": "Section 2 — Definitions",
        "type": "Act",
        "version": 1,
        "summary": "Defines 28 key terms including Data Principal, Data Fiduciary, Consent Manager, Data Processor, Digital Personal Data, Personal Data Breach, Significant Data Fiduciary (SDF), and the Data Protection Board of India (DPBI). Establishes the foundational vocabulary for the entire regulatory framework.",
        "confidence_score": 1.00,
        "legal_time_start": "2023-08-11T00:00:00Z",
        "entities": ["Data Principal", "Data Fiduciary", "Consent Manager", "Data Processor", "Data Category", "Authority"],
        "business_impact": {"impact_summary": "All compliance mapping begins with these definitions.", "action_required": "Map organizational roles to Act definitions (Data Fiduciary vs Data Processor)."},
        "evidence": [{"id": "ev-sec2", "source_urn": "urn:ki:in:dpdp:source:gazette-dpdpa-2023", "source_name": "Gazette of India — DPDPA 2023", "source_tier": "primary", "citation_text": "Section 2: In this Act, unless the context otherwise requires...", "coordinates": {"section": "Section 2"}, "verification_status": "verified"}],
        "linked_objects": ["urn:ki:in:dpdp:act:dpdpa-2023"],
        "relations": [{"target_urn": "urn:ki:in:dpdp:act:dpdpa-2023", "edge_type": "Depends On"}]
    },
    {
        "urn": "urn:ki:in:dpdp:act:2023:sec:3",
        "title": "Section 3 — Application and Territorial Scope",
        "type": "Act",
        "version": 1,
        "summary": "The Act applies to digital personal data processed within India, and to processing outside India if related to offering goods or services to individuals in India. Excludes non-digital data and data processed for personal/domestic purposes.",
        "confidence_score": 1.00,
        "legal_time_start": "2023-08-11T00:00:00Z",
        "entities": ["Act", "Country"],
        "business_impact": {"impact_summary": "Extraterritorial scope affects any global company serving Indian customers.", "action_required": "Assess if your organization processes data of Indian residents even from outside India."},
        "evidence": [{"id": "ev-sec3", "source_urn": "urn:ki:in:dpdp:source:gazette-dpdpa-2023", "source_name": "Gazette of India — DPDPA 2023", "source_tier": "primary", "citation_text": "This Act shall apply to the processing of digital personal data within the territory of India...", "coordinates": {"section": "Section 3"}, "verification_status": "verified"}],
        "linked_objects": ["urn:ki:in:dpdp:act:dpdpa-2023"],
        "relations": [{"target_urn": "urn:ki:in:dpdp:act:dpdpa-2023", "edge_type": "Depends On"}]
    },
    {
        "urn": "urn:ki:in:dpdp:act:2023:sec:4",
        "title": "Section 4 — Grounds for Processing Personal Data",
        "type": "Act",
        "version": 1,
        "summary": "Personal data may only be processed for a lawful purpose: (a) based on consent of the Data Principal, or (b) for certain legitimate uses as defined in Section 7. Processing without a valid ground is prohibited.",
        "confidence_score": 1.00,
        "legal_time_start": "2023-08-11T00:00:00Z",
        "entities": ["Consent", "Legal Basis", "Purpose"],
        "business_impact": {"impact_summary": "Every data processing activity must map to either consent or a legitimate use.", "action_required": "Create a purpose-to-legal-basis mapping for all data processing activities."},
        "evidence": [{"id": "ev-sec4", "source_urn": "urn:ki:in:dpdp:source:gazette-dpdpa-2023", "source_name": "Gazette of India — DPDPA 2023", "source_tier": "primary", "citation_text": "A person may process the personal data of a Data Principal only in accordance with the provisions of this Act and for a lawful purpose...", "coordinates": {"section": "Section 4"}, "verification_status": "verified"}],
        "linked_objects": ["urn:ki:in:dpdp:act:dpdpa-2023", "urn:ki:in:dpdp:act:2023:sec:6", "urn:ki:in:dpdp:act:2023:sec:7"],
        "relations": [{"target_urn": "urn:ki:in:dpdp:act:dpdpa-2023", "edge_type": "Depends On"}, {"target_urn": "urn:ki:in:dpdp:act:2023:sec:6", "edge_type": "Depends On"}, {"target_urn": "urn:ki:in:dpdp:act:2023:sec:7", "edge_type": "Depends On"}]
    },
    {
        "urn": "urn:ki:in:dpdp:act:2023:sec:5",
        "title": "Section 5 — Notice",
        "type": "Act",
        "version": 1,
        "summary": "Before or at the time of seeking consent, the Data Fiduciary must give the Data Principal a notice containing: (a) a description of the personal data sought, (b) the purpose of processing, and (c) how the Data Principal may exercise their rights. Notice must be standalone, itemized, and in plain language available in 22 scheduled Indian languages.",
        "confidence_score": 1.00,
        "legal_time_start": "2023-08-11T00:00:00Z",
        "entities": ["Consent", "Data Fiduciary", "Data Principal"],
        "business_impact": {"impact_summary": "Requires a complete redesign of privacy notices across all customer touchpoints.", "action_required": "Draft standalone privacy notices in plain language for each purpose; translate into applicable scheduled languages."},
        "evidence": [{"id": "ev-sec5", "source_urn": "urn:ki:in:dpdp:source:gazette-dpdpa-2023", "source_name": "Gazette of India — DPDPA 2023", "source_tier": "primary", "citation_text": "Every request for consent shall be accompanied or preceded by a notice...", "coordinates": {"section": "Section 5"}, "verification_status": "verified"}],
        "linked_objects": ["urn:ki:in:dpdp:act:dpdpa-2023"],
        "relations": [{"target_urn": "urn:ki:in:dpdp:act:dpdpa-2023", "edge_type": "Depends On"}]
    },
    {
        "urn": "urn:ki:in:dpdp:act:2023:sec:6",
        "title": "Section 6 — Consent",
        "type": "Act",
        "version": 1,
        "summary": "Consent must be free, specific, informed, unconditional, and unambiguous, given for a specified purpose. It must be limited to the personal data necessary for that purpose. The Data Principal has the right to withdraw consent at any time through an easily accessible mechanism. Withdrawal does not affect lawfulness of prior processing.",
        "confidence_score": 1.00,
        "legal_time_start": "2023-08-11T00:00:00Z",
        "entities": ["Consent", "Data Principal", "Purpose"],
        "business_impact": {"impact_summary": "Take-it-or-leave-it consent models are no longer valid. Granular, purpose-specific consent required.", "action_required": "Implement granular consent collection with easy withdrawal mechanism at every data collection point."},
        "evidence": [{"id": "ev-sec6", "source_urn": "urn:ki:in:dpdp:source:gazette-dpdpa-2023", "source_name": "Gazette of India — DPDPA 2023", "source_tier": "primary", "citation_text": "Consent given by the Data Principal shall be free, specific, informed, unconditional and unambiguous...", "coordinates": {"section": "Section 6"}, "verification_status": "verified"}],
        "linked_objects": ["urn:ki:in:dpdp:act:dpdpa-2023"],
        "relations": [{"target_urn": "urn:ki:in:dpdp:act:dpdpa-2023", "edge_type": "Depends On"}]
    },
    {
        "urn": "urn:ki:in:dpdp:act:2023:sec:7",
        "title": "Section 7 — Certain Legitimate Uses",
        "type": "Act",
        "version": 1,
        "summary": "Processing without consent is permitted for: (a) State functions/subsidies, (b) performance of legal obligations, (c) response to medical emergencies, (d) employment purposes, (e) voluntary provision of data by the Data Principal. These are exhaustive categories — no open-ended 'legitimate interest' ground exists.",
        "confidence_score": 1.00,
        "legal_time_start": "2023-08-11T00:00:00Z",
        "entities": ["Legal Basis", "Purpose", "Organization"],
        "business_impact": {"impact_summary": "Unlike GDPR, there is no broad 'legitimate interest' ground. Only specific enumerated exceptions.", "action_required": "Map each non-consent processing activity to one of the five specific legitimate use categories."},
        "evidence": [{"id": "ev-sec7", "source_urn": "urn:ki:in:dpdp:source:gazette-dpdpa-2023", "source_name": "Gazette of India — DPDPA 2023", "source_tier": "primary", "citation_text": "A Data Fiduciary may process personal data of a Data Principal for the following legitimate uses...", "coordinates": {"section": "Section 7"}, "verification_status": "verified"}],
        "linked_objects": ["urn:ki:in:dpdp:act:dpdpa-2023"],
        "relations": [{"target_urn": "urn:ki:in:dpdp:act:dpdpa-2023", "edge_type": "Depends On"}]
    },
    {
        "urn": "urn:ki:in:dpdp:act:2023:sec:8",
        "title": "Section 8 — General Obligations of Data Fiduciary",
        "type": "Act",
        "version": 1,
        "summary": "Data Fiduciaries must: (a) ensure completeness, accuracy, and consistency of data, (b) implement reasonable security safeguards, (c) notify DPBI and affected Data Principals of any breach, (d) erase personal data when purpose is fulfilled or consent withdrawn, (e) publish contact details of a Data Protection Officer or authorized person.",
        "confidence_score": 1.00,
        "legal_time_start": "2023-08-11T00:00:00Z",
        "entities": ["Data Fiduciary", "Control", "Risk"],
        "business_impact": {"impact_summary": "Comprehensive operational compliance mandate for every data-processing entity.", "action_required": "Implement data accuracy checks, security safeguards, breach response playbook, and data retention/erasure policies."},
        "evidence": [{"id": "ev-sec8", "source_urn": "urn:ki:in:dpdp:source:gazette-dpdpa-2023", "source_name": "Gazette of India — DPDPA 2023", "source_tier": "primary", "citation_text": "A Data Fiduciary shall make reasonable efforts to ensure the accuracy and completeness...", "coordinates": {"section": "Section 8"}, "verification_status": "verified"}],
        "linked_objects": ["urn:ki:in:dpdp:act:dpdpa-2023"],
        "relations": [{"target_urn": "urn:ki:in:dpdp:act:dpdpa-2023", "edge_type": "Depends On"}]
    },
    {
        "urn": "urn:ki:in:dpdp:act:2023:sec:9",
        "title": "Section 9 — Processing of Children's Data",
        "type": "Act",
        "version": 1,
        "summary": "Processing personal data of children (persons under 18) requires verifiable consent from a parent or lawful guardian. Data Fiduciaries must not undertake tracking, behavioural monitoring, or targeted advertising directed at children. The government may exempt certain classes of Data Fiduciaries from the verifiable consent requirement.",
        "confidence_score": 1.00,
        "legal_time_start": "2023-08-11T00:00:00Z",
        "entities": ["Consent", "Data Principal", "Person", "Control"],
        "business_impact": {"impact_summary": "EdTech, gaming, social media, and any child-facing services face strict new obligations.", "action_required": "Implement age verification, verifiable parental consent flows, and disable tracking/targeting for users under 18."},
        "evidence": [{"id": "ev-sec9", "source_urn": "urn:ki:in:dpdp:source:gazette-dpdpa-2023", "source_name": "Gazette of India — DPDPA 2023", "source_tier": "primary", "citation_text": "Before processing any personal data of a child, a Data Fiduciary shall obtain verifiable consent of the parent...", "coordinates": {"section": "Section 9"}, "verification_status": "verified"}],
        "linked_objects": ["urn:ki:in:dpdp:act:dpdpa-2023"],
        "relations": [{"target_urn": "urn:ki:in:dpdp:act:dpdpa-2023", "edge_type": "Depends On"}]
    },
    {
        "urn": "urn:ki:in:dpdp:act:2023:sec:10",
        "title": "Section 10 — Significant Data Fiduciary (SDF)",
        "type": "Act",
        "version": 1,
        "summary": "The Central Government may designate any Data Fiduciary as a Significant Data Fiduciary (SDF) based on: volume and sensitivity of data, risk to Data Principals, impact on sovereignty, or use of new technologies. SDFs must: (a) appoint a DPO based in India, (b) appoint an independent data auditor, (c) conduct periodic Data Protection Impact Assessments (DPIAs), (d) take additional measures as prescribed.",
        "confidence_score": 1.00,
        "legal_time_start": "2023-08-11T00:00:00Z",
        "entities": ["Data Fiduciary", "Person", "Control", "Risk", "Authority"],
        "business_impact": {"impact_summary": "Large tech companies, banks, and government platforms will likely be designated as SDFs.", "action_required": "Assess SDF designation risk; preemptively appoint DPO, engage independent auditors, and initiate DPIA frameworks."},
        "evidence": [{"id": "ev-sec10", "source_urn": "urn:ki:in:dpdp:source:gazette-dpdpa-2023", "source_name": "Gazette of India — DPDPA 2023", "source_tier": "primary", "citation_text": "The Central Government may notify any Data Fiduciary or class of Data Fiduciaries as Significant Data Fiduciary...", "coordinates": {"section": "Section 10"}, "verification_status": "verified"}],
        "linked_objects": ["urn:ki:in:dpdp:act:dpdpa-2023"],
        "relations": [{"target_urn": "urn:ki:in:dpdp:act:dpdpa-2023", "edge_type": "Depends On"}]
    },
    {
        "urn": "urn:ki:in:dpdp:act:2023:sec:11",
        "title": "Section 11 — Right of Access to Information",
        "type": "Act",
        "version": 1,
        "summary": "Every Data Principal has the right to obtain from the Data Fiduciary: (a) a summary of the personal data being processed and the processing activities undertaken, (b) the identities of all Data Fiduciaries and Data Processors with whom their data has been shared, and (c) any other information prescribed by rules.",
        "confidence_score": 1.00,
        "legal_time_start": "2023-08-11T00:00:00Z",
        "entities": ["Data Principal", "Data Fiduciary"],
        "business_impact": {"impact_summary": "Requires building data subject access request (DSAR) fulfilment workflows.", "action_required": "Implement automated DSAR response pipeline capable of providing data summaries within prescribed timelines."},
        "evidence": [{"id": "ev-sec11", "source_urn": "urn:ki:in:dpdp:source:gazette-dpdpa-2023", "source_name": "Gazette of India — DPDPA 2023", "source_tier": "primary", "citation_text": "The Data Principal shall have the right to obtain from the Data Fiduciary a summary of personal data...", "coordinates": {"section": "Section 11"}, "verification_status": "verified"}],
        "linked_objects": ["urn:ki:in:dpdp:act:dpdpa-2023"],
        "relations": [{"target_urn": "urn:ki:in:dpdp:act:dpdpa-2023", "edge_type": "Depends On"}]
    },
    {
        "urn": "urn:ki:in:dpdp:act:2023:sec:12",
        "title": "Section 12 — Right of Correction and Erasure",
        "type": "Act",
        "version": 1,
        "summary": "Data Principals have the right to: (a) correct inaccurate or misleading personal data, (b) complete incomplete data, (c) update personal data, and (d) erase personal data that is no longer necessary for the purpose. Upon receiving a request, the Data Fiduciary must comply unless retention is required by law.",
        "confidence_score": 1.00,
        "legal_time_start": "2023-08-11T00:00:00Z",
        "entities": ["Data Principal", "Data Fiduciary"],
        "business_impact": {"impact_summary": "Right to erasure ('right to be forgotten') applies to all digital personal data.", "action_required": "Build data correction and erasure workflows across all systems, databases, and third-party processors."},
        "evidence": [{"id": "ev-sec12", "source_urn": "urn:ki:in:dpdp:source:gazette-dpdpa-2023", "source_name": "Gazette of India — DPDPA 2023", "source_tier": "primary", "citation_text": "The Data Principal shall have the right to correction and erasure of personal data...", "coordinates": {"section": "Section 12"}, "verification_status": "verified"}],
        "linked_objects": ["urn:ki:in:dpdp:act:dpdpa-2023"],
        "relations": [{"target_urn": "urn:ki:in:dpdp:act:dpdpa-2023", "edge_type": "Depends On"}]
    },
    {
        "urn": "urn:ki:in:dpdp:act:2023:sec:13",
        "title": "Section 13 — Right of Grievance Redressal",
        "type": "Act",
        "version": 1,
        "summary": "Data Principals have the right to readily available grievance redressal. Data Fiduciaries must respond to grievances within a prescribed period. If unsatisfied, the Data Principal may complain to the Data Protection Board.",
        "confidence_score": 1.00,
        "legal_time_start": "2023-08-11T00:00:00Z",
        "entities": ["Data Principal", "Data Fiduciary", "Authority"],
        "business_impact": {"impact_summary": "Mandatory internal grievance redressal mechanism required before DPBI escalation.", "action_required": "Establish a privacy grievance channel with defined SLAs and escalation paths."},
        "evidence": [{"id": "ev-sec13", "source_urn": "urn:ki:in:dpdp:source:gazette-dpdpa-2023", "source_name": "Gazette of India — DPDPA 2023", "source_tier": "primary", "citation_text": "The Data Principal shall have the right to have readily available means of grievance redressal...", "coordinates": {"section": "Section 13"}, "verification_status": "verified"}],
        "linked_objects": ["urn:ki:in:dpdp:act:dpdpa-2023"],
        "relations": [{"target_urn": "urn:ki:in:dpdp:act:dpdpa-2023", "edge_type": "Depends On"}]
    },
    {
        "urn": "urn:ki:in:dpdp:act:2023:sec:14",
        "title": "Section 14 — Right of Nomination",
        "type": "Act",
        "version": 1,
        "summary": "A Data Principal may nominate any other individual to exercise their rights in the event of their death or incapacity. The nominated person can then act on behalf of the Data Principal for access, correction, erasure, and grievance redressal.",
        "confidence_score": 1.00,
        "legal_time_start": "2023-08-11T00:00:00Z",
        "entities": ["Data Principal", "Person"],
        "business_impact": {"impact_summary": "Requires nomination workflows in user account settings.", "action_required": "Add nomination feature to user profile/settings allowing designation of a nominee."},
        "evidence": [{"id": "ev-sec14", "source_urn": "urn:ki:in:dpdp:source:gazette-dpdpa-2023", "source_name": "Gazette of India — DPDPA 2023", "source_tier": "primary", "citation_text": "The Data Principal may nominate any other individual...", "coordinates": {"section": "Section 14"}, "verification_status": "verified"}],
        "linked_objects": ["urn:ki:in:dpdp:act:dpdpa-2023"],
        "relations": [{"target_urn": "urn:ki:in:dpdp:act:dpdpa-2023", "edge_type": "Depends On"}]
    },
    {
        "urn": "urn:ki:in:dpdp:act:2023:sec:16",
        "title": "Section 16 — Transfer of Personal Data Outside India",
        "type": "Act",
        "version": 1,
        "summary": "Cross-border transfer of personal data is permitted by default. The Central Government may restrict transfer to specific countries or territories by notification (negative-list / blacklist model). No restricted-country list has been published as of July 2026. Does not override pre-existing sector-specific data localization mandates (e.g., RBI, IRDAI).",
        "confidence_score": 1.00,
        "legal_time_start": "2023-08-11T00:00:00Z",
        "entities": ["Country", "Data Fiduciary", "Authority"],
        "business_impact": {"impact_summary": "Liberal cross-border regime but subject to future government restrictions and sector-specific overrides.", "action_required": "Monitor government notifications for blacklisted jurisdictions; maintain sector-specific compliance for RBI/IRDAI/SEBI data."},
        "evidence": [{"id": "ev-sec16", "source_urn": "urn:ki:in:dpdp:source:gazette-dpdpa-2023", "source_name": "Gazette of India — DPDPA 2023", "source_tier": "primary", "citation_text": "The Central Government may, after an assessment of such factors as it may consider necessary, restrict the transfer of personal data...", "coordinates": {"section": "Section 16"}, "verification_status": "verified"}],
        "linked_objects": ["urn:ki:in:dpdp:act:dpdpa-2023"],
        "relations": [{"target_urn": "urn:ki:in:dpdp:act:dpdpa-2023", "edge_type": "Depends On"}]
    },
    {
        "urn": "urn:ki:in:dpdp:act:2023:sec:17",
        "title": "Section 17 — Exemptions",
        "type": "Act",
        "version": 1,
        "summary": "The Central Government may exempt State instrumentalities from DPDPA obligations in the interests of sovereignty, integrity of India, security of the State, friendly relations with foreign states, or maintenance of public order. Criticized for being sweeping with insufficient oversight, potentially enabling mass surveillance. Currently challenged in the Supreme Court.",
        "confidence_score": 1.00,
        "legal_time_start": "2023-08-11T00:00:00Z",
        "entities": ["Authority", "Act"],
        "business_impact": {"impact_summary": "Government agencies processing citizen data may claim exemptions — creates asymmetric accountability.", "action_required": "Monitor government exemption notifications; assess implications for B2G data processing contracts."},
        "evidence": [{"id": "ev-sec17", "source_urn": "urn:ki:in:dpdp:source:gazette-dpdpa-2023", "source_name": "Gazette of India — DPDPA 2023", "source_tier": "primary", "citation_text": "The Central Government may, by notification, exempt any instrumentality of the State...", "coordinates": {"section": "Section 17"}, "verification_status": "verified"}],
        "linked_objects": ["urn:ki:in:dpdp:act:dpdpa-2023", "urn:ki:in:dpdp:case:sc-dpdpa-challenge-2026"],
        "relations": [{"target_urn": "urn:ki:in:dpdp:act:dpdpa-2023", "edge_type": "Depends On"}]
    },
    {
        "urn": "urn:ki:in:dpdp:act:2023:sec:18",
        "title": "Section 18 — Data Protection Board of India",
        "type": "Act",
        "version": 1,
        "summary": "Establishes the Data Protection Board of India (DPBI) as a body corporate. The Board adjudicates complaints, investigates breaches, imposes penalties, and provides guidance. Designed as a 'digital-by-design' institution. Composed of 1 Chairperson + up to 4 Members. As of July 2026, recruitment initiated but not yet fully operational.",
        "confidence_score": 1.00,
        "legal_time_start": "2023-08-11T00:00:00Z",
        "entities": ["Authority", "Organization"],
        "business_impact": {"impact_summary": "The DPBI is the primary enforcement body — all complaints and penalties flow through it.", "action_required": "Familiarize with DPBI complaint process; prepare breach notification templates for Board filings."},
        "evidence": [{"id": "ev-sec18", "source_urn": "urn:ki:in:dpdp:source:gazette-dpdpa-2023", "source_name": "Gazette of India — DPDPA 2023", "source_tier": "primary", "citation_text": "The Central Government shall, by notification, establish a Board to be known as the Data Protection Board of India...", "coordinates": {"section": "Section 18"}, "verification_status": "verified"}],
        "linked_objects": ["urn:ki:in:dpdp:act:dpdpa-2023"],
        "relations": [{"target_urn": "urn:ki:in:dpdp:act:dpdpa-2023", "edge_type": "Depends On"}]
    },
    {
        "urn": "urn:ki:in:dpdp:act:2023:sec:33",
        "title": "Section 33 — Penalties",
        "type": "Act",
        "version": 1,
        "summary": "Empowers the DPBI to impose monetary penalties per the Schedule. Maximum penalties: ₹250 Cr (security safeguard failure), ₹200 Cr (breach notification failure), ₹200 Cr (children's data breach), ₹150 Cr (SDF obligations breach), ₹50 Cr (other breaches), ₹10,000 (Data Principal duty breach). Penalties are assessed per instance; multiple violations can compound.",
        "confidence_score": 1.00,
        "legal_time_start": "2023-08-11T00:00:00Z",
        "entities": ["Penalty", "Authority", "Risk"],
        "business_impact": {"impact_summary": "Penalties can reach ₹250 crore per instance — existential risk for many organizations.", "action_required": "Quantify financial exposure; ensure security safeguards and breach response meet Act standards to mitigate penalty risk."},
        "evidence": [{"id": "ev-sec33", "source_urn": "urn:ki:in:dpdp:source:gazette-dpdpa-2023", "source_name": "Gazette of India — DPDPA 2023", "source_tier": "primary", "citation_text": "The Board may, after inquiry, impose such monetary penalty as specified in the Schedule...", "coordinates": {"section": "Section 33, Schedule"}, "verification_status": "verified"}],
        "linked_objects": ["urn:ki:in:dpdp:act:dpdpa-2023"],
        "relations": [{"target_urn": "urn:ki:in:dpdp:act:dpdpa-2023", "edge_type": "Depends On"}]
    },
    {
        "urn": "urn:ki:in:dpdp:act:2023:sec:44",
        "title": "Section 44 — Amendment to Other Laws (RTI Act)",
        "type": "Act",
        "version": 1,
        "summary": "Section 44(3) amends Section 8(1)(j) of the Right to Information Act 2005, replacing the prior 'public interest' override for personal information with a broader exemption: 'information which relates to personal information'. Critics argue this removes the public interest test entirely, severely weakening RTI transparency. Matter referred to Constitution Bench of the Supreme Court.",
        "confidence_score": 1.00,
        "legal_time_start": "2023-08-11T00:00:00Z",
        "entities": ["Act"],
        "business_impact": {"impact_summary": "May limit access to public officials' personal data under RTI; impacts journalism and governance accountability.", "action_required": "Monitor Supreme Court Constitution Bench proceedings for any ruling that could alter this provision."},
        "evidence": [{"id": "ev-sec44", "source_urn": "urn:ki:in:dpdp:source:gazette-dpdpa-2023", "source_name": "Gazette of India — DPDPA 2023", "source_tier": "primary", "citation_text": "In Section 8 of the Right to Information Act, 2005, for clause (j), the following clause shall be substituted...", "coordinates": {"section": "Section 44(3)"}, "verification_status": "verified"}],
        "linked_objects": ["urn:ki:in:dpdp:act:dpdpa-2023", "urn:ki:in:dpdp:case:sc-rti-conflict-2026"],
        "relations": [{"target_urn": "urn:ki:in:dpdp:act:dpdpa-2023", "edge_type": "Depends On"}, {"target_urn": "urn:ki:in:dpdp:case:sc-rti-conflict-2026", "edge_type": "Conflicts With"}]
    },
]

# ═══════════════════════════════════════════════════════════════════════════════
# LAYER 1: PRIMARY AUTHORITY — THE RULES (Confidence = 1.0)
# ═══════════════════════════════════════════════════════════════════════════════

RULES_PARENT = {
    "urn": "urn:ki:in:dpdp:rule:dpdp-rules-2025",
    "title": "Digital Personal Data Protection Rules 2025",
    "type": "Rule",
    "version": 1,
    "summary": "The official rules specifying procedural details under the DPDP Act. Notified on November 13, 2025. Lays down concrete timelines, form templates, and rules for consent notices, DPBI operation, children's verifiable consent, consent managers, breach notification (72 hours), and cross-border transfers. Phased implementation concluding May 13, 2027.",
    "confidence_score": 0.98,
    "legal_time_start": "2025-11-13T00:00:00Z",
    "entities": ["Rule", "Consent Manager", "Consent", "Authority", "Control"],
    "business_impact": {"impact_summary": "Mandates phased compliance timeline reaching full enforcement by May 13, 2027.", "action_required": "Align corporate privacy readiness program with the 18-month phased implementation roadmap."},
    "evidence": [{"id": "ev-002", "source_urn": "urn:ki:in:dpdp:source:gazette-rules-2025", "source_name": "MeitY Notification G.S.R.", "source_tier": "primary", "citation_text": "In exercise of the powers conferred by section 40 of the Digital Personal Data Protection Act, 2023, the Central Government hereby makes the following rules...", "coordinates": {"page": 1, "section": "Rule 1"}, "hash": "e5473a216db8aefcd81ab45dcf328a9be45c6db274f8a8de751db432ef5012ab", "verification_status": "verified"}],
    "linked_objects": ["urn:ki:in:dpdp:act:dpdpa-2023"],
    "relations": [{"target_urn": "urn:ki:in:dpdp:act:dpdpa-2023", "edge_type": "Implements"}]
}

RULE_SECTIONS = [
    {
        "urn": "urn:ki:in:dpdp:rule:breach-notification-rule7",
        "title": "DPDP Rules 2025 — Rule 7: Personal Data Breach Intimation",
        "type": "Rule", "version": 1,
        "summary": "Mandates that Data Fiduciaries must report personal data breaches to the Data Protection Board of India and affected Data Principals without delay and within 72 hours. Reports must detail the nature of the breach, data categories affected, approximate number of individuals impacted, potential consequences, and measures taken or proposed to mitigate the breach. Effective May 13, 2027.",
        "confidence_score": 1.00, "legal_time_start": "2025-11-13T00:00:00Z",
        "entities": ["Rule", "Control", "Risk", "Data Fiduciary", "Authority"],
        "business_impact": {"impact_summary": "72-hour mandatory breach reporting to DPBI creates high-pressure incident response requirements.", "action_required": "Deploy a 72-hour breach reporting SOC playbook with pre-drafted DPBI notification templates."},
        "evidence": [{"id": "ev-r7", "source_urn": "urn:ki:in:dpdp:source:gazette-rules-2025", "source_name": "MeitY Notification — DPDP Rules 2025", "source_tier": "primary", "citation_text": "In the event of a personal data breach, the Data Fiduciary shall intimate the Board and each affected Data Principal...", "coordinates": {"section": "Rule 7"}, "verification_status": "verified"}],
        "linked_objects": ["urn:ki:in:dpdp:rule:dpdp-rules-2025"],
        "relations": [{"target_urn": "urn:ki:in:dpdp:rule:dpdp-rules-2025", "edge_type": "Depends On"}]
    },
    {
        "urn": "urn:ki:in:dpdp:rule:2025:r4",
        "title": "DPDP Rules 2025 — Rule 4: Consent Manager Registration",
        "type": "Rule", "version": 1,
        "summary": "Establishes the regulatory framework for Consent Managers as registered intermediaries. Requirements: must be an India-incorporated company, demonstrate technical/financial capacity (minimum ₹2 crore net worth), maintain consent records for 7 years, undergo regular audits, and provide secure, interoperable, user-friendly platforms based on DEPA architecture. Effective November 13, 2026.",
        "confidence_score": 1.00, "legal_time_start": "2025-11-13T00:00:00Z",
        "entities": ["Rule", "Consent Manager", "Consent", "Organization"],
        "business_impact": {"impact_summary": "Creates a new regulated entity category — businesses wanting to operate as Consent Managers must register.", "action_required": "If planning to offer consent management services, begin registration preparation by mid-2026. If a Data Fiduciary, plan integration with registered Consent Managers."},
        "evidence": [{"id": "ev-r4", "source_urn": "urn:ki:in:dpdp:source:gazette-rules-2025", "source_name": "MeitY Notification — DPDP Rules 2025", "source_tier": "primary", "citation_text": "An entity seeking registration as a Consent Manager shall submit an application to the Board...", "coordinates": {"section": "Rule 4, First Schedule"}, "verification_status": "verified"}],
        "linked_objects": ["urn:ki:in:dpdp:rule:dpdp-rules-2025"],
        "relations": [{"target_urn": "urn:ki:in:dpdp:rule:dpdp-rules-2025", "edge_type": "Depends On"}]
    },
    {
        "urn": "urn:ki:in:dpdp:rule:2025:r5",
        "title": "DPDP Rules 2025 — Rule 5: Verifiable Consent for Children",
        "type": "Rule", "version": 1,
        "summary": "Specifies procedures for obtaining verifiable parental consent before processing children's data. Verification may use reliable identity details or digital tokens. Prohibits tracking, monitoring, targeted advertising, and profiling of children. A child is any individual under 18. Government may exempt certain classes of Data Fiduciaries. Effective May 13, 2027.",
        "confidence_score": 1.00, "legal_time_start": "2025-11-13T00:00:00Z",
        "entities": ["Rule", "Consent", "Person", "Control"],
        "business_impact": {"impact_summary": "EdTech, gaming, and social media companies must implement age gates and parental consent flows.", "action_required": "Implement age verification at onboarding; build verifiable parental consent workflow; disable ad targeting for minors."},
        "evidence": [{"id": "ev-r5", "source_urn": "urn:ki:in:dpdp:source:gazette-rules-2025", "source_name": "MeitY Notification — DPDP Rules 2025", "source_tier": "primary", "citation_text": "The Data Fiduciary shall obtain verifiable consent of the parent or lawful guardian...", "coordinates": {"section": "Rule 5"}, "verification_status": "verified"}],
        "linked_objects": ["urn:ki:in:dpdp:rule:dpdp-rules-2025", "urn:ki:in:dpdp:act:2023:sec:9"],
        "relations": [{"target_urn": "urn:ki:in:dpdp:rule:dpdp-rules-2025", "edge_type": "Depends On"}, {"target_urn": "urn:ki:in:dpdp:act:2023:sec:9", "edge_type": "Implements"}]
    },
    {
        "urn": "urn:ki:in:dpdp:rule:2025:r23",
        "title": "DPDP Rules 2025 — Rule 23: Cross-Border Data Transfer",
        "type": "Rule", "version": 1,
        "summary": "Operationalizes the negative-list (blacklist) cross-border transfer model under Section 16. Transfers are permitted by default unless the government restricts specific destinations by notification. As of July 2026, no restricted-country list has been published. Does not override sector-specific localization mandates (RBI, IRDAI, SEBI).",
        "confidence_score": 1.00, "legal_time_start": "2025-11-13T00:00:00Z",
        "entities": ["Rule", "Country", "Data Fiduciary"],
        "business_impact": {"impact_summary": "Relatively liberal cross-border regime compared to GDPR — no adequacy/SCC requirements currently.", "action_required": "Monitor government notifications; maintain sector-specific compliance for financial/insurance data."},
        "evidence": [{"id": "ev-r23", "source_urn": "urn:ki:in:dpdp:source:gazette-rules-2025", "source_name": "MeitY Notification — DPDP Rules 2025", "source_tier": "primary", "citation_text": "The Central Government may, by general or special order, restrict transfer of personal data to such country or territory...", "coordinates": {"section": "Rule 23"}, "verification_status": "verified"}],
        "linked_objects": ["urn:ki:in:dpdp:rule:dpdp-rules-2025", "urn:ki:in:dpdp:act:2023:sec:16"],
        "relations": [{"target_urn": "urn:ki:in:dpdp:rule:dpdp-rules-2025", "edge_type": "Depends On"}, {"target_urn": "urn:ki:in:dpdp:act:2023:sec:16", "edge_type": "Implements"}]
    },
]

# ═══════════════════════════════════════════════════════════════════════════════
# LAYER 1: PENALTY SCHEDULE (Confidence = 1.0)
# ═══════════════════════════════════════════════════════════════════════════════

PENALTIES = [
    {"urn": "urn:ki:in:dpdp:penalty:security-safeguards", "title": "Penalty: Failure to Take Reasonable Security Safeguards", "type": "Penalty", "version": 1, "summary": "Maximum penalty of ₹250 crore for failure to take reasonable security safeguards to prevent a personal data breach. Assessed by DPBI after inquiry.", "confidence_score": 1.00, "legal_time_start": "2023-08-11T00:00:00Z", "entities": ["Penalty", "Risk", "Control"], "business_impact": {"impact_summary": "Highest penalty in the Act — existential risk for negligent organizations.", "action_required": "Implement and document 'reasonable security safeguards' per industry standards (ISO 27001, SOC 2)."}, "evidence": [{"id": "ev-pen1", "source_urn": "urn:ki:in:dpdp:source:gazette-dpdpa-2023", "source_name": "DPDPA 2023 — Schedule", "source_tier": "primary", "citation_text": "Breach of section 8(5): Up to two hundred and fifty crore rupees", "coordinates": {"section": "Schedule, Item 1"}, "verification_status": "verified"}], "linked_objects": ["urn:ki:in:dpdp:act:2023:sec:33"], "relations": [{"target_urn": "urn:ki:in:dpdp:act:2023:sec:33", "edge_type": "Depends On"}]},
    {"urn": "urn:ki:in:dpdp:penalty:breach-notification", "title": "Penalty: Failure to Notify Data Breach", "type": "Penalty", "version": 1, "summary": "Maximum penalty of ₹200 crore for failure to notify the Board or affected Data Principals of a personal data breach.", "confidence_score": 1.00, "legal_time_start": "2023-08-11T00:00:00Z", "entities": ["Penalty", "Risk"], "business_impact": {"impact_summary": "₹200 crore exposure for suppressing or delaying breach notifications.", "action_required": "Establish automated breach detection and 72-hour notification pipeline."}, "evidence": [{"id": "ev-pen2", "source_urn": "urn:ki:in:dpdp:source:gazette-dpdpa-2023", "source_name": "DPDPA 2023 — Schedule", "source_tier": "primary", "citation_text": "Breach of section 8(6): Up to two hundred crore rupees", "coordinates": {"section": "Schedule, Item 2"}, "verification_status": "verified"}], "linked_objects": ["urn:ki:in:dpdp:act:2023:sec:33"], "relations": [{"target_urn": "urn:ki:in:dpdp:act:2023:sec:33", "edge_type": "Depends On"}]},
    {"urn": "urn:ki:in:dpdp:penalty:children-data", "title": "Penalty: Breach of Children's Data Obligations", "type": "Penalty", "version": 1, "summary": "Maximum penalty of ₹200 crore for breach of additional obligations relating to processing children's data (Section 9).", "confidence_score": 1.00, "legal_time_start": "2023-08-11T00:00:00Z", "entities": ["Penalty", "Person", "Risk"], "business_impact": {"impact_summary": "EdTech and child-facing services face ₹200 crore per violation.", "action_required": "Prioritize children's data compliance — age verification, parental consent, and no-targeting policies."}, "evidence": [{"id": "ev-pen3", "source_urn": "urn:ki:in:dpdp:source:gazette-dpdpa-2023", "source_name": "DPDPA 2023 — Schedule", "source_tier": "primary", "citation_text": "Breach of section 9: Up to two hundred crore rupees", "coordinates": {"section": "Schedule, Item 3"}, "verification_status": "verified"}], "linked_objects": ["urn:ki:in:dpdp:act:2023:sec:33"], "relations": [{"target_urn": "urn:ki:in:dpdp:act:2023:sec:33", "edge_type": "Depends On"}]},
    {"urn": "urn:ki:in:dpdp:penalty:sdf-obligations", "title": "Penalty: Breach of SDF Obligations", "type": "Penalty", "version": 1, "summary": "Maximum penalty of ₹150 crore for breach of additional obligations of a Significant Data Fiduciary (Section 10).", "confidence_score": 1.00, "legal_time_start": "2023-08-11T00:00:00Z", "entities": ["Penalty", "Data Fiduciary", "Risk"], "business_impact": {"impact_summary": "SDFs face ₹150 crore for DPO/DPIA/audit non-compliance.", "action_required": "Ensure DPO appointment, annual audit, and DPIA completion for SDF-designated entities."}, "evidence": [{"id": "ev-pen4", "source_urn": "urn:ki:in:dpdp:source:gazette-dpdpa-2023", "source_name": "DPDPA 2023 — Schedule", "source_tier": "primary", "citation_text": "Breach of section 10: Up to one hundred and fifty crore rupees", "coordinates": {"section": "Schedule, Item 4"}, "verification_status": "verified"}], "linked_objects": ["urn:ki:in:dpdp:act:2023:sec:33"], "relations": [{"target_urn": "urn:ki:in:dpdp:act:2023:sec:33", "edge_type": "Depends On"}]},
    {"urn": "urn:ki:in:dpdp:penalty:general-breach", "title": "Penalty: General Breach of Other Provisions", "type": "Penalty", "version": 1, "summary": "Maximum penalty of ₹50 crore for breach of any other provision of the Act or rules not specifically listed in the Schedule.", "confidence_score": 1.00, "legal_time_start": "2023-08-11T00:00:00Z", "entities": ["Penalty", "Risk"], "business_impact": {"impact_summary": "Catch-all penalty for any non-compliance not covered by higher-tier penalties.", "action_required": "Comprehensive compliance across all Act provisions to avoid residual liability."}, "evidence": [{"id": "ev-pen5", "source_urn": "urn:ki:in:dpdp:source:gazette-dpdpa-2023", "source_name": "DPDPA 2023 — Schedule", "source_tier": "primary", "citation_text": "Breach of any other provision: Up to fifty crore rupees", "coordinates": {"section": "Schedule, Item 7"}, "verification_status": "verified"}], "linked_objects": ["urn:ki:in:dpdp:act:2023:sec:33"], "relations": [{"target_urn": "urn:ki:in:dpdp:act:2023:sec:33", "edge_type": "Depends On"}]},
]

# ═══════════════════════════════════════════════════════════════════════════════
# LAYER 2: JUDICIAL AUTHORITY (Confidence = 0.9)
# ═══════════════════════════════════════════════════════════════════════════════

JUDICIAL = [
    {"urn": "urn:ki:in:privacy:judgement:puttaswamy-2017", "title": "Justice K.S. Puttaswamy v. Union of India (2017)", "type": "Judgement", "version": 1, "summary": "Landmark 9-judge bench ruling unanimously declaring the Right to Privacy a fundamental right under Article 21 of the Indian Constitution. Established the proportionality test: any state interference with privacy must be (1) backed by a valid law, (2) pursue a legitimate state aim, and (3) be proportionate. Mandated creation of a comprehensive data protection framework — directly leading to the DPDPA 2023.", "confidence_score": 0.95, "legal_time_start": "2017-08-24T00:00:00Z", "entities": ["Judgement", "Act", "Person", "Authority"], "business_impact": {"impact_summary": "Constitutional foundation for all data protection law in India. All DPDPA provisions are tested against this standard.", "action_required": "Understand the proportionality test — it is the judicial standard against which DPDPA provisions and government exemptions are challenged."}, "evidence": [{"id": "ev-putt", "source_urn": "urn:ki:in:sc:judgement:puttaswamy-2017", "source_name": "Supreme Court of India — W.P.(C) 494/2012", "source_tier": "primary", "citation_text": "The right to privacy is protected as an intrinsic part of the right to life and personal liberty under Article 21 and as a part of the freedoms guaranteed by Part III of the Constitution.", "coordinates": {"section": "Majority Opinion"}, "verification_status": "verified"}], "linked_objects": ["urn:ki:in:dpdp:act:dpdpa-2023"], "relations": [{"target_urn": "urn:ki:in:dpdp:act:dpdpa-2023", "edge_type": "Supports"}]},
    {"urn": "urn:ki:in:dpdp:case:sc-dpdpa-challenge-2026", "title": "DPDPA Constitutional Challenge — Supreme Court (2026)", "type": "Case", "version": 1, "summary": "A clutch of writ petitions challenging the DPDPA 2023 and DPDP Rules 2025 before the Supreme Court. Filed by Geeta Seshu, SFLC, Reporters Collective, Nitin Sethi, NCPRI, Venkatesh Nayak. Key issues: (1) independence of DPBI, (2) RTI dilution via Sec 44(3), (3) state surveillance via Sec 17, (4) definitional ambiguity. Status: sub judice; notices issued; no interim stay. Next hearing: August 2026.", "confidence_score": 0.90, "legal_time_start": "2026-02-01T00:00:00Z", "entities": ["Case", "Act", "Authority", "Person"], "business_impact": {"impact_summary": "Could result in structural changes to DPBI governance, modification of Sec 17 exemptions, or reinstatement of RTI public interest test.", "action_required": "Monitor proceedings closely; any ruling could invalidate or modify key Act provisions, requiring rapid compliance adjustments."}, "evidence": [{"id": "ev-sc-challenge", "source_urn": "urn:ki:in:sc:case:dpdpa-2026", "source_name": "LiveLaw.in — SC Issues Notice on DPDPA Challenge", "source_tier": "secondary", "citation_text": "The Supreme Court issued notices to the Union of India regarding multiple writ petitions challenging the DPDPA.", "coordinates": {"section": "Legal reporting"}, "verification_status": "verified"}], "linked_objects": ["urn:ki:in:dpdp:act:dpdpa-2023", "urn:ki:in:dpdp:act:2023:sec:17", "urn:ki:in:dpdp:act:2023:sec:44"], "relations": [{"target_urn": "urn:ki:in:dpdp:act:2023:sec:17", "edge_type": "Conflicts With"}, {"target_urn": "urn:ki:in:dpdp:act:2023:sec:44", "edge_type": "Conflicts With"}]},
    {"urn": "urn:ki:in:dpdp:case:sc-rti-conflict-2026", "title": "RTI Act vs DPDPA Conflict — Constitution Bench Referral", "type": "Case", "version": 1, "summary": "The Supreme Court referred the question of whether Section 44(3) of DPDPA (amending RTI Act Section 8(1)(j)) unconstitutionally removes the 'public interest' test for disclosure of personal information. Filed by NCPRI and journalists. Status: referred to Constitution Bench as of July 2026.", "confidence_score": 0.90, "legal_time_start": "2026-07-01T00:00:00Z", "entities": ["Case", "Act"], "business_impact": {"impact_summary": "If the Constitution Bench strikes down Sec 44(3), the RTI public interest override would be restored.", "action_required": "Track Constitution Bench hearings; prepare for potential re-alignment of RTI and data protection obligations."}, "evidence": [{"id": "ev-rti-case", "source_urn": "urn:ki:in:sc:case:rti-dpdpa-2026", "source_name": "The Hindu — SC refers RTI vs DPDPA to Constitution Bench", "source_tier": "secondary", "citation_text": "The Supreme Court referred the RTI vs DPDPA conflict to a Constitution Bench.", "coordinates": {"section": "Legal reporting"}, "verification_status": "verified"}], "linked_objects": ["urn:ki:in:dpdp:act:2023:sec:44"], "relations": [{"target_urn": "urn:ki:in:dpdp:act:2023:sec:44", "edge_type": "Conflicts With"}]},
]

# ═══════════════════════════════════════════════════════════════════════════════
# LAYER 3: REGULATORY NOTIFICATIONS & SECTOR OVERLAPS (Confidence = 0.7)
# ═══════════════════════════════════════════════════════════════════════════════

REGULATORY = [
    {"urn": "urn:ki:in:dpdp:notification:rules-gazette-2025", "title": "Gazette Notification: DPDP Rules 2025", "type": "Notification", "version": 1, "summary": "Official publication of the Digital Personal Data Protection Rules 2025 in the Gazette of India Extraordinary Part II Section 3(i). Published by MeitY on November 13, 2025. Triggers the 18-month phased implementation timeline.", "confidence_score": 0.70, "legal_time_start": "2025-11-13T00:00:00Z", "entities": ["Notification", "Authority", "Rule"], "business_impact": {"impact_summary": "The clock starts ticking — compliance deadlines are now legally binding.", "action_required": "Begin Phase 1 compliance immediately; plan for Phase 2 (Nov 2026) and Phase 3 (May 2027)."}, "evidence": [{"id": "ev-gazette-rules", "source_urn": "urn:ki:in:meity:gazette:2025", "source_name": "Gazette of India Extraordinary", "source_tier": "primary", "citation_text": "In exercise of the powers conferred by section 40...", "coordinates": {"section": "Gazette"}, "verification_status": "verified"}], "linked_objects": ["urn:ki:in:dpdp:rule:dpdp-rules-2025"], "relations": [{"target_urn": "urn:ki:in:dpdp:rule:dpdp-rules-2025", "edge_type": "References"}]},
    {"urn": "urn:ki:in:dpdp:notification:dpbi-recruitment-2026", "title": "MeitY: DPBI Chairperson & Members Recruitment (May 2026)", "type": "Notification", "version": 1, "summary": "MeitY invited public applications for the appointment of 1 Chairperson and 4 Members of the Data Protection Board of India in May 2026. Candidates require 5+ years experience in data governance, law, or digital economy. Selection via Search-cum-Selection Committee (SCSC). As of July 2026, appointment process is ongoing.", "confidence_score": 0.70, "legal_time_start": "2026-05-01T00:00:00Z", "entities": ["Notification", "Authority", "Person", "Organization"], "business_impact": {"impact_summary": "Once appointed, the DPBI will begin active enforcement — complaint adjudication and penalty imposition.", "action_required": "Monitor appointment announcements; prepare for potential enforcement actions post-DPBI operationalization."}, "evidence": [{"id": "ev-dpbi-recruit", "source_urn": "urn:ki:in:meity:notification:dpbi-2026", "source_name": "NASSCOM / BestMediaInfo reporting", "source_tier": "secondary", "citation_text": "MeitY initiated the formal process to appoint the Chairperson and four Members of the Board...", "coordinates": {"section": "News reporting"}, "verification_status": "verified"}], "linked_objects": ["urn:ki:in:dpdp:act:2023:sec:18"], "relations": [{"target_urn": "urn:ki:in:dpdp:act:2023:sec:18", "edge_type": "Implements"}]},
    {"urn": "urn:ki:in:sector:rbi:data-localization-2018", "title": "RBI Circular: Storage of Payment System Data in India", "type": "Circular", "version": 1, "summary": "RBI circular of April 2018 mandating that all system providers operating payment systems in India must ensure that the entire payment data is stored in India only. Overrides the DPDPA's permissive cross-border transfer model for payment data. Remains in full force alongside DPDPA.", "confidence_score": 0.70, "legal_time_start": "2018-04-06T00:00:00Z", "entities": ["Circular", "Authority", "Industry", "Data Category", "Country"], "business_impact": {"impact_summary": "Payment data MUST be stored in India regardless of DPDPA's liberal cross-border provisions.", "action_required": "Ensure all payment data infrastructure is India-resident; do not rely solely on DPDPA's permissive regime."}, "evidence": [{"id": "ev-rbi-local", "source_urn": "urn:ki:in:rbi:circular:data-localization", "source_name": "RBI Circular DPSS.CO.OD No. 2785/06.08.005/2017-18", "source_tier": "primary", "citation_text": "...all system providers shall ensure that the entire data relating to payment systems operated by them are stored in a system only in India.", "coordinates": {"section": "Para 2"}, "verification_status": "verified"}], "linked_objects": ["urn:ki:in:dpdp:act:2023:sec:16"], "relations": [{"target_urn": "urn:ki:in:dpdp:act:2023:sec:16", "edge_type": "Overrides"}]},
    {"urn": "urn:ki:in:sector:sebi:data-governance", "title": "SEBI Framework: Regulated Entities Data Governance", "type": "Circular", "version": 1, "summary": "SEBI's data governance framework for regulated entities (stockbrokers, depositories, mutual funds). Mandates data handling standards for capital market entities that operate alongside and in addition to DPDPA requirements. Creates dual compliance obligation for BFSI entities.", "confidence_score": 0.70, "legal_time_start": "2023-01-01T00:00:00Z", "entities": ["Circular", "Authority", "Industry", "Organization"], "business_impact": {"impact_summary": "Capital market entities face dual compliance — DPDPA + SEBI-specific data governance standards.", "action_required": "Map SEBI data governance requirements alongside DPDPA obligations for capital market operations."}, "evidence": [{"id": "ev-sebi-dg", "source_urn": "urn:ki:in:sebi:framework:data-governance", "source_name": "SEBI Data Governance Framework", "source_tier": "primary", "citation_text": "All regulated entities shall implement comprehensive data governance standards...", "coordinates": {"section": "Framework"}, "verification_status": "verified"}], "linked_objects": ["urn:ki:in:dpdp:act:dpdpa-2023"], "relations": [{"target_urn": "urn:ki:in:dpdp:act:dpdpa-2023", "edge_type": "References"}]},
]

# ═══════════════════════════════════════════════════════════════════════════════
# LAYER 4: EXPERT OPINIONS (Confidence = 0.5)
# ═══════════════════════════════════════════════════════════════════════════════

OPINIONS = [
    {"urn": "urn:ki:in:dpdp:opinion:azb:rules-impact-2025", "title": "AZB & Partners: DPDP Rules 2025 Impact Assessment", "type": "Opinion", "version": 1, "summary": "Client advisory analyzing the operational impact of the DPDP Rules 2025 on corporate India. Key points: phased compliance timeline creates urgency, consent architecture redesign needed, 72-hour breach notification is aggressive but manageable with proper SOC playbook.", "confidence_score": 0.50, "source_credibility": "Tier 1", "forum_published": "AZB & Partners Client Advisory", "interpretation_stance": "Supportive", "legal_time_start": "2025-11-20T00:00:00Z", "entities": ["Opinion", "Organization", "Rule", "Control"], "business_impact": {"impact_summary": "Tier-1 law firm analysis validates the urgency of compliance preparation.", "action_required": "Use AZB's analysis as a compliance benchmark for enterprise readiness."}, "evidence": [{"id": "ev-azb", "source_urn": "urn:ki:in:dpdp:source:azb-advisory", "source_name": "AZB & Partners Client Advisory", "source_tier": "tertiary", "citation_text": "The notification of DPDP Rules represents a watershed moment requiring immediate corporate action.", "coordinates": {"section": "Advisory"}, "verification_status": "verified"}], "linked_objects": ["urn:ki:in:dpdp:rule:dpdp-rules-2025"], "relations": [{"target_urn": "urn:ki:in:dpdp:rule:dpdp-rules-2025", "edge_type": "Interprets"}]},
    {"urn": "urn:ki:in:dpdp:opinion:trilegal:compliance-roadmap-2025", "title": "Trilegal: DPDP Compliance Roadmap for Indian Enterprises", "type": "Opinion", "version": 1, "summary": "Comprehensive roadmap for DPDPA compliance. Advocates phased approach: (1) data mapping as first priority, (2) consent architecture design, (3) vendor contract updates, (4) breach response playbook deployment. Highlights that 2026 is the 'critical build year' before full enforcement in May 2027.", "confidence_score": 0.50, "source_credibility": "Tier 1", "forum_published": "Trilegal Insights", "interpretation_stance": "Supportive", "legal_time_start": "2025-12-01T00:00:00Z", "entities": ["Opinion", "Organization", "Business Process", "Control"], "business_impact": {"impact_summary": "Provides a structured compliance roadmap from a leading law firm.", "action_required": "Adopt the phased compliance approach: data mapping → consent → vendor contracts → breach playbook."}, "evidence": [{"id": "ev-trilegal", "source_urn": "urn:ki:in:dpdp:source:trilegal-insight", "source_name": "Trilegal Insights Publication", "source_tier": "tertiary", "citation_text": "2026 is the critical build year — organizations that delay data mapping will face compounded compliance debt.", "coordinates": {"section": "Compliance Roadmap"}, "verification_status": "verified"}], "linked_objects": ["urn:ki:in:dpdp:rule:dpdp-rules-2025"], "relations": [{"target_urn": "urn:ki:in:dpdp:rule:dpdp-rules-2025", "edge_type": "Interprets"}]},
    {"urn": "urn:ki:in:dpdp:opinion:cyril:internal-investigations-2026", "title": "Cyril Amarchand Mangaldas: Data Protection & Internal Investigations", "type": "Opinion", "version": 1, "summary": "Analysis of tension between DPDPA obligations and corporate internal investigations. Key insight: companies acting as Data Fiduciaries must balance investigative integrity with Data Principal rights (access, erasure, correction). The 'Data Fiduciary as investigator' paradox creates legal grey areas for forensic evidence collection and whistleblower protection.", "confidence_score": 0.50, "source_credibility": "Tier 1", "forum_published": "Cyril Amarchand Mangaldas Blog", "interpretation_stance": "Cautionary", "legal_time_start": "2026-03-01T00:00:00Z", "entities": ["Opinion", "Organization", "Business Process", "Risk"], "business_impact": {"impact_summary": "Internal investigations may conflict with DPDPA rights — legal grey area requires careful navigation.", "action_required": "Develop investigation protocols that respect DPDPA rights while preserving investigative capability."}, "evidence": [{"id": "ev-cyril", "source_urn": "urn:ki:in:dpdp:source:cyril-blog", "source_name": "Cyril Amarchand Mangaldas Blog", "source_tier": "tertiary", "citation_text": "The new data protection regime complicates internal investigations...", "coordinates": {"section": "Blog post"}, "verification_status": "verified"}], "linked_objects": ["urn:ki:in:dpdp:act:dpdpa-2023"], "relations": [{"target_urn": "urn:ki:in:dpdp:act:dpdpa-2023", "edge_type": "Interprets"}]},
    {"urn": "urn:ki:in:dpdp:opinion:nda:boardroom-governance-2026", "title": "Nishith Desai Associates: Data Protection as Boardroom Priority", "type": "Opinion", "version": 1, "summary": "Argues that data protection is no longer an IT/legal issue but a C-suite governance matter. DPOs should report to Board of Directors. Board-level accountability for data breaches. Privacy should be a standing board agenda item alongside financial risk and ESG.", "confidence_score": 0.50, "source_credibility": "Tier 1", "forum_published": "Nishith Desai Associates Publication", "interpretation_stance": "Supportive", "legal_time_start": "2026-01-15T00:00:00Z", "entities": ["Opinion", "Organization", "Person", "Control"], "business_impact": {"impact_summary": "Elevates data protection from operational to strategic board-level concern.", "action_required": "Position DPO as board-reporting role; include privacy metrics in board risk dashboard."}, "evidence": [{"id": "ev-nda", "source_urn": "urn:ki:in:dpdp:source:nda-publication", "source_name": "Nishith Desai Associates Research Papers", "source_tier": "tertiary", "citation_text": "Data protection must be treated as a boardroom priority, not merely an IT compliance checkbox.", "coordinates": {"section": "Research Paper"}, "verification_status": "verified"}], "linked_objects": ["urn:ki:in:dpdp:act:dpdpa-2023"], "relations": [{"target_urn": "urn:ki:in:dpdp:act:dpdpa-2023", "edge_type": "Interprets"}]},
    {"urn": "urn:ki:in:dpdp:opinion:khaitan:sdf-obligations-2026", "title": "Khaitan & Co: Navigating SDF Obligations Under DPDPA", "type": "Opinion", "version": 1, "summary": "Detailed analysis of Significant Data Fiduciary obligations. Covers SDF classification criteria, DPO role and responsibilities, DPIA methodology, audit cycle requirements (annual), and algorithmic due diligence expectations. Recommends proactive SDF self-assessment even before government designation.", "confidence_score": 0.50, "source_credibility": "Tier 1", "forum_published": "Khaitan & Co Client Alert", "interpretation_stance": "Supportive", "legal_time_start": "2026-02-01T00:00:00Z", "entities": ["Opinion", "Organization", "Data Fiduciary", "Control", "Risk"], "business_impact": {"impact_summary": "Practical guidance for organizations expecting SDF designation.", "action_required": "Conduct proactive SDF self-assessment; implement DPO, DPIA, and audit programs preemptively."}, "evidence": [{"id": "ev-khaitan", "source_urn": "urn:ki:in:dpdp:source:khaitan-alert", "source_name": "Khaitan & Co Client Alert", "source_tier": "tertiary", "citation_text": "Organizations should not wait for formal SDF designation but proactively assess their exposure...", "coordinates": {"section": "Client Alert"}, "verification_status": "verified"}], "linked_objects": ["urn:ki:in:dpdp:act:2023:sec:10"], "relations": [{"target_urn": "urn:ki:in:dpdp:act:2023:sec:10", "edge_type": "Interprets"}]},
    {"urn": "urn:ki:in:dpdp:opinion:sflc:rti-impact-analysis", "title": "SFLC: Impact of DPDPA Section 44(3) on Right to Information", "type": "Opinion", "version": 1, "summary": "Software Freedom Law Centre analysis arguing that Section 44(3) of DPDPA effectively 'guts' the RTI Act by removing the public interest test for disclosure of personal information. Creates a blanket ban on accessing personal data of public officials, undermining transparency and accountability. Petitioner in the Supreme Court challenge.", "confidence_score": 0.50, "source_credibility": "Tier 2", "forum_published": "SFLC.in Legal Analysis", "interpretation_stance": "Critical", "legal_time_start": "2025-12-15T00:00:00Z", "entities": ["Opinion", "Act", "Organization"], "business_impact": {"impact_summary": "If SFLC's position prevails in SC, Section 44(3) may be struck down, restoring RTI's public interest override.", "action_required": "Monitor the SC Constitution Bench proceedings for potential impact on RTI-DPDPA interactions."}, "evidence": [{"id": "ev-sflc", "source_urn": "urn:ki:in:dpdp:source:sflc-analysis", "source_name": "SFLC.in Legal Analysis", "source_tier": "tertiary", "citation_text": "Section 44(3) creates an unguided, broad discretion for the state to deny information...", "coordinates": {"section": "Analysis"}, "verification_status": "verified"}], "linked_objects": ["urn:ki:in:dpdp:act:2023:sec:44", "urn:ki:in:dpdp:case:sc-rti-conflict-2026"], "relations": [{"target_urn": "urn:ki:in:dpdp:act:2023:sec:44", "edge_type": "Interprets"}, {"target_urn": "urn:ki:in:dpdp:case:sc-rti-conflict-2026", "edge_type": "Supports"}]},
]

# ═══════════════════════════════════════════════════════════════════════════════
# LAYER 5: INDUSTRY GUIDANCE (Confidence = 0.3)
# ═══════════════════════════════════════════════════════════════════════════════

INDUSTRY = [
    {"urn": "urn:ki:in:dpdp:industry:nasscom:feedback-2024", "title": "NASSCOM: Industry Feedback on Draft DPDP Rules (2024)", "type": "Opinion", "version": 1, "summary": "NASSCOM consolidated industry inputs during 2024 public consultation on draft DPDP Rules. Key concerns: cross-border transfer restrictions, parental consent age (18 vs 16), proportional compliance burden for startups/SMEs, and consent manager interoperability standards.", "confidence_score": 0.30, "source_credibility": "Tier 2", "forum_published": "NASSCOM Submissions to MeitY", "interpretation_stance": "Supportive", "legal_time_start": "2024-06-01T00:00:00Z", "entities": ["Organization", "Industry", "Rule"], "business_impact": {"impact_summary": "NASSCOM's advocacy shaped the final form of several Rules provisions.", "action_required": "Reference NASSCOM's analysis for practical compliance guidance tailored to Indian tech industry."}, "evidence": [{"id": "ev-nasscom-fb", "source_urn": "urn:ki:in:dpdp:source:nasscom-submission", "source_name": "NASSCOM Industry Submission", "source_tier": "tertiary", "citation_text": "NASSCOM actively consolidated industry inputs on provisions such as cross-border data transfer restrictions...", "coordinates": {"section": "Submission"}, "verification_status": "verified"}], "linked_objects": ["urn:ki:in:dpdp:rule:dpdp-rules-2025"], "relations": [{"target_urn": "urn:ki:in:dpdp:rule:dpdp-rules-2025", "edge_type": "Supports"}]},
    {"urn": "urn:ki:in:dpdp:industry:nasscom:digital-trust-2026", "title": "NASSCOM: Mandated Digital Trust Framework (2026)", "type": "Opinion", "version": 1, "summary": "NASSCOM positions the DPDPA as a vehicle for building 'mandated digital trust' — beyond mere regulation, it creates market opportunities for Indian startups and Global Capability Centers (GCCs) to demonstrate trustworthiness as a competitive differentiator.", "confidence_score": 0.30, "source_credibility": "Tier 2", "forum_published": "NASSCOM Framework", "interpretation_stance": "Supportive", "legal_time_start": "2026-01-01T00:00:00Z", "entities": ["Organization", "Industry"], "business_impact": {"impact_summary": "Compliance as competitive advantage — trust as market differentiator.", "action_required": "Position DPDPA compliance as a trust-building exercise, not just a regulatory burden."}, "evidence": [{"id": "ev-nasscom-dt", "source_urn": "urn:ki:in:dpdp:source:nasscom-framework", "source_name": "NASSCOM Digital Trust Framework", "source_tier": "tertiary", "citation_text": "NASSCOM promotes the DPDPA as a vehicle to build mandated digital trust...", "coordinates": {"section": "Framework"}, "verification_status": "verified"}], "linked_objects": ["urn:ki:in:dpdp:act:dpdpa-2023"], "relations": [{"target_urn": "urn:ki:in:dpdp:act:dpdpa-2023", "edge_type": "Supports"}]},
    {"urn": "urn:ki:in:dpdp:industry:dsci:privacy-framework", "title": "DSCI: Privacy Framework for Indian Enterprises", "type": "Opinion", "version": 1, "summary": "Data Security Council of India (DSCI) best-practices framework for implementing DPDPA at organizational level. Covers data inventory, consent management, vendor governance, incident response, and privacy-by-design integration into SDLC.", "confidence_score": 0.30, "source_credibility": "Tier 2", "forum_published": "DSCI Publication", "interpretation_stance": "Supportive", "legal_time_start": "2025-06-01T00:00:00Z", "entities": ["Organization", "Control", "Business Process"], "business_impact": {"impact_summary": "Practical implementation framework from India's leading data security council.", "action_required": "Adopt DSCI's framework as operational blueprint for DPDPA compliance implementation."}, "evidence": [{"id": "ev-dsci", "source_urn": "urn:ki:in:dpdp:source:dsci-framework", "source_name": "DSCI Privacy Framework", "source_tier": "tertiary", "citation_text": "Organizations should implement comprehensive privacy frameworks aligned with DPDPA requirements...", "coordinates": {"section": "Framework"}, "verification_status": "verified"}], "linked_objects": ["urn:ki:in:dpdp:act:dpdpa-2023"], "relations": [{"target_urn": "urn:ki:in:dpdp:act:dpdpa-2023", "edge_type": "Supports"}]},
]

# ═══════════════════════════════════════════════════════════════════════════════
# REGULATORY EVENTS
# ═══════════════════════════════════════════════════════════════════════════════

EVENTS = [
    {"id": "evt-001", "title": "Presidential Assent to DPDPA", "type": "Legislative", "authority": "Parliament of India", "jurisdiction": "India", "date_published": "2023-08-11", "date_effective": "2023-08-11", "impact_level": "critical", "status": "active", "review_status": "approved", "summary": "The Digital Personal Data Protection Act 2023 received Presidential Assent and became law.", "change_description": "India's first comprehensive digital personal data protection law was enacted after years of deliberation.", "affected_ko_urns": ["urn:ki:in:dpdp:act:dpdpa-2023"], "evidence_count": {"primary": 1, "secondary": 5, "tertiary": 20}, "affected_industries": ["All"], "affected_processes": ["All data processing activities"]},
    {"id": "evt-002", "title": "Draft DPDP Rules Public Consultation", "type": "Regulatory", "authority": "MeitY", "jurisdiction": "India", "date_published": "2024-01-15", "date_effective": "2024-01-15", "impact_level": "high", "status": "active", "review_status": "approved", "summary": "MeitY conducted extensive public consultations on draft DPDP Rules across major Indian cities.", "change_description": "Public consultations held in Delhi, Mumbai, Bengaluru, Chennai. Thousands of inputs from startups, industry bodies, and civil society.", "affected_ko_urns": ["urn:ki:in:dpdp:rule:dpdp-rules-2025"], "evidence_count": {"primary": 1, "secondary": 10, "tertiary": 50}, "affected_industries": ["Technology", "Financial Services", "Healthcare"], "affected_processes": ["Consent Management", "Data Processing"]},
    {"id": "evt-003", "title": "Gazette Notification of DPDP Rules 2025", "type": "Regulatory", "authority": "MeitY", "jurisdiction": "India", "date_published": "2025-11-13", "date_effective": "2025-11-13", "impact_level": "critical", "status": "active", "review_status": "approved", "summary": "The Digital Personal Data Protection Rules 2025 were officially notified in the Gazette of India, operationalizing the DPDPA.", "change_description": "Phase 1 triggered: DPBI established, foundational provisions in force. 18-month countdown to full compliance begins.", "affected_ko_urns": ["urn:ki:in:dpdp:rule:dpdp-rules-2025", "urn:ki:in:dpdp:act:dpdpa-2023"], "evidence_count": {"primary": 1, "secondary": 20, "tertiary": 100}, "affected_industries": ["All"], "affected_processes": ["All data processing activities"]},
    {"id": "evt-004", "title": "Supreme Court Issues Notice on DPDPA Challenge", "type": "Judicial", "authority": "Supreme Court of India", "jurisdiction": "India", "date_published": "2026-02-01", "date_effective": "2026-02-01", "impact_level": "high", "status": "active", "review_status": "approved", "summary": "The Supreme Court issued notices to the Union of India on writ petitions challenging DPDPA constitutionality.", "change_description": "Multiple petitions filed by journalists, activists, and organizations challenging DPBI independence, Sec 17 exemptions, and Sec 44 RTI amendment.", "affected_ko_urns": ["urn:ki:in:dpdp:act:dpdpa-2023", "urn:ki:in:dpdp:act:2023:sec:17", "urn:ki:in:dpdp:act:2023:sec:44"], "evidence_count": {"primary": 0, "secondary": 5, "tertiary": 30}, "affected_industries": ["All"], "affected_processes": ["Governance", "Regulatory Compliance"]},
    {"id": "evt-005", "title": "MeitY Initiates DPBI Chairperson Recruitment", "type": "Regulatory", "authority": "MeitY", "jurisdiction": "India", "date_published": "2026-05-01", "date_effective": "2026-05-01", "impact_level": "high", "status": "active", "review_status": "approved", "summary": "MeitY invited public applications for the appointment of DPBI Chairperson and 4 Members.", "change_description": "Public recruitment process initiated via Search-cum-Selection Committee. Board transitioning to operational phase.", "affected_ko_urns": ["urn:ki:in:dpdp:act:2023:sec:18", "urn:ki:in:dpdp:notification:dpbi-recruitment-2026"], "evidence_count": {"primary": 1, "secondary": 3, "tertiary": 15}, "affected_industries": ["All"], "affected_processes": ["Regulatory Compliance", "Enforcement"]},
    {"id": "evt-006", "title": "SC Refers RTI vs DPDPA to Constitution Bench", "type": "Judicial", "authority": "Supreme Court of India", "jurisdiction": "India", "date_published": "2026-07-01", "date_effective": "2026-07-01", "impact_level": "critical", "status": "active", "review_status": "approved", "summary": "The Supreme Court referred the RTI Act vs DPDPA Section 44(3) conflict to a Constitution Bench for adjudication.", "change_description": "Constitution Bench will decide if Sec 44(3) unconstitutionally removes the public interest test from RTI disclosures.", "affected_ko_urns": ["urn:ki:in:dpdp:act:2023:sec:44", "urn:ki:in:dpdp:case:sc-rti-conflict-2026"], "evidence_count": {"primary": 0, "secondary": 3, "tertiary": 20}, "affected_industries": ["All"], "affected_processes": ["Governance", "Transparency"]},
]

# ═══════════════════════════════════════════════════════════════════════════════
# ACTION ITEMS
# ═══════════════════════════════════════════════════════════════════════════════

ACTION_ITEMS = [
    {"id": "act-001", "title": "Map Corporate Digital Personal Data Flows", "source_obligation": "Section 8 — General Obligations of Data Fiduciary", "triggering_event_id": "evt-003", "ko_urn": "urn:ki:in:dpdp:act:2023:sec:8", "priority": "critical", "status": "in_progress", "owner": "Data Protection Officer", "reviewer": "Chief Privacy Officer", "due_date": "2026-09-30", "applicability": "applies", "affected_roles": ["DPO", "CTO", "Legal Counsel"], "affected_process": "Enterprise Data Management", "description": "Conduct a comprehensive discovery and mapping exercise to identify all digital personal data storage and processing locations within the enterprise. Map each data flow to its legal basis (consent or legitimate use)."},
    {"id": "act-002", "title": "Implement Granular Consent Collection System", "source_obligation": "Section 6 — Consent", "triggering_event_id": "evt-003", "ko_urn": "urn:ki:in:dpdp:act:2023:sec:6", "priority": "critical", "status": "proposed", "owner": "Product Manager", "reviewer": "DPO", "due_date": "2027-02-28", "applicability": "applies", "affected_roles": ["Product Manager", "UX Designer", "Backend Engineer"], "affected_process": "User Onboarding", "description": "Replace take-it-or-leave-it consent with granular, purpose-specific consent collection. Implement easy withdrawal mechanism. Ensure consent records are audit-ready."},
    {"id": "act-003", "title": "Deploy 72-Hour Breach Reporting SOC Playbook", "source_obligation": "Rule 7 — Breach Notification", "triggering_event_id": "evt-003", "ko_urn": "urn:ki:in:dpdp:rule:breach-notification-rule7", "priority": "critical", "status": "proposed", "owner": "CISO", "reviewer": "DPO", "due_date": "2026-11-30", "applicability": "applies", "affected_roles": ["CISO", "SOC Team", "Legal Counsel", "DPO"], "affected_process": "Incident Response", "description": "Establish a rapid incident response SOP to evaluate data breaches and trigger DPBI notifications within 72 hours. Pre-draft notification templates for Board and Data Principal communications."},
    {"id": "act-004", "title": "Implement Children's Data Protection Controls", "source_obligation": "Section 9 — Children's Data + Rule 5", "triggering_event_id": "evt-003", "ko_urn": "urn:ki:in:dpdp:act:2023:sec:9", "priority": "high", "status": "proposed", "owner": "Product Manager", "reviewer": "DPO", "due_date": "2027-03-31", "applicability": "applies", "affected_roles": ["Product Manager", "UX Designer", "Legal Counsel"], "affected_process": "User Onboarding", "description": "Implement age verification at onboarding, verifiable parental consent workflow, and disable tracking/targeting/profiling for users identified as under 18."},
    {"id": "act-005", "title": "Conduct SDF Self-Assessment", "source_obligation": "Section 10 — Significant Data Fiduciary", "triggering_event_id": "evt-003", "ko_urn": "urn:ki:in:dpdp:act:2023:sec:10", "priority": "high", "status": "proposed", "owner": "DPO", "reviewer": "Board of Directors", "due_date": "2026-12-31", "applicability": "assess", "affected_roles": ["DPO", "CTO", "Board"], "affected_process": "Governance", "description": "Proactively assess whether the organization meets SDF classification criteria (data volume, sensitivity, technology usage). If likely, initiate DPO appointment, DPIA framework, and annual audit program."},
]


# ═══════════════════════════════════════════════════════════════════════════════
# SEEDING LOGIC
# ═══════════════════════════════════════════════════════════════════════════════

def upsert_ko(supabase: Client, ko: dict):
    """Upsert a single Knowledge Object and its graph edges."""
    row = {
        "urn": ko["urn"],
        "version": ko["version"],
        "type": ko["type"],
        "title": ko["title"],
        "summary": ko["summary"],
        "confidence_score": ko["confidence_score"],
        "source_credibility": ko.get("source_credibility"),
        "forum_published": ko.get("forum_published"),
        "interpretation_stance": ko.get("interpretation_stance"),
        "legal_time_start": ko["legal_time_start"],
        "body": ko.get("body", {}),
        "business_impact": ko.get("business_impact", {}),
        "evidence": ko.get("evidence", []),
        "linked_objects": ko.get("linked_objects", []),
        "entities": ko.get("entities", []),
        "relations": ko.get("relations", []),
    }
    supabase.table("knowledge_objects").upsert(row).execute()
    
    # Insert graph edges
    for rel in ko.get("relations", []):
        supabase.table("graph_edges").upsert({
            "source_urn": ko["urn"],
            "source_version": ko["version"],
            "target_urn": rel["target_urn"],
            "edge_type": rel["edge_type"]
        }).execute()


def seed():
    url = os.environ.get("SUPABASE_URL", "")
    key = os.environ.get("SUPABASE_SERVICE_KEY", "")
    if not url or not key:
        print("[!] ERROR: SUPABASE_URL and SUPABASE_SERVICE_KEY must be set.")
        sys.exit(1)
    
    print(f"[*] Connecting to Supabase at {url}...")
    supabase: Client = create_client(url, key)
    
    # Collect all KOs
    all_kos = (
        [ACT_PARENT] + ACT_SECTIONS +
        [RULES_PARENT] + RULE_SECTIONS +
        PENALTIES + JUDICIAL + REGULATORY + OPINIONS + INDUSTRY
    )
    
    print(f"\n[*] Seeding {len(all_kos)} Knowledge Objects...")
    for i, ko in enumerate(all_kos, 1):
        label = ko["type"]
        print(f"  [{i:02d}/{len(all_kos)}] {label}: {ko['title'][:70]}...")
        upsert_ko(supabase, ko)
    
    print(f"\n[*] Seeding {len(EVENTS)} Regulatory Events...")
    for evt in EVENTS:
        print(f"  • {evt['title'][:70]}...")
        supabase.table("regulatory_events").upsert(evt).execute()
    
    print(f"\n[*] Seeding {len(ACTION_ITEMS)} Action Items...")
    for act in ACTION_ITEMS:
        print(f"  • {act['title'][:70]}...")
        supabase.table("action_items").upsert(act).execute()
    
    print(f"\n[+] ══════════════════════════════════════════════════")
    print(f"[+] COMPLETE: {len(all_kos)} KOs, {len(EVENTS)} Events, {len(ACTION_ITEMS)} Actions seeded!")
    print(f"[+] ══════════════════════════════════════════════════")


if __name__ == "__main__":
    seed()
