"""E15 mutation run: switch off one check at a time; the test suite must fail every time.

Run: python3 scripts/training_examples/mutation_run.py
Exits 1 if any mutant survives (the tests stayed green with a check switched off).
"""

import importlib
import io
import os
import re
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))
import check_examples as c  # noqa: E402
import test_check_examples  # noqa: E402

NEVER = re.compile(r"(?!x)x")


def _no_parse_errors(orig):
    return lambda t: (orig(t)[0], [])


def _all_claims_good(claims, law):
    return [], [(i, cl) for i, cl in enumerate(claims, 1) if cl.get("cite") in law]


def _prose_check(i):
    def apply(m):
        m.PROSE_CHECKS[i] = lambda prose: []
    return apply


MUTANTS = {
    "E1 template required": lambda m: setattr(m, "check_has_template", lambda t: []),
    "E1 answer equals rendering": lambda m: setattr(m, "check_rendered", lambda a, r: []),
    "E2 parse errors": lambda m: setattr(m, "parse_template", _no_parse_errors(m.parse_template)),
    "E3 digits": _prose_check(0),
    "E4 characters": _prose_check(1),
    "E4 punctuation allowlist": lambda m: setattr(m, "PROSE_PUNCT", set(" .,")),
    "E5 unit and reference words": _prose_check(2),
    "E5 word list": lambda m: setattr(m, "UNIT_WORDS", {}),
    "E5 per cent": lambda m: setattr(m, "PER_CENT", NEVER),
    "E5 Part X": lambda m: setattr(m, "PART_REF", NEVER),
    "E6 fuzzy": _prose_check(3),
    "E6 exempt list": lambda m: setattr(m, "FUZZY_EXEMPT", set()),
    "E6 length floor": lambda m: setattr(m, "FUZZY_MIN", 99),
    "E7 number words": _prose_check(4),
    "E7 English list": lambda m: setattr(m, "NUMBER_WORDS", m.HINGLISH_NUMBER_WORDS),
    "E7 Hinglish list": lambda m: setattr(m, "NUMBER_WORDS", m.ENGLISH_NUMBER_WORDS),
    "E7 joined number words": lambda m: setattr(m, "_COMPOUND", NEVER),
    "E7 Roman numerals": lambda m: setattr(m, "ROMAN", NEVER),
    "E9 ref slots": lambda m: setattr(m, "check_ref_slots", lambda s, law, q: []),
    "E10 figure slots": lambda m: setattr(m, "check_figure_slots", lambda s, law, q: []),
    "E11 date slots": lambda m: setattr(m, "check_date_slots", lambda s, law, need: []),
    "E11 pending dates": lambda m: setattr(m, "_pending", lambda *a: (set(), [])),
    "E12 notifications": lambda m: setattr(m, "check_notification_slots", lambda s: []),
    "E13 quotes": lambda m: setattr(m, "check_claims", _all_claims_good),
    "E13 word boundaries": lambda m: setattr(m, "_on_word_boundaries", lambda q, t: True),
    "E13 elision": lambda m: setattr(m, "ELISION", NEVER),
    "E13 quote length": lambda m: setattr(m, "MIN_QUOTE_WORDS", 1),
    "E13 labels": lambda m: setattr(m, "check_labels", lambda e: []),
    "E13 lanes and refusals": lambda m: setattr(m, "check_lane", lambda e, a: []),
    "E13 refusal phrase": lambda m: setattr(m, "REFUSAL", re.compile("")),
    "E13 duty words": lambda m: setattr(m, "DUTY_WORDS", NEVER),
    "E13 invented names": lambda m: setattr(m, "check_names", lambda a, law: []),
    "E13 known wrong words": lambda m: setattr(m, "KNOWN_WRONG_WORDS", NEVER),
    "check date validation": lambda m: setattr(m, "valid_date", lambda t: t),
    # Round 1 review: finer mutants
    "E13 number cut at quote start": lambda m: setattr(m, "_cuts_number_start", lambda q, p: False),
    "E13 number cut at quote end": lambda m: setattr(m, "_cuts_number_end", lambda q, n: False),
    "E2 no part on value slots": lambda m: setattr(m, "NO_PART_SLOTS", set()),
    "E10 money vs count": lambda m: setattr(m, "money", lambda text, rupees: m.amounts(text)),
    "E10 canonical period": lambda m: setattr(m, "_canonical_period", lambda v: True),
    "E10 same-sentence reference": lambda m: setattr(m, "_sentences", lambda pieces: []),
    "E9 date id named in a quote": lambda m: setattr(m, "_named_in_quotes", lambda q: set(m.LAW_IDS_ALL)),
    "E5 part markers": lambda m: setattr(m, "PART_MARKER", NEVER),
    "E7 month names": lambda m: setattr(m, "MONTH_NAMES", NEVER),
    "E7 high ordinals": lambda m: setattr(m, "HIGH_ORDINAL", NEVER),
    "E7 number+unit joined": lambda m: setattr(m, "_NUMBER_UNIT", NEVER),
    "E9 part structure": lambda m: setattr(m, "_marker_kind", lambda mk, parent: "num" if mk.isdigit() else "letter"),
}


def suite_passes():
    suite = unittest.defaultTestLoader.loadTestsFromModule(test_check_examples)
    result = unittest.TextTestRunner(stream=io.StringIO(), verbosity=0).run(suite)
    return result.wasSuccessful(), result.testsRun


def main():
    ok, n = suite_passes()
    if not ok:
        sys.exit("The unmutated suite fails; fix it before the mutation run.")
    survivors = []
    for name, mutate in MUTANTS.items():
        importlib.reload(c)
        mutate(c)
        passed, _ = suite_passes()
        print(f"{'SURVIVED' if passed else 'killed  '}  {name}")
        if passed:
            survivors.append(name)
    importlib.reload(c)
    print(f"{len(MUTANTS) - len(survivors)} of {len(MUTANTS)} mutants killed ({n} tests).")
    sys.exit(1 if survivors else 0)


if __name__ == "__main__":
    main()
