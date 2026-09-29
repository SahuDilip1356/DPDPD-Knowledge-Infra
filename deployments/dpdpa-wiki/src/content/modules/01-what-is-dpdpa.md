---
slug: what-is-dpdpa
order: 1
title: What is the DPDPA?
summary: What the Digital Personal Data Protection Act, 2023 is, the words it uses, who it covers, what it changed in other laws, and how the 2025 Rules and their three start dates attach to it.
minutes: 10
provisions: [S1, S2, S3, S40, S41, S42, S43, S44, R1, R2]
next: core-rules
quiz:
  - q: "A company in Singapore runs a shopping app used by customers in India. Does the Act reach its processing?"
    a: "No; the Act applies only to processing carried out inside India"
    b: "Yes, because the processing is connected with offering goods or services to Data Principals in India"
    c: "Only if the company has a registered office in India"
    d: "Only if the customers pay in rupees"
    answer: b
    cites: S3
  - q: "Which of these is outside the Act under Section 3(c)?"
    a: "A shop's customer list typed into a spreadsheet"
    b: "A payroll file held by a company's outsourced vendor"
    c: "An individual's own phone contacts kept for personal or domestic purposes"
    d: "Customer forms collected on paper and later scanned"
    answer: c
    cites: S3
  - q: "Under the Act, who is the Data Fiduciary?"
    a: "The individual the personal data is about"
    b: "The vendor that stores data on someone else's instructions"
    c: "The registered platform through which consent is given and withdrawn"
    d: "The person who, alone or with others, determines the purpose and means of processing"
    answer: d
    cites: S2
  - q: "When does the Act come into force?"
    a: "On dates the Central Government notifies, which may differ for different provisions"
    b: "On 11 August 2023, the day it was published in the Gazette"
    c: "Eighteen months after the Rules were published"
    d: "Only once the Data Protection Board has been constituted"
    answer: a
    cites: S1
  - q: "What does Section 44(3) do to the Right to Information Act, 2005?"
    a: "Repeals it"
    b: "Substitutes its personal-information exemption with the words 'information which relates to personal information'"
    c: "Removes every exemption available to public authorities"
    d: "Adds a new right of appeal to the Data Protection Board"
    answer: b
    cites: S44
  - q: "From which date do the Rules on notice, security safeguards, breach intimation and retention apply?"
    a: "13 November 2025"
    b: "13 November 2026"
    c: "13 May 2027"
    d: "11 August 2023"
    answer: c
    cites: R1
  - q: "When the Central Government amends the penalty Schedule under Section 42, what limit applies?"
    a: "There is no limit"
    b: "Each amendment needs a fresh Act of Parliament"
    c: "Penalties may only be lowered, never raised"
    d: "No penalty may be raised to more than twice what the Act originally specified"
    answer: d
    cites: S42
---

This module explains what the Digital Personal Data Protection Act, 2023 is, the words it uses, who it covers, and how the Rules of 2025 attach to it. Read it first; every later module assumes these basics.

## What the Act is and how it starts
::: short
The Digital Personal Data Protection Act, 2023 is India's law on processing digital personal data. It was published on 11 August 2023, but it is switched on in stages: each provision starts on a date the Central Government notifies, as Section 1(2) provides.
:::

::: figure
{
 "type": "actmap",
 "title": "The Act at a glance: nine chapters and a penalty table",
 "caption": "Bar length shows how many sections each chapter holds. Colour shows whose chapter it is: the business's duties, the individual's rights, or the Board's machinery. Select a chapter to read it."
}
:::

The Digital Personal Data Protection Act, 2023 is India's law on how digital personal data may be processed. It received the President's assent and was published in the Gazette of India on 11 August 2023; the gazette text of Section 1 carries that date. Section 1(1) gives the short title. Section 1(2) deals with when the Act starts, and that second point matters more than it looks.

The Act did not come into force on the day it was published. Section 1(2) says it comes into force "on such date as the Central Government may, by notification in the Official Gazette, appoint", and that "different dates may be appointed for different provisions". So the Act is switched on in stages, by notification, and a reference in any provision to "the commencement of this Act" means the day that particular provision starts.

