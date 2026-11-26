---
slug: scenarios
order: 0
title: Six napkins: the DPDP Act in six pictures
summary: One customer, one tiffin service, six everyday questions about her data. Each answer is a single picture, in plain words, resting on the Act's or the Rules' own text.
provisions: [S1, S2, S4, S6, S7, S8, S10, S12, S13, S16, S33, ACT-SCHEDULE, R1, R7, R14, R15]
next: null
---

Asha lives in Pune and orders lunch every day from a tiffin service through its app. Her name, phone number and address now sit with a business. Each scenario below asks one question about that data, and the kind of question picks the picture: who becomes a portrait, how much a chart, where a map, when a timeline, how a flow, and why a plot. Asha and the tiffin service are made up.

## Who is who when Asha orders lunch

::: short
Asha is the Data Principal, because the data is about her. The tiffin service is the Data Fiduciary, because it decides why and how her data is used. The delivery partner is a Data Processor, because it uses the data only for the service (Section 2).
:::

::: figure
{
  "type": "roles",
  "title": "Five roles around one lunch order",
  "caption": "The business that decides the purpose answers for its helpers too.",
  "nodes": [
    { "id": "asha", "name": "Asha", "role": "principal", "def": "The person the data is about.", "example": "She gives her name, phone number and address to order lunch.", "cite": "Section 2(j)" },
    { "id": "service", "name": "The tiffin service", "role": "fiduciary", "def": "Decides why and how her data is used.", "cite": "Section 2(i)" },
    { "id": "delivery", "name": "Delivery partner", "role": "processor", "def": "Uses her address only to deliver for the service.", "cite": "Section 2(k)" },
    { "id": "cm", "name": "Consent Manager", "role": "manager", "def": "Optional. A platform registered with the Board where Asha can give, manage, review and withdraw her consent.", "cite": "Section 2(g)" },
    { "id": "board", "name": "Data Protection Board", "role": "state", "def": "Hears Asha's complaint once she has tried the service's own grievance channel.", "cite": "Section 13(3)" }
  ],
  "edges": [
    { "from": "asha", "to": "service", "label": "gives her data to" },
    { "from": "service", "to": "delivery", "label": "hires, under a valid contract,", "cite": "Section 8(2)" },
    { "from": "service", "to": "delivery", "label": "stays responsible for the work of", "cite": "Section 8(1)" }
  ]
}
:::

::: try The delivery partner leaks Asha's address. Who answers to her?
The tiffin service. Section 8(1) makes the Data Fiduciary responsible for processing done by it “or on its behalf by a Data Processor”, whatever their contract says.
:::

Section 2 names the roles. A Data Fiduciary is the one who “determines the purpose and means of processing of personal data”. A Data Processor is anyone who “processes personal data on behalf of a Data Fiduciary”. The Data Principal is “the individual to whom the personal data relates”.

The tiffin service may use helpers. Section 8(2) lets it use a Data Processor “only under a valid contract”. The contract does not move the duty. Section 8(1) keeps the service responsible “irrespective of any agreement to the contrary”.

A Consent Manager is optional. It is “registered with the Board” and acts as “a single point of contact” for Asha's consents (Section 2(g)).

## How big can a penalty get?

::: short
The Schedule to the Act lists the highest penalty for each kind of breach of the law. The Board sets the amount after an inquiry, up to these limits (Section 33). Poor security sits at the top. Asha has duties too, with a far smaller limit.
:::

::: figure
{
  "type": "scale",
  "title": "The highest penalty for each kind of breach",
  "caption": "Six of the Schedule's seven rows. The one left out, row 6, is for breaking a promise made to the Board (a voluntary undertaking). Its limit is the limit for the breach the promise was about.",
  "items": [
    { "label": "Not keeping reasonable security safeguards", "value": 250, "display": "up to ₹250 crore", "role": "fiduciary", "cite": "the Schedule to the Act" },
    { "label": "Not telling the Board and the affected people about a breach", "value": 200, "display": "up to ₹200 crore", "role": "fiduciary", "cite": "the Schedule to the Act" },
    { "label": "Breaking the extra duties for children's data", "value": 200, "display": "up to ₹200 crore", "role": "fiduciary", "cite": "the Schedule to the Act" },
    { "label": "Breaking the extra duties of a Significant Data Fiduciary, a business the Central Government names under Section 10", "value": 150, "display": "up to ₹150 crore", "role": "fiduciary", "cite": "the Schedule to the Act" },
    { "label": "Breaking any other provision of the Act or the Rules", "value": 50, "display": "up to ₹50 crore", "role": "fiduciary", "cite": "the Schedule to the Act" },
    { "label": "A Data Principal breaking her own duties", "value": 0.0001, "display": "up to ₹10,000", "role": "principal", "cite": "the Schedule to the Act" }
  ]
}
:::

::: try The tiffin service leaves its order database open, the addresses leak, and it tells no one. Which rows apply?
Two. The first row, for not keeping reasonable security safeguards (up to ₹250 crore), and the second, for not giving the Board or the affected people notice of the breach (up to ₹200 crore).
:::

