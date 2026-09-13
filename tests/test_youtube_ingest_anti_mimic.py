"""Tests for 2-stage transformative ingestion and anti-mimicking distillation engine."""

from src.scripts.youtube_ingest import (
    audit_script_originality,
    compute_text_cosine_similarity,
    distill_reference_source,
    extract_ngrams,
)


def test_extract_ngrams():
    """Verify clean n-gram extraction."""
    text = "Work from home is totally different from working in the office every single morning."
    ngrams = extract_ngrams(text, n=3)
    assert len(ngrams) > 0
    assert "work from home" in ngrams or "working in the" in ngrams


def test_cosine_similarity_computation():
    """Verify bag-of-words cosine similarity calculation."""
    text_a = "Work from home software engineer morning standup meeting calls"
    text_b = "Work from home software engineer morning standup meeting calls"
    similarity_same = compute_text_cosine_similarity(text_a, text_b)
    assert similarity_same > 0.95

    text_c = "Ancient mythological dynasty warriors fighting in colossal golden battlefield"
    similarity_diff = compute_text_cosine_similarity(text_a, text_c)
    assert similarity_diff < 0.20


def test_distill_reference_source():
    """Stage 1: Verify extraction of abstract hooks, conflicts, and prohibited phrases."""
    sample_transcript = (
        "In this video I will show you how remote work turned into a nightmare. "
        "Every single day my manager calls at 9 PM asking for commit status updates. "
        "The WiFi router drops right when the CEO joins the all-hands broadcast."
    )

    metadata = distill_reference_source(sample_transcript, genre_hint="comedy")
    assert metadata.genre == "comedy"
    assert len(metadata.prohibited_borrowed_phrases) > 0
    assert len(metadata.key_entities) > 0
    assert "conflict" in metadata.dramatic_conflict.lower()


def test_audit_script_originality_pass_and_fail():
    """Stage 2: Verify anti-mimicking guarantee passes for original scripts and catches copycats."""
    source_reference = (
        "The software engineer sat at her kitchen desk sipping cold coffee. "
        "Her laptop buzzed with five consecutive emergency messages from product management."
    )

    # 1. Copycat script (should FAIL audit)
    copycat_script = (
        "The software engineer sat at her kitchen desk sipping cold coffee. "
        "Her laptop buzzed with five consecutive emergency messages from management."
    )
    fail_audit = audit_script_originality(source_reference, copycat_script, max_cosine_threshold=0.60)
    assert not fail_audit.is_safe
    assert fail_audit.risk_level in ("medium", "high")

    # 2. Truly original synthesized narrative starring persistent characters (should PASS audit)
    original_script = (
        "Aaradhya glared at the frozen spinning loading wheel on her dual monitors. "
        "Kabir casually muted his microphone and pretended his fiber optic broadband failed."
    )
    pass_audit = audit_script_originality(source_reference, original_script, max_cosine_threshold=0.60)
    assert pass_audit.is_safe
    assert pass_audit.cosine_similarity < 0.50
    assert pass_audit.risk_level == "low"
