---
slug: special-cases
order: 4
title: Special cases
summary: "Significant Data Fiduciaries, Consent Managers, sending personal data abroad, the exemptions, and how the State processes personal data: the parts of the Act most businesses meet only once."
minutes: 9
provisions: [S10, S16, S17, R4, R5, R13, R15, R16, SCH-FIRST, SCH-SECOND]
next: enforcement
quiz:
  - q: "Who decides that a Data Fiduciary is a Significant Data Fiduciary?"
    a: "The Central Government, by notification, after weighing the factors in Section 10(1)"
    b: "The Data Protection Board, on a complaint from a Data Principal"
    c: "The Data Fiduciary itself, by a self-assessment of its data volumes"
    d: "The sectoral regulator for that industry, such as a banking or insurance regulator"
    answer: a
    cites: S10
  - q: "Under Rule 13(1), how often must a Significant Data Fiduciary carry out a Data Protection Impact Assessment and an audit?"
    a: "Once, within six months of being notified"
    b: "Once in every period of twelve months from the date of notification"
    c: "Every quarter, with a report to the Board each time"
    d: "Only when the Board directs one after a complaint"
    answer: b
    cites: R13
  - q: "Which of these is a condition for registration as a Consent Manager in Part A of the First Schedule?"
    a: "The applicant has at least one hundred employees based in India"
    b: "The applicant holds a licence from the Reserve Bank of India"
    c: "The applicant is a company incorporated in India with a net worth of not less than two crore rupees"
    d: "The applicant is a registered society or trust, not a company"
    answer: c
    cites: SCH-FIRST, R4
  - q: "How does Section 16 deal with transfers of personal data outside India?"
    a: "All transfers are prohibited unless the destination is on a Government whitelist"
    b: "Transfers are allowed only to countries with a data protection law of their own"
    c: "Every transfer needs the prior approval of the Data Protection Board"
    d: "The Central Government may, by notification, restrict transfer to particular countries or territories"
    answer: d
    cites: S16
  - q: "Where the Section 17(1) exemption applies, which duties still bind the Data Fiduciary?"
    a: "Its overall responsibility for processing done by it or on its behalf, and the duty to take reasonable security safeguards"
    b: "Only the duty to give notice and take consent"
    c: "None; the Act switches off completely"
    d: "Only the additional duties in relation to children"
    answer: a
    cites: S17
  - q: "Under Rule 16, processing for research, archiving or statistical purposes is outside the Act if it is carried on..."
    a: "With the prior approval of the Data Protection Board"
    b: "In accordance with the standards specified in the Second Schedule"
    c: "By a university or a Government research body only"
    d: "On personal data that is anonymised within thirty days"
    answer: b
    cites: R16, SCH-SECOND
  - q: "Rule 5 and the Second Schedule set standards for the State processing personal data in order to..."
    a: "Investigate and prosecute offences"
    b: "Conduct elections and maintain electoral rolls"
    c: "Provide or issue a subsidy, benefit, service, certificate, licence or permit"
    d: "Assess and collect taxes"
    answer: c
    cites: R5, SCH-SECOND
---

Modules 2 and 3 covered the duties every Data Fiduciary carries and the rights every Data Principal holds. This module covers the situations that only some businesses meet: being named a Significant Data Fiduciary, running a Consent Manager, sending personal data abroad, relying on an exemption, and processing done by the State.

## Significant Data Fiduciaries: notified, never self-declared
::: short
A business becomes a Significant Data Fiduciary only when the Central Government notifies it, or a class it belongs to, under Section 10(1); it cannot designate itself. Once notified, it must appoint a Data Protection Officer and an independent data auditor, and carry out a Data Protection Impact Assessment and an audit every twelve months under Rule 13.
:::

