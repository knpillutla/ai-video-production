"""Phase 5 Tests: Scale, Multi-Language Audio (MLA), Dance Motion & Cloud Infrastructure."""

import os
import tempfile
from pathlib import Path
import pytest
from src.agents.choreography_agent import ChoreographyAgent
from src.agents.epic_cinema_agent import EpicCinemaAgent
from src.analytics.feedback_loop import (
    AnalyticsFeedbackLoop,
    VideoPerformanceMetric,
)
from deploy.multi_cloud.failover_probe import MultiCloudFailoverManager
from src.providers.dance.fal_mimicmotion import FalMimicMotionAdapter
from src.scripts.local_mla_muxer import AudioTrackSpec, MLAMuxer



def test_mla_muxer_ffmpeg_command_generation():
    """Verify MLAMuxer generates correct multi-stream FFmpeg arguments with ISO 639-2 tags."""
    muxer = MLAMuxer(ffmpeg_bin="ffmpeg")
    tracks = [
        AudioTrackSpec(language_code="en-US", audio_path="/tmp/en.wav", is_default=True, title="English [Original]"),
        AudioTrackSpec(language_code="te-IN", audio_path="/tmp/te.wav", is_default=False, title="Telugu [Dubbed]"),
        AudioTrackSpec(language_code="hi-IN", audio_path="/tmp/hi.wav", is_default=False, title="Hindi [Dubbed]"),
    ]

    cmd = muxer.compile_ffmpeg_args("/tmp/video.mp4", tracks, "/tmp/out.mp4")

    # Verify input mapping
    assert "-i" in cmd
    assert "/tmp/video.mp4" in cmd
    assert "/tmp/en.wav" in cmd
    assert "/tmp/te.wav" in cmd
    assert "/tmp/hi.wav" in cmd

    # Verify stream mapping
    assert "-map" in cmd
    assert "0:v:0" in cmd
    assert "1:a:0" in cmd
    assert "2:a:0" in cmd
    assert "3:a:0" in cmd

    # Verify ISO 639-2 language metadata
    joined = " ".join(cmd)
    assert "language=eng" in joined
    assert "language=tel" in joined
    assert "language=hin" in joined
    assert "-disposition:a:0 default" in joined
    assert "-disposition:a:1 0" in joined


def test_mla_youtube_manifest_builder():
    """Verify YouTube Data API v3 multi-language audio manifest structure."""
    muxer = MLAMuxer()
    tracks = [
        AudioTrackSpec(language_code="en", audio_path="audio_en.wav", is_default=True),
        AudioTrackSpec(language_code="te", audio_path="audio_te.wav", is_default=False),
        AudioTrackSpec(language_code="es", audio_path="audio_es.wav", is_default=False),
    ]

    manifest = muxer.build_youtube_mla_manifest("YT_VID_12345", tracks, default_language="en")

    assert manifest["video_id"] == "YT_VID_12345"
    assert manifest["total_audio_tracks"] == 3
    assert manifest["contains_mla"] is True
    assert manifest["tracks"][0]["audio_track_type"] == "primary"
    assert manifest["tracks"][0]["iso_639_2"] == "eng"
    assert manifest["tracks"][1]["audio_track_type"] == "dubbed"
    assert manifest["tracks"][1]["iso_639_2"] == "tel"
    assert manifest["tracks"][2]["iso_639_2"] == "spa"


def test_mla_muxer_execution_with_fallback():
    """Verify MLAMuxer produces output file safely in headless test environment."""
    muxer = MLAMuxer()
    with tempfile.TemporaryDirectory() as tmpdir:
        vid = Path(tmpdir) / "input.mp4"
        aud1 = Path(tmpdir) / "track1.wav"
        out = Path(tmpdir) / "output_mla.mp4"

        vid.write_bytes(b"VID_DATA")
        aud1.write_bytes(b"AUD_DATA")

        tracks = [AudioTrackSpec(language_code="en", audio_path=str(aud1), is_default=True)]
        result = muxer.mux_multi_language_audio(str(vid), tracks, str(out))

        assert Path(result).exists()
        assert Path(result).stat().st_size > 0