Two practical consequences follow. First, if someone tells you "the whole Act has been in force since 2023", that is not what Section 1(2) says; the sections start on notified dates, and this course does not restate those notifications. Second, the timetable most businesses actually work to comes from the Rules rather than the Act. Rule 1 sets out which rules apply from which date, and the last lesson in this module walks through it.

The Act runs to forty-four sections and a penalty table. This course covers them in the order a business meets them: this module for the foundations, then the core obligations, people's rights, special cases, enforcement, and finally how it lands in your own business.


## The words the Act uses
::: short
Four roles carry the whole Act. The Data Principal is the person the data is about, the Data Fiduciary decides why and how it is processed, the Data Processor processes it on the Fiduciary's behalf, and the Consent Manager helps the person manage consent.
:::

::: figure
{
 "type": "roles",
 "title": "Who is who under the Act",
 "caption": "Every duty and right in the Act attaches to one of these roles. The colours stay the same in every figure in this course.",
 "nodes": [
  {
   "id": "dp",
   "name": "Data Principal",
   "role": "principal",
   "def": "The individual the personal data is about. For a child, it includes the parents or lawful guardian.",
   "example": "A patient, a customer, an employee",
   "cite": "Section 2(j)"
  },
  {
   "id": "df",
   "name": "Data Fiduciary",
   "role": "fiduciary",
   "def": "Any person who, alone or with others, determines the purpose and means of processing.",
   "example": "Usually you: the clinic, the shop, the app",
   "cite": "Section 2(i)"
  },
  {
   "id": "pr",
   "name": "Data Processor",
   "role": "processor",
   "def": "Any person who processes personal data on behalf of a Data Fiduciary.",
   "example": "Your cloud host, payroll vendor or CRM provider",
   "cite": "Section 2(k)"
  },
  {
   "id": "cm",
   "name": "Consent Manager",
   "role": "manager",
   "def": "A person registered with the Board who is a single point of contact for the Data Principal to give, manage, review and withdraw consent.",
   "cite": "Section 2(g)"
  },
  {
   "id": "bd",
   "name": "The Board",
   "role": "state",
   "def": "The Data Protection Board of India, established by the Central Government.",
   "cite": "Section 2(c)"
  }
 ],
 "edges": [
  {
   "from": "df",
   "to": "dp",
   "label": "determines the purpose and means of processing the personal data of",
   "cite": "Section 2(i)"
  },
  {
   "from": "pr",
   "to": "df",
   "label": "processes personal data on behalf of",
   "cite": "Section 2(k)"
  },
  {
   "from": "cm",
   "to": "dp",
   "label": "is a single point of contact for",
   "cite": "Section 2(g)"
  },
  {
   "from": "cm",
   "to": "bd",
   "label": "is registered with",
   "cite": "Section 2(g)"
  }
 ]
}
:::

Section 2 defines the vocabulary, and the rest of the Act only makes sense once you have these nine terms.

Personal data is "any data about an individual who is identifiable by or in relation to such data" (Section 2(t)). Digital personal data is personal data in digital form (Section 2(n)). Processing is any wholly or partly automated operation on digital personal data: collection, recording, storage, use, sharing, erasure and everything between (Section 2(x)).

The Data Principal is the individual the data is about; for a child it includes the parents or lawful guardian, and for a person with disability it includes the lawful guardian acting on her behalf (Section 2(j)). The Data Fiduciary is any person who, alone or with others, "determines the purpose and means of processing" (Section 2(i)). In most businesses, that is you. A Data Processor processes personal data on behalf of a Data Fiduciary (Section 2(k)): your cloud host, payroll vendor or CRM provider.

A Consent Manager is a person registered with the Board who acts as a single point of contact for a Data Principal to give, manage, review and withdraw consent (Section 2(g)). A child is an individual who has not completed eighteen years (Section 2(f)). A Significant Data Fiduciary is a Data Fiduciary, or class of them, that the Central Government notifies as such (Section 2(z)); extra duties attach to that status and module 4 covers them.

Two more definitions are worth knowing. "Person" includes an individual, a Hindu undivided family, a company, a firm, an association of persons and the State (Section 2(s)), so a sole proprietor and a listed company are equally capable of being a Data Fiduciary. And the Act uses "she" and "her" for every individual regardless of gender (Section 2(y)); this course follows the same convention.

