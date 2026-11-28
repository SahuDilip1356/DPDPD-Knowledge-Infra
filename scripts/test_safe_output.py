"""Tests for scripts/safe_output.py, the one way our scripts write market-lane or draft data.

Run: python3 -m unittest scripts/test_safe_output.py -v
"""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(__file__))
import safe_output as so  # noqa: E402

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


class TestSafeOutput(unittest.TestCase):
    def setUp(self):
        self.rel = ("staging", "zz-safe-output-test")
        self.dir = os.path.join(REPO, *self.rel)
        self.cleanup = []

    def tearDown(self):
        if os.path.isdir(self.dir) and not os.path.islink(self.dir):
            for n in os.listdir(self.dir):
                os.remove(os.path.join(self.dir, n))
            os.rmdir(self.dir)
        for p in self.cleanup:
            if os.path.lexists(p):
                os.remove(p)

    def test_writes_files_in_the_folder(self):
        so.write_files(REPO, self.rel, {"a.jsonl": "x\n", "a_summary.json": "{}"})
        with open(os.path.join(self.dir, "a.jsonl")) as f:
            self.assertEqual(f.read(), "x\n")

    def test_hard_link_target_is_not_overwritten(self):
        victim_dir = tempfile.mkdtemp()
        victim = os.path.join(victim_dir, "secret.env")
        with open(victim, "w") as f:
            f.write("TOKEN=keep\n")
        os.makedirs(self.dir, exist_ok=True)
        os.link(victim, os.path.join(self.dir, "a.jsonl"))
        so.write_files(REPO, self.rel, {"a.jsonl": "new\n"})
        with open(victim) as f:
            self.assertEqual(f.read(), "TOKEN=keep\n")
        with open(os.path.join(self.dir, "a.jsonl")) as f:
            self.assertEqual(f.read(), "new\n")

    def test_symlink_target_is_not_followed(self):
        victim_dir = tempfile.mkdtemp()
        victim = os.path.join(victim_dir, "tracked.md")
        with open(victim, "w") as f:
            f.write("keep\n")
        os.makedirs(self.dir, exist_ok=True)
        os.symlink(victim, os.path.join(self.dir, "a.jsonl"))
        so.write_files(REPO, self.rel, {"a.jsonl": "new\n"})
        with open(victim) as f:
            self.assertEqual(f.read(), "keep\n")

    def test_symlinked_folder_is_refused_and_nothing_created_there(self):
        elsewhere = tempfile.mkdtemp()
        os.symlink(elsewhere, self.dir)
        self.cleanup.append(self.dir)
        with self.assertRaises(SystemExit):
            so.write_files(REPO, self.rel, {"a.jsonl": "x"})
        self.assertEqual(os.listdir(elsewhere), [])

    def test_names_must_be_plain(self):
        for bad in ("../x", "a/b", ".", "..", ""):
            with self.assertRaises(SystemExit, msg=bad):
                so.write_files(REPO, self.rel, {bad: "x"})

    def test_folder_must_be_gitignored(self):
        with self.assertRaises(SystemExit):
            so.write_files(REPO, ("scripts", "zz-not-ignored"), {"a.txt": "x"})
        self.assertFalse(os.path.exists(os.path.join(REPO, "scripts", "zz-not-ignored")))

    def test_nothing_written_if_one_name_is_bad(self):
        with self.assertRaises(SystemExit):
            so.write_files(REPO, self.rel, {"ok.jsonl": "x", "../bad": "y"})
        self.assertFalse(os.path.exists(os.path.join(self.dir, "ok.jsonl")))


if __name__ == "__main__":
    unittest.main()