::: figure
{
 "type": "gate",
 "title": "Significant Data Fiduciary: one test, and the Government applies it",
 "caption": "You cannot declare yourself a Significant Data Fiduciary, and no volume of data makes you one automatically: the Government weighs the factors in Section 10(1) and notifies. Rule 13 applies from 13 May 2027.",
 "steps": [
  {
   "q": "Has the Central Government notified you, or a class of Data Fiduciaries you belong to, as a Significant Data Fiduciary?",
   "cite": "Section 10(1)",
   "failLabel": "If no",
   "fail": "The additional duties in Section 10(2) and Rule 13 do not apply to you.",
   "pass": "If yes, from the date of notification:"
  }
 ],
 "result": {
  "label": "Section 10(2) applies: appoint a Data Protection Officer based in India and responsible to your board of directors or similar governing body, appoint an independent data auditor, and carry out a periodic Data Protection Impact Assessment and a periodic audit. Rule 13 sets the cycle at once in every twelve months from notification, with a report of significant observations to the Board.",
  "cite": "Section 10(2)",
  "role": "fiduciary"
 }
}
:::

Most Data Fiduciaries carry the general duties covered in module 2. A smaller group carries more. Section 10(1) lets the Central Government notify "any Data Fiduciary or class of Data Fiduciaries" as a Significant Data Fiduciary, after weighing the factors it lists: the volume and sensitivity of the personal data processed, the risk to the rights of Data Principals, the potential impact on the sovereignty and integrity of India, the risk to electoral democracy, the security of the State, and public order.

Two things follow from that wording. A business cannot make itself a Significant Data Fiduciary, and it cannot become one by accident; the status arrives by notification. Until a notification names you or a class you belong to, the extra duties in this lesson do not apply, however large your customer base.

Once notified, Section 10(2) adds three duties. First, appoint a Data Protection Officer who is based in India, is responsible to the board of directors or a similar governing body, represents the Significant Data Fiduciary under the Act, and is the point of contact for grievance redressal. Second, appoint an independent data auditor to evaluate compliance with the Act. Third, carry out a periodic Data Protection Impact Assessment and a periodic audit, together with any other measures that may be prescribed.

Rule 13 fills in the rhythm. Rule 13(1) requires the Data Protection Impact Assessment and the audit once in every period of twelve months from the date of notification. Rule 13(2) requires the person who carries them out to send the Board a report of the significant observations. Rule 13(3) asks the Significant Data Fiduciary to verify, with due diligence, that its technical measures, including algorithmic software, are not likely to pose a risk to the rights of Data Principals. Rule 13(4) lets the Central Government, on the recommendation of a committee, specify personal data that must not be transferred outside India along with its traffic data. Rule 13 applies from 13 May 2027.

The Act sets a separate penalty row for breaches of Section 10; module 5 covers it.

::: example a health-records app in Hyderabad
A health-records app in Hyderabad holds the health records of many patients, but no notification has named it or a class it belongs to. Until one does, the Section 10(2) duties do not apply to it, however large its user base grows. If the Central Government notifies it, it must appoint a Data Protection Officer based in India and an independent data auditor. From 13 May 2027, it must also carry out a Data Protection Impact Assessment and an audit once in every twelve months from the date of notification, and the person who carries them out sends the Board a report of the significant observations.
:::


## Consent Managers: registered with the Board
::: short
Only a company that meets every condition in Part A of the First Schedule may apply to the Board to register as a Consent Manager, and once registered it carries the obligations in Part B. Rule 4 and the First Schedule apply from 13 November 2026.
:::

