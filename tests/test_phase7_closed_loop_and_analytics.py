"""Phase 7 Tests: Closed-Loop Analytics, Growth A/B & Audience Retention Engine."""

from uuid import uuid4
import numpy as np
import pytest
from httpx import ASGITransport, AsyncClient

from src.analytics.ab_testing import ab_optimizer
from src.analytics.feedback_loop import AnalyticsFeedbackLoop, VideoPerformanceMetric, feedback_loop
from src.api.main import app
from src.domain.creative import Episode, Show
from src.domain.repo import repo
from src.domain.user import User
from src.scripts.local_beat_detector import beat_detector


@pytest.fixture
def auth_creator():
    """Create test creator and access headers."""
    user = User(
        id=uuid4(),
        google_sub=f"sub_{uuid4().hex[:8]}",
        email=f"phase7_{uuid4().hex[:6]}@cineai.studio",
        display_name="Phase 7 Growth Director",
        storage_container_name="user-phase7-test",
    )
    repo.save_user(user)
    return user


@pytest.fixture
def creator_episode(auth_creator):
    """Create test episode in repo."""
    show = repo.save_show(
        Show(user_id=auth_creator.id, title="Growth Universe", slug="growth-u", genre="comedy")
    )
    return repo.save_episode(
        Episode(
            user_id=auth_creator.id,
            show_id=show.id,
            title="WFH Remote Secrets Revealed",
            episode_number=1,
            duration_seconds=480,
        )
    )


def test_beat_detector_synthetic_and_waveform_analysis():
    """Verify beat detector extracts BPM, downbeat intervals, and snaps scene cuts."""
    # 1. Synthetic fallback test
    grid = beat_detector.analyze_audio_buffer(None, sample_rate=44100, duration_seconds=12.0)
    assert grid.bpm == 120.0
    assert len(grid.beat_timestamps) == 24  # 12s * 2 beats/sec
    assert len(grid.downbeat_timestamps) == 6  # 1 downbeat per 4 beats

    # 2. Alignment test
    rough_cuts = [4.1, 3.9, 4.2]
    snapped = beat_detector.align_scene_cuts_to_beats(rough_cuts, grid)
    assert len(snapped) == 4
    assert snapped[0] == 0.0
    # Snapped to nearest downbeat (e.g., 4.0, 8.0, 12.0)
    assert snapped[1] == 4.0
    assert snapped[2] == 8.0

    # 3. Waveform energy analysis test
    t = np.linspace(0, 2.0, 44100 * 2, endpoint=False)
    # Synthetic pulses at 0.5s intervals (120 BPM)
    signal = np.sin(2 * np.pi * 440 * t) * (np.sin(2 * np.pi * 2 * t) ** 4)
    wave_grid = beat_detector.analyze_audio_buffer(signal, sample_rate=44100)
    assert wave_grid.duration_seconds == 2.0
    assert len(wave_grid.beat_timestamps) >= 1


def test_feedback_loop_pacing_and_hook_adaptation():
    """Verify Bayesian calibration shifts hook weights and speeds up scene pacing on low retention."""
    loop = AnalyticsFeedbackLoop()
    initial_scene_sec = loop.priors.recommended_scene_duration_sec
    initial_curiosity_w = loop.priors.hook_weights["curiosity_intrigue"]

    # Ingest high-performing video with curiosity hook
    high_metric = VideoPerformanceMetric(
        video_id="yt_high_01",
        views=15000,
        impressions_ctr=0.11,
        average_view_duration_pct=0.78,
        retention_at_30s=0.82,
        hook_style_used="curiosity_intrigue",
    )
    priors = loop.ingest_metrics(high_metric)
    assert priors.hook_weights["curiosity_intrigue"] > initial_curiosity_w
    assert loop.get_best_hook_style() == "curiosity_intrigue"

    # Ingest low retention video (<60% at 30s) -> pacing must shorten
    low_metric = VideoPerformanceMetric(
        video_id="yt_low_01",
        views=3000,
        impressions_ctr=0.04,
        average_view_duration_pct=0.35,
        retention_at_30s=0.48,
        hook_style_used="direct_question",
    )
    priors_after_drop = loop.ingest_metrics(low_metric)
    assert priors_after_drop.recommended_scene_duration_sec < initial_scene_sec
    assert priors_after_drop.recommended_words_per_minute > 145


