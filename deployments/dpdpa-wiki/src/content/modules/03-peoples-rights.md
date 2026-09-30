---
slug: peoples-rights
order: 3
title: People's rights
summary: "Children's data and verifiable parental consent, guardians of persons with disability, the children's exemptions, and the rights to access, correction, erasure, grievance redressal and nomination, with the Data Principal's own duties."
minutes: 10
provisions: [S9, S11, S12, S13, S14, S15, R9, R10, R11, R12, R14, SCH-FOURTH]
next: special-cases
quiz:
  - q: "Which of these does Section 9(3) forbid a Data Fiduciary to do?"
    a: "Process any personal data of a child for any purpose"
    b: "Undertake tracking or behavioural monitoring of children, or targeted advertising directed at children"
    c: "Send a child's parent a notice by email"
    d: "Store a child's personal data outside the child's home state"
    answer: b
    cites: S9
  - q: "A parent who is not a registered user of a platform wants to consent for her child. Under Rule 10, how may the platform check she is an identifiable adult?"
    a: "By asking her to tick a box confirming she is over eighteen"
    b: "By asking the child to confirm the parent's age"
    c: "By reference to identity and age details issued by an entity entrusted by law or the Government, or a virtual token mapped to them"
    d: "By waiting for the Board to verify her"
    answer: c
    cites: R10
  - q: "A school tracks pupils' attendance and behaviour for its educational activities. What do Rule 12 and Part A of the Fourth Schedule do?"
    a: "Exempt the school from all of Section 9"
    b: "Lift Section 9(1) and 9(3) for that tracking and behavioural monitoring, subject to the stated conditions"
    c: "Require the school to register with the Board before tracking"
    d: "Nothing; schools are not named in the Fourth Schedule"
    answer: b
    cites: R12, SCH-FOURTH
  - q: "What must a Data Fiduciary give a Data Principal who makes an access request under Section 11(1)?"
    a: "A copy of its internal security policies"
    b: "Only a confirmation that it holds some personal data about her"
    c: "A summary of her personal data and the processing activities, and the identities of other Data Fiduciaries and Data Processors it was shared with, with a description of what was shared"
    d: "The source code of the systems that process her data"
    answer: c
    cites: S11
  - q: "A customer asks for her personal data to be erased. Under Section 12(3), when may the Data Fiduciary keep it?"
    a: "Whenever it might be useful for future marketing"
    b: "When retention is necessary for the specified purpose or for compliance with a law in force"
    c: "Never; every erasure request must be carried out in full at once"
    d: "Only if she has not paid an erasure fee"
    answer: b
    cites: S12
  - q: "What does Rule 14(3) require about the time taken to respond to grievances?"
    a: "Each grievance must be answered within twenty-four hours"
    b: "There is no time limit, so long as a reply is eventually sent"
    c: "The Board sets a separate deadline for every grievance"
    d: "The Data Fiduciary must prominently publish its response period, a reasonable period not exceeding ninety days"
    answer: d
    cites: R14, S13
  - q: "Under Section 14, when does a nominee exercise a Data Principal's rights?"
    a: "In the event of the Data Principal's death or incapacity"
    b: "Whenever the Data Principal is travelling abroad"
    c: "Only after the Board approves the nomination"
    d: "Whenever the Data Fiduciary asks the nominee to"
    answer: a
    cites: S14
  - q: "Which of these is a duty of the Data Principal under Section 15?"
    a: "To keep her password confidential"
    b: "To read every privacy notice in full before using a service"
    c: "Not to register a false or frivolous grievance or complaint with a Data Fiduciary or the Board"
    d: "To tell the Data Fiduciary about any breach she suspects"
    answer: c
    cites: S15
---

This module covers what the Act gives the people whose data you hold: special protection for children and persons with disability, and the rights to access, correction, erasure, grievance redressal and nomination, with the duties that come alongside them. Rules 9, 10, 11, 12 and 14, and the Fourth Schedule, apply from 13 May 2027.

