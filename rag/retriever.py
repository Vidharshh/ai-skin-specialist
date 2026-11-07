"""Retrieve attributed notes from the local starter knowledge base."""

from collections import Counter
import json
from math import log
from pathlib import Path
import re

_KNOWLEDGE_PATH = Path(__file__).with_name("knowledge_base.json")
_TOKEN_PATTERN = re.compile(r"[a-z0-9]+")
_STOP_WORDS = {
    "a", "an", "and", "are", "area", "be", "can", "check", "concern",
    "do", "doctor", "for", "from", "have", "health", "how", "i", "if",
    "in", "is", "it", "medical", "me", "my", "of", "on", "or", "please",
    "problem", "same", "skin", "the", "to", "what", "with", "you", "your",
}


def _tokens(text: str) -> list[str]:
    words = _TOKEN_PATTERN.findall(text.lower())
    normalized = []
    for word in words:
        if word.endswith("ies") and len(word) > 5:
            word = word[:-3] + "y"
        elif word.endswith("s") and len(word) > 4 and not word.endswith("ss"):
            word = word[:-1]
        if len(word) > 1 and word not in _STOP_WORDS:
            normalized.append(word)
    return normalized


def retrieve_knowledge(query: str, limit: int = 3) -> list[dict]:
    """Return relevant notes ranked by local BM25-style word overlap.

    This is lexical retrieval, not a semantic embedding model. It makes no
    network requests and returns an empty list when no terms match.
    """
    if limit < 1 or not query or not query.strip():
        return []

    knowledge = json.loads(_KNOWLEDGE_PATH.read_text(encoding="utf-8"))
    documents = knowledge.get("documents", [])
    if not documents:
        return []

    tokenized_docs = [
        _tokens(document.get("title", "") + " " + document.get("text", ""))
        for document in documents
    ]
    document_frequency = Counter(
        token for tokens in tokenized_docs for token in set(tokens)
    )
    average_length = sum(map(len, tokenized_docs)) / len(tokenized_docs) or 1
    query_terms = set(_tokens(query))
    if not query_terms:
        return []

    total_documents = len(documents)
    k1 = 1.2
    b = 0.75
    ranked = []
    for document, tokens in zip(documents, tokenized_docs):
        frequencies = Counter(tokens)
        length = len(tokens)
        score = 0.0
        for term in query_terms:
            frequency = frequencies[term]
            if not frequency:
                continue
            inverse_frequency = log(
                1 + (total_documents - document_frequency[term] + 0.5)
                / (document_frequency[term] + 0.5)
            )
            denominator = frequency + k1 * (1 - b + b * length / average_length)
            score += inverse_frequency * frequency * (k1 + 1) / denominator
        if score > 0:
            ranked.append({**document, "score": score})

    return sorted(ranked, key=lambda item: item["score"], reverse=True)[:limit]
