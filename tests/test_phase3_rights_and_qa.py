"""Phase 3 Comprehensive Test Suite: Rights Ledger, Provenance Bundle, YPP Safety, & QA Gate."""

import json
from pathlib import Path
from uuid import uuid4
import pytest
from src.agents.qa_gate_agent import qa_gate_agent
from src.compliance.evidence_bundle import build_evidence_bundle, save_evidence_bundle
from src.compliance.rights_ledger import rights_ledger
from src.compliance.ypp_safety import (
    evaluate_ypp_safety,
    get_synthetic_media_disclosure,
    screen_opening_profanity,
    screen_script_for_adsense,
)
from src.domain.rights import AssetType, CommercialLicenseType
from src.providers.lipsync.fal_liveportrait import liveportrait_adapter
from src.scripts.local_video_qa import detect_frame_defects, measure_loudness_ebur128, run_video_qa_audit


@pytest.fixture(autouse=True)
def reset_ledger():
    """Reset rights ledger before each test."""
    rights_ledger.clear_ledger()
    yield
    rights_ledger.clear_ledger()


def test_rights_ledger_recording_and_verification():
    """Verify that rights ledger records cleared assets and passes commercial check."""
    ep_id = uuid4()
    # Register image asset
    img_rec = rights_ledger.record_asset(
        episode_id=ep_id,
        asset_type=AssetType.IMAGE,
        file_path="/storage/img1.png",
        provider="TogetherAI",
        model_name="flux-1-schnell",
        license_type=CommercialLicenseType.FULL_COMMERCIAL_OWNERSHIP,
        license_id="TOGETHER-COMM-1",
        cleared=True,
    )
    assert img_rec.cleared_for_commercial_monetization is True

    # Register voice asset
    voice_rec = rights_ledger.record_asset(
        episode_id=ep_id,
        asset_type=AssetType.VOICE,
        file_path="/storage/voice1.wav",
        provider="Azure",
        model_name="te-IN-MohanNeural",
        license_type=CommercialLicenseType.COMMERCIAL_ROYALTY_FREE,
        license_id="AZURE-SPEECH-1",
        cleared=True,
    )
    assert voice_rec.cleared_for_commercial_monetization is True

    cleared, violations = rights_ledger.verify_episode_rights(ep_id)
    assert cleared is True
    assert len(violations) == 0


def test_unverified_or_uncleared_asset_blocks_rights():
    """Verify that unverified or uncleared assets fail the commercial verification."""
    ep_id = uuid4()
    rights_ledger.record_asset(
        episode_id=ep_id,
        asset_type=AssetType.MUSIC,
        file_path="/storage/bgm_unverified.mp3",
        provider="RandomWeb",
        model_name="unknown",
        license_type=CommercialLicenseType.UNVERIFIED,
        license_id="NONE",
        cleared=False,
    )

    cleared, violations = rights_ledger.verify_episode_rights(ep_id)
    assert cleared is False
    assert len(violations) >= 1


def test_adsense_compliance_screener_clean_and_dirty():
    """Verify 11-category AdSense screener and opening 7s profanity check."""
    clean_script = (
        "Welcome back to tech comedy! Today we explore the humorous side of working from home. "
        "From Zoom meetings in pajamas to pet interruptions, remote work has revolutionized offices."
    )
    dirty_script = (
        "This is an explicit murder plot with hate speech and stolen heroin recipe for firearms."
    )

    # Clean script audit
    clean_violations = screen_script_for_adsense(clean_script)
    assert len(clean_violations) == 0

    clean_eval = evaluate_ypp_safety(clean_script)
    assert clean_eval["is_monetization_safe"] is True
    assert clean_eval["risk_level"] == "LOW"

    # Dirty script audit
    dirty_violations = screen_script_for_adsense(dirty_script)
    assert "violence" in dirty_violations or "hate_speech" in dirty_violations or "drugs" in dirty_violations

    dirty_eval = evaluate_ypp_safety(dirty_script)
    assert dirty_eval["is_monetization_safe"] is False
    assert dirty_eval["risk_level"] in ("MEDIUM", "HIGH")


def test_opening_seven_sec_profanity_detection():
    """Verify opening 7-second zero-profanity enforcement for YouTube monetization."""
    bad_hook = "Fuck yeah, welcome to our brand new channel!"
    violations = screen_opening_profanity(bad_hook)
    assert len(violations) > 0


