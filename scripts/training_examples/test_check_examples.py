"""Tests for the structured-answer checker (option C, evals E1-E15).

Run: python3 -m unittest scripts/training_examples/test_check_examples.py -v
Each test class names the eval in EVALS-structured-answers.md it covers.
"""

import os
import subprocess
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))
import check_examples as c  # noqa: E402

AS_OF = "2026-11-27"

LAW = {
    "act-s2": {"id": "act-s2", "citation": "Section 2", "number": "2",
               "text": "2. In this Act,— (j) “Data Principal” means the individual to whom the personal data relates",
               "in_force": [{"provision": "section 2", "from": "2025-11-13"}]},
    "act-s6": {"id": "act-s6", "citation": "Section 6", "number": "6",
               "text": "6. (1) The consent given by the Data Principal shall be free, specific, informed, unconditional and unambiguous\n"
                       "(9) Every Consent Manager shall be registered with the Board in such manner",
               "in_force": [{"provision": "section 6(1)-(8), (10)", "from": "2027-05-13"},
                            {"provision": "section 6(9)", "from": "2026-11-13"}]},
    "act-s8": {"id": "act-s8", "citation": "Section 8", "number": "8",
               "text": "8. (6) In the event of a personal data breach, the Data Fiduciary shall give the Board and each "
                       "affected Data Principal, intimation of such breach in such form and manner as may be prescribed.",
               "in_force": [{"provision": "section 8", "from": "2027-05-13"}]},
    "act-schedule": {"id": "act-schedule", "citation": "Schedule", "number": None,
                     "text": "1. Breach in observing the obligation to take reasonable security safeguards. "
                             "May extend to two hundred and fifty crore rupees. 2. Breach of any other provision. "
                             "May extend to ten thousand rupees.",
                     "in_force": [{"provision": "Schedule (applied through section 33)", "from": "2027-05-13"}]},
    "rules-r7": {"id": "rules-r7", "citation": "Rule 7", "number": "7",
                 "text": "7. (1) On becoming aware of any personal data breach, the Data Fiduciary shall intimate to the Board\n"
                         "(2) The Data Fiduciary shall also intimate to the Board,—\n"
                         "(b) within seventy-two hours of becoming aware of the breach, or within such longer period as the Board may allow",
                 "in_force": [{"provision": "rule 7", "from": "2027-05-13"}]},
    "rules-r8": {"id": "rules-r8", "citation": "Rule 8", "number": "8",
                 "text": "8. (3) A Data Fiduciary shall retain such personal data and logs for a minimum period of one year",
                 "in_force": [{"provision": "rule 8", "from": "2027-05-13"}]},
    "rules-sch3": {"id": "rules-sch3", "citation": "Third Schedule", "number": None,
                   "text": "Such class of Data Fiduciaries as an e-commerce entity having not less than two crore registered users in India",
                   "in_force": [{"provision": "Third Schedule (applies through rule 8(1))", "from": "2027-05-13"}]},
}
NOTES = {"gsr-843e-2025": {"citation": "G.S.R. 843(E)", "date": "2025-11-13"},
         "gsr-846e-2025": {"citation": "G.S.R. 846(E)", "date": "2025-11-13"}}

Q8 = "the Data Fiduciary shall give the Board and each affected Data Principal, intimation of such breach"
Q7 = "within seventy-two hours of becoming aware of the breach"
QSCH = "May extend to two hundred and fifty crore rupees"
QSCH2 = "Breach of any other provision. May extend to ten thousand rupees"
Q83 = "retain such personal data and logs for a minimum period of one year"
QSC3 = "an e-commerce entity having not less than two crore registered users in India"
Q69 = "Every Consent Manager shall be registered with the Board"
Q61 = "The consent given by the Data Principal shall be free, specific, informed"
Q2 = "means the individual to whom the personal data relates"

CL = {"act-s8": Q8, "rules-r7": Q7, "act-schedule": QSCH, "rules-r8": Q83, "rules-sch3": QSC3, "act-s2": Q2}


def claim(cite, quote=None, **kw):
    d = {"text": "x", "cite": cite, "quote": quote or CL[cite]}
    d.update(kw)
    return d