::: figure
{
 "type": "checklist",
 "title": "Conditions for registration as a Consent Manager, from Part A of the First Schedule",
 "caption": "All nine must hold before a person may apply under Rule 4(1). The Board may inquire, then registers the applicant or rejects the application with reasons (Rule 4(2)). Applies from 13 November 2026.",
 "role": "manager",
 "items": [
  {
   "label": "The applicant is a company incorporated in India.",
   "cite": "First Schedule, Part A, item 1"
  },
  {
   "label": "It has sufficient technical, operational and financial capacity to fulfil its obligations as a Consent Manager.",
   "cite": "First Schedule, Part A, item 2"
  },
  {
   "label": "Its financial condition and the general character of its management are sound.",
   "cite": "First Schedule, Part A, item 3"
  },
  {
   "label": "Its net worth is at or above the minimum that Part A sets.",
   "cite": "First Schedule, Part A, item 4"
  },
  {
   "label": "Its likely volume of business, capital structure and earning prospects are adequate.",
   "cite": "First Schedule, Part A, item 5"
  },
  {
   "label": "Its directors, key managerial personnel and senior management have a general reputation and record of fairness and integrity.",
   "cite": "First Schedule, Part A, item 6"
  },
  {
   "label": "Its memorandum and articles require adherence to the conflict-of-interest obligations in Part B.",
   "detail": "Those provisions may be amended only with the previous approval of the Board.",
   "cite": "First Schedule, Part A, item 7"
  },
  {
   "label": "The operations it proposes are in the interests of Data Principals.",
   "cite": "First Schedule, Part A, item 8"
  },
  {
   "label": "It is independently certified.",
   "detail": "Its interoperable platform must be consistent with the data protection standards and assurance framework the Board publishes, with technical and organisational measures in place to adhere to them.",
   "cite": "First Schedule, Part A, item 9"
  }
 ]
}
:::

A Consent Manager runs an interoperable platform through which a Data Principal can give, manage, review and withdraw consent to Data Fiduciaries in one place. The consent provisions themselves are in module 2; this lesson covers who may run such a platform and what they owe.

Rule 4(1) says a person who meets the conditions in Part A of the First Schedule may apply to the Board for registration. The Board may inquire into the application and, if satisfied, registers the applicant and publishes its particulars on the Board's website; if not satisfied, it rejects the application and gives reasons (Rule 4(2)). Rule 4 and the First Schedule apply from 13 November 2026.

Part A of the First Schedule sets the entry conditions. The applicant must be a company incorporated in India with a net worth of not less than two crore rupees, sound finances and management, directors and senior management with a record of fairness and integrity, and operations that are in the interests of Data Principals. Its platform must be independently certified as consistent with the data protection standards the Board publishes.

Part B of the First Schedule sets the running obligations. The Consent Manager must share personal data in a way that its contents are not readable by the Consent Manager itself. It must keep a record of consents given, denied or withdrawn, of the notices behind them, and of every sharing of personal data; give the Data Principal access to that record in machine-readable form; and keep it for at least seven years. It must act in a fiduciary capacity towards the Data Principal, avoid conflicts of interest with Data Fiduciaries, publish its promoters, directors and every shareholder above two per cent, not sub-contract its obligations, and run audit mechanisms that report to the Board. Control of the company cannot change hands without the Board's prior approval.

Rule 4(4) and Rule 4(5) let the Board direct a Consent Manager to correct non-adherence and, after a hearing, suspend or cancel its registration. An ordinary business does not register; only an entity that wants to run such a platform does.

::: example a consent-platform company in Bengaluru
A company incorporated in Bengaluru wants to run a platform through which people give, review and withdraw consent to lenders in one place. From 13 November 2026, it must first meet every condition in Part A of the First Schedule, including independent certification of its platform, and then apply to the Board under Rule 4(1). Once registered, it must share personal data in a way that keeps the contents unreadable by itself, and keep a record of consents given, denied or withdrawn for at least seven years. If it later stops meeting its conditions, the Board may, after a hearing, direct it to comply, or suspend or cancel its registration.
:::


## Sending personal data outside India
::: short
Personal data may be transferred abroad unless the Central Government, by notification under Section 16(1), restricts transfer to a named country or territory. Rule 15 adds any requirements the Government specifies by order about making the data available to a foreign State, and Section 16(2) keeps any stricter Indian law in force.
:::