## Children's data: verifiable consent and what is forbidden
::: short
Before processing a child's personal data, Section 9(1) requires the verifiable consent of her parent, and Section 9(2) and 9(3) forbid harmful processing, tracking, behavioural monitoring and targeted advertising even with that consent. From 13 May 2027, Rule 10 requires you to check that the person consenting is an identifiable adult.
:::

::: figure
{
 "type": "gate",
 "title": "Processing a child's personal data: four tests",
 "caption": "Rule 10 applies from 13 May 2027. Rule 12 and the Fourth Schedule lift the consent and tracking tests for some classes and purposes, as a later lesson shows; the well-being test is never lifted.",
 "steps": [
  {
   "q": "Are you about to process personal data of a child?",
   "cite": "Section 9(1)",
   "failLabel": "If no",
   "fail": "Section 9's rules for children do not apply.",
   "pass": "If yes, go to the next test."
  },
  {
   "q": "Have you obtained the verifiable consent of her parent or lawful guardian, before processing?",
   "cite": "Section 9(1)",
   "failLabel": "If no",
   "fail": "Do not process. Consent comes first.",
   "pass": "If yes, go to the next test."
  },
  {
   "q": "Have you checked that the person consenting as parent is an identifiable adult?",
   "cite": "Rule 10(1)",
   "failLabel": "If no",
   "fail": "Rule 10(1) names how to check: by reference to reliable details of identity and age you already hold, or details provided voluntarily by the individual or through a virtual token issued by an authorised entity.",
   "pass": "If yes, go to the next test."
  },
  {
   "q": "Would the processing track or behaviourally monitor her, target advertising at her, or be likely to harm her well-being?",
   "cite": "Section 9(2) and 9(3)",
   "failLabel": "If yes",
   "fail": "Forbidden, even with the parent's consent.",
   "pass": "If no, you may proceed."
  }
 ],
 "result": {
  "label": "You may process the child's personal data, within the consent given.",
  "cite": "Section 9",
  "role": "fiduciary"
 }
}
:::

Section 9(1) requires a Data Fiduciary, before processing any personal data of a child, to obtain the "verifiable consent" of the parent, in the manner prescribed. The Explanation to Section 9(1) makes "consent of the parent" include the consent of a lawful guardian where applicable. Module 1 covered who counts as a child under the Act.

Two prohibitions sit beside consent and apply even when the parent agrees. Section 9(2) forbids processing that is "likely to cause any detrimental effect on the well-being of a child". Section 9(3) forbids tracking or behavioural monitoring of children, and targeted advertising directed at children.

Rule 10 prescribes how verifiable consent works. Under Rule 10(1), the Data Fiduciary must adopt appropriate technical and organisational measures to ensure the parent's verifiable consent is obtained before processing, and must observe due diligence to check that the individual identifying herself as the parent is an adult who is identifiable if required under Indian law. It checks this by reference to either reliable identity and age details it already holds (Rule 10(1)(a)), or identity and age details voluntarily provided by the individual or through a virtual token mapped to such details, issued by an authorised entity (Rule 10(1)(b)). An "adult" is an individual who has completed eighteen years (Rule 10(2)(a)). Authorised entities include those entrusted by law or by government with issuing such details, and details verified by a Digital Locker service provider count (Rule 10(2)(b)).

The four illustrations to Rule 10, whoever starts the sign-up, turn on one fact. If the parent is already a registered user who has given her identity and age details, the Data Fiduciary checks that it holds reliable details and that she is an identifiable adult. If she is not, it checks by reference to details issued by an entity entrusted by law or the Government, or a token mapped to them; she may use a Digital Locker service provider to share them.

Rule 10(1) describes the check by reference to reliable identity and age details the Data Fiduciary holds, or details provided voluntarily by the individual or through a virtual token issued by an authorised entity. Rule 10 applies from 13 May 2027.