def ex(template, claims=None, answer=None, **kw):
    """An example whose answer is the rendering of its template (unless answer is given)."""
    claims = [claim("act-s8")] if claims is None else claims
    e = {"id": "E-001", "question": "q", "kind": "who", "reader": "business", "lane": "law_answers",
         "provisions": sorted({x["cite"] for x in claims}), "answer_template": template, "claims": claims}
    if answer is None:
        answer = c.render(c.parse_template(template)[0], LAW)
    e["answer"] = answer
    e.update(kw)
    return e


def run(e, as_of=AS_OF):
    return c.check(e, LAW, as_of=as_of)


GOOD = "From {date:act-s8}, tell the Board and every affected person {ref:act-s8}."


class Base(unittest.TestCase):
    def setUp(self):
        c.KNOWN_NOTIFICATIONS.clear()
        c.KNOWN_NOTIFICATIONS.update(NOTES)

    def ok(self, e, as_of=AS_OF):
        self.assertEqual(run(e, as_of), [], e["answer_template"])

    def bad(self, e, needle=None, as_of=AS_OF):
        errs = run(e, as_of)
        self.assertTrue(errs, e.get("answer_template"))
        if needle:
            self.assertTrue(any(needle in x for x in errs), (needle, errs))


class TestE1Format(Base):
    def test_good_example_passes(self):
        self.ok(ex(GOOD))

    def test_missing_template_fails(self):
        e = ex(GOOD)
        del e["answer_template"]
        self.bad(e, "no answer_template")
        self.bad(ex("   "), "no answer_template")

    def test_answer_must_be_the_rendering(self):
        self.bad(ex(GOOD, answer="From 13 May 2027, tell the Board within 48 hours (Section 8)."), "rendered")
        self.bad(ex(GOOD, answer=""), "rendered")

    def test_rendering(self):
        cases = {
            "{ref:act-s8}": "(Section 8)",
            "{ref:act-s8#6}": "(Section 8(6))",
            "{ref:rules-r7#2(b)}": "(Rule 7(2)(b))",
            "{ref:rules-r8,rules-sch3}": "(Rule 8, Third Schedule)",
            "{ref:act-schedule}": "(The Schedule)",
            "{name:act-s8} applies": "Section 8 applies",
            "under {name:act-schedule}": "under the Schedule",
            "{period:rules-r7|72 hours}": "72 hours",
            "{amount:act-schedule|₹250 crore}": "₹250 crore",
            "{count:rules-sch3|2 crore}": "2 crore",
            "{date:act-s8}": "13 May 2027",
            "{date:act-s6#9}": "13 November 2026",
            "{date:act-s6#1}": "13 May 2027",
            "{notification:gsr-843e-2025}": "G.S.R. 843(E)",
            "{notified:gsr-843e-2025}": "13 November 2025",
        }
        for t, want in cases.items():
            self.assertEqual(c.render(c.parse_template(t)[0], LAW), want, t)


class TestE2Malformed(Base):
    def test_malformed_slots_fail(self):
        for t in ("{foo:act-s8} tell the Board.", "Tell the Board {ref:}.", "Tell the Board {ref:Act S8}.",
                  "Tell the Board {ref:act-s8.", "Tell the Board ref:act-s8}.", "Tell {ref:{ref:act-s8}}.",
                  "Report within {period:rules-r7}.", "From {date:act-s8|13 May 2027}, tell the Board.",
                  "Tell the Board {refact-s8}.", "See {notification:gsr-843e-2025#1}.",
                  "Report within {period:rules-r7#2|72 hours}."):
            self.bad(ex(t, answer="x"), None)

    def test_error_names_the_problem(self):
        self.bad(ex("{foo:act-s8} x", answer="x"), "unknown slot type")
        self.bad(ex("Tell the Board {ref:act-s8.", answer="x"), "brace")


class TestE3Digits(Base):
    def test_any_digit_in_prose_fails(self):
        for d in ("72", "７２", "⁴⁸", "४८", "٤٨", "Ⅻ"):
            self.bad(ex(f"From {{date:act-s8}}, report within {d} {{ref:act-s8}}."), "figures may only enter through a slot")


class TestE4Characters(Base):
    def test_characters_outside_the_allowlist_fail(self):
        for ch in ("₹", "$", "%", "§", "​", " ", "е", "द", "/", "&", "*", "\n"):
            self.bad(ex(f"From {{date:act-s8}}, tell the Board{ch}now {{ref:act-s8}}."), "prose has")

    def test_allowed_punctuation_passes(self):
        self.ok(ex("From {date:act-s8}: tell the Board’s “team” — fast; why? now! (yes) - ‘ok’ – \"fine\" {ref:act-s8}."))


