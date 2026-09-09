"""Claude lyric generation with a deterministic local fallback."""

from __future__ import annotations

import os

from .coverage import Concept, check_coverage

SYSTEM_PROMPT = """You write educational songs for children aged 6 to 10.
Use very simple words, short lines, a nursery-rhyme or catchy kids-pop rhythm,
and Verse, Chorus, and Bridge headings. Keep every fact and detail from the
provided notes. Never summarize away a detail or invent a fact. Put technical
words from the notes in the lyrics and explain them with simple words."""


def generate_lyrics(notes: str, concepts: list[Concept]) -> tuple[str, dict]:
    lyrics = _generate_with_claude(notes) if os.getenv("ANTHROPIC_API_KEY") else None
    if not lyrics:
        lyrics = _fallback_lyrics(concepts)
    coverage = check_coverage(concepts, lyrics)
    if not coverage["passed"]:
        lyrics = _append_coverage_refrain(lyrics, concepts, coverage)
        coverage = check_coverage(concepts, lyrics)
    return lyrics, coverage


def _generate_with_claude(notes: str) -> str | None:
    import anthropic

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    response = client.messages.create(
        model=os.getenv("CLAUDE_MODEL", "claude-3-5-haiku-latest"),
        max_tokens=3000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": f"Turn these notes into a song:\n\n{notes}"}],
    )
    return "".join(block.text for block in response.content if getattr(block, "type", "") == "text").strip()


def _fallback_lyrics(concepts: list[Concept]) -> str:
    lines = ["[Verse 1]"]
    for concept in concepts[: max(1, len(concepts) // 2)]:
        lines.append(f"{concept.text} — sing it bright today!")
    lines += ["", "[Chorus]", "Learn it, sing it, clap along,", "Every little fact belongs!", ""]
    lines.append("[Verse 2]")
    for concept in concepts[max(1, len(concepts) // 2) :]:
        lines.append(f"{concept.text} — remember it this way!")
    lines += ["", "[Bridge]", "Read it, hear it, now we know,", "Let the happy knowledge grow!"]
    return "\n".join(lines)


def _append_coverage_refrain(lyrics: str, concepts: list[Concept], coverage: dict) -> str:
    missing = {item["index"] for item in coverage["items"] if not item["covered"]}
    extra = [concept.text for concept in concepts if concept.index in missing]
    if not extra:
        return lyrics
    return lyrics.rstrip() + "\n\n[Coverage Refrain]\n" + "\n".join(f"{item}!" for item in extra)