::: figure
{
 "type": "gate",
 "title": "Can this personal data go abroad? Four checks",
 "caption": "The default is that transfer is allowed; each check can only add a restriction. Rule 13 and Rule 15 apply from 13 May 2027.",
 "steps": [
  {
   "q": "Has the Central Government, by notification, restricted transfer to that country or territory?",
   "cite": "Section 16(1)",
   "failLabel": "If yes",
   "fail": "Transfer to that destination is restricted.",
   "pass": "If no, go to the next check."
  },
  {
   "q": "Does another Indian law give a higher degree of protection for, or restriction on, transferring this personal data or this kind of Data Fiduciary?",
   "cite": "Section 16(2)",
   "failLabel": "If yes",
   "fail": "That law still applies; Section 16 does not restrict it.",
   "pass": "If no, go to the next check."
  },
  {
   "q": "Are you a Significant Data Fiduciary, and is this personal data specified by the Central Government on a committee's recommendation?",
   "cite": "Rule 13(4)",
   "failLabel": "If yes",
   "fail": "That personal data, and the traffic data about its flow, must not be transferred outside India.",
   "pass": "If no, go to the next check."
  },
  {
   "q": "Has the Central Government, by general or special order, specified requirements about making this personal data available to a foreign State or an entity it controls?",
   "cite": "Rule 15",
   "failLabel": "If yes",
   "fail": "Meet those requirements as a condition of the transfer.",
   "pass": "If no, Rule 15 adds no further step."
  }
 ],
 "result": {
  "label": "The personal data may be transferred outside India.",
  "cite": "Rule 15",
  "role": "fiduciary"
 }
}
:::

The Act does not require personal data to stay in India. Section 16(1) lets the Central Government, by notification, restrict transfer "to such country or territory outside India as may be so notified". The default is that transfer is allowed; a restriction exists only where a notification names a destination. Section 16(2) preserves any other Indian law that sets a higher degree of protection or a tighter restriction for particular personal data or particular Data Fiduciaries, so a sectoral regulator's localisation requirement continues to bind the businesses it covers.

Rule 15 adds one condition. Personal data may be transferred outside India subject to the Data Fiduciary meeting "such requirements as the Central Government may, by general or special order, specify" about making that personal data available to a foreign State, or to a person, entity or agency under the control of a foreign State. Until such an order is made, the Rule itself imposes no further step. Rule 15 applies from 13 May 2027.

One group faces a firmer restriction. Under Rule 13(4), a Significant Data Fiduciary must ensure that personal data specified by the Central Government, on the recommendation of a committee, is not transferred outside India, and nor is the traffic data pertaining to its flow. That obligation attaches only to Significant Data Fiduciaries and only to the categories the Government specifies.

So for a small business using a foreign cloud provider or payment gateway, the questions are three: has the destination been notified under Section 16(1), does an order under Rule 15 apply, and does your own sector's regulator add a requirement of its own. The general duties from module 2 do not switch off because the server is abroad; they travel with the personal data.

::: example an online furniture store in Jaipur
An online furniture store in Jaipur hosts its customer database with a cloud provider in Singapore. Section 16(1) allows this unless the Central Government has notified a restriction on transfer to that country. From 13 May 2027, Rule 15 also requires the store to meet any requirements the Government specifies by order about making that data available to a foreign State. The store is not a Significant Data Fiduciary, so the Rule 13(4) restriction on specified personal data does not reach it.
:::


## The exemptions: what falls outside, and how far
::: short
Section 17 works in layers: in six listed situations most duties and rights switch off, though responsibility for processing and reasonable security safeguards remain, while some processing is outside the Act entirely. Research, archiving and statistics are outside only if they follow the Second Schedule standards, under Rule 16 from 13 May 2027.
:::

