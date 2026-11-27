"""Tests for the review-sheet maker: plain names only, written through scripts/safe_output.py.

Run: python3 -m unittest scripts/training_examples/test_make_review_sheet.py scripts/test_safe_output.py -v
"""

import inspect
import os
import subprocess
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))
import make_review_sheet as m  # noqa: E402


class TestSheet(unittest.TestCase):
    def test_sheet_name_follows_the_batch(self):
        self.assertEqual(m.sheet_name("staging/training-examples/batch01.jsonl"), "batch01_review.md")

    def test_batch_outside_the_folder_is_refused(self):
        for bad in (".env", "deployments/dpdpa-backend/.env", "staging/question-map/question_map.jsonl"):
            res = subprocess.run([sys.executable, m.__file__, "--law", "x", os.path.join(m.REPO_ROOT, bad)],
                                 capture_output=True, text=True)
            self.assertNotEqual(res.returncode, 0, bad)

    def test_uses_the_shared_safe_writer(self):
        src = inspect.getsource(m.main)
        self.assertIn("safe_output.write_files", src)
        self.assertNotIn("os.open(", src)


if __name__ == "__main__":
    unittest.main()
