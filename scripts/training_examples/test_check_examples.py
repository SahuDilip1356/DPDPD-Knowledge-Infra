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
        self.assertTrue(any("Section 33" in e for e in c.check(bad, LAW)))

    def test_rule_not_cited_fails(self):
        bad = ex(answer="Tell the Board within 72 hours under Rule 7.")
        self.assertTrue(any("Rule 7" in e for e in c.check(bad, LAW)))

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
