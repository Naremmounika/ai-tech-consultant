import json
import math
import re
from collections import Counter

from app.config import (
    INDEX_PATH,
    MIN_QUERY_COVERAGE,
    MIN_SIMILARITY_SCORE,
)

STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "been",
    "being", "but", "by", "can", "could", "did", "do",
    "does", "for", "from", "had", "has", "have", "how",
    "i", "if", "in", "into", "is", "it", "its", "may",
    "me", "my", "of", "on", "or", "our", "please",
    "should", "the", "their", "them", "there", "these",
    "this", "those", "to", "was", "we", "were", "what",
    "when", "where", "which", "who", "why", "will",
    "with", "would", "you", "your", "brilliant",
    "directories", "website", "websites",
}

QUERY_SYNONYMS = {
    "homepage": ["home", "design", "colors"],
    "color": ["colors", "design", "theme"],
    "colors": ["color", "design", "theme"],
    "colour": ["colors", "design", "theme"],
    "colours": ["colors", "design", "theme"],
    "theme": ["design", "colors", "fonts"],
    "settings": ["design", "configuration"],
    "customize": ["customize", "design", "colors"],
    "customise": ["customize", "design", "colors"],
    "match": ["design", "colors"],
    "different": ["design", "colors"],
}


def load_documents() -> list[dict]:
    """Load indexed document chunks from disk."""
    if not INDEX_PATH.exists():
        return []

    try:
        payload = json.loads(
            INDEX_PATH.read_text(encoding="utf-8")
        )
        documents = payload.get("documents", [])

        if not isinstance(documents, list):
            return []

        return [
            doc
            for doc in documents
            if isinstance(doc, dict)
            and isinstance(doc.get("text"), str)
            and doc.get("text", "").strip()
        ]
    except (json.JSONDecodeError, OSError):
        return []


def tokenize(text: str) -> list[str]:
    """Normalize text and remove common words."""
    words = re.findall(r"[a-z0-9]+", text.lower())
    return [
        word for word in words
        if word not in STOP_WORDS and len(word) > 1
    ]


def expand_query_tokens(tokens: list[str]) -> list[str]:
    """Add a limited set of domain synonyms to the query."""
    expanded = list(tokens)

    for token in tokens:
        expanded.extend(QUERY_SYNONYMS.get(token, []))

    return list(dict.fromkeys(expanded))


def search_knowledge(
    question: str,
    top_k: int = 5,
) -> list[dict]:
    """
    Rank indexed chunks using TF-IDF cosine similarity.

    Synonyms help rank natural customer wording, but relevance coverage
    is calculated against the original query terms. Unknown topic words
    therefore remain in the denominator instead of being silently
    discarded.
    """
    if not isinstance(question, str) or not question.strip():
        return []

    documents = load_documents()
    original_tokens = tokenize(question)

    if not documents or not original_tokens:
        return []

    top_k = max(1, min(int(top_k), 10))

    tokenized_documents = [
        tokenize(f"{doc.get('title', '')} {doc.get('text', '')}")
        for doc in documents
    ]

    document_count = len(documents)
    document_frequency = Counter()

    for tokens in tokenized_documents:
        document_frequency.update(set(tokens))

    def idf(term: str) -> float:
        frequency = document_frequency.get(term, 0)
        return math.log(1 + document_count / (1 + frequency))

    def make_vector(tokens: list[str]) -> dict[str, float]:
        counts = Counter(tokens)
        total = max(len(tokens), 1)

        return {
            term: (count / total) * idf(term)
            for term, count in counts.items()
        }

    expanded_tokens = expand_query_tokens(original_tokens)
    known_expanded_tokens = [
        term for term in expanded_tokens
        if document_frequency.get(term, 0) > 0
    ]

    if not known_expanded_tokens:
        return []

    query_vector = make_vector(known_expanded_tokens)
    query_norm = math.sqrt(
        sum(value * value for value in query_vector.values())
    )

    if query_norm == 0:
        return []

    original_weights = {
        term: idf(term) for term in set(original_tokens)
    }
    total_query_weight = sum(original_weights.values())

    if total_query_weight == 0:
        return []

    scored = []

    for document, tokens in zip(documents, tokenized_documents):
        document_vector = make_vector(tokens)
        document_norm = math.sqrt(
            sum(value * value for value in document_vector.values())
        )

        if document_norm == 0:
            continue

        dot_product = sum(
            weight * document_vector.get(term, 0.0)
            for term, weight in query_vector.items()
        )
        similarity = dot_product / (query_norm * document_norm)

        document_terms = set(tokens)
        matched_weight = 0.0

        for term, weight in original_weights.items():
            equivalents = {term, *QUERY_SYNONYMS.get(term, [])}
            if document_terms.intersection(equivalents):
                matched_weight += weight

        coverage = matched_weight / total_query_weight

        if (
            similarity < MIN_SIMILARITY_SCORE
            or coverage < MIN_QUERY_COVERAGE
        ):
            continue

        scored.append({
            **document,
            "score": round(similarity, 6),
            "coverage": round(coverage, 4),
        })

    scored.sort(
        key=lambda item: (item["score"], item["coverage"]),
        reverse=True,
    )

    return scored[:top_k]
