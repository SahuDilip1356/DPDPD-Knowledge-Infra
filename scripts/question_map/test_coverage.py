"""Coverage checks for the Setu questionnaire (training guide step 1).

Run: python3 -m unittest scripts/question_map/test_coverage.py -v
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))
import coverage_check as cov  # noqa: E402
import written_questions as wq  # noqa: E402

MAP = os.path.join(os.path.dirname(__file__), "..", "..", "staging", "question-map", "question_map.jsonl")
LAW_DIR = "/Users/sahudilip/Desktop/Product Dev/DPDPD Knowldge Infra/staging/law-import"


class TestWrittenQuestionsAreWellFormed(unittest.TestCase):
    def test_ids_unique_and_labels_valid(self):
        rows = wq.rows()
        ids = [r["id"] for r in rows]
        self.assertEqual(len(ids), len(set(ids)))
        for r in rows:
            self.assertIn(r["kind"], cov.KINDS, r["id"])
            self.assertIn(r["reader"], cov.READERS, r["id"])
            self.assertIn(r["lane"], cov.LANES, r["id"])
            self.assertTrue(r["question"].endswith("?"), r["id"])
            self.assertEqual(r["source"], "written")

    def test_no_duplicate_questions(self):
        seen = set()
        for r in wq.rows():
            k = cov.norm(r["question"])
            self.assertNotIn(k, seen, r["question"])
            seen.add(k)

    def test_law_answers_questions_name_a_provision(self):
        for r in wq.rows():
            if r["lane"] == "law_answers":
                self.assertTrue(r["provisions"], r["id"])


@unittest.skipUnless(os.path.isdir(LAW_DIR), "needs the law-import folder")
class TestCoverageAgainstTheLaw(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.law_ids = cov.law_ids(LAW_DIR)

    def test_every_cited_provision_exists(self):
        for r in wq.rows():
            for p in r["provisions"]:
                self.assertIn(p, self.law_ids, (r["id"], p))

    def test_written_questions_cover_every_provision_and_lane(self):
        report = cov.report(wq.rows(), [], self.law_ids)
        own = [m for m in report["misses"] if not m.startswith(("reader", "kind"))]
        self.assertEqual(own, [], own)

    @unittest.skipUnless(os.path.exists(MAP), "needs the built question map")
    def test_whole_bank_meets_every_target(self):
        import json
        with open(MAP) as f:
            mapped = [json.loads(x) for x in f if x.strip()]
        mapped = [r for r in mapped if r["source"] != "written"]
        report = cov.report(wq.rows(), mapped, self.law_ids)
        self.assertEqual(report["misses"], [], report["misses"])

    def test_report_names_a_miss(self):
        report = cov.report([], [], self.law_ids)
        self.assertTrue(any("act-s8" in m for m in report["misses"]))
        self.assertTrue(any("needs_lawyer" in m for m in report["misses"]))


class TestHintMapping(unittest.TestCase):
    def test_graph_hints_map_to_law_ids(self):
        self.assertEqual(cov.hint_to_id("S8"), "act-s8")
        self.assertEqual(cov.hint_to_id("R7"), "rules-r7")
        self.assertIsNone(cov.hint_to_id("X1"))


if __name__ == "__main__":
    unittest.main()