PEER_ROUND_3 = [
    "do hafte", "das hours", "chaubis ghanton", "das rupaiye", "pandrah laakh", "fourty-eight hours",
    "sevnty-two hours", "seventytwo hours", "within X days", "Section X", "one lac", "one cr", "one bn",
    "one arab", "one grand", "section one", "sub-rule (ix) of Rule seven", "clause (z) of Rule seven",
]


class TestE5UnitAndReferenceWords(Base):
    def t(self, words):
        return ex(f"From {{date:act-s8}}, tell the Board {words} {{ref:act-s8}}.")

    def test_peer_round_three_inputs_fail(self):
        for w in PEER_ROUND_3:
            self.bad(self.t(w))

    def test_each_word_group_fails(self):
        for w in ("within the hour", "in minutes", "by the fortnight", "each quarter", "per annum", "a decade",
                  "monthly", "in rupees", "Rs", "INR", "paise", "crores", "lakhs", "karod", "hazaar", "millions",
                  "bn", "USD", "euros", "pounds", "percent", "per cent", "per-cent", "the percentage",
                  "the section", "SECTIONS", "the subsection", "as a rule", "the sub-rule", "the clause",
                  "the schedules", "the article", "the regulation", "a chapter", "the paragraph", "para",
                  "the item", "the entries", "Part A", "Part IV", "part (b)", "ghante", "din", "mahine", "saal",
                  "varsh", "baras", "rupaye", "the year's end", "the sub-clause"):
            self.bad(self.t(w), "prose has")

    def test_the_rules_and_ordinary_words_pass(self):
        for w in ("under the Rules", "under the DPDP Rules", "today", "on Monday", "in part", "first",
                  "the second step", "part of the duty"):
            self.ok(self.t(w))


class TestE6Misspellings(Base):
    def test_one_letter_off_fails(self):
        for w in ("hourss", "yeras", "secton", "sectoin", "schedle", "monthss", "minuts", "crorre"):
            self.bad(ex(f"From {{date:act-s8}}, tell the Board within {w} {{ref:act-s8}}."), "one letter away")

    def test_real_words_and_short_words_are_exempt(self):
        for w in ("cause", "causes", "scheduled", "ruled", "sentry", "particles"):
            self.ok(ex(f"From {{date:act-s8}}, tell the Board of the {w} {{ref:act-s8}}."))


class TestE7NumberWords(Base):
    def test_number_words_fail(self):
        for w in ("two", "seventy-two", "seventytwo", "twenty", "a dozen", "half", "twice", "zero",
                  "ek", "das", "pandrah", "chaubis", "dhai", "XLVIII", "hundreds of"):
            self.bad(ex(f"From {{date:act-s8}}, tell the Board {w} times {{ref:act-s8}}."), "prose has")

    def test_one_passes(self):
        self.ok(ex("From {date:act-s8}, this is one of the duties: tell the Board {ref:act-s8}."))


class TestE8FixedNames(Base):
    def test_fixed_names_pass(self):
        for n in ("the DPDP Act", "the DPDP Rules", "the Act", "the Rules", "the Act and Rules",
                  "the Data Protection Board"):
            self.ok(ex(f"From {{date:act-s8}}, {n} says tell the Board {{ref:act-s8}}."))


class TestE9RefSlots(Base):
    def test_unknown_id_fails(self):
        self.bad(ex("From {date:act-s8}, tell the Board {ref:act-s8,act-s99}."), "unknown provision")

    def test_part_must_exist(self):
        self.bad(ex("From {date:act-s8}, tell the Board {ref:act-s8#9}."), "no part")
        self.bad(ex("From {date:rules-r7}, report {ref:rules-r7#2(e)}.", [claim("rules-r7")]), "no part")
        self.bad(ex("Pay up to {amount:act-schedule|₹250 crore} {ref:act-schedule#1}, from {date:act-schedule}.",
                    [claim("act-schedule")]), "no numbered parts")
        self.ok(ex("From {date:rules-r7}, report {ref:rules-r7#2(b)}.", [claim("rules-r7")]))

    def test_a_claim_with_a_quote_must_cite_it(self):
        self.bad(ex("From {date:act-s8}, tell the Board {ref:act-s8} {ref:rules-r7}."), "no claim with a quote cites rules-r7")
        self.bad(ex("Section {name:rules-r7} x"), "no claim")
        broken = claim("rules-r7", quote="within forty-eight hours of becoming aware of the breach")
        self.bad(ex("From {date:act-s8}, tell the Board {ref:act-s8} {ref:rules-r7}.", [claim("act-s8"), broken]),
                 "no claim with a quote cites rules-r7")

    def test_date_slot_needs_a_known_provision(self):
        self.ok(ex("From {date:rules-r7,act-s8}, tell the Board {ref:act-s8} {ref:rules-r7}.", [claim("act-s8"), claim("rules-r7")]))
        self.bad(ex("From {date:act-s8,act-s99}, tell the Board {ref:act-s8}."), "unknown provision")


