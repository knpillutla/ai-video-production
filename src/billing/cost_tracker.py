"""Pre-Flight Cost Estimation and Post-Execution Model Spend Actualization Engine."""

import json
from datetime import datetime, timezone
from pathlib import Path
from src.core.telemetry import logger
from src.domain.cost import EpisodeCostRecord, ModelCostItem
from src.domain.creative import Episode


def calculate_preflight_estimate(episode: Episode) -> EpisodeCostRecord:
    """Calculate itemized pre-flight cost prediction and model breakdown before production."""
    duration_mins = max(1, episode.duration_seconds // 60)
    tts_enabled = getattr(episode.options, "enable_tts", True)
    stems_count = len(episode.options.target_languages) if tts_enabled else 0
    est_images = max(3, duration_mins * 3)

    items: list[ModelCostItem] = [
        ModelCostItem(
            component="Creative Script & Retention Loop",
            model_name="Gemini 1.5 Pro",
            category="scripting",
            unit_cost_usd=0.00000125,
            predicted_units="~14,000 tokens",
            predicted_cost_usd=0.0200,
        ),
        ModelCostItem(
            component=f"Multilingual Neural Voiceovers ({stems_count} Stems)" if tts_enabled else "Neural Voiceovers (Disabled)",
            model_name="Azure Speech HD (Neural)",
            category="voice",
            unit_cost_usd=0.000016,
            predicted_units=f"~{duration_mins * 600} characters" if tts_enabled else "0 characters (disabled)",
            predicted_cost_usd=round(0.0700 * max(1, stems_count), 4) if tts_enabled else 0.0,
        ),
        ModelCostItem(
            component="4K Keyframe Visual Diffusion",
            model_name="Together AI (FLUX.1-schnell)",
            category="visuals",
            unit_cost_usd=0.0030,
            predicted_units=f"{est_images} keyframes",
            predicted_cost_usd=round(est_images * 0.0030, 4),
        ),
        ModelCostItem(
            component="Original Commercial Soundtrack" if getattr(episode.options, "enable_bgm", True) else "Soundtrack / BGM (Disabled)",
            model_name="Suno v3.5 Pro",
            category="soundtrack",
            unit_cost_usd=0.0800,
            predicted_units="1 master soundtrack" if getattr(episode.options, "enable_bgm", True) else "0 tracks (disabled)",
            predicted_cost_usd=0.0800 if getattr(episode.options, "enable_bgm", True) else 0.0,
        ),
        ModelCostItem(
            component="Python Single-Pass FFmpeg Compositor",
            model_name="CPU FFmpeg Compositor",
            category="compute",
            unit_cost_usd=0.00028,
            predicted_units=f"~{max(12, duration_mins * 15)}s render",
            predicted_cost_usd=round(max(12, duration_mins * 15) * 0.00028, 4),
        ),
    ]

    # Optional Fal.ai hero motion or talking avatar items if configured
    if getattr(episode.options, "enable_video_motion", False):
        items.append(
            ModelCostItem(
                component="Hero Action Motion Synthesis",
                model_name="Fal.ai (Minimax Video-01)",
                category="motion",
                unit_cost_usd=0.1500,
                predicted_units="2 motion clips",
                predicted_cost_usd=0.3000,
            )
        )

    if getattr(episode.options, "enable_lipsync", False):
        items.append(
            ModelCostItem(
                component="Talking Avatar Lip-Sync",
                model_name="Fal.ai (LivePortrait)",
                category="lipsync",
                unit_cost_usd=0.0120,
                predicted_units="45s active speech",
                predicted_cost_usd=0.5400,
            )
        )

    predicted_total = round(sum(it.predicted_cost_usd for it in items), 4)

    record = EpisodeCostRecord(
        episode_id=episode.id,
        project_title=episode.title,
        predicted_total_usd=predicted_total,
        items=items,
        status="estimated",
        estimated_at=datetime.now(timezone.utc),
    )
    logger.info(f"cost_estimate_calculated: ep={episode.id}, total=${predicted_total:.4f}")
    return record


def actualize_production_cost(
    record: EpisodeCostRecord,
    execution_metrics: dict,
) -> EpisodeCostRecord:
    """Update the same cost record in-place with measured execution actuals and variances."""
    tokens = execution_metrics.get("tokens_used", 13420)
    chars = execution_metrics.get("voice_characters", 1450)
    images = execution_metrics.get("images_generated", 3)
    tracks = execution_metrics.get("music_tracks", 1)
    render_s = execution_metrics.get("render_seconds", 12.0)
    motion_clips = execution_metrics.get("motion_clips", 0)
    lipsync_s = execution_metrics.get("lipsync_seconds", 0.0)

    for item in record.items:
        if item.category == "scripting":
            item.actual_units = f"{tokens:,} tokens"
            item.actual_cost_usd = round(tokens * item.unit_cost_usd, 4)
        elif item.category == "voice":
            item.actual_units = f"{chars:,} characters"
            item.actual_cost_usd = round(chars * item.unit_cost_usd, 4)
        elif item.category == "visuals":
            item.actual_units = f"{images} keyframes"
            item.actual_cost_usd = round(images * item.unit_cost_usd, 4)
        elif item.category == "soundtrack":
            item.actual_units = f"{tracks} master soundtrack"
            item.actual_cost_usd = round(tracks * item.unit_cost_usd, 4)
        elif item.category == "compute":
            item.actual_units = f"{render_s:.1f}s render"
            item.actual_cost_usd = round(render_s * item.unit_cost_usd, 4)
        elif item.category == "motion":
            item.actual_units = f"{motion_clips} motion clips"
            item.actual_cost_usd = round(motion_clips * item.unit_cost_usd, 4)
        elif item.category == "lipsync":
            item.actual_units = f"{lipsync_s:.1f}s lipsync"
            item.actual_cost_usd = round(lipsync_s * item.unit_cost_usd, 4)

        if item.actual_cost_usd is not None:
            item.variance_usd = round(item.actual_cost_usd - item.predicted_cost_usd, 4)
            if item.predicted_cost_usd > 0:
                item.variance_pct = round((item.variance_usd / item.predicted_cost_usd) * 100.0, 2)
            else:
                item.variance_pct = 0.0

    actual_total = round(sum(it.actual_cost_usd or 0.0 for it in record.items), 4)
    total_var = round(actual_total - record.predicted_total_usd, 4)

    record.actual_total_usd = actual_total
    record.total_variance_usd = total_var

    # Accuracy percentage: 100% means actual matched predicted exactly
    if record.predicted_total_usd > 0:
        pct_err = (abs(total_var) / record.predicted_total_usd) * 100.0
        record.accuracy_pct = round(max(0.0, 100.0 - pct_err), 2)
    else:
        record.accuracy_pct = 100.0

    record.status = "actualized"
    record.actualized_at = datetime.now(timezone.utc)
    logger.info(
        f"cost_actualized: ep={record.episode_id}, pred=${record.predicted_total_usd:.4f}, "
        f"actual=${actual_total:.4f}, var=${total_var:.4f}, acc={record.accuracy_pct}%"
    )
    return record


def save_cost_report(record: EpisodeCostRecord, output_dir: Path | str) -> Path:
    """Serialize and save the cost audit report into the episode vault directory."""
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    report_path = out_dir / "cost_report.json"

    data = json.loads(record.model_dump_json())
    report_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    logger.info(f"cost_report_saved: {report_path}")
    return report_path


__all__ = [
    "calculate_preflight_estimate",
    "actualize_production_cost",
    "save_cost_report",
]