::: figure
{
 "type": "compare",
 "title": "Two layers of exemption in Section 17",
 "caption": "Two further powers need a notification before they help anyone: Section 17(3) for notified classes of Data Fiduciaries, including startups, and Section 17(5) for any Data Fiduciary for a stated period, within five years of commencement. Rule 16 applies from 13 May 2027.",
 "columns": [
  {
   "heading": "Most duties and rights switch off",
   "role": "fiduciary",
   "cite": "Section 17(1)",
   "points": [
    {
     "text": "Enforcing a legal right or claim",
     "cite": "Section 17(1)(a)"
    },
    {
     "text": "Courts, tribunals and regulatory or supervisory bodies performing their functions",
     "cite": "Section 17(1)(b)"
    },
    {
     "text": "Preventing, detecting, investigating or prosecuting offences",
     "cite": "Section 17(1)(c)"
    },
    {
     "text": "Personal data of people outside India, processed under a contract with a person outside India by a person based in India",
     "cite": "Section 17(1)(d)"
    },
    {
     "text": "Approved mergers, demergers and similar schemes",
     "cite": "Section 17(1)(e)"
    },
    {
     "text": "Ascertaining the financial information of a loan defaulter",
     "cite": "Section 17(1)(f)"
    },
    {
     "text": "Still binding: responsibility for processing done by you or on your behalf, and reasonable security safeguards",
     "cite": "Section 17(1)"
    }
   ]
  },
  {
   "heading": "The Act does not apply at all",
   "role": "neutral",
   "cite": "Section 17(2)",
   "points": [
    {
     "text": "Processing by a State instrumentality the Central Government notifies, in the interests of sovereignty, security of the State, public order and similar grounds",
     "cite": "Section 17(2)(a)"
    },
    {
     "text": "Research, archiving or statistical processing, where the personal data is not used to take a decision specific to a Data Principal",
     "cite": "Section 17(2)(b)"
    },
    {
     "text": "…and only if carried on following the standards in the Second Schedule",
     "cite": "Rule 16"
    }
   ]
  }
 ]
}
:::

Section 17 is where readers hope to find an escape hatch. It is narrower than it looks, and it works in layers.

Section 17(1) switches off most of the Data Fiduciary duties, the Data Principal rights and Section 16 in six situations: enforcing a legal right or claim; processing by courts, tribunals and regulatory or supervisory bodies performing their functions; prevention, detection, investigation or prosecution of offences; processing of personal data of Data Principals outside India under a contract with a person outside India by a person based in India; approved mergers, demergers and similar schemes; and ascertaining the financial position of a loan defaulter. Two duties survive even here: the Data Fiduciary stays responsible for processing done by it or on its behalf, and it must still take reasonable security safeguards.

The fourth situation matters to India's outsourcing sector. An Indian business processing foreign individuals' personal data under a contract with a foreign client is outside most of the Act for that work.

Section 17(2) takes some processing outside the Act entirely: processing by State instrumentalities the Central Government notifies on grounds such as sovereignty, security and public order; and processing "necessary for research, archiving or statistical purposes" that is not used to take a decision specific to a Data Principal and follows prescribed standards. Rule 16 names those standards: the Second Schedule. Rule 16 and the Second Schedule apply from 13 May 2027.

Section 17(3) lets the Central Government notify classes of Data Fiduciaries, "including startups", to whom the notice duty, the accuracy and erasure duties, the Significant Data Fiduciary duties in Section 10 and the right of access do not apply, having regard to the volume and nature of personal data they process. It defines a startup by reference to recognition under the Government's startup criteria. No such notification is a given; until one names your class, the full Act applies. Section 17(5) lets the Government exempt any Data Fiduciary or class from any provision for a stated period, within five years of the Act's commencement.

::: example an IT services firm in Pune
An IT services firm in Pune runs payroll for a client in Germany, processing the personal data of that client's employees in Germany under its contract with the client. Section 17(1)(d) takes that work outside most of the Act's duties and rights. Two duties stay: the firm remains responsible for processing done by it or on its behalf, and it must take reasonable security safeguards. The personal data of the firm's own staff in India is not covered by Section 17(1)(d), because those Data Principals are within India.
:::


## When the State processes your personal data
::: short
When the State or its instrumentalities process personal data to provide a subsidy, benefit, service, certificate, licence or permit, Rule 5 requires them to follow the Second Schedule standards. Those cover lawful and limited processing, accuracy, retention, security, an intimation to the person, and accountability, and apply from 13 May 2027.
:::