class TestE10FigureSlots(Base):
    def r7(self, t):
        return ex("From {date:rules-r7}, " + t + " {ref:rules-r7}.", [claim("rules-r7")])

    def sch(self, t, claims=None):
        return ex("From {date:act-schedule}, " + t + " {ref:act-schedule}.", claims or [claim("act-schedule")])

    def test_quoted_figures_pass(self):
        self.ok(self.r7("report within {period:rules-r7|72 hours}"))
        self.ok(self.r7("report within {period:rules-r7|seventy-two hours}"))
        self.ok(self.sch("pay up to {amount:act-schedule|₹250 crore}"))
        self.ok(self.sch("pay up to {amount:act-schedule|₹10,000}", [claim("act-schedule", QSCH2)]))
        self.ok(ex("From {date:rules-r8}, keep logs for {period:rules-r8|one year} {ref:rules-r8}.", [claim("rules-r8")]))
        self.ok(ex("From {date:rules-sch3}, sites with {count:rules-sch3|2 crore} users {ref:rules-sch3}.",
                   [claim("rules-sch3")]))

    def test_unquoted_figures_fail(self):
        self.bad(self.r7("report within {period:rules-r7|48 hours}"), "no quote")
        self.bad(self.r7("report within {period:rules-r7|72 days}"), "no quote")
        self.bad(self.sch("pay up to {amount:act-schedule|₹200 crore}"), "no quote")
        self.bad(self.sch("pay up to {amount:act-schedule|₹50 crore}"), "no quote")
        self.bad(self.sch("pay up to {amount:act-schedule|₹250 lakh}"), "no quote")
        self.bad(ex("From {date:rules-sch3}, sites with {count:rules-sch3|3 crore} users {ref:rules-sch3}.",
                    [claim("rules-sch3")]), "no quote")

    def test_figure_must_come_from_that_provision(self):
        e = ex("From {date:act-s8}, tell the Board within {period:act-s8|72 hours} {ref:act-s8} {ref:rules-r7}.",
               [claim("act-s8"), claim("rules-r7")])
        self.bad(e, "no quote of a claim citing act-s8")

    def test_values_must_parse(self):
        for v in ("72 hrs", "72-hour", "about 72 hours", "₹ 250 crore", "Rs 250 crore", "₹250 crores", "250 crore"):
            self.bad(self.r7(f"report within {{period:rules-r7|{v}}}"))
            self.bad(self.sch(f"pay {{amount:act-schedule|{v}}}"))
        self.bad(self.r7("report within {period:act-s99|72 hours}"), "unknown provision")


