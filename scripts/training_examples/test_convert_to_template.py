"""Tests for the v2-to-template converter (E14).

Run: python3 -m unittest scripts/training_examples/test_convert_to_template.py -v
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))
import convert_to_template as conv  # noqa: E402

LAW = {
    "rules-r4": {"id": "rules-r4", "citation": "Rule 4", "number": "4",
                 "text": "4. (1) A person who fulfils the conditions for registration of Consent Managers may apply",
                 "in_force": [{"provision": "rule 4", "from": "2026-11-13"}]},
    "rules-r7": {"id": "rules-r7", "citation": "Rule 7", "number": "7",
                 "text": "7. (2) (b) within seventy-two hours of becoming aware of the breach, or within such longer period",
                 "in_force": [{"provision": "rule 7", "from": "2027-05-13"}]},
}
Q4 = "A person who fulfils the conditions for registration of Consent Managers may apply"
Q7 = "within seventy-two hours of becoming aware of the breach"


def ex(answer):
    return {"id": "X", "answer": answer, "claims": [{"text": "x", "cite": "rules-r4", "quote": Q4},
                                                    {"text": "x", "cite": "rules-r7", "quote": Q7}]}


class TestAttribution(unittest.TestCase):
    def setUp(self):
        conv.LAW.clear()
        conv.LAW.update(LAW)
        conv.FLAGS.clear()

    def test_sentence_naming_a_provision_with_another_date_is_flagged(self):
        conv.convert(ex("Rule 4 and Rule 7 start on 13 November 2026. Report within 72 hours (Rule 7)."))
        self.assertTrue(any("Rule 7" in f or "rules-r7" in f for f in conv.FLAGS), conv.FLAGS)

    def test_clean_sentence_is_not_flagged(self):
        tpl = conv.convert(ex("From 13 May 2027, report within 72 hours (Rule 7). Consent Managers register (Rule 4)."))
        self.assertIn("{date:rules-r7}", tpl)
        self.assertIn("{period:rules-r7|72 hours}", tpl)

    def test_figure_quoted_by_another_provision_is_flagged(self):
        conv.convert(ex("From 13 May 2027, apply within 72 hours (Rule 4)."))
        self.assertTrue(any("72 hours" in f for f in conv.FLAGS), conv.FLAGS)


class TestClaims(unittest.TestCase):
    def setUp(self):
        conv.LAW.clear()
        conv.LAW.update(LAW)
        conv.FLAGS.clear()

    def test_claim_text_becomes_a_template_with_its_own_provision(self):   # E35
        cl = {"text": "Full report within 72 hours (Rule 7).", "cite": "rules-r7", "quote": Q7}
        self.assertEqual(conv.claim_template(cl), "Full report within {period:rules-r7|72 hours} {ref:rules-r7}.")

    def test_invalid_date_is_unresolved_not_a_crash(self):                # E32
        with self.assertRaises(conv.Unresolved):
            conv.claim_template({"text": "From 31 February 2027.", "cite": "rules-r7", "quote": Q7})


class TestRewriteChains(unittest.TestCase):
    def test_a_chain_of_claim_rewrites_reruns_from_the_original(self):
        rw = {"X#claim1": [["Under 18.", "Under eighteen."], ["Under eighteen.", "Under eighteen years."]]}
        e = {"id": "X", "answer": "a", "claims": [{"text": "Under 18.", "cite": "act-s2", "quote": "q"}]}
        conv.apply_rewrites(e, rw)
        self.assertEqual(e["claims"][0]["text"], "Under eighteen years.")
        train, v2 = conv.split_v2([dict(e, answer_v2="a", claims_v2=["Under 18."])])
        self.assertNotIn("claims_v2", train[0])
        rerun = dict(train[0], claims=[dict(cl) for cl in train[0]["claims"]])
        conv.restore_originals(rerun, v2[0])
        conv.apply_rewrites(rerun, rw)
        self.assertEqual(rerun["claims"][0]["text"], "Under eighteen years.")


class TestOutputs(unittest.TestCase):
    def test_rewrites_reach_the_answer_and_named_claims(self):
        e = {"id": "X", "answer": "a rule here", "claims": [{"text": "Rule 4, one year.", "cite": "rules-r1", "quote": "q"}]}
        conv.apply_rewrites(e, {"X": [["a rule", "a requirement"]], "X#claim1": [["Rule 4", "Consent Manager rules"]]})
        self.assertEqual(e["answer"], "a requirement here")
        self.assertEqual(e["claims"][0]["text"], "Consent Manager rules, one year.")
        conv.apply_rewrites(e, {"X#claim1": [["Rule 4", "Consent Manager rules"]]})   # rerun: no-op
        self.assertEqual(e["claims"][0]["text"], "Consent Manager rules, one year.")
        with self.assertRaises(SystemExit):
            conv.apply_rewrites(e, {"X#claim1": [["not there", "x"]]})

    def test_rows_drop_answer_v2_and_v2_goes_to_its_own_file(self):        # E20
        row = {"id": "X", "answer": "a", "answer_v2": "old", "answer_template": "a"}
        train, v2 = conv.split_v2([row])
        self.assertNotIn("answer_v2", train[0])
        self.assertEqual(v2, [{"id": "X", "answer_v2": "old", "claims_v2": []}])

    def test_outputs_go_through_the_safe_writer(self):
        import inspect
        src = inspect.getsource(conv.main)
        self.assertIn("safe_output.write_files", src)
        self.assertNotIn('open(a.out', src)
        self.assertNotIn('open(a.report', src)


if __name__ == "__main__":
    unittest.main()