::: example a physiotherapy clinic in Pune
The clinic decides why it collects patients' names, phone numbers and treatment notes, and how it keeps them, so the clinic is the Data Fiduciary. Each patient is a Data Principal. The company that hosts the clinic's appointment software processes those records on the clinic's behalf, so it is a Data Processor.
:::


## Who the Act applies to, and who it leaves out
::: short
The Act covers digital personal data processed in India, and processing abroad connected with offering goods or services to people in India. It leaves out data used for a personal or domestic purpose, and data made public by the person herself or under a legal duty.
:::

::: figure
{
 "type": "gate",
 "title": "Does the Act apply? Three tests, in the order Section 3 sets them",
 "caption": "There is no size test. And data that someone else scraped, leaked or published without a legal duty is not covered by the exclusion, so it stays inside the Act.",
 "steps": [
  {
   "q": "Is it personal data in digital form, or collected on paper and digitised later?",
   "cite": "Section 3(a)",
   "failLabel": "If no",
   "fail": "Paper records that are never digitised are outside the Act.",
   "pass": "If yes, go to the next test."
  },
  {
   "q": "Is it processed in India, or outside India in connection with offering goods or services to Data Principals in India?",
   "cite": "Section 3(b)",
   "failLabel": "If no",
   "fail": "Processing abroad with no offering to people in India is outside the Act.",
   "pass": "If yes, go to the next test."
  },
  {
   "q": "Is it processed by an individual for a personal or domestic purpose, or was it made publicly available by the Data Principal herself or under a legal duty in India?",
   "cite": "Section 3(c)",
   "failLabel": "If yes",
   "fail": "The Act does not apply to that data.",
   "pass": "If no, the Act applies."
  }
 ],
 "result": {
  "label": "The Act applies, whatever the size of the business.",
  "cite": "Section 3",
  "role": "fiduciary"
 }
}
:::

Section 3 draws the boundary. The Act applies to the processing of digital personal data within India, whether the data was collected in digital form or collected on paper and digitised later (Section 3(a)). It also applies to processing outside India, if that processing is connected with offering goods or services to Data Principals inside India (Section 3(b)). A foreign app with Indian customers is inside the boundary; a business in India processing its own customers' data plainly is.

There is no size threshold in Section 3. A three-person shop that keeps customer details in a spreadsheet is processing digital personal data just as a large platform is. Whether obligations differ by size is a separate question, answered by the notified classes of Significant Data Fiduciary and by the Rules; whether the Act applies at all is answered by Section 3 alone.

Section 3(c) then carves out two situations. The first is personal data processed by an individual for a personal or domestic purpose: your own phone contacts, a family chat group. The second is personal data that has been made publicly available either by the Data Principal herself, or by someone under a legal duty in India to publish it. The Act gives its own example: an individual who blogs her views and publicly posts her personal data on social media. The Act does not apply to that data (Section 3, Illustration).

Note what the second exclusion does not say. It covers data the Data Principal herself made public, or data published under a legal obligation. Data that a third party scraped, leaked or published without either of those is not described by Section 3(c)(ii), and so remains inside the Act.

Paper records that are never digitised are also outside Section 3(a). The moment they are scanned or typed into a system, they are in.

::: example two businesses, two sides of the boundary
A saree seller in Surat keeps customer names and delivery addresses in a spreadsheet. That is digital personal data processed in India, so the Act applies, however small the business. A software company in Singapore sells a subscription app to users in India; its processing happens abroad but is connected with offering a service to Data Principals in India, so the Act applies to that processing too.
:::


## What the Act changed in other laws
::: short
Section 44 amends three older laws. Appeals under this Act go to the telecom appellate tribunal, the IT Act loses its data-protection compensation provision, and the RTI exemption for personal information is rewritten.
:::