class TestE11StartDates(Base):
    def test_pending_provision_needs_a_date_slot(self):
        self.bad(ex("Tell the Board {ref:act-s8}."), "needs a {date:act-s8} slot")

    def test_date_slot_for_another_provision_does_not_count(self):
        e = ex("From {date:rules-r7}, tell the Board {ref:act-s8} {ref:rules-r7}.", [claim("act-s8"), claim("rules-r7")])
        self.bad(e, "needs a {date:act-s8} slot")

    def test_in_force_already_needs_nothing(self):
        self.ok(ex("Tell the Board {ref:act-s8}."), as_of="2027-06-01")
        self.ok(ex("A Data Principal is the person the data is about {ref:act-s2}.", [claim("act-s2")]))

    def test_example_cannot_set_its_own_date(self):
        self.bad(ex("Tell the Board {ref:act-s8}.", as_of="2030-01-01"))

    def test_one_slot_can_date_several_provisions(self):
        e = ex("From {date:act-s8,rules-r7}, tell the Board {ref:act-s8} {ref:rules-r7}.", [claim("act-s8"), claim("rules-r7")])
        self.assertEqual(e["answer"], "From 13 May 2027, tell the Board (Section 8) (Rule 7).")
        self.ok(e)

    def test_several_provisions_in_one_slot_must_share_a_date(self):
        e = ex("Since {date:act-s8,act-s6#9}, tell the Board {ref:act-s8}.", answer="x")
        self.bad(e, "different dates")

    def test_multi_date_provision_needs_the_part(self):
        e = ex("From {date:act-s6}, use one {ref:act-s6}.", [claim("act-s6", Q61)])
        self.bad(e, "more than one start date")
        self.ok(ex("From {date:act-s6#1}, consent must be free {ref:act-s6}.", [claim("act-s6", Q61)]))

    def test_applies_from_names_the_part_in_force(self):
        e = ex("Consent Managers register with the Board, since {date:act-s6#9} {ref:act-s6}.",
               [claim("act-s6", Q69, applies_from="2026-11-13")])
        self.ok(e)
        e = ex("Consent Managers register with the Board {ref:act-s6}.", [claim("act-s6", Q69)])
        self.bad(e, "needs a {date:act-s6} slot")

    def test_applies_from_must_match_the_quoted_part(self):
        e = ex("Consent is free {ref:act-s6}.", [claim("act-s6", Q61, applies_from="2026-11-13")])
        self.bad(e, "applies_from")

    def test_date_slot_part_without_a_start_date_fails(self):
        self.bad(ex("From {date:act-s6#11}, tell {ref:act-s6}.", [claim("act-s6", Q61)]))


class TestE12Notifications(Base):
    def test_unknown_notification_fails(self):
        self.bad(ex("From {date:act-s8}, tell the Board {ref:act-s8} ({notification:gsr-999e-2025})."), "unknown notification")
        self.bad(ex("From {date:act-s8}, tell the Board {ref:act-s8}, notified {notified:gsr-999e-2025}."), "unknown notification")

    def test_known_notification_passes(self):
        self.ok(ex("From {date:act-s8}, tell the Board {ref:act-s8} ({notification:gsr-843e-2025}, {notified:gsr-843e-2025})."))


class TestE13Quotes(Base):
    def q(self, quote):
        return ex(GOOD, [claim("act-s8", quote)])

    def test_quote_rules(self):
        self.bad(self.q("the Data Fiduciary shall inform the Board within seventy two hours"), "not found")
        self.bad(self.q("the Data Fiduciary shall … intimation of such breach"), "elision")
        self.bad(self.q("the Data Fiduciary shall"), "6 words")
        self.bad(self.q(Q8.upper()), "not found")
        self.bad(self.q("he Data Fiduciary shall give the Board and each affected"), "mid-word")
        self.ok(self.q(Q8.replace(" ", "  \n")))

    def test_unknown_cite_fails(self):
        self.bad(ex(GOOD, [claim("act-s8"), {"text": "x", "cite": "act-s99", "quote": Q8}]), "unknown provision")

    def test_number_phrase_may_not_be_cut(self):
        e = ex("From {date:rules-r7}, report within {period:rules-r7|2 hours} {ref:rules-r7}.",
               [claim("rules-r7", "two hours of becoming aware of the breach")])
        self.bad(e)

    def test_claim_text_amount_must_be_in_its_quote(self):
        e = ex("From {date:act-schedule}, pay up to {amount:act-schedule|₹250 crore} {ref:act-schedule}.",
               [claim("act-schedule", text="Up to ₹300 crore.")])
        self.bad(e, "its own quote")


