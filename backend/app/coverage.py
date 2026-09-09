"""Ordered concept parsing and lyric coverage checks."""

from __future__ import annotations

import re
from dataclasses import dataclass

STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "in",
    "is", "it", "of", "on", "or", "that", "the", "this", "to", "was", "with",
}


@dataclass(frozen=True)
class Concept:
    index: int
    text: str


def parse_concepts(text: str) -> list[Concept]:
    """Split notes into ordered, meaningful sentences or bullet points."""
    fragments = re.split(r"(?<=[.!?])\s+|\n+", text)
    concepts = []
    for fragment in fragments:
        value = re.sub(r"^\s*[-*•]\s*", "", fragment).strip()
        value = re.sub(r"^\[Source:[^\]]+\]\s*", "", value)
        if value:
            concepts.append(Concept(len(concepts) + 1, value))
    return concepts


def _keywords(value: str) -> set[str]:
    words = re.findall(r"[a-z0-9]+", value.lower())
    return {word for word in words if len(word) > 2 and word not in STOP_WORDS}


def check_coverage(concepts: list[Concept], lyrics: str) -> dict:
    """Return per-concept matches; all keywords are required for full coverage."""
    lyric_words = set(re.findall(r"[a-z0-9]+", lyrics.lower()))
    results = []
    for concept in concepts:
        keywords = _keywords(concept.text)
        missing = sorted(keywords - lyric_words)
        results.append(
            {
                "index": concept.index,
                "concept": concept.text,
                "missing_keywords": missing,
                "covered": not missing,
            }
        )
    covered = sum(item["covered"] for item in results)
    return {
        "passed": covered == len(results),
        "covered": covered,
        "total": len(results),
        "items": results,
    }