@pytest.mark.asyncio
async def test_fal_mimicmotion_mock_mode_and_clamping():
    """Verify MimicMotion adapter operates deterministically offline and clamps duration to <= 10s."""
    adapter = FalMimicMotionAdapter(api_key="mock_fal_key")

    with tempfile.TemporaryDirectory() as tmpdir:
        img = Path(tmpdir) / "character.png"
        audio = Path(tmpdir) / "dance_beat.wav"
        out = Path(tmpdir) / "dance_clip.mp4"

        img.write_bytes(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4")
        audio.write_bytes(b"RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00D\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00")

        # Pass 25s duration to test automatic cost-guard clamping to <= 10s
        rendered = await adapter.transfer_dance_motion(
            character_image_path=img,
            motion_or_audio_path=audio,
            output_path=out,
            duration_seconds=25.0,
        )

        assert rendered.exists()
        assert rendered.stat().st_size > 0


def test_choreography_agent_beat_grid_and_plan():
    """Verify choreography agent beat detection and structured dance routine generation."""
    agent = ChoreographyAgent()

    # 1. Beat grid at 120 BPM over 6 seconds -> 1 beat every 0.5s = 12 beats
    beats = agent.detect_beat_grid(tempo_bpm=120.0, duration_sec=6.0)
    assert len(beats) == 12
    assert beats[0] == 0.0
    assert beats[1] == 0.5

    # 2. Plan choreography for Tollywood Mass genre
    plan = agent.plan_choreography(genre="tollywood_mass", tempo_bpm=128.0, duration_sec=8.0)
    assert plan["genre"] == "tollywood_mass"
    assert plan["total_sections"] > 0
    assert any("mass_step" in s["move_name"] or "lungi_swag" in s["move_name"] for s in plan["choreography"])


@pytest.mark.asyncio
async def test_choreography_agent_synthesis_workflow():
    """Verify choreography agent end-to-end motion synthesis execution."""
    agent = ChoreographyAgent()

    with tempfile.TemporaryDirectory() as tmpdir:
        img = Path(tmpdir) / "hero.png"
        audio = Path(tmpdir) / "rhythm.wav"
        out = Path(tmpdir) / "mass_dance.mp4"

        img.write_bytes(b"IMAGE_BYTES")
        audio.write_bytes(b"AUDIO_BYTES")

        result = await agent.execute_dance_synthesis(
            character_image=img,
            audio_stem=audio,
            output_clip_path=out,
            genre="tollywood_mass",
            duration_sec=5.0,
        )

        assert result["status"] == "success"
        assert result["duration_sec"] == 5.0
        assert Path(result["video_path"]).exists()


def test_epic_cinema_agent_mass_action_direction():
    """Verify EpicCinemaAgent constructs high-tension narrative acts and elevation shots."""
    agent = EpicCinemaAgent()

    narrative = agent.direct_mass_action_scene(
        title="Battle of Mahishmati",
        protagonist="Baahubali",
        antagonist="Bhallaladeva",
        setting="Fortress Gate",
    )

    assert narrative["hero"] == "Baahubali"
    assert len(narrative["acts"]) == 3
    assert "Interval Bang" in narrative["acts"][2]["title"]
    assert "camera_move" in narrative["acts"][0]
    assert "foley_fx" in narrative["acts"][0]

    shots = agent.generate_elevation_shots("Baahubali", count=3)
    assert len(shots) == 3
    assert "slow-motion" in shots[0]["description"]


def test_closed_loop_feedback_ingestion_and_calibration():
    """Verify feedback loop updates Bayesian hook priors and adapts scene pacing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        persist_file = Path(tmpdir) / "feedback_state.json"
        loop = AnalyticsFeedbackLoop(persistence_file=persist_file)

        # Record high-performing curiosity hook video
        metric_success = VideoPerformanceMetric(
            video_id="v_001",
            views=250000,
            impressions_ctr=0.092,
            average_view_duration_pct=0.72,
            retention_at_30s=0.81,
            hook_style_used="curiosity_intrigue",
        )
        priors = loop.ingest_metrics(metric_success)

        # Weight for curiosity_intrigue should increase
        assert priors.hook_weights["curiosity_intrigue"] > 0.30
        assert priors.samples_ingested == 1
        assert persist_file.exists()

        # Ingest poor retention video to verify pacing adaptation
        metric_poor = VideoPerformanceMetric(
            video_id="v_002",
            views=10000,
            impressions_ctr=0.03,
            average_view_duration_pct=0.35,
            retention_at_30s=0.45,  # < 0.60 threshold
            hook_style_used="direct_question",
        )
        updated = loop.ingest_metrics(metric_poor)

        # Scene duration should be shortened to accelerate pacing
        assert updated.recommended_scene_duration_sec <= 6.0
        guidelines = loop.get_production_guidelines()
        assert "target_scene_duration_sec" in guidelines
        assert guidelines["total_feedback_samples"] == 2


@pytest.mark.asyncio
async def test_multi_cloud_failover_and_deployment_blueprints():
    """Verify multi-cloud failover manager and cloud scale-to-zero manifests."""
    manager = MultiCloudFailoverManager()
    assert manager.active_cloud == "azure"

    # Test cloud switch
    await manager.switch_traffic("gcp")
    assert manager.active_cloud == "gcp"

    # Verify cloud deployment blueprints exist with scale-to-zero definitions (Terraform only)
    azure_tf_path = Path("deploy/azure/terraform/main.tf")
    terraform_path = Path("deploy/gcp/terraform/cloud_run.tf")
    cloudflare_path = Path("deploy/multi_cloud/cloudflare_failover.tf")

    assert azure_tf_path.exists()
    assert terraform_path.exists()
    assert cloudflare_path.exists()

    azure_tf_content = azure_tf_path.read_text(encoding="utf-8")
    assert "min_replicas = 0" in azure_tf_content  # Scale to zero when idle


    tf_content = terraform_path.read_text(encoding="utf-8")
    assert "min_instance_count = 0" in tf_content  # Scale to zero when idle

    cf_content = cloudflare_path.read_text(encoding="utf-8")
    assert "cloudflare_load_balancer" in cf_content