::: figure
{
 "type": "changes",
 "title": "Three older laws, amended by Section 44",
 "caption": "The words on the right are quoted from Section 44. The descriptions on the left summarise the earlier position.",
 "items": [
  {
   "law": "Telecom Regulatory Authority of India Act, 1997",
   "before": "The tribunal heard appeals under the IT Act, 2000 and the AERA Act, 2008",
   "after": "It is also “the Appellate Tribunal under the Digital Personal Data Protection Act, 2023”",
   "cite": "Section 44(1)"
  },
  {
   "law": "Information Technology Act, 2000, provision numbered 43A",
   "before": "Compensation for failure to protect data",
   "after": "Omitted",
   "omitted": true,
   "cite": "Section 44(2)(a)"
  },
  {
   "law": "Information Technology Act, 2000, proviso numbered 81",
   "before": "Named the Copyright Act, 1957 and the Patents Act, 1970",
   "after": "Now also names “the Digital Personal Data Protection Act, 2023”",
   "cite": "Section 44(2)(b)"
  },
  {
   "law": "Right to Information Act, 2005, clause 8(1)(j)",
   "before": "A narrower exemption for personal information, with a public-interest test",
   "after": "“information which relates to personal information”",
   "cite": "Section 44(3)"
  }
 ]
}
:::

Section 44 makes three consequential amendments to older statutes. None of them adds a duty for a business, but each explains something you will meet later.

Section 44(1) amends the Telecom Regulatory Authority of India Act, 1997 so that the Telecom Disputes Settlement and Appellate Tribunal also serves as the Appellate Tribunal under this Act, alongside its existing roles under the Information Technology Act, 2000 and the Airports Economic Regulatory Authority of India Act, 2008. This is why Section 2(a) defines "Appellate Tribunal" as that tribunal: appeals from the Board go there, as module 5 explains.

Section 44(2) amends the Information Technology Act, 2000 in three ways. Its provision numbered 43A is omitted (Section 44(2)(a)). Its saving clause, which lists the laws the IT Act does not override, now also names the Digital Personal Data Protection Act, 2023 (Section 44(2)(b)). And one of its rule-making clauses, lettered (ob), is omitted (Section 44(2)(c)).

Section 44(3) is the one that draws the most questions. It replaces the personal-information exemption in the Right to Information Act, 2005, the clause numbered 8(1)(j), with a single line: "information which relates to personal information". Section 44(3) changes only that clause; the rest of the Right to Information Act is untouched by this Act, and how the new words apply to a particular request is decided under that Act, not this one.

The practical reading of Section 44 is modest. Your appeals route runs to an existing tribunal. The IT Act no longer carries the provision numbered 43A. And the RTI exemption for personal information now reads in the short form quoted above.


## The Act and the Rules: how they fit together
::: short
The Act says what must happen; the Rules say how. The Central Government makes the Rules under Section 40, they cannot go beyond the Act, and Parliament can modify or annul them.
:::

::: figure
{
 "type": "stack",
 "title": "Where each layer gets its authority",
 "caption": "Read from the top. Each layer can only do what the layer above allows.",
 "layers": [
  {
   "name": "The Digital Personal Data Protection Act, 2023",
   "role": "state",
   "detail": "Made by Parliament. Forty-four sections and a penalty table. Often says a thing must be done “in such manner as may be prescribed”.",
   "cite": "Section 2(v)"
  },
  {
   "name": "The Digital Personal Data Protection Rules, 2025",
   "role": "state",
   "detail": "Twenty-three rules made by the Central Government, published on 13 November 2025. They prescribe the manner: notice, breach intimation, retention periods and more.",
   "cite": "Section 40"
  },
  {
   "name": "The seven Schedules to the Rules",
   "role": "neutral",
   "detail": "Detailed conditions and tables that individual rules call on, such as the conditions for Consent Managers and the retention periods for certain businesses."
  }
 ],
 "links": [
  "Section 40: rules “not inconsistent with the provisions of this Act”",
  "Each schedule is invoked by a rule"
 ],
 "checksTitle": "Checks on the rule-making power",
 "checks": [
  {
   "label": "Parliament reviews every rule.",
   "detail": "Each rule is laid before both Houses for thirty days, and either House may modify or annul it.",
   "cite": "Section 41"
  },
  {
   "label": "Penalties have a ceiling.",
   "detail": "The Government may amend the penalty table, but never to more than twice the amount in the original Act.",
   "cite": "Section 42"
  },
  {
   "label": "Difficulty orders expire.",
   "detail": "Orders to remove difficulties may be made only within three years of commencement, and each is laid before Parliament.",
   "cite": "Section 43"
  }
 ]
}
:::