Every row of the Schedule to the Act uses the same words: the penalty “may extend to” an amount. The amount is a ceiling. The top row is for failing to take “reasonable security safeguards to prevent personal data breach”, at “two hundred and fifty crore rupees”. The second is for failing to give “notice of a personal data breach”, at “two hundred crore rupees”.

Asha has duties as well, such as not impersonating someone else and not filing a false complaint. Breaking them “may extend to ten thousand rupees”.

Who sets the amount? Section 33(1) lets the Board “impose such monetary penalty specified in the Schedule” after an inquiry finds a breach significant. Section 33(2) lists what the Board weighs, such as how serious the breach was and how long it lasted.

## Where Asha's data travels

::: short
Asha's details go from her phone to the tiffin service, then to helpers who take payment and deliver, and may sit on a server abroad. Sending data outside India is allowed unless the Central Government restricts that country by notification (Section 16), and the service must meet any requirements the Government sets by order (Rule 15).
:::

::: figure
{
  "type": "map",
  "title": "One lunch order, four places, one border",
  "caption": "Wherever the data sits, the tiffin service must keep it safe.",
  "regions": [
    {
      "name": "In India",
      "places": [
        { "name": "Asha's phone, Pune", "role": "principal", "detail": "where her order starts" },
        { "name": "The tiffin service", "role": "fiduciary", "detail": "decides what happens to her data" },
        { "name": "Payment company", "role": "processor", "detail": "takes her payment for the service" },
        { "name": "Delivery partner", "role": "processor", "detail": "brings the lunch to her address" }
      ]
    },
    {
      "name": "Outside India",
      "places": [
        { "name": "Cloud server", "role": "processor", "detail": "stores order records, if the service keeps them abroad", "cite": "Section 16(1), Rule 15" }
      ]
    }
  ],
  "routes": [
    { "from": "Asha's phone, Pune", "to": "The tiffin service", "label": "her name, phone and address" },
    { "from": "The tiffin service", "to": "Payment company", "label": "what is needed to take payment" },
    { "from": "The tiffin service", "to": "Delivery partner", "label": "her address" },
    { "from": "The tiffin service", "to": "Cloud server", "label": "order records, unless that country is restricted", "cite": "Section 16(1)" }
  ]
}
:::

::: try The tiffin service moves its order records to a server in another country. Is that allowed?
Yes, unless the Central Government has restricted transfers to that country by notification (Section 16(1)). From 13 May 2027 the service must also meet any requirements the Government sets by order about making the data available to a foreign State (Rule 15). Any Indian law with stricter rules for that kind of data still applies (Section 16(2)). The service stays responsible for the data while a helper holds it (Section 8(1)).
:::

Section 16(1) lets the Central Government “restrict the transfer of personal data by a Data Fiduciary for processing to such country or territory outside India as may be so notified”. The default is open; a notification closes a country. Section 16(2) keeps any Indian law that gives “a higher degree of protection” for such transfers. Rule 15 adds that a transfer is “subject to the restriction that the Data Fiduciary shall meet such requirements as the Central Government may, by general or special order, specify”.

Distance does not change the duty. Section 8(5) requires the service to protect personal data “in its possession or under its control, including in respect of any processing undertaken by it or on its behalf by a Data Processor”.

## When the duties start, and how fast to act

::: short
The Rules start in three steps. Most of the Rules that set out the service's duties, breach reporting included, apply from 13 May 2027 (Rule 1). After that, a breach starts a short clock: tell people without delay, and send the Board a full report within 72 hours (Rule 7).
:::

::: figure
{
  "type": "timeline",
  "title": "When the Rules start",
  "caption": "The Act's own sections start on dates the Central Government notifies (Section 1(2)).",
  "events": [
    { "date": "2025-11-13", "label": "The first Rules start", "detail": "definitions, and setting up the Board", "role": "state", "cite": "Rule 1(2)" },
    { "date": "2026-11-13", "label": "The rule on Consent Managers starts", "detail": "one year after the Rules were published", "role": "manager", "cite": "Rule 1(3)" },
    { "date": "2027-05-13", "label": "Most of the Rules start", "detail": "notices, security, breach reporting, rights and the rest, eighteen months after publication", "role": "fiduciary", "cite": "Rule 1(4)" }
  ]
}
:::

::: figure
{
  "type": "steps",
  "title": "The breach clock",
  "caption": "The Board can allow longer than 72 hours on a written request.",
  "steps": [
    { "when": "Without delay", "label": "Tell Asha", "detail": "what happened, what it means for her, what she can do, and whom to contact", "role": "principal", "cite": "Rule 7(1)" },
    { "when": "Without delay", "label": "Tell the Board", "detail": "a description of the breach and its likely impact", "role": "state", "cite": "Rule 7(2)" },
    { "when": "Within 72 hours", "label": "Send the Board a full report", "detail": "the facts, the causes, the fixes, and what Asha was told", "role": "state", "cite": "Rule 7(2)" }
  ]
}
:::

