"""Tier-0 Transformative Ingestion and 2-Stage Anti-Mimicking Idea Distiller."""

import math
import re
from collections import Counter
from dataclasses import dataclass, field
from pydantic import BaseModel, Field


class DistilledIdeaMetadata(BaseModel):
    """Abstract thematic essence extracted from reference material without dialogue."""

    core_theme: str = Field(description="High-level topic or thesis")
    genre: str = Field(default="comedy", description="Genre classification")
    psychological_hook: str = Field(description="Core curiosity gap or premise")
    pacing_curve: str = Field(default="escalation", description="Narrative rhythm")
    dramatic_conflict: str = Field(description="Abstract central tension")
    key_entities: list[str] = Field(default_factory=list, description="Topical anchors")
    prohibited_borrowed_phrases: list[str] = Field(
        default_factory=list, description="Extracted source n-grams strictly banned from synthesis"
    )


@dataclass
class AntiMimicAudit:
    """Compliance audit result verifying generated script does not mimic source."""

    cosine_similarity: float
    is_safe: bool
    verbatim_matching_ngrams: list[str] = field(default_factory=list)
    risk_level: str = "low"  # low | medium | high


def extract_ngrams(text: str, n: int = 3) -> list[str]:
    """Extract clean lower-case n-grams from text."""
    clean = re.sub(r"[^\w\s]", "", text.lower())
    words = [w for w in clean.split() if len(w) > 2]
    if len(words) < n:
        return []
    return [" ".join(words[i : i + n]) for i in range(len(words) - n + 1)]


def compute_text_cosine_similarity(text1: str, text2: str) -> float:
    """Compute deterministic bag-of-words cosine similarity between two texts."""
    words1 = re.findall(r"\b\w{3,}\b", text1.lower())
    words2 = re.findall(r"\b\w{3,}\b", text2.lower())

    if not words1 or not words2:
        return 0.0

    vec1 = Counter(words1)
    vec2 = Counter(words2)

    intersection = set(vec1.keys()) & set(vec2.keys())
    numerator = sum(vec1[x] * vec2[x] for x in intersection)

    sum1 = sum(v**2 for v in vec1.values())
    sum2 = sum(v**2 for v in vec2.values())
    denominator = math.sqrt(sum1) * math.sqrt(sum2)

    if not denominator:
        return 0.0
    return float(numerator / denominator)


def distill_reference_source(
    raw_source_text: str,
    genre_hint: str = "comedy",
) -> DistilledIdeaMetadata:
    """Stage 1: Distill raw reference transcript into abstract tension and prohibited phrases."""
    # 1. Extract frequent 3-grams as strictly prohibited phrases
    source_ngrams = extract_ngrams(raw_source_text, n=3)
    ngram_counts = Counter(source_ngrams).most_common(30)
    prohibited = [ng for ng, _ in ngram_counts]

    # 2. Extract potential key topic words (frequency filtering)
    words = re.findall(r"\b[A-Za-z]{4,}\b", raw_source_text)
    common_words = [w.lower() for w, _ in Counter(words).most_common(10)]

    # 3. Formulate abstract psychological hook & dramatic conflict
    first_sentence = (raw_source_text.strip().split(".")[0] or "Exploration of modern conflicts").strip()
    abstract_hook = f"The paradoxical reality of {common_words[0] if common_words else 'modern life'}"
    abstract_conflict = f"Expectations vs lived experience conflict in {genre_hint} format"

    return DistilledIdeaMetadata(
        core_theme=first_sentence[:120],
        genre=genre_hint,
        psychological_hook=abstract_hook,
        pacing_curve="fast_hook_then_conflict_escalation",
        dramatic_conflict=abstract_conflict,
        key_entities=common_words[:6],
        prohibited_borrowed_phrases=prohibited,
    )


def audit_script_originality(
    source_reference: str,
    synthesized_script: str,
    max_cosine_threshold: float = 0.60,
) -> AntiMimicAudit:
    """Stage 2: Deterministic anti-mimicking verification against source reference."""
    # 1. Compute cosine similarity
    cosine = compute_text_cosine_similarity(source_reference, synthesized_script)

    # 2. Verify zero overlapping 3-grams
    source_ngrams = set(extract_ngrams(source_reference, n=3))
    synth_ngrams = set(extract_ngrams(synthesized_script, n=3))
    overlapping = list(source_ngrams & synth_ngrams)

    # 3. Evaluate safety (cosine < 0.60 and no significant verbatim repetition)
    is_safe = (cosine <= max_cosine_threshold) and (len(overlapping) <= 2)
    risk_level = "low" if is_safe else ("high" if cosine > 0.75 else "medium")

    return AntiMimicAudit(
        cosine_similarity=round(cosine, 4),
        is_safe=is_safe,
        verbatim_matching_ngrams=overlapping[:5],
        risk_level=risk_level,
    )


__all__ = [
    "DistilledIdeaMetadata",
    "AntiMimicAudit",
    "extract_ngrams",
    "compute_text_cosine_similarity",
    "distill_reference_source",
    "audit_script_originality",
]