def test_synthetic_media_disclosure_payload():
    """Verify YouTube Data API synthetic media disclosure structure."""
    payload = get_synthetic_media_disclosure()
    assert payload["status"]["containsSyntheticMedia"] is True
    assert payload["status"]["selfDeclaredMadeForKids"] is False
    assert "c2pa" in payload


def test_evidence_bundle_compilation_and_serialization(tmp_path: Path):
    """Verify originality evidence bundle packaging and JSON persistence."""
    proj_id = uuid4()
    ep_id = uuid4()

    # Record compliant asset
    rights_ledger.record_asset(
        episode_id=ep_id,
        asset_type=AssetType.IMAGE,
        file_path="/storage/keyframe.png",
        provider="Flux",
        model_name="schnell",
        cleared=True,
    )

    bundle = build_evidence_bundle(
        project_id=proj_id,
        episode_id=ep_id,
        title="Tech Satire Ep 1",
        script_thesis="A lighthearted comedic take on remote IT culture.",
        research_sources=[{"title": "Remote Work Survey 2026", "url": "https://example.com/survey"}],
        originality_score=0.96,
    )

    assert bundle.monetization_approved is True
    assert bundle.total_assets_cleared == 1

    bundle_path = save_evidence_bundle(bundle, tmp_path)
    assert bundle_path.exists()

    data = json.loads(bundle_path.read_text(encoding="utf-8"))
    assert data["title"] == "Tech Satire Ep 1"
    assert data["monetization_approved"] is True
    assert len(data["rights_records"]) == 1


def test_local_video_qa_audit(tmp_path: Path):
    """Verify deterministic Video QA loudness and frame defect audit."""
    dummy_vid = tmp_path / "test_video.mp4"
    dummy_vid.write_bytes(b"dummy mp4 content")

    loudness = measure_loudness_ebur128(dummy_vid)
    assert loudness.integrated_lufs == -14.0
    assert loudness.lufs_passed is True

    defects = detect_frame_defects(dummy_vid)
    assert defects.defects_passed is True

    report = run_video_qa_audit(dummy_vid, duration_seconds=10.0)
    assert report.scores.composite_score >= 90.0
    assert report.scores.verdict == "PUBLISH_ELIGIBLE"
    assert report.passed is True


def test_qa_gate_agent_decision_matrix(tmp_path: Path):
    """Verify QA Gate Agent grants eligibility when compliant and blocks when violated."""
    ep_id = uuid4()
    dummy_vid = tmp_path / "gate_test.mp4"
    dummy_vid.write_bytes(b"dummy content")

    # 1. Unregistered asset -> Should block
    clean_script = "A wonderful educational presentation about solar energy systems."
    eligible, report, reasons = qa_gate_agent.audit_rendered_episode(
        episode_id=ep_id,
        video_path=dummy_vid,
        script_text=clean_script,
    )
    assert eligible is False
    assert any("No asset rights recorded" in r for r in reasons)

    # 2. Register cleared asset -> Should pass
    rights_ledger.record_asset(
        episode_id=ep_id,
        asset_type=AssetType.VOICE,
        file_path="/storage/clean_audio.wav",
        provider="Azure",
        model_name="en-US",
        cleared=True,
    )
    eligible2, report2, reasons2 = qa_gate_agent.audit_rendered_episode(
        episode_id=ep_id,
        video_path=dummy_vid,
        script_text=clean_script,
    )
    assert eligible2 is True
    assert len(reasons2) == 0
    assert report2.scores.verdict == "PUBLISH_ELIGIBLE"


@pytest.mark.asyncio
async def test_liveportrait_talking_avatar_simulator(tmp_path: Path):
    """Verify talking avatar animator returns valid generated video in simulator mode."""
    portrait = tmp_path / "face.png"
    portrait.write_bytes(b"dummy image")
    audio = tmp_path / "speech.wav"
    audio.write_bytes(b"dummy audio")
    out_dir = tmp_path / "avatar_out"
    output_mp4 = out_dir / "avatar.mp4"
    avatar_video = await liveportrait_adapter.animate_avatar(
        image_path=portrait,
        audio_path=audio,
        output_path=output_mp4,
        duration_seconds=2.0,
    )
    assert avatar_video.exists()
    assert avatar_video.suffix == ".mp4"