Much of the Act says a thing must be done "in such manner as may be prescribed". "Prescribed" means prescribed by rules made under the Act (Section 2(v)), and Section 40 is where the power to make those rules lives. Section 40(1) lets the Central Government make rules, by notification and after previous publication, that are "not inconsistent with the provisions of this Act". Section 40(2) then lists the matters the rules may cover: the manner of notice, the registration and obligations of Consent Managers, the form of breach intimation to the Board, retention time periods, how a Data Protection Officer's contact details are published, verifiable consent for children, how access, erasure, grievance and nomination requests are made, and the Board's own procedures.

The Rules cannot go beyond the Act, and Parliament keeps a check. Section 41 requires every rule to be laid before both Houses for thirty days, and either House may modify or annul it. Section 42 lets the Central Government amend the penalty Schedule by notification, but never so as to raise a penalty to more than twice the amount in the original Act. Section 43 lets the Government issue orders to remove difficulties in giving effect to the Act, only within three years of commencement, each order laid before Parliament.

The Digital Personal Data Protection Rules, 2025 are the rules made under Section 40. Rule 2 does the housekeeping. "Act" means the Digital Personal Data Protection Act, 2023 (Rule 2(1)(a)). A "user account" is the online account a Data Principal registers with a Data Fiduciary, including profiles, pages, handles, email addresses and mobile numbers through which she accesses the service (Rule 2(1)(c)). "Verifiable consent" points to the children's-consent rules covered in module 3 (Rule 2(1)(d)). Any word the Rules use but do not define carries its meaning from the Act (Rule 2(2)).

So when this course says "the Act requires it and the Rules say how", that is the Section 40 relationship at work.


## When the Rules apply: the three dates
::: short
The Rules start in three steps. The Board's machinery has applied since 13 November 2025, Consent Manager registration applies from 13 November 2026, and almost everything a business must do applies from 13 May 2027.
:::

::: figure
{
 "type": "timeline",
 "title": "The compliance calendar, from Rule 1",
 "caption": "Filled dots have passed; hollow dots are still ahead. The Act's own sections start on dates notified under Section 1(2), which this course does not restate.",
 "events": [
  {
   "date": "2023-08-11",
   "label": "The Act is published in the Gazette",
   "detail": "Its provisions start on dates the Central Government notifies.",
   "role": "state",
   "cite": "Section 1(2)"
  },
  {
   "date": "2025-11-13",
   "label": "The Rules are published; the first group applies",
   "detail": "The two opening rules, and the five rules on the Board's machinery (numbered seventeen to twenty-one).",
   "role": "state",
   "cite": "Rule 1(2)"
  },
  {
   "date": "2026-11-13",
   "label": "Consent Manager registration applies",
   "detail": "The fourth rule, one year after publication.",
   "role": "manager",
   "cite": "Rule 1(3)"
  },
  {
   "date": "2027-05-13",
   "label": "The rest of the Rules apply",
   "detail": "Notice, security safeguards, breach intimation, retention, children's consent, the contact person and the mechanics of people's rights.",
   "role": "fiduciary",
   "cite": "Rule 1(4)"
  }
 ]
}
:::

Rule 1 is short, but it is the calendar the whole compliance conversation runs on. The Rules were published in the Official Gazette on 13 November 2025, and Rule 1 splits them into three groups by start date.

Rule 1(2): the first group came into force on the day of publication, 13 November 2025. It contains the two opening rules, title and definitions, and five rules towards the end (numbered seventeen to twenty-one) that deal with the machinery of the Board. So Rule 1 and Rule 2 have been in force since that day.

Rule 1(3): one rule, the fourth, comes into force one year after publication, on 13 November 2026.

Rule 1(4): everything else, that is the third rule, the fifth to the sixteenth, and the twenty-second and twenty-third, comes into force eighteen months after publication, on 13 May 2027. That group is where the operative detail sits: the notice, security safeguards, breach intimation, retention periods, verifiable consent for children, the contact person and the mechanics of Data Principal rights. Modules 2 and 3 cover those rules and flag the date each time it matters.

Two points of care. First, these dates are for the Rules. The Act's own sections start on dates the Central Government notifies under Section 1(2); this course does not restate those notifications, so check the provision page for any section you rely on. Second, a rule that is not yet in force still tells you what "prescribed" will mean when it arrives, which is why this course teaches the Rules alongside the Act rather than after it.