class TestE13LabelsLanes(Base):
    def test_bad_labels_fail(self):
        errs = run(ex(GOOD, kind="whom", reader="lawyer", lane="maybe"))
        self.assertEqual(len([x for x in errs if "label" in x]), 3)

    def test_law_answers_needs_a_claim(self):
        self.bad(ex("Tell the Board.", []), "needs at least one")

    def test_refusal_lanes(self):
        self.bad(ex("Yes, you can.", [], lane="law_silent"), "say plainly")
        self.ok(ex("The DPDP Act and Rules do not set up any certificate.", [], lane="law_silent"))
        self.bad(ex("The DPDP Act does not say so, but you must delete it.", [], lane="law_silent"), "must")
        for a in ("Get legal advice before you use it.", "This needs a lawyer.", "Check your setup with a lawyer.",
                  "A lawyer can check your case.", "I cannot answer outside the law."):
            self.ok(ex(a, [], lane="needs_lawyer"))
        self.bad(ex("It depends on many things.", [], lane="needs_lawyer"))

    def test_refusal_checked_on_the_rendering(self):
        self.bad(ex("It depends {ref:act-s8}, from {date:act-s8}.", lane="needs_lawyer"), "say plainly")

    def test_comparison_needs_quotes(self):
        self.bad(ex("You must report breaches quickly.", [], lane="comparison"))

    def test_invented_and_wrong_names_fail(self):
        for a in ("File a Data Personal Breach Inquiry", "The Data Protection Act requires it",
                  "The Commissioner decides", "The Indian Data Protection Rules require it"):
            self.bad(ex("From {date:act-s8}, " + a + " {ref:act-s8}."), "not in the law text")


class TestAsOf(Base):
    def test_bad_dates_are_refused(self):
        for bad in ("27-11-2026", "2026/11/27", "tomorrow", "2026-13-01", ""):
            with self.assertRaises((SystemExit, ValueError), msg=bad):
                c.check(ex(GOOD), LAW, as_of=bad)

    def test_cli_refuses_bad_date(self):
        res = subprocess.run([sys.executable, c.__file__, "--law", ".", "--as-of", "27-11-2026", "x.jsonl"],
                             capture_output=True, text=True)
        self.assertNotEqual(res.returncode, 0)
        self.assertIn("YYYY-MM-DD", res.stderr + res.stdout)
        self.assertNotIn("Traceback", res.stderr)


# Every wording a reviewer found against the free-text checker (PR #17, rounds 1-3 and F13).
# With citations moved into slots, the wording left in the prose must still fail.
OLD_BYPASSES = [
    "The fine is ₹300 crores", "The fine is Rs. 300 crores", "The fine is ₹5 lakhs", "A 300-crore fine applies",
    "The fine is 10,000 rupees", "The fine is $30 million", "The fine is INR 250 crore", "The fine is 250 crore",
    "Report within 72 hrs", "Report within 72h", "Report within 30 working days", "Report within seven business days",
    "Report within 90 minutes", "Report within a fortnight", "Send the 72-hour report",
    "Tell the Board u/s 8", "Tell the Board under s 8", "Report under r 7", "Tell the Board under §8",
    "Read Section 8 read with 7", "See Sections 8 through 12", "See Sections 8—12", "Tell the Board (Sec. 8)",
    "See the fourth schedule", "See Schedule I", "See the schedules",
    "It was uploaded on 14 November", "The Act has 44 sections", "It is the 45th section",
    "Under s. 9 you must tell", "Per sec 9 you must tell", "See r. 7 too", "Rule7 applies", "Section 8A applies",
    "Send the 48-hour report", "Report within a week", "A 16-year-old is a child", "Tell the Board (Section 8 (15))",
    "pay four per cent of turnover", "pay 4% of turnover", "pay a crore", "pay one and a half crore",
    "pay a trillion", "report by the fifth day", "report within a dozen days", "report within a couple of days",
    "report within five full calendar days", "report within ⁴⁸ hours", "report within ７２ hours",
    "forty-eight at the latest", "report on day five", "report within two nights", "report within two weekends",
    "report within XLVIII hours", "fines run to tens of millions",
    "pay दो सौ पचास करोड़ रुपये", "report within बहत्तर घंटे", "pay dhai sau karod rupaye",
    "pay pachas hazaar rupaye", "report within bahattar ghante", "report within do din",
    "report within teen mahine", "keep it for ek saal", "pay dedh lakh", "pay sawa crore",
    "report within sevеnty-two hours", "report within s​eventy-two hours", "report within seventy‑two hours",
    "report within 72 hours", "under the DPDP Rules 2025",
]


class TestOldBypassesStillFail(Base):
    def test_each_old_bypass_fails_in_prose(self):
        for w in OLD_BYPASSES:
            self.bad(ex("From {date:rules-r7}, " + w + " {ref:rules-r7}.", [claim("rules-r7")]))