::: try The service finds a leak late on a Friday in June 2027. When is the full report due?
Within 72 hours of finding out, so by late Monday, unless the Board allows more time on a written request (Rule 7(2)). The first messages, to Asha and to the Board, go without delay.
:::

Rule 1 sets the dates. The rules on breach reporting, notices, security and rights come into force “eighteen months after the date of publication in the Official Gazette”, which is 13 May 2027.

Rule 7(1) asks the service to tell each affected person “in a concise, clear and plain manner and without delay”. Rule 7(2) asks for a first report to the Board “without delay”, then a detailed one “within seventy-two hours of becoming aware of the breach, or within such longer period as the Board may allow on a request made in writing in this behalf”.

## How Asha gets her data erased

::: short
Asha asks the tiffin service, using the method it publishes on its app or website. It erases her data unless the purpose or a law needs it kept. If she is not satisfied, she raises a grievance with the service first, and only then goes to the Board (Section 13).
:::

::: figure
{
  "type": "steps",
  "title": "From a request to the Board, in order",
  "caption": "The Board comes last. Asha first uses the service's own grievance channel.",
  "steps": [
    { "when": "First", "label": "Asha asks the service to erase her data", "detail": "using the means it publishes on its website or app", "role": "principal", "cite": "Rule 14(1)" },
    { "when": "Then", "label": "The service erases it", "detail": "unless keeping it is needed for the purpose or for a law", "role": "fiduciary", "cite": "Section 12(3)" },
    { "when": "If she is not satisfied", "label": "She raises a grievance with the service", "detail": "it answers within the period it publishes, at most 90 days", "role": "fiduciary", "cite": "Rule 14(3)" },
    { "when": "Only then", "label": "She can complain to the Board", "role": "state", "cite": "Section 13(3)" }
  ]
}
:::

::: try Asha is annoyed. Can she skip the service and complain straight to the Board?
No. Section 13(3) says she “shall exhaust the opportunity of redressing her grievance under this section before approaching the Board”.
:::

Section 12(3) gives Asha the right to ask for erasure. On her request the service “shall erase her personal data unless retention of the same is necessary for the specified purpose or for compliance with any law for the time being in force”. Rule 14(1) asks the service to publish how she can make that request.

If she is unhappy, Section 13(1) gives her the right to “readily available means of grievance redressal”. Rule 14(3) asks the service to publish the period in which it answers grievances, “within a reasonable period not exceeding ninety days”. Rule 14 applies from 13 May 2027.

## Why the service may use some data and not other data

::: short
Two questions decide it. Did Asha agree, or hand the data over herself for this purpose? Is the data needed for that purpose? Her address passes both. Her contact list fails the second, even if she tapped Allow, because consent covers only what the purpose needs (Section 6).
:::

::: figure
{
  "type": "plot",
  "title": "Four pieces of data, placed by two questions",
  "caption": "Filled dots, top right, may be used. Hollow dots, on the left, may not. The key under the chart explains each one.",
  "x": { "label": "Is it needed for the purpose?", "low": "not needed", "high": "needed" },
  "y": { "label": "Did Asha agree, or hand it over herself?", "low": "no", "high": "yes" },
  "points": [
    { "label": "Her delivery address", "x": 0.82, "y": 0.86, "ok": true, "verdict": "Allowed", "detail": "She gave it to get lunch delivered, and delivery needs it.", "cite": "Section 6(1)" },
    { "label": "Her phone number, for the bill by SMS", "x": 0.68, "y": 0.6, "ok": true, "verdict": "Allowed", "detail": "She handed it over for the receipt and has not said no.", "cite": "Section 7(a)" },
    { "label": "Her contact list", "x": 0.18, "y": 0.8, "ok": false, "verdict": "Not allowed, even after a tap on Allow", "detail": "Consent covers only data the purpose needs, and lunch delivery does not need her contacts.", "cite": "Section 6(1)" },
    { "label": "Selling her number to advertisers", "x": 0.14, "y": 0.14, "ok": false, "verdict": "Not allowed", "detail": "She gave her number for lunch, not for advertising. Without her consent for that purpose, it is not a use the Act allows.", "cite": "Section 4(1)" }
  ]
}
:::

::: try Asha gave her number only so the service could text her the bill. She never ticked a consent box. Can it send the receipt?
Yes. Section 7(a) allows use “for the specified purpose for which the Data Principal has voluntarily provided her personal data”, as long as she has not said she does not consent. The Act's own example is a pharmacy texting a receipt.
:::

Section 4(1) allows processing for a lawful purpose only with Asha's consent or for “certain legitimate uses”. Consent has limits. Section 6(1) says it must “be limited to such personal data as is necessary for such specified purpose”. The Act's own illustration is a telemedicine app that also asks for the phone's contact list: the consent covers only what the service needs.

A legitimate use needs no consent box. Section 7(a) covers data she “has voluntarily provided” for a specified purpose, while she has not said no.
