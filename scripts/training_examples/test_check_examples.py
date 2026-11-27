"""Checks for the training-example quote checker (training guide step 2).

Run: python3 -m unittest scripts/training_examples/test_check_examples.py -v
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))
import check_examples as c  # noqa: E402

LAW = {
    "act-s8": {"id": "act-s8", "citation": "Section 8", "number": "8",
               "text": "(6) In the event of a personal data breach, the Data Fiduciary shall give the Board and each affected Data Principal, intimation of such breach in such form and manner as may be prescribed."},
    "act-sch": {"id": "act-sch", "citation": "The Schedule", "number": "",
                "text": "Breach in observing the obligation to take reasonable security safeguards to prevent personal data breach under sub-section (5) of section 8. May extend to two hundred and fifty crore rupees."},
}
GOOD_QUOTE = "the Data Fiduciary shall give the Board and each affected Data Principal, intimation of such breach"


def ex(**kw):
    base = {
        "id": "E-001", "question": "Who do we tell after a breach?", "kind": "who",
        "reader": "business", "lane": "law_answers", "provisions": ["act-s8"],
        "answer": "Tell the Board and every affected person (Section 8).",
        "claims": [{"text": "Tell the Board and every affected person.", "cite": "act-s8", "quote": GOOD_QUOTE}],
    }
    base.update(kw)
    return base


class TestQuotes(unittest.TestCase):
    def test_good_example_passes(self):
        self.assertEqual(c.check(ex(), LAW), [])

    def test_quote_not_in_text_fails(self):
        bad = ex(claims=[{"text": "x", "cite": "act-s8", "quote": "the Data Fiduciary shall inform the Board within seventy two hours"}])
        self.assertTrue(any("not found" in e for e in c.check(bad, LAW)))

    def test_elision_fails(self):
        bad = ex(claims=[{"text": "x", "cite": "act-s8", "quote": "the Data Fiduciary shall … intimation of such breach"}])
        self.assertTrue(any("elision" in e for e in c.check(bad, LAW)))

    def test_short_quote_fails(self):
        bad = ex(claims=[{"text": "x", "cite": "act-s8", "quote": "the Data Fiduciary shall"}])
        self.assertTrue(any("6 words" in e for e in c.check(bad, LAW)))

    def test_case_must_match(self):
        bad = ex(claims=[{"text": "x", "cite": "act-s8", "quote": GOOD_QUOTE.upper()}])
        self.assertTrue(any("not found" in e for e in c.check(bad, LAW)))

    def test_whitespace_is_normalised(self):
        ok = ex(claims=[{"text": "x", "cite": "act-s8", "quote": GOOD_QUOTE.replace(" ", "  \n")}])
        self.assertEqual(c.check(ok, LAW), [])

    def test_unknown_cite_fails(self):
        bad = ex(claims=[{"text": "x", "cite": "act-s99", "quote": GOOD_QUOTE}])
        self.assertTrue(any("unknown provision" in e for e in c.check(bad, LAW)))


class TestAnswerText(unittest.TestCase):
    def test_section_not_cited_fails(self):
        bad = ex(answer="Tell the Board (Section 8). Section 33 sets the fine.")
        self.assertTrue(any("section 33" in e for e in c.check(bad, LAW)))

    def test_rule_not_cited_fails(self):
        bad = ex(answer="Tell the Board within 72 hours under Rule 7.")
        self.assertTrue(any("rule 7" in e for e in c.check(bad, LAW)))

    def test_amount_must_be_in_a_quote(self):
        bad = ex(answer="Tell the Board (Section 8). The fine can reach ₹300 crore.")
        self.assertTrue(any("300" in e for e in c.check(bad, LAW)))

    def test_amount_backed_by_quote_passes(self):
        ok = ex(provisions=["act-s8", "act-sch"], answer="The cap is ₹250 crore (The Schedule).",
                claims=[{"text": "The cap is ₹250 crore.", "cite": "act-sch",
                         "quote": "May extend to two hundred and fifty crore rupees"}])
        self.assertEqual(c.check(ok, LAW), [])

    def test_invented_term_fails(self):
        bad = ex(answer="File a Data Personal Breach Inquiry with the Board (Section 8).")
        self.assertTrue(any("Data Personal Breach Inquiry" in e for e in c.check(bad, LAW)))


class TestRealLawShapes(unittest.TestCase):
    def test_numeric_number_field(self):
        law = {k: dict(v) for k, v in LAW.items()}
        law["act-s8"]["number"] = 8
        self.assertEqual(c.check(ex(), law), [])

    def test_plural_of_a_law_term_is_fine(self):
        law = {k: dict(v) for k, v in LAW.items()}
        law["act-s8"]["text"] += " Significant Data Fiduciary"
        ok = ex(answer="Significant Data Fiduciaries have more duties (Section 8).")
        self.assertEqual(c.check(ok, law), [])


class TestInForce(unittest.TestCase):
    def law(self):
        law = {k: dict(v) for k, v in LAW.items()}
        law["act-s8"]["in_force"] = [{"provision": "section 8", "from": "2027-05-13"}]
        return law

    def test_duty_not_yet_in_force_must_give_its_date(self):
        errs = c.check(ex(), self.law(), as_of="2026-11-27")
        self.assertTrue(any("13 May 2027" in e for e in errs))

    def test_date_in_answer_passes(self):
        ok = ex(answer="From 13 May 2027, tell the Board and every affected person (Section 8).")
        self.assertEqual(c.check(ok, self.law(), as_of="2026-11-27"), [])

    def test_in_force_already_needs_nothing(self):
        self.assertEqual(c.check(ex(), self.law(), as_of="2027-06-01"), [])

    def test_in_force_as_string_is_read(self):
        law = self.law()
        law["act-s8"]["in_force"] = "[{'provision': 'section 8', 'from': '2027-05-13'}]"
        self.assertTrue(c.check(ex(), law, as_of="2026-11-27"))


class TestLanes(unittest.TestCase):
    def test_law_answers_needs_a_claim(self):
        bad = ex(claims=[])
        self.assertTrue(any("needs at least one" in e for e in c.check(bad, LAW)))

    def test_refusal_lanes_need_a_reason(self):
        bad = ex(lane="law_silent", claims=[], provisions=[], answer="Yes, you can.")
        self.assertTrue(any("say plainly" in e for e in c.check(bad, LAW)))
        ok = ex(lane="law_silent", claims=[], provisions=[],
                answer="The DPDP Act and Rules do not set up any certificate.")
        self.assertEqual(c.check(ok, LAW), [])

    def test_bad_labels_fail(self):
        bad = ex(kind="whom", reader="lawyer", lane="maybe")
        errs = c.check(bad, LAW)
        self.assertEqual(len([e for e in errs if "label" in e]), 3)


if __name__ == "__main__":
    unittest.main()


# ---- Round 2: bypasses found by the code review of 1a65df0 ----
SCH_QUOTE_250 = "May extend to two hundred and fifty crore rupees"


def law_with_dates():
    law = {k: dict(v) for k, v in LAW.items()}
    law["act-s8"]["in_force"] = [{"provision": "section 8", "from": "2027-05-13"}]
    law["act-s6"] = {"id": "act-s6", "citation": "Section 6", "number": "6",
                     "text": "(9) Every Consent Manager shall be registered with the Board in such manner",
                     "in_force": [{"provision": "6(1)-(8)", "from": "2027-05-13"},
                                  {"provision": "section 6(9)", "from": "2026-11-13"}]}
    law["rules-r7"] = {"id": "rules-r7", "citation": "Rule 7", "number": "7",
                       "text": "(2)(b) within seventy-two hours of becoming aware of the breach, or within such longer period",
                       "in_force": [{"provision": "rule 7", "from": "2027-05-13"}]}
    return law


class TestRefBypasses(unittest.TestCase):
    def test_short_forms_and_plurals(self):
        for a in ("Under s. 9 you must tell.", "Per sec 9 you must tell.", "Sections 8 and 9 apply.",
                  "See r. 7 too.", "Rule7 applies.", "Section 8A applies.", "Rules 3, 5 to 16 apply."):
            errs = c.check(ex(answer=a), LAW, as_of="2030-01-01")
            self.assertTrue(errs, a)

    def test_subsection_must_exist_in_cited_text(self):
        errs = c.check(ex(answer="Tell the Board (Section 8(9))."), LAW, as_of="2030-01-01")
        self.assertTrue(any("8(9)" in e for e in errs))
        self.assertEqual(c.check(ex(answer="Tell the Board (Section 8(6))."), LAW, as_of="2030-01-01"), [])

    def test_gazette_numbers_are_not_rules(self):
        self.assertEqual(c.check(ex(answer="Tell the Board (Section 8, G.S.R. 843(E))."), LAW, as_of="2030-01-01"), [])

    def test_schedule_mentions_need_a_cite(self):
        errs = c.check(ex(answer="See the Fourth Schedule (Section 8)."), LAW, as_of="2030-01-01")
        self.assertTrue(any("Fourth Schedule" in e for e in errs))


class TestAmountBypasses(unittest.TestCase):
    def amt(self, answer, quote=SCH_QUOTE_250, text=None):
        return ex(provisions=["act-sch"], answer=answer,
                  claims=[{"text": text or answer, "cite": "act-sch", "quote": quote}])

    def test_rs_inr_and_bare(self):
        for a in ("The cap is Rs 500 crore.", "The cap is INR 500 crore.", "The cap is 500 crore."):
            self.assertTrue(c.check(self.amt(a), LAW, as_of="2030-01-01"), a)

    def test_fifty_inside_two_hundred_and_fifty_is_not_fifty(self):
        self.assertTrue(c.check(self.amt("The cap is ₹50 crore."), LAW, as_of="2030-01-01"))
        self.assertTrue(c.check(self.amt("The cap is ₹200 crore."), LAW, as_of="2030-01-01"))
        self.assertEqual(c.check(self.amt("The cap is ₹250 crore."), LAW, as_of="2030-01-01"), [])

    def test_unit_matters(self):
        self.assertTrue(c.check(self.amt("The cap is ₹250 lakh."), LAW, as_of="2030-01-01"))

    def test_amount_must_come_from_its_own_claim(self):
        e = ex(provisions=["act-s8", "act-sch"],
               answer="Not telling the Board costs up to ₹250 crore (Section 8).",
               claims=[{"text": "Tell the Board.", "cite": "act-s8", "quote": GOOD_QUOTE},
                       {"text": "Not telling the Board costs up to ₹200 crore.", "cite": "act-sch", "quote": SCH_QUOTE_250}])
        self.assertTrue(c.check(e, LAW, as_of="2030-01-01"))


class TestTimeLimits(unittest.TestCase):
    def test_time_limit_must_be_in_a_quote(self):
        law = law_with_dates()
        base = dict(provisions=["rules-r7"], claims=[{"text": "x", "cite": "rules-r7",
                    "quote": "within seventy-two hours of becoming aware of the breach"}])
        ok = ex(answer="From 13 May 2027, report within 72 hours (Rule 7).", **base)
        bad = ex(answer="From 13 May 2027, report within 7 days (Rule 7).", **base)
        self.assertEqual(c.check(ok, law, as_of="2026-11-27"), [])
        self.assertTrue(any("7 days" in e for e in c.check(bad, law, as_of="2026-11-27")))


class TestInForceBypasses(unittest.TestCase):
    def test_example_cannot_set_its_own_date(self):
        e = ex(as_of="2030-01-01")
        self.assertTrue(c.check(e, law_with_dates(), as_of="2026-11-27"))

    def test_a_past_date_does_not_cover_a_pending_one(self):
        e = ex(provisions=["act-s6"], answer="Consent rules started on 13 November 2026 (Section 6).",
               claims=[{"text": "x", "cite": "act-s6", "quote": "Every Consent Manager shall be registered with the Board"}])
        self.assertTrue(any("13 May 2027" in x for x in c.check(e, law_with_dates(), as_of="2026-11-27")))

    def test_claim_can_name_the_part_already_in_force(self):
        e = ex(provisions=["act-s6"], answer="Consent Managers register with the Board, since 13 November 2026 (Section 6).",
               claims=[{"text": "x", "cite": "act-s6", "applies_from": "2026-11-13",
                        "quote": "Every Consent Manager shall be registered with the Board"}])
        self.assertEqual(c.check(e, law_with_dates(), as_of="2026-11-27"), [])

    def test_applies_from_must_be_a_real_date_of_that_provision(self):
        e = ex(provisions=["act-s6"], answer="Since 1 January 2020 (Section 6).",
               claims=[{"text": "x", "cite": "act-s6", "applies_from": "2020-01-01",
                        "quote": "Every Consent Manager shall be registered with the Board"}])
        self.assertTrue(any("applies_from" in x for x in c.check(e, law_with_dates(), as_of="2026-11-27")))


class TestRefusalAndTerms(unittest.TestCase):
    def test_refusal_needs_a_real_refusal_phrase(self):
        e = ex(lane="law_silent", claims=[], provisions=[], answer="This is not hard: delete data in 30 days.")
        self.assertTrue(c.check(e, LAW, as_of="2030-01-01"))

    def test_refusal_stating_a_duty_needs_a_quote(self):
        e = ex(lane="law_silent", claims=[], provisions=[],
               answer="The DPDP Act does not say so, but you must delete data in a month.")
        self.assertTrue(any("must" in x for x in c.check(e, LAW, as_of="2030-01-01")))

    def test_comparison_needs_quotes(self):
        e = ex(lane="comparison", claims=[], provisions=[], answer="You must report breaches quickly.")
        self.assertTrue(c.check(e, LAW, as_of="2030-01-01"))

    def test_known_wrong_names(self):
        for a in ("The Data Protection Act requires it (Section 8).",
                  "The Indian Data Protection Rules require it (Section 8).",
                  "The Commissioner decides (Section 8)."):
            self.assertTrue(c.check(ex(answer=a), LAW, as_of="2030-01-01"), a)


# ---- Round 3: holes left after 3b5e5f3 ----
class TestRound3(unittest.TestCase):
    def law44(self):
        law = law_with_dates()
        law["act-s44"] = {"id": "act-s44", "citation": "Section 44", "number": "44",
                          "text": "44. (1) Section 43A of the said Act shall be omitted from the date notified.\n"
                                  "(2) In section 8 of the Right to Information Act, clause (j) shall be substituted by this text.",
                          "in_force": [{"provision": "section 44(1)", "from": "2025-11-13"},
                                       {"provision": "section 44(2)", "from": "2027-05-13"}]}
        return law

    def test_applies_from_must_match_the_part_the_quote_is_in(self):
        bad = ex(provisions=["act-s44"], answer="Since 13 November 2025 (Section 44).",
                 claims=[{"text": "x", "cite": "act-s44", "applies_from": "2025-11-13",
                          "quote": "In section 8 of the Right to Information Act, clause (j)"}])
        self.assertTrue(any("applies_from" in e for e in c.check(bad, self.law44(), as_of="2026-11-27")))
        ok = ex(provisions=["act-s44"], answer="Since 13 November 2025 (Section 44).",
                claims=[{"text": "x", "cite": "act-s44", "applies_from": "2025-11-13",
                         "quote": "Section 43A of the said Act shall be omitted"}])
        self.assertEqual(c.check(ok, self.law44(), as_of="2026-11-27"), [])

    def test_hyphenated_and_article_time_limits(self):
        law = law_with_dates()
        base = dict(provisions=["rules-r7"], claims=[{"text": "x", "cite": "rules-r7",
                    "quote": "within seventy-two hours of becoming aware of the breach"}])
        # Fail-closed design: "72-hour" is not a house form, so it fails even when 72 is quoted.
        self.assertTrue(c.check(ex(answer="Send the 72-hour report (Rule 7).", **base), law, as_of="2030-01-01"))
        self.assertEqual(c.check(ex(answer="Send the report within 72 hours (Rule 7).", **base), law, as_of="2030-01-01"), [])
        self.assertTrue(c.check(ex(answer="Send the 48-hour report (Rule 7).", **base), law, as_of="2030-01-01"))
        self.assertTrue(c.check(ex(answer="Report within a week (Rule 7).", **base), law, as_of="2030-01-01"))
        self.assertTrue(c.check(ex(answer="A 16-year-old is a child (Rule 7).", **base), law, as_of="2030-01-01"))

    def test_space_before_subsection(self):
        self.assertTrue(c.check(ex(answer="Tell the Board (Section 8 (15))."), LAW, as_of="2030-01-01"))


class TestRefusalPhrases(unittest.TestCase):
    def test_common_lawyer_phrasings_count(self):
        for a in ("Get legal advice before you use it.", "This needs a lawyer.",
                  "Check your setup with a lawyer.", "Check the records with a lawyer or your CA.",
                  "A lawyer can check your case."):
            e = ex(lane="needs_lawyer", claims=[], provisions=[], answer=a)
            self.assertEqual(c.check(e, LAW, as_of="2030-01-01"), [], a)

    def test_vague_text_still_fails(self):
        e = ex(lane="needs_lawyer", claims=[], provisions=[], answer="It depends on many things.")
        self.assertTrue(c.check(e, LAW, as_of="2030-01-01"))


class TestAsOfValidation(unittest.TestCase):
    def test_bad_dates_are_refused(self):
        for bad in ("27-11-2026", "2026/11/27", "tomorrow", "2026-13-01", ""):
            with self.assertRaises((SystemExit, ValueError), msg=bad):
                c.check(ex(), LAW, as_of=bad)

    def test_cli_refuses_bad_date(self):
        import subprocess
        res = subprocess.run([sys.executable, c.__file__, "--law", ".", "--as-of", "27-11-2026", "x.jsonl"],
                             capture_output=True, text=True)
        self.assertNotEqual(res.returncode, 0)
        self.assertIn("YYYY-MM-DD", res.stderr + res.stdout)


# ---- Fail-closed design (Dilip approved 2026-11-27) ----
# Every wording a reviewer found must fail; every house-style form must pass. Narrowing the
# canonical patterns breaks TestHouseStylePasses; widening the residual check breaks
# TestEveryBypassFails. Both are the mutation guard the PR #17 review asked for.
LAW_FC = {k: dict(v) for k, v in LAW.items()}
LAW_FC["rules-r7"] = {"id": "rules-r7", "citation": "Rule 7", "number": "7",
                      "text": "(2) (b) within seventy-two hours of becoming aware of the breach, or within such longer period"}
LAW_FC["act-schedule"] = LAW_FC.pop("act-sch")
LAW_FC["act-schedule"]["id"] = "act-schedule"
LAW_FC["act-s8"]["in_force"] = [{"provision": "section 8", "from": "2027-05-13"}]
R7 = {"text": "x", "cite": "rules-r7", "quote": "within seventy-two hours of becoming aware of the breach"}
S8 = {"text": "x", "cite": "act-s8", "quote": GOOD_QUOTE}
SCH = {"text": "Up to ₹250 crore.", "cite": "act-schedule", "quote": "May extend to two hundred and fifty crore rupees"}


def fc(answer, claims=None):
    claims = claims or [S8, R7, SCH]
    return ex(answer=answer, claims=claims, provisions=sorted({x["cite"] for x in claims}))


class TestEveryBypassFails(unittest.TestCase):
    BYPASSES = [
        # amounts
        "The fine is ₹300 crores (Section 8).", "The fine is Rs. 300 crores (Section 8).",
        "The fine is ₹5 lakhs (Section 8).", "A 300-crore fine applies (Section 8).",
        "The fine is 10,000 rupees (Section 8).", "The fine is $30 million (Section 8).",
        "The fine is INR 250 crore (Section 8).", "The fine is 250 crore (Section 8).",
        # time limits
        "Report within 72 hrs (Rule 7).", "Report within 72h (Rule 7).",
        "Report within 30 working days (Rule 7).", "Report within seven business days (Rule 7).",
        "Report within 90 minutes (Rule 7).", "Report within a fortnight (Rule 7).",
        "Send the 72-hour report (Rule 7).",
        # references
        "Tell the Board u/s 8.", "Tell the Board under s 8.", "Report under r 7 (Section 8).",
        "Tell the Board under §8.", "Read Section 8 read with 7.", "See Sections 8 through 12.",
        "See Sections 8—12.", "See Sections 8–12.", "Tell the Board (Sec. 8).",
        # schedules
        "See the fourth schedule (Section 8).", "See Schedule I (Section 8).",
        "See the schedules (Section 8).",
        # stray numbers and partial dates
        "It was uploaded on 14 November (Section 8).", "The Act has 44 sections (Section 8).",
        "It is the 45th section (Section 8).",
    ]

    def test_each_bypass_fails(self):
        for a in self.BYPASSES:
            self.assertTrue(c.check(fc(a), LAW_FC, as_of="2030-01-01"), a)


class TestHouseStylePasses(unittest.TestCase):
    GOOD = [
        "Tell the Board and every affected person (Section 8).",
        "Tell the Board (Section 8(6)).",
        "The full report is due within 72 hours (Rule 7).",
        "The full report is due within seventy-two hours (Rule 7).",
        "The cap is ₹250 crore (The Schedule).",
        "The cap is ₹250 crore, for failing safeguards (The Schedule).",
        "From 13 May 2027, tell the Board (Section 8).",
        "Most duties start on 13 May 2027 (G.S.R. 843(E)).",
        "Read it in any language in the Eighth Schedule to the Constitution (Section 8).",
        "Tell the Board in one place, as one of the steps, with a government ID (Section 8).",
    ]

    def test_each_form_passes(self):
        c.KNOWN_NOTIFICATIONS["G.S.R. 843(E)"] = "2025-11-13"
        for a in self.GOOD:
            self.assertEqual(c.check(fc(a), LAW_FC, as_of="2030-01-01"), [], a)


class TestQuoteBoundaries(unittest.TestCase):
    def test_quote_must_start_and_end_on_word_boundaries(self):
        mid = {"text": "x", "cite": "act-s8", "quote": "he Data Fiduciary shall give the Board and each affected"}
        self.assertTrue(any("word" in e for e in c.check(fc("Tell the Board (Section 8).", [mid]), LAW_FC, as_of="2030-01-01")))
        end = {"text": "x", "cite": "act-s8", "quote": "the Data Fiduciary shall give the Board and each affec"}
        self.assertTrue(any("word" in e for e in c.check(fc("Tell the Board (Section 8).", [end]), LAW_FC, as_of="2030-01-01")))


# ---- Fail-closed round 2: false passes found by the review of 2b542ff ----
REAL_LAW_DIR = "/Users/sahudilip/Desktop/Product Dev/DPDPD Knowldge Infra/staging/law-import"


@unittest.skipUnless(os.path.isdir(REAL_LAW_DIR), "needs the law-import folder")
class TestRealLawFalsePasses(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.law = c.load_law(REAL_LAW_DIR)

    def r7(self, answer, quote="within seventy-two hours of becoming aware of the breach", extra=None):
        claims = [{"text": "x", "cite": "rules-r7", "quote": quote}] + (extra or [])
        return ex(answer="From 13 May 2027, " + answer, claims=claims,
                  provisions=sorted({x["cite"] for x in claims}))

    def bad(self, e):
        self.assertTrue(c.check(e, self.law, as_of="2026-11-27"), e["answer"])

    def good(self, e):
        self.assertEqual(c.check(e, self.law, as_of="2026-11-27"), [], e["answer"])

    def test_quote_cut_inside_hyphenated_number(self):
        self.bad(self.r7("report within 2 hours (Rule 7).", quote="two hours of becoming aware of the breach"))

    def test_quote_keeping_only_the_tail_of_a_number(self):
        sch = {"text": "Up to ₹50 crore.", "cite": "act-schedule",
               "quote": "fifty crore rupees. 2. Breach in observing the obligation"}
        self.bad(self.r7("security failures cost up to ₹50 crore (The Schedule) (Rule 7).", extra=[sch]))

    def test_dates_must_be_real_start_or_gazette_dates(self):
        self.bad(self.r7("the Board has enforced it since 1 January 2024 (Rule 7)."))
        self.bad(ex(answer="These Rules came into force on 13 November 2024 (Rule 1).",
                    claims=[{"text": "x", "cite": "rules-r1",
                             "quote": "Rules 1, 2 and 17 to 21 shall come into force on the date of their publication"}],
                    provisions=["rules-r1"]))
        self.good(ex(answer="These Rules came into force on 13 November 2025 (Rule 1).",
                     claims=[{"text": "x", "cite": "rules-r1",
                              "quote": "Rules 1, 2 and 17 to 21 shall come into force on the date of their publication"}],
                     provisions=["rules-r1"]))

    def test_unknown_notification_number_fails(self):
        self.bad(self.r7("report within 72 hours (Rule 7, G.S.R. 999(E))."))
        self.good(self.r7("report within 72 hours (Rule 7, G.S.R. 846(E))."))

    def test_number_words_and_symbols(self):
        for a in ("pay four per cent of turnover (Rule 7).", "pay 4% of turnover (Rule 7).",
                  "pay a crore (Rule 7).", "pay one and a half crore (Rule 7).", "pay a trillion (Rule 7).",
                  "report by the fifth day (Rule 7).", "report within a dozen days (Rule 7).",
                  "report within a couple of days (Rule 7).", "report within five full calendar days (Rule 7).",
                  "report within ⁴⁸ hours (Rule 7).", "report within ７２ hours (Rule 7)."):
            self.bad(self.r7(a))

    def test_clause_must_be_in_the_named_subsection(self):
        self.bad(self.r7("report the contact person (Rule 7(2)(e))."))
        self.good(self.r7("report within 72 hours (Rule 7(2)(b))."))

    def test_house_text_still_passes(self):
        self.good(self.r7("report within 72 hours (Rule 7)."))


@unittest.skipUnless(os.path.isdir(REAL_LAW_DIR), "needs the law-import folder")
class TestRound3NumberWords(TestRealLawFalsePasses):
    def test_leftover_number_words_fail(self):
        for a in ("report within 72 hours (Rule 7), or forty-eight at the latest.",
                  "report on day five (Rule 7).", "report within two nights (Rule 7).",
                  "report within two weekends (Rule 7).", "report within XLVIII hours (Rule 7).",
                  "fines run to tens of millions (Rule 7)."):
            self.bad(self.r7(a))

    def test_one_and_articles_still_pass(self):
        self.good(self.r7("report within 72 hours; this is one of the duties (Rule 7)."))