::: example an online art-class platform in Hyderabad
An online art-class platform in Hyderabad lets children sign up for weekend lessons. Before creating a child's account, it must obtain her parent's verifiable consent (Section 9(1)). From 13 May 2027, it must also check that the parent is an identifiable adult: against identity and age details it already holds if the parent is a registered user, or otherwise against details issued by an entity entrusted by law or the Government, which she may share through a Digital Locker service provider (Rule 10). Even with that consent, it may not track or behaviourally monitor the child, or show her targeted advertising (Section 9(3)).
:::


## Persons with disability who have a lawful guardian
::: short
For a person with disability who has a lawful guardian, Section 9(1) requires the guardian's verifiable consent before processing. From 13 May 2027, Rule 11 requires you to verify that a court, a designated authority or a local level committee appointed that guardian under the applicable guardianship law.
:::

::: figure
{
 "type": "steps",
 "title": "Consent through a lawful guardian: verify the appointment",
 "caption": "Rule 11 applies from 13 May 2027. The check is on who appointed the guardian, not an assessment of the disability.",
 "steps": [
  {
   "label": "Someone says she is the lawful guardian of a person with disability",
   "role": "principal",
   "cite": "Rule 11(1)"
  },
  {
   "label": "Verify who appointed her",
   "detail": "A court of law, a designated authority, or a local level committee, under the law applicable to guardianship.",
   "role": "fiduciary",
   "cite": "Rule 11(1)"
  },
  {
   "label": "Match the appointment to the right law",
   "detail": "Long-term impairment that leaves her unable to take legally binding decisions despite support: the Rights of Persons with Disabilities Act, 2016. Autism, cerebral palsy, mental retardation (the Rule's term) or a combination, including severe multiple disability: the National Trust Act, 1999.",
   "role": "fiduciary",
   "cite": "Rule 11(2)(b)"
  },
  {
   "label": "Obtain the guardian's verifiable consent before processing",
   "role": "fiduciary",
   "cite": "Section 9(1)"
  }
 ]
}
:::

Section 9(1) also covers a person with disability who has a lawful guardian. Before processing her personal data, the Data Fiduciary must obtain the verifiable consent of that lawful guardian, in the manner prescribed.

Rule 11 prescribes the check. When an individual identifies herself as the lawful guardian of a person with disability, the Data Fiduciary must observe due diligence to verify that the guardian was appointed by a court of law, by a designated authority, or by a local level committee, under the law applicable to guardianship (Rule 11(1)).

