"""Tests for the v2-to-template converter (E14).

Run: python3 -m unittest scripts/training_examples/test_convert_to_template.py -v
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))
import check_examples as c  # noqa: E402
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


if __name__ == "__main__":
    unittest.main()