class TestReview1Fake(Base):
    """PR review round 1 of 1b85826: false passes reproduced on the test law."""

    def test_no_part_marker_in_prose(self):
        for t in ("A Data Principal is defined in {name:act-s2}(q) of the Act.",
                  "A Data Principal is defined in {name:act-s2}(zz).",
                  "See cl. (z) of {name:act-s2}.", "See sec of {name:act-s2}.", "See sch {name:act-s2}."):
            self.bad(ex(t, [claim("act-s2")]), "prose has")

    def test_month_names_and_high_ordinals_fail(self):
        for w in ("in January", "on the fourteenth of", "by the thirtieth", "in mid-May", "each September"):
            self.bad(ex(f"From {{date:act-s8}}, tell the Board {w} {{ref:act-s8}}."), "prose has")
        self.ok(ex("May the Board ask? From {date:act-s8}, it may {ref:act-s8}."))
        self.ok(ex("From {date:act-s8}, first, second and third steps follow {ref:act-s8}."))

    def test_amount_needs_rupees_and_count_needs_no_rupees(self):
        self.bad(ex("From {date:rules-sch3}, fines up to {amount:rules-sch3|₹2 crore} {ref:rules-sch3}.",
                    [claim("rules-sch3")]), "no quote")
        self.bad(ex("From {date:act-schedule}, a site with {count:act-schedule|250 crore} users {ref:act-schedule}.",
                    [claim("act-schedule")]), "no quote")

    def test_figure_needs_a_reference_to_its_provision_in_the_sentence(self):
        e = ex("From {date:rules-r7}, tell the Board within {period:rules-r7|72 hours} {ref:act-s2}.",
               [claim("rules-r7"), claim("act-s2")])
        self.bad(e, "same sentence")
        e = ex("From {date:rules-r7}, report within {period:rules-r7|72 hours}. See {name:rules-r7}.", [claim("rules-r7")])
        self.bad(e, "same sentence")

    def test_date_slot_needs_a_cited_or_quoted_provision(self):
        e = ex("The Act does not say. The Board starts work on {date:act-s8}. Ask a lawyer.", [], lane="needs_lawyer")
        self.bad(e, "not cited")
        named = {"text": "x", "cite": "rules-r1", "quote": "Rules 3, 5 to 16, 22 and 23 shall come into force"}
        law = dict(LAW, **{"rules-r1": {"id": "rules-r1", "citation": "Rule 1", "number": "1",
                                        "text": "1. (4) Rules 3, 5 to 16, 22 and 23 shall come into force eighteen months after",
                                        "in_force": [{"provision": "rule 1", "from": "2025-11-13"}]},
                           "rules-r9": {"id": "rules-r9", "citation": "Rule 9", "number": "9", "text": "9. x",
                                        "in_force": [{"provision": "rule 9", "from": "2027-05-13"}]},
                           "rules-r4": {"id": "rules-r4", "citation": "Rule 4", "number": "4", "text": "4. x",
                                        "in_force": [{"provision": "rule 4", "from": "2026-11-13"}]}})
        good = {"id": "X", "question": "q", "kind": "when", "reader": "business", "lane": "law_answers",
                "answer_template": "Most Rules start on {date:rules-r9} {ref:rules-r1}.",
                "answer": "Most Rules start on 13 May 2027 (Rule 1).", "claims": [named]}
        self.assertEqual(c.check(good, law, as_of=AS_OF), [])
        good["answer_template"], good["answer"] = "Some start on {date:rules-r4} {ref:rules-r1}.", "Some start on 13 November 2026 (Rule 1)."
        self.assertTrue(any("not cited" in x for x in c.check(good, law, as_of=AS_OF)))

    def test_prose_leaks(self):
        for w in ("in Part-A", "in Part one", "in Part (b)", "a twelvemonth", "one la-kh", "seventy-two-hours",
                  "within seventytwohours", "a tenyear wait"):
            self.bad(ex(f"From {{date:act-s8}}, tell the Board {w} {{ref:act-s8}}."), "prose has")
        self.ok(ex("From {date:act-s8}, consent is in part a matter of design {ref:act-s8}."))
        for w in ("annul", "scheduler"):
            self.ok(ex(f"From {{date:act-s8}}, the Board may {w} it {{ref:act-s8}}."))

    def test_figure_values_must_be_canonical(self):
        for v in ("₹2,50 crore", "₹25,0 crore", "₹2,500,000"):
            self.bad(ex("From {date:act-schedule}, pay {amount:act-schedule|" + v + "} {ref:act-schedule}.",
                        [claim("act-schedule")]), "house form")
        for v in ("seventy and two hours", "Seventy-Two hours", "seventy two hours", "seventytwo hours",
                  "two-seventy hours", "72 hour", "one years"):
            self.bad(ex("From {date:rules-r7}, report within {period:rules-r7|" + v + "} {ref:rules-r7}.",
                        [claim("rules-r7")]), "house form")
        self.ok(ex("From {date:act-schedule}, pay {amount:act-schedule|₹10,000} {ref:act-schedule}.",
                   [claim("act-schedule", QSCH2)]))

    def test_value_slots_take_no_part(self):
        self.bad(ex("Report within {period:rules-r7#2|72 hours}.", answer="x"), "takes no part")

    def test_quote_may_not_start_or_end_inside_a_number(self):
        start = claim("act-schedule", "fifty crore rupees. 2. Breach of any other provision")
        self.bad(ex("From {date:act-schedule}, pay up to {amount:act-schedule|₹50 crore} {ref:act-schedule}.", [start]),
                 "mid-word")
        end = claim("act-schedule", "reasonable security safeguards. May extend to two")
        self.bad(ex("From {date:act-schedule}, keep safeguards {ref:act-schedule}.", [end]), "mid-word")


