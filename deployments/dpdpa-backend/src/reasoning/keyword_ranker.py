"""
Keyword ranker — the retrieval fallback when vector search is unavailable.

BM25 over each Knowledge Object's title, summary and entities, capped at the same
top-k as the Pinecone path. A relevance floor keeps an object only when it matches
enough of the query's informative words (by IDF weight). A query word that no object
contains weighs as much as the rarest word that one does, so a question whose key
term is absent from the corpus retrieves nothing and the engine refuses instead of
answering off-topic.
"""

import math
import re
from collections import Counter
from typing import Callable, Dict, List, Sequence

TOP_K = 5              # matches the Pinecone query's topK
MIN_COVERAGE = 0.2     # share of the query's IDF weight an object must match
K1, B = 1.5, 0.75      # standard BM25 parameters

STOPWORDS = frozenset("""
a about above after again against all also am an and any are as at be because been
before being below between both but by can could did do does doing done down during
each either else ever every few for from further get gets got had has have having he
her here hers him his how i if in into is it its itself just let may me might more
most must my no nor not now of off on once only or other our ours out over own per
same shall she should so some such than that the their theirs them then there these
they this those through to too under until up upon us very via was we were what when
where whether which while who whom whose why will with within without would yes yet
you your yours
""".split())


def _stem(word: str) -> str:
    """Fold plurals so 'penalties' matches 'penalty' and 'notices' matches 'notice'."""
    if len(word) > 4 and word.endswith("ies"):
        return word[:-3] + "y"
    if len(word) > 3 and word.endswith("s") and not word.endswith(("ss", "us", "is")):
        return word[:-1]
    return word


def tokenize(text: str) -> List[str]:
    return [_stem(t) for t in re.findall(r"[a-z0-9]+", text.lower())
            if len(t) > 1 and t not in STOPWORDS]


def ko_text(ko: Dict) -> str:
    """The fields the fallback searches: title, summary and entities."""
    entities = ko.get("entities") or []
    return f"{ko.get('title') or ''} {ko.get('summary') or ''} {' '.join(map(str, entities))}"


def rank_by_relevance(
    query: str,
    docs: Sequence[Dict],
    text_of: Callable[[Dict], str] = ko_text,
    top_k: int = TOP_K,
    min_coverage: float = MIN_COVERAGE,
) -> List[Dict]:
    """Return at most top_k docs, best first, each clearing the relevance floor."""
    terms = list(dict.fromkeys(tokenize(query)))
    if not terms or not docs:
        return []

    doc_terms = [Counter(tokenize(text_of(d))) for d in docs]
    n = len(docs)
    avg_len = sum(sum(tf.values()) for tf in doc_terms) / n or 1.0
    df = Counter(t for tf in doc_terms for t in terms if t in tf)
    # df floored at 1: an unseen word weighs like the rarest seen one. Unfloored, it would
    # outweigh every matched word in a small corpus and nothing could clear the floor.
    idf = {t: math.log(1 + (n - max(df[t], 1) + 0.5) / (max(df[t], 1) + 0.5)) for t in terms}
    query_weight = sum(idf.values())

    scored = []
    for i, tf in enumerate(doc_terms):
        matched = [t for t in terms if t in tf]
        if not matched or sum(idf[t] for t in matched) / query_weight < min_coverage:
            continue
        length_norm = K1 * (1 - B + B * sum(tf.values()) / avg_len)
        score = sum(idf[t] * tf[t] * (K1 + 1) / (tf[t] + length_norm) for t in matched)
        scored.append((score, i))
    scored.sort(key=lambda s: (-s[0], s[1]))
    return [docs[i] for _, i in scored[:top_k]]
