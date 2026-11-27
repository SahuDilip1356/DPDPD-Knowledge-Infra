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
                       "text": "(2)(b) within seventy-two hours of becoming aware of the breach, or within such longer period"}
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
        self.assertEqual(c.check(ex(answer="Send the 72-hour report (Rule 7).", **base), law, as_of="2030-01-01"), [])
        self.assertTrue(c.check(ex(answer="Send the 48-hour report (Rule 7).", **base), law, as_of="2030-01-01"))
        self.assertTrue(c.check(ex(answer="Report within a week (Rule 7).", **base), law, as_of="2030-01-01"))
        self.assertEqual(c.check(ex(answer="A 16-year-old is a child (Rule 7).", **base), law, as_of="2030-01-01"), [])

    def test_space_before_subsection(self):
        self.assertTrue(c.check(ex(answer="Tell the Board (Section 8 (15))."), LAW, as_of="2030-01-01"))