REAL_LAW_DIR = "/Users/sahudilip/Desktop/Product Dev/DPDPD Knowldge Infra/staging/law-import"


@unittest.skipUnless(os.path.isdir(REAL_LAW_DIR), "needs the law-import folder")
class TestRealLaw(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.law = c.load_law(REAL_LAW_DIR)

    def date(self, ident, part=None):
        return c._date_for(self.law[ident], part)[0]

    def test_start_dates_by_part(self):
        self.assertEqual(self.date("act-s6", "9"), "2026-11-13")
        self.assertEqual(self.date("act-s6", "1"), "2027-05-13")
        self.assertEqual(self.date("act-s6", "10"), "2027-05-13")
        self.assertIsNone(self.date("act-s6"))
        self.assertEqual(self.date("act-s27", "1(d)"), "2026-11-13")
        self.assertEqual(self.date("act-s27", "2"), "2027-05-13")
        self.assertIsNone(self.date("act-s27", "1"))
        self.assertEqual(self.date("act-s44", "2"), "2027-05-13")
        self.assertEqual(self.date("act-s44", "3"), "2025-11-13")
        self.assertEqual(self.date("act-s8"), "2027-05-13")
        self.assertEqual(self.date("act-schedule"), "2027-05-13")

    def test_parts_follow_the_structure(self):
        def has(ident, part):
            kind = "rule" if ident.startswith("rules-r") else "section"
            rec = self.law[ident]
            return c._part_text(rec, f"{kind} {rec['number']}" + "".join(f"({x})" for x in c._part_labels(part))) is not None
        for part in ("2(b)(i)", "2(b)(vi)", "2(b)", "1(e)", "2"):
            self.assertTrue(has("rules-r7", part), part)
        for part in ("2(i)", "2(vi)", "1(i)", "2(f)", "3"):
            self.assertFalse(has("rules-r7", part), part)
        for part in ("j(i)", "j(ii)", "f", "i", "k"):
            self.assertTrue(has("act-s2", part), part)
        self.assertFalse(has("act-s2", "zz"))
        self.assertIn("Data Fiduciary", c._part_text(self.law["act-s2"], "section 2(i)"))

    def test_rules_notification_is_known(self):
        self.assertIn("gsr-846e-2025", c.KNOWN_NOTIFICATIONS)
        self.assertIn("gsr-843e-2025", c.KNOWN_NOTIFICATIONS)

    def test_real_example(self):
        e = {"id": "Q-00022", "question": "q", "kind": "when", "reader": "business", "lane": "law_answers",
             "answer_template": "From {date:rules-r7}: send the full report within {period:rules-r7|72 hours} "
                                "of finding out {ref:rules-r7}.",
             "answer": "From 13 May 2027: send the full report within 72 hours of finding out (Rule 7).",
             "claims": [{"text": "x", "cite": "rules-r7",
                         "quote": "within seventy-two hours of becoming aware of the breach, or within such longer period as the Board may allow"}]}
        self.assertEqual(c.check(e, self.law, as_of=AS_OF), [])


if __name__ == "__main__":
    unittest.main()