def test_ab_testing_flight_and_evaluation():
    """Verify generation of 3x3 title and thumbnail variants and statistical winner selection."""
    flight = ab_optimizer.generate_flight("ep_999", "IT Standup Comedy Confusions", "telugu_comedy")
    assert len(flight.title_variants) == 3
    assert len(flight.thumbnail_variants) == 3
    assert flight.status == "active"

    # Ingest simulated CTR telemetry
    sim_data = {
        flight.title_variants[0].variant_id: {"impressions": 2000, "clicks": 110},   # 5.5%
        flight.title_variants[1].variant_id: {"impressions": 2000, "clicks": 210},   # 10.5% (WINNER)
        flight.title_variants[2].variant_id: {"impressions": 2000, "clicks": 140},   # 7.0%
        flight.thumbnail_variants[0].variant_id: {"impressions": 2000, "clicks": 180},
        flight.thumbnail_variants[1].variant_id: {"impressions": 2000, "clicks": 240}, # 12.0% (WINNER)
        flight.thumbnail_variants[2].variant_id: {"impressions": 2000, "clicks": 120},
    }

    concluded = ab_optimizer.ingest_flight_results(flight.flight_id, sim_data)
    assert concluded.status == "concluded"
    assert concluded.winning_title == flight.title_variants[1].content
    assert concluded.winning_thumbnail == flight.thumbnail_variants[1].content
    assert flight.title_variants[1].is_winner is True


@pytest.mark.asyncio
async def test_analytics_api_endpoints(auth_creator, creator_episode):
    """Verify RESTful API endpoints for metrics ingestion, webhooks, priors, and retention curves."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        auth_res = await client.post(
            "/api/auth/test-token",
            json={"email": auth_creator.email, "display_name": auth_creator.display_name},
        )
        headers = {"Authorization": f"Bearer {auth_res.json()['token']}"}

        # 1. Ingest metrics endpoint
        ingest_res = await client.post(
            "/api/analytics/ingest-metrics",
            headers=headers,
            json={
                "video_id": "yt_prod_101",
                "views": 5200,
                "impressions_ctr": 0.092,
                "average_view_duration_pct": 0.65,
                "retention_at_30s": 0.71,
                "hook_style_used": "curiosity_intrigue",
            },
        )
        assert ingest_res.status_code == 200
        assert ingest_res.json()["status"] == "calibrated"

        # 2. Webhook simulation endpoint
        hook_res = await client.post(
            "/api/analytics/webhook",
            json={"video_id": "yt_webhook_02", "retention_at_30s": 0.74, "impressions_ctr": 0.088},
        )
        assert hook_res.status_code == 200
        assert hook_res.json()["status"] == "success"

        # 3. Priors endpoint
        priors_res = await client.get("/api/analytics/priors")
        assert priors_res.status_code == 200
        assert "target_scene_duration_sec" in priors_res.json()

        # 4. A/B Test Flight Generation & Evaluation
        ab_gen_res = await client.post(
            "/api/analytics/ab-tests/generate",
            headers=headers,
            json={"episode_id": str(creator_episode.id), "title": creator_episode.title, "theme": "telugu_comedy"},
        )
        assert ab_gen_res.status_code == 200
        flight_id = ab_gen_res.json()["flight_id"]

        eval_res = await client.post(f"/api/analytics/ab-tests/{flight_id}/evaluate", headers=headers)
        assert eval_res.status_code == 200
        assert eval_res.json()["status"] == "concluded"
        assert eval_res.json()["winning_title"] is not None

        # 5. Retention Curve Endpoint
        ret_res = await client.get(f"/api/analytics/retention-curve/{creator_episode.id}")
        assert ret_res.status_code == 200
        assert "retention_curve" in ret_res.json()
        assert len(ret_res.json()["retention_curve"]) > 10

        # 6. Beat Detection Endpoint
        beat_res = await client.post(
            "/api/analytics/beat-detect",
            json={"bpm": 128.0, "duration_seconds": 30.0, "scene_durations": [4.0, 4.0, 4.0]},
        )
        assert beat_res.status_code == 200
        assert beat_res.json()["bpm"] == 128.0
        assert len(beat_res.json()["aligned_scene_cuts"]) == 4
