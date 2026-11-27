"""Guard tests for the review-sheet maker: it may write only inside staging/training-examples/.

Run: python3 -m unittest scripts/training_examples/test_make_review_sheet.py -v
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))
import make_review_sheet as m  # noqa: E402


class TestOutputConfinement(unittest.TestCase):
    def setUp(self):
        self.dir = os.path.join(m.REPO_ROOT, "staging", "training-examples")
        os.makedirs(self.dir, exist_ok=True)
        self.made = []

    def tearDown(self):
        for p in self.made:
            if os.path.lexists(p):
                os.remove(p)

    def test_sheet_path_follows_the_batch(self):
        self.assertEqual(m.sheet_path(os.path.join(self.dir, "b.jsonl")), os.path.join(self.dir, "b_review.md"))

    def test_refuses_batches_outside_the_folder(self):
        for rel in (".env.jsonl", "deployments/dpdpa-backend/.env", "staging/question-map/x.jsonl", ".agent/x.jsonl"):
            with self.assertRaises(SystemExit, msg=rel):
                m.check_output(m.sheet_path(os.path.join(m.REPO_ROOT, rel)))

    def test_refuses_symlinked_sheet(self):
        link = os.path.join(self.dir, "zz_guard_review.md")
        os.symlink(os.path.join(m.REPO_ROOT, "scripts", "training_examples", "README.md"), link)
        self.made.append(link)
        with self.assertRaises(SystemExit):
            m.check_output(link)

    def test_allows_plain_file(self):
        m.check_output(os.path.join(self.dir, "zz_ok_review.md"))


if __name__ == "__main__":
    unittest.main()