Rule 11(2) explains who is meant. A "person with disability" means an individual with a long-term physical, mental, intellectual or sensory impairment which, in interaction with barriers, hinders her full and effective participation in society, and who, despite adequate and appropriate support, is unable to take legally binding decisions. It also includes an individual with autism, cerebral palsy, mental retardation (the Rule's term), or a combination of two or more of these, including severe multiple disability, who despite such support is unable to take legally binding decisions (Rule 11(2)(d)).

The law applicable to guardianship depends on which description fits. For the first group it is the Rights of Persons with Disabilities Act, 2016 and its rules; for the second it is the National Trust for the Welfare of Persons with Autism, Cerebral Palsy, Mental Retardation and Multiple Disabilities Act, 1999 and its rules (Rule 11(2)(b)). The designated authority and the local level committee are bodies set up under those two Acts (Rule 11(2)(a) and 11(2)(c)).

Two practical points. First, Rule 11 is about verifying the appointment, not about assessing the person's disability yourself; the check is whether a court, designated authority or local level committee appointed this guardian. Second, the prohibitions in Section 9(2) and 9(3) speak of children; for a person with disability, Section 9 turns on the guardian's verifiable consent. Rule 11 applies from 13 May 2027.

::: example a hearing-aid clinic in Chandigarh
A mother asks a hearing-aid clinic in Chandigarh to register her adult daughter, who has cerebral palsy and is unable to take legally binding decisions, and says she is the daughter's lawful guardian. Before processing the daughter's personal data, the clinic must obtain the mother's verifiable consent (Section 9(1)). From 13 May 2027, it must also verify that she was appointed by a court of law, a designated authority or a local level committee; for cerebral palsy, the applicable law is the National Trust Act of 1999 (Rule 11(2)(b)). The clinic's check is on the appointment, not on the daughter's condition.
:::


## Where the children's rules do not apply
::: short
Rule 12 and the Fourth Schedule lift the parental-consent rule and the tracking and advertising ban for named classes, such as clinics, schools and crèches, and named purposes, such as a child's safety, each only on its stated condition. The ban on processing likely to harm a child's well-being, Section 9(2), is never lifted.
:::

::: figure
{
 "type": "compare",
 "title": "What the Fourth Schedule lifts, and for whom",
 "caption": "Each entry lifts only Section 9(1) and 9(3), and only on its condition. Section 9(2), the ban on processing likely to harm a child's well-being, still applies to everyone. From 13 May 2027.",
 "columns": [
  {
   "heading": "Part A: classes of Data Fiduciary",
   "role": "fiduciary",
   "cite": "Rule 12(1)",
   "points": [
    "Clinical establishments, mental health establishments and healthcare professionals: health services to the child, as far as needed to protect her health",
    "Allied healthcare professionals: supporting a treatment and referral plan they recommended for the child, as far as needed to protect her health",
    "Educational institutions: tracking and behavioural monitoring for their educational activities or the safety of enrolled children",
    "Individuals caring for children in a crèche or day care centre: tracking and behavioural monitoring for the children's safety",
    "Transport providers engaged by a school, crèche or centre: tracking the children's location for their safety while travelling to and from it"
   ]
  },
  {
   "heading": "Part B: purposes",
   "role": "neutral",
   "cite": "Rule 12(2)",
   "points": [
    "A power, function or duty under Indian law, in the child's interests",
    "A subsidy, benefit, service, certificate, licence or permit provided in the child's interests",
    "Creating a user account used only for communication by email",
    "Tracking a child's real-time location for her safety and protection or security",
    "Keeping information, services or advertisements likely to harm her well-being from reaching her",
    "Confirming that a Data Principal is not a child, and due diligence under Rule 10"
   ]
  }
 ]
}
:::

Section 9(4) allows the Rules to lift Section 9(1) and 9(3), consent and the tracking and advertising ban, for classes of Data Fiduciaries or purposes, subject to conditions. Rule 12 does this through the two Parts of the Fourth Schedule. The exemption never lifts Section 9(2): processing likely to harm a child's well-being stays forbidden for everyone.

Part A of the Fourth Schedule names classes of Data Fiduciaries (Rule 12(1)), each with a condition:

- a clinical establishment, mental health establishment or healthcare professional, restricted to health services to the child, to the extent necessary to protect her health;
- an allied healthcare professional, restricted to supporting a treatment and referral plan such a professional recommended for the child;
- an educational institution, restricted to tracking and behavioural monitoring for its educational activities or the safety of its enrolled children;
- an individual caring for infants and children in a crèche or day care centre, restricted to tracking and monitoring for their safety;
- a transport provider engaged by a school, crèche or centre, restricted to tracking the children's location for safety while travelling to and from it.

Part B names purposes (Rule 12(2)): exercising a power or duty under Indian law in the interests of a child; providing a subsidy, benefit, service, certificate, licence or permit in a child's interests; creating a user account limited to communication by email; determining a child's real-time location for her safety; keeping harmful information, services or advertisements from reaching her; and confirming that a Data Principal is not a child, including due diligence under Rule 10.

Each entry is restricted "to the extent necessary". Rule 12 and the Fourth Schedule apply from 13 May 2027.

Separately, Section 9(5) lets the Central Government notify, for a Data Fiduciary whose processing of children's data is "verifiably safe", an age above which it is exempt from all or any obligations under Section 9(1) and 9(3).

::: example a school in Nashik
A school in Nashik uses an app to record pupils' attendance and classroom behaviour, and the operator it engages to run the school bus tracks the bus on its route. From 13 May 2027, under Rule 12(1) and Part A of the Fourth Schedule, the school needs no parental consent for tracking and behavioural monitoring for its educational activities or the children's safety, and the bus operator may track the children's location for their safety while travelling to and from school. Neither exemption reaches beyond its condition, such as showing the children targeted advertising, and neither lifts the ban on processing likely to harm a child's well-being (Section 9(2)).
:::


## Access, correction and erasure
::: short
Section 11 lets a Data Principal ask what personal data you process about her and whom you shared it with, and Section 12 lets her have it corrected, completed, updated or erased. You must erase on request unless the specified purpose or a law in force requires you to keep it.
:::

::: figure
{
 "type": "checklist",
 "title": "Access, correction and erasure: what she can ask, and what you must do",
 "caption": "These rights run against the Data Fiduciary she gave consent to, including for data she voluntarily provided for a specified purpose. Sections 11 and 12 set no response deadline of their own.",
 "role": "fiduciary",
 "items": [
  {
   "label": "A summary of her personal data and your processing activities",
   "cite": "Section 11(1)(a)"
  },
  {
   "label": "Who else has it",
   "detail": "The identities of all other Data Fiduciaries and Data Processors you shared it with, and a description of what was shared. Not required for sharing with a Data Fiduciary authorised by law, on its written request, to prevent, detect or investigate offences or cyber incidents (Section 11(2)).",
   "cite": "Section 11(1)(b)"
  },
  {
   "label": "Any other information that is prescribed",
   "cite": "Section 11(1)(c)"
  },
  {
   "label": "Correction, completion and updating",
   "detail": "Correct inaccurate or misleading data, complete incomplete data, and update it.",
   "cite": "Section 12(2)"
  },
  {
   "label": "Erasure",
   "detail": "Erase it unless keeping it is necessary for the specified purpose or to comply with a law in force.",
   "cite": "Section 12(3)"
  },
  {
   "label": "A published way to ask",
   "detail": "From 13 May 2027, publish on your website or app how to make a request, and any username or other identifier she must give.",
   "cite": "Rule 14(1)"
  }
 ]
}
:::

Section 11(1) gives a Data Principal the right to ask the Data Fiduciary to whom she previously gave consent, including personal data she voluntarily provided for a specified purpose (the first legitimate use in module 2), for:

- a summary of her personal data being processed and the processing activities (Section 11(1)(a));
- the identities of all other Data Fiduciaries and Data Processors with whom her data has been shared, with a description of what was shared (Section 11(1)(b));
- any other information about her personal data and its processing that is prescribed (Section 11(1)(c)).

Section 11(2) makes one exception: the sharing details need not be given where the data went to another Data Fiduciary authorised by law, on its written request, for preventing, detecting or investigating offences or cyber incidents, or for prosecution or punishment.

Section 12(1) gives her the right to correction, completion, updating and erasure of that personal data, in line with any other law's requirements. On a request, the Data Fiduciary must correct inaccurate or misleading data, complete incomplete data, and update it (Section 12(2)). On an erasure request, it must erase her personal data unless retention is necessary for the specified purpose or to comply with a law in force (Section 12(3)).

Rule 14 sets how requests reach you. Every Data Fiduciary must prominently publish on its website or app the means by which a Data Principal can make a request, and any particulars, such as a username or other identifier, needed to identify her under its terms of service (Rule 14(1)). She then makes the request using those means and particulars (Rule 14(2)). An "identifier" includes a customer file number, application reference number, enrolment ID, email address, mobile number or licence number (Rule 14(5)).

Sections 11 and 12 set no response deadline of their own; the ninety-day ceiling in Rule 14(3) belongs to grievances, as the next lesson explains. Rule 14 applies from 13 May 2027.

::: example an insurance agency in Patna
A customer of an insurance agency in Patna asks what data it holds about her and whether it has shared her details with anyone. The agency must give her a summary of her personal data and its processing, and name the other Data Fiduciaries and Data Processors it shared the data with, such as the firm that hosts its customer records, with a description of what was shared (Section 11(1)). She then asks it to correct her misspelt surname and to erase her data. It must correct the name, and must erase her data unless keeping it is necessary for the specified purpose or to comply with a law in force (Section 12(3)).
:::


## Grievances, and the person who answers
::: short
Section 13 gives a Data Principal readily available means of grievance redressal, and she must use them before approaching the Board. From 13 May 2027, Rule 14(3) requires you to publish a response period of no more than ninety days, and to respond within it.
:::

::: figure
{
 "type": "steps",
 "title": "A grievance, from receipt to the Board",
 "caption": "Rules 9 and 14 apply from 13 May 2027. Ninety days is the ceiling for the period you publish, not a target.",
 "steps": [
  {
   "when": "Before any grievance",
   "label": "Publish the route, the response period and a contact",
   "detail": "On your website or app: how to make a request, the identifier needed, your response period, and the business contact information of your Data Protection Officer, if applicable, or a person who can answer.",
   "role": "fiduciary",
   "cite": "Rule 14(3)"
  },
  {
   "when": "Date of receipt",
   "label": "She raises a grievance with you",
   "detail": "About any act or omission in your obligations about her personal data, or in her exercise of her rights.",
   "role": "principal",
   "cite": "Section 13(1)"
  },
  {
   "when": "Within your published period, at most ninety days",
   "label": "Respond",
   "detail": "Your system must be able to respond within the period you publish, and every response about her rights names your contact person (Rule 9).",
   "role": "fiduciary",
   "cite": "Rule 14(3)"
  },
  {
   "when": "Only after that",
   "label": "She may approach the Board",
   "detail": "She must first exhaust your grievance route.",
   "role": "state",
   "cite": "Section 13(3)"
  }
 ]
}
:::

Section 13(1) gives a Data Principal the right to "readily available means of grievance redressal" from a Data Fiduciary or Consent Manager, for any act or omission in performing its obligations about her personal data or in the exercise of her rights. Section 13(2) requires a response within the prescribed period. Section 13(3) requires her to exhaust this route before approaching the Board, so a grievance system that works is also your first chance to settle a matter before it becomes a complaint.

Rule 14(3) prescribes the period. Every Data Fiduciary and Consent Manager must prominently publish on its website or app the period under its grievance redressal system for responding to grievances, which must be "a reasonable period not exceeding ninety days". It must also implement appropriate technical and organisational measures so the system actually responds within that period. Ninety days is a ceiling, not a target, and the system must be able to respond within the period you publish.

Rule 9 names the person behind the system. Every Data Fiduciary must prominently publish on its website or app, and mention in every response to a communication about the exercise of a Data Principal's rights, the business contact information of the Data Protection Officer, if applicable, or of a person able to answer, on the Data Fiduciary's behalf, the Data Principal's questions about the processing of her personal data.

Put together, a small business needs four things on its website or app: how to make a request and what identifier to give (Rule 14(1)), the grievance response period (Rule 14(3)), the contact person (Rule 9), and a working process behind them. Log each request and grievance with its date of receipt, since the period runs from then (Section 13(2)).

Rules 9 and 14 apply from 13 May 2027.

::: example a broadband provider in Guwahati
A customer of a local broadband provider in Guwahati complains that it kept messaging her after she asked it to stop. The provider's website publishes a thirty-day response period for grievances, within the ninety-day ceiling in Rule 14(3), and names a contact person under Rule 9. It logs the grievance with its date of receipt and must respond within thirty days of that date. She must exhaust this route before she can approach the Board (Section 13(3)).
:::


## Nomination, and the Data Principal's duties
::: short
Section 14 lets a Data Principal nominate someone to exercise her rights if she dies or becomes incapable, and Section 15 sets five duties she owes, such as not impersonating anyone and not filing false or frivolous grievances. From 13 May 2027, Rule 14(4) lets her nominate one or more individuals.
:::

::: figure
{
 "type": "compare",
 "title": "What the Data Principal may do, and what she must do",
 "caption": "Rule 14 applies from 13 May 2027. She nominates using the means and particulars you require, so your published request route should cover nomination.",
 "columns": [
  {
   "heading": "Her right to nominate",
   "role": "principal",
   "points": [
    {
     "text": "She may nominate any other individual to exercise her rights in the event of her death or incapacity.",
     "cite": "Section 14(1)"
    },
    {
     "text": "Incapacity means being unable to exercise those rights because of unsoundness of mind or infirmity of body.",
     "cite": "Section 14(2)"
    },
    {
     "text": "She may nominate one or more individuals, in line with your terms of service and any applicable law.",
     "cite": "Rule 14(4)"
    }
   ]
  },
  {
   "heading": "Her duties",
   "role": "principal",
   "points": [
    {
     "text": "Comply with all applicable laws while exercising her rights.",
     "cite": "Section 15(a)"
    },
    {
     "text": "Not impersonate another person when providing her personal data for a specified purpose.",
     "cite": "Section 15(b)"
    },
    {
     "text": "Not suppress material information when providing her personal data for a State-issued document, unique identifier, proof of identity or proof of address.",
     "cite": "Section 15(c)"
    },
    {
     "text": "Not register a false or frivolous grievance or complaint with a Data Fiduciary or the Board.",
     "cite": "Section 15(d)"
    },
    {
     "text": "Give only verifiably authentic information when seeking correction or erasure.",
     "cite": "Section 15(e)"
    }
   ]
  }
 ]
}
:::

Section 14(1) gives a Data Principal the right to nominate any other individual who will, in the event of her death or incapacity, exercise her rights under the Act and the Rules. "Incapacity" means being unable to exercise those rights because of unsoundness of mind or infirmity of body (Section 14(2)).

Rule 14(4) sets the mechanics. She may nominate one or more individuals, in line with the Data Fiduciary's terms of service and any applicable law, using the means and furnishing the particulars the Data Fiduciary requires. So your published request route under Rule 14(1) should cover nomination too, and your records should be able to hold a nominee against a Data Principal's account. Rule 14 applies from 13 May 2027.

Section 15 then sets out duties the Data Principal owes. She must:

- comply with all applicable laws while exercising her rights (Section 15(a));
- not impersonate another person when providing her personal data for a specified purpose (Section 15(b));
- not suppress material information when providing her personal data for any document, unique identifier, proof of identity or proof of address issued by the State or its instrumentalities (Section 15(c));
- not register a false or frivolous grievance or complaint with a Data Fiduciary or the Board (Section 15(d));
- furnish only verifiably authentic information when exercising her right to correction or erasure (Section 15(e)).

These duties do not shift your obligations onto her. As module 2 explained, a Data Fiduciary stays responsible for compliance even if a Data Principal fails in her duties. Section 15(e) does mean that information she supplies for a correction or erasure should be verifiably authentic. What the Board can do about a breach of these duties is covered in module 5.

::: example a diagnostic centre in Jaipur
A patient of a diagnostic centre in Jaipur uses the centre's published request route to nominate her son to exercise her rights under the Act in the event of her death or incapacity (Section 14(1)). If an illness later leaves her unable to exercise those rights through infirmity of body, her son may, for example, ask the centre for a summary of her personal data on her behalf. While she can act for herself, her own duties apply: when she asks for a correction, she must give only verifiably authentic information (Section 15(e)).
:::