::: figure
{
 "type": "checklist",
 "title": "The standards in the Second Schedule",
 "caption": "Rule 5(2) says when a subsidy, benefit, service, certificate, licence or permit counts: provided under law, under policy, or using public funds. The same standards govern research, archiving and statistics under Rule 16. Both rules apply from 13 May 2027.",
 "role": "state",
 "items": [
  {
   "label": "Processing is carried out lawfully.",
   "cite": "Second Schedule, clause (a)"
  },
  {
   "label": "It is done only for the State's use in providing the benefit or service, or for the research, archiving or statistical purpose.",
   "cite": "Second Schedule, clause (b)"
  },
  {
   "label": "It is limited to the personal data necessary for that use or purpose.",
   "cite": "Second Schedule, clause (c)"
  },
  {
   "label": "Reasonable efforts are made to keep the personal data complete, accurate and consistent.",
   "cite": "Second Schedule, clause (d)"
  },
  {
   "label": "Personal data is retained only while required for the use or purpose, or for compliance with law.",
   "cite": "Second Schedule, clause (e)"
  },
  {
   "label": "Reasonable security safeguards prevent personal data breach, including in processing by a Data Processor.",
   "cite": "Second Schedule, clause (f)"
  },
  {
   "label": "The Data Principal receives an intimation of the processing.",
   "detail": "With the business contact of a person who can answer her questions, and the link to the website or app through which she can exercise her rights.",
   "cite": "Second Schedule, clause (g)"
  },
  {
   "label": "Whoever determines the purpose and means of processing is accountable for observing these standards.",
   "cite": "Second Schedule, clause (h)"
  }
 ]
}
:::

Government departments and their instrumentalities are Data Fiduciaries too. The Act gives them a legitimate use for providing or issuing a subsidy, benefit, service, certificate, licence or permit (module 2 covers legitimate uses), and the Rules set the standards they must meet when they do.

Rule 5(1) says such processing "shall be done following the standards specified in Second Schedule". Rule 5(2) explains what counts: a subsidy, benefit, service, certificate, licence or permit provided under law (in exercise of a statutory power or function), under policy (an instruction of the Central or a State Government in its executive power), or using public funds (paid from the Consolidated Fund of India or of a State, the public account, or the funds of a local authority). Rule 5 and the Second Schedule apply from 13 May 2027.

The Second Schedule reads like a checklist of good practice. Processing must be lawful, limited to the personal data necessary for the use, and carried out with reasonable efforts at completeness, accuracy and consistency. Personal data is retained only while required for the use or by law. Reasonable security safeguards must protect it, including in processing done by a Data Processor. The Data Principal must be given an intimation of the processing, with the business contact information of a person who can answer her questions and the link to the website or app through which she can exercise her rights. The person who determines the purpose and means of processing is accountable for observing these standards. The same Second Schedule governs the research, archiving and statistical processing exempted by Section 17(2) and Rule 16.

Two further State-specific provisions sit in Section 17. Section 17(2) takes notified security and intelligence instrumentalities outside the Act altogether. Section 17(4) relieves the State and its instrumentalities of the duty to erase personal data once the purpose is served and of the Data Principal's right to erasure; where the processing does not involve a decision affecting the Data Principal, the right to correction does not apply either.

For a private business the practical point is narrow: if you process personal data on behalf of a Government body under one of these schemes, expect the Second Schedule standards to flow into your contract.

::: example a software firm in Lucknow
A software firm in Lucknow runs a scholarship portal for a State education department, and the scholarships are paid from the Consolidated Fund of the State. That makes them a benefit provided using public funds under Rule 5(2)(c), so from 13 May 2027 the department's processing must follow the Second Schedule standards. Those standards include reasonable security safeguards over processing done on the department's behalf by a Data Processor, which is the firm's role here. Each student must also receive an intimation naming a contact person and the link through which she can exercise her rights.
:::
