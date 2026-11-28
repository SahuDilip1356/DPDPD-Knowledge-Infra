"""Checks for the question-map builder (training guide step 1).

Run: python3 -m unittest scripts/question_map/test_build_question_map.py -v
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(__file__))
import build_question_map as b  # noqa: E402

KINDS = {"who", "why", "how", "what", "when", "where"}
READERS = {"business", "learner", "public"}
LANES = {"law_answers", "law_silent", "needs_lawyer", "comparison", "out_of_scope"}
ALLOWED_KEYS = {
    "id", "question", "kind", "reader", "lane", "topic", "provision_hints",
    "source", "demand", "first_person", "label_source", "review",
}


def graph_row(qid, q, topic="Consent", audience="business owner", intent="obligation",
              provisions=None, sites=3, street=0):
    return {
        "question_id": qid, "question": q, "topic": topic, "audience": audience,
        "intent": intent, "provisions": provisions or [], "demand_sites": sites,
        "street_hits": street, "saralprivacy_asks": False,
        "asked_on": ["competitor.example"], "example_urls": ["https://competitor.example/x"],
        "variants": [q + " (variant)"],
    }


def street_row(sid, text, grade="cook_now", quality="india_dpdpa", hits=2):
    return {"id": sid, "text": text, "topic": "x", "grade": grade, "quality": quality,
            "hits": str(hits)}


class TestKind(unittest.TestCase):
    def test_question_words(self):
        self.assertEqual(b.label_kind("Who is a Data Fiduciary?", "definition"), "who")
        self.assertEqual(b.label_kind("Why does consent matter?", "obligation"), "why")
        self.assertEqual(b.label_kind("How do I report a breach?", "how-to"), "how")
        self.assertEqual(b.label_kind("Where can I file a complaint?", "rights"), "where")
        self.assertEqual(b.label_kind("When do the Rules come into force?", "deadline"), "when")

    def test_intent_fallback(self):
        self.assertEqual(b.label_kind("Does the Act apply to startups?", "applicability"), "who")
        self.assertEqual(b.label_kind("DPDP Rules implementation date", "deadline"), "when")
        self.assertEqual(b.label_kind("Can data be sent abroad?", "obligation"), "where")
        self.assertEqual(b.label_kind("Consent under DPDPA", "definition"), "what")

    def test_deadline_intent_needs_a_time_word(self):
        q = "What is the penalty for failing to meet Significant Data Fiduciary duties?"
        self.assertEqual(b.label_kind(q, "deadline"), "what")


class TestLane(unittest.TestCase):
    def test_comparison(self):
        self.assertEqual(b.label_lane("Is GDPR mandatory in India?", "comparison", "graph", None), "comparison")

    def test_needs_lawyer(self):
        self.assertEqual(b.label_lane("Is my company compliant with DPDPA?", "obligation", "graph", None), "needs_lawyer")

    def test_myth_and_shopping_are_silent(self):
        self.assertEqual(b.label_lane("DPDPA certification", "obligation", "street", "myth_jar"), "law_silent")

    def test_noise_out_of_scope(self):
        self.assertEqual(b.label_lane("UPSC notes", "obligation", "street", "throw_out"), "out_of_scope")

    def test_default(self):
        self.assertEqual(b.label_lane("What is a consent notice?", "definition", "graph", None), "law_answers")


class TestReader(unittest.TestCase):
    def test_map(self):
        self.assertEqual(b.label_reader("compliance/DPO", "q"), "business")
        self.assertEqual(b.label_reader("individual", "q"), "public")
        self.assertEqual(b.label_reader(None, "DPDPA course for beginners"), "learner")


class TestBuild(unittest.TestCase):
    def setUp(self):
        graph = [graph_row(f"Q-{i:05d}", f"What is duty number {i} under the Act?",
                           topic=["Consent", "Breach", "Notice"][i % 3], sites=i % 7)
                 for i in range(1, 60)]
        graph.append(graph_row("Q-09999", "What is duty number 1 under the Act?"))  # duplicate
        street = [street_row("S-001", "DPDPA certification", grade="myth_jar"),
                  street_row("S-002", "who is data fiduciary", hits=9),
                  street_row("S-003", "upsc privacy notes", grade="throw_out")]
        self.rows = b.build(graph, street, target=40, topic_floor=5)

    def test_every_row_labelled(self):
        for r in self.rows:
            self.assertIn(r["kind"], KINDS)
            self.assertIn(r["reader"], READERS)
            self.assertIn(r["lane"], LANES)
            self.assertEqual(r["review"], "pending")
            self.assertEqual(r["label_source"], "rule")

    def test_no_answer_text_or_competitor_names(self):
        for r in self.rows:
            self.assertLessEqual(set(r), ALLOWED_KEYS)
            self.assertNotIn("competitor.example", json.dumps(r))

    def test_no_duplicates(self):
        keys = [b.norm(r["question"]) for r in self.rows]
        self.assertEqual(len(keys), len(set(keys)))

    def test_size_and_topic_floor(self):
        self.assertLessEqual(len(self.rows), 40)
        topics = [r["topic"] for r in self.rows if r["source"] == "graph"]
        for t in ("Consent", "Breach", "Notice"):
            self.assertGreaterEqual(topics.count(t), 5)

    def test_street_questions_kept_but_noise_dropped(self):
        qs = {r["question"] for r in self.rows}
        self.assertIn("who is data fiduciary", qs)
        self.assertIn("DPDPA certification", qs)
        noise = [r for r in self.rows if r["question"] == "upsc privacy notes"]
        self.assertEqual([r["lane"] for r in noise], ["out_of_scope"])


class TestRegressionsFromReview(unittest.TestCase):
    """Real questions the first rules got wrong."""

    def test_when_only_as_time(self):
        self.assertEqual(b.label_kind("What happens when a user withdraws consent under the DPDP Act?", "obligation"), "what")
        self.assertEqual(b.label_kind("What are the best practices for implementing effective privacy consent management?", "how-to"), "how")
        self.assertEqual(b.label_kind("What is the effective date of the DPDP Rules?", "deadline"), "when")

    def test_transfer_of_liability_is_not_where(self):
        self.assertEqual(b.label_kind("Can a Data Fiduciary transfer liability to a Data Processor?", "obligation"), "what")
        self.assertEqual(b.label_kind("Can personal data be transferred outside India?", "obligation"), "where")

    def test_first_person_situation_needs_lawyer(self):
        self.assertEqual(b.label_lane("Will our company be fined for this breach?", "penalty", "graph", None), "needs_lawyer")
        self.assertEqual(b.label_lane("Is our app DPDPA compliant?", "obligation", "graph", None), "needs_lawyer")

    def test_off_topic_out_of_scope(self):
        self.assertEqual(b.label_lane("WhatsApp Business Terms and conditions pdf", "obligation", "street", "review"), "out_of_scope")
        self.assertEqual(b.label_lane("Which AI privacy risks are explored in the report?", "obligation", "graph", None), "out_of_scope")

    def test_other_foreign_laws_are_comparison(self):
        for q in ("Does the FADP apply to AI-based processing of data?",
                  "What are the penalties for breaching the PDPA?"):
            self.assertEqual(b.label_lane(q, "obligation", "graph", None), "comparison")
        self.assertEqual(b.label_lane("What does the DPDPA say about notice?", "obligation", "graph", None), "law_answers")

    def test_internal_dpdpa_comparison_stays_law(self):
        self.assertEqual(b.label_lane("Are Legitimate Uses the same as consent under the DPDP Act?", "comparison", "graph", None), "law_answers")

    def test_security_questions_on_topic(self):
        self.assertEqual(b.label_lane("What is encryption at rest?", "definition", "graph", None), "law_answers")
        self.assertEqual(b.label_lane("DPBI portal", "obligation", "street", "review"), "law_answers")

    def test_class_whatsapp_group_is_not_learner(self):
        self.assertEqual(b.label_reader("individual", "Is your class WhatsApp group a data problem?"), "public")

    def test_norm_merges_hyphen_and_dpdpa(self):
        self.assertEqual(b.norm("Cross-border transfer under DPDPA"), b.norm("cross border transfer under DPDP"))

    def test_questions_with_urls_dropped(self):
        rows = b.build([graph_row("Q-1", "See www.example.com for consent rules?")], [], target=10, topic_floor=1)
        self.assertEqual(rows, [])

    def test_street_noise_kept_as_out_of_scope(self):
        rows = b.build([], [street_row("S-9", "upsc privacy notes", grade="throw_out")], target=10, topic_floor=1)
        self.assertEqual([r["lane"] for r in rows], ["out_of_scope"])


class TestOutputs(unittest.TestCase):
    """Outputs go through scripts/safe_output.py (its own tests cover links and swaps)."""

    def run_main(self, name, graph_rows=None):
        tmp = tempfile.mkdtemp()
        graph = os.path.join(tmp, "g.jsonl")
        street = os.path.join(tmp, "s.csv")
        with open(graph, "w") as f:
            for r in graph_rows or [graph_row("Q-1", "What is consent under the Act?")]:
                f.write(json.dumps(r) + "\n")
        with open(street, "w") as f:
            f.write("id,text,topic,grade,quality,hits\n")
        return subprocess.run([sys.executable, b.__file__, "--graph", graph, "--street", street, "--name", name],
                              capture_output=True, text=True)

    def tearDown(self):
        d = os.path.join(b.REPO_ROOT, *b.OUT_REL)
        for n in ("zz_out_test.jsonl", "zz_out_test_summary.json", "zz_out_test_review.csv"):
            p = os.path.join(d, n)
            if os.path.lexists(p):
                os.remove(p)

    def test_writes_three_files_in_staging_question_map(self):
        res = self.run_main("zz_out_test")
        self.assertEqual(res.returncode, 0, res.stderr)
        d = os.path.join(b.REPO_ROOT, *b.OUT_REL)
        for n in ("zz_out_test.jsonl", "zz_out_test_summary.json", "zz_out_test_review.csv"):
            self.assertTrue(os.path.isfile(os.path.join(d, n)), n)

    def test_name_with_path_is_refused(self):
        for bad in ("../x", "a/b", "../../deployments/dpdpa-backend/.env", "/tmp/x"):
            res = self.run_main(bad)
            self.assertNotEqual(res.returncode, 0, bad)

    def test_uses_the_shared_safe_writer(self):
        import inspect
        src = inspect.getsource(b.main)
        self.assertIn("safe_output.write_files", src)
        self.assertNotIn("open(", src.replace("with open(a.graph)", "").replace("with open(a.street", ""))


if __name__ == "__main__":
    unittest.main()
