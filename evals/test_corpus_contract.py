"""The committed answer corpus against the corpus contract. Run: python -m pytest -q evals/test_corpus_contract.py"""

import evals.runner  # noqa: F401  puts the deployed backend first on sys.path
from evals import real_corpus
from src.schemas.corpus_contract import check_corpus, load_law, read_jsonl, report


def test_every_answer_in_the_corpus_conforms():
    """Shape, and every quote and hash checked against the gazette text the site is built from."""
    rows = read_jsonl(real_corpus.ANSWERS_PATH)
    assert len(rows) > 500
    failures = check_corpus(rows, load_law(real_corpus.PROVISIONS_PATH))
    assert not failures, report(failures, len(rows))
