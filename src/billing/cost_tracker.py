"""Pre-Flight Cost Estimation and Post-Execution Model Spend Actualization Engine."""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from src.core.telemetry import logger
from src.domain.cost import EpisodeCostRecord, ModelCostItem
from src.domain.creative import Episode


_CALIBRATION_FILE = Path("storage/cost_calibration.json")

_DEFAULT_PROVIDER_MODELS = {
    "Google Gemini/gemini-1.5-pro": {"unit_cost": 0.00000125, "category": "scripting", "unit": "tokens"},
    "Google Gemini/gemini-1.5-flash": {"unit_cost": 0.000000075, "category": "scripting", "unit": "tokens"},
    "Fal.ai/FLUX.1-dev": {"unit_cost": 0.0250, "category": "visuals", "unit": "keyframes"},
    "Together AI/FLUX.1-schnell": {"unit_cost": 0.0030, "category": "visuals", "unit": "keyframes"},
    "Fal.ai/Kling-v1.5-Pro": {"unit_cost": 0.1400, "category": "motion", "unit": "clips"},
    "Azure Speech HD/Neural": {"unit_cost": 0.000016, "category": "voice", "unit": "characters"},
    "Edge-TTS/Serverless": {"unit_cost": 0.0000, "category": "voice", "unit": "characters"},
    "Suno/v3.5-pro": {"unit_cost": 0.0800, "category": "soundtrack", "unit": "tracks"},
    "FFmpeg/CPU-Compositor": {"unit_cost": 0.00028, "category": "compute", "unit": "seconds"},
}


def load_cost_calibration() -> dict[str, Any]:
    """Load empirical actuals calibration multipliers and provider/model cost ledger."""
    defaults: dict[str, Any] = {
        "tokens_per_sec": 28.0,
        "chars_per_sec": 14.0,
        "render_sec_per_video_sec": 0.8,
        "provider_models": dict(_DEFAULT_PROVIDER_MODELS),
        "episodes_calibrated": 0,
        "last_updated": datetime.now(timezone.utc).isoformat(),
    }
    if _CALIBRATION_FILE.is_file():
        try:
            stored = json.loads(_CALIBRATION_FILE.read_text(encoding="utf-8"))
            if "provider_models" in stored:
                defaults["provider_models"].update(stored["provider_models"])
            for k in ("tokens_per_sec", "chars_per_sec", "render_sec_per_video_sec", "episodes_calibrated"):
                if k in stored:
                    defaults[k] = stored[k]
        except Exception:
            pass
    return defaults


def update_cost_calibration(record: EpisodeCostRecord, execution_metrics: dict, duration_seconds: float = 10.0) -> None:
    """Update running calibration weights and provider/model rates using exponential moving average."""
    calib = load_cost_calibration()
    dur = max(1.0, float(duration_seconds))
    tokens = execution_metrics.get("tokens_used")
    chars = execution_metrics.get("voice_characters")
    render_s = execution_metrics.get("render_seconds")

    alpha = 0.35  # Learning rate / smoothing factor
    if tokens and tokens > 0:
        calib["tokens_per_sec"] = round(calib["tokens_per_sec"] * (1 - alpha) + (tokens / dur) * alpha, 2)
    if chars and chars > 0:
        calib["chars_per_sec"] = round(calib["chars_per_sec"] * (1 - alpha) + (chars / dur) * alpha, 2)
    if render_s and render_s > 0:
        calib["render_sec_per_video_sec"] = round(calib["render_sec_per_video_sec"] * (1 - alpha) + (render_s / dur) * alpha, 2)

    # Record provider & model specific unit actuals
    for item in record.items:
        key = f"{item.model_name}"
        if key not in calib["provider_models"]:
            calib["provider_models"][key] = {
                "unit_cost": item.unit_cost_usd,
                "category": item.category,
                "unit": item.actual_units.split()[-1] if item.actual_units else "units",
            }

    calib["episodes_calibrated"] = calib.get("episodes_calibrated", 0) + 1
    calib["last_updated"] = datetime.now(timezone.utc).isoformat()

    try:
        _CALIBRATION_FILE.parent.mkdir(parents=True, exist_ok=True)
        _CALIBRATION_FILE.write_text(json.dumps(calib, indent=2), encoding="utf-8")
        logger.info(f"cost_calibration_updated: eps={calib['episodes_calibrated']}, tokens/s={calib['tokens_per_sec']}, chars/s={calib['chars_per_sec']}")
    except Exception as ex:
        logger.warning(f"cost_calibration_save_failed: {ex}")


def calculate_preflight_estimate(episode: Episode) -> EpisodeCostRecord:
    """Calculate itemized pre-flight cost prediction and model breakdown calibrated by historical actuals."""
    calib = load_cost_calibration()
    pm = calib.get("provider_models", {})

    dur_sec = max(5.0, float(episode.duration_seconds))
    duration_mins = max(1, int(dur_sec // 60))
    tts_enabled = getattr(episode.options, "enable_tts", True)
    stems_count = len(episode.options.target_languages) if tts_enabled else 0
    est_scenes = getattr(episode, "scenes_count", None) or (max(2, int(dur_sec / 5.0)) if dur_sec <= 20 else max(3, int(dur_sec / 15.0)))
    est_images = est_scenes

    pred_tokens = max(12000, int(dur_sec * calib["tokens_per_sec"]))
    pred_chars = max(300, int(dur_sec * calib["chars_per_sec"])) if tts_enabled else 0
    pred_render_s = max(8.0, round(dur_sec * calib["render_sec_per_video_sec"], 1))

    gemini_rate = pm.get("Google Gemini/gemini-1.5-pro", {}).get("unit_cost", 0.00000125)
    azure_rate = pm.get("Azure Speech HD/Neural", {}).get("unit_cost", 0.000016)
    flux_rate = pm.get("Fal.ai/FLUX.1-dev", {}).get("unit_cost", 0.0250)
    suno_rate = pm.get("Suno/v3.5-pro", {}).get("unit_cost", 0.0800)
    kling_rate = pm.get("Fal.ai/Kling-v1.5-Pro", {}).get("unit_cost", 0.1400)
    ffmpeg_rate = pm.get("FFmpeg/CPU-Compositor", {}).get("unit_cost", 0.00028)

    items: list[ModelCostItem] = [
        ModelCostItem(
            component="Creative Script & Retention Loop",
            model_name="Gemini 1.5 Pro",
            category="scripting",
            unit_cost_usd=gemini_rate,
            predicted_units=f"~{pred_tokens:,} tokens",
            predicted_cost_usd=round(pred_tokens * gemini_rate, 4),
        ),
        ModelCostItem(
            component=f"Multilingual Neural Voiceovers ({stems_count} Stems)" if tts_enabled else "Neural Voiceovers (Disabled)",
            model_name="Azure Speech HD (Neural)",
            category="voice",
            unit_cost_usd=azure_rate,
            predicted_units=f"~{pred_chars:,} characters" if tts_enabled else "0 characters (disabled)",
            predicted_cost_usd=round(pred_chars * azure_rate * max(1, stems_count), 4) if tts_enabled else 0.0,
        ),
        ModelCostItem(
            component="4K Keyframe Visual Diffusion",
            model_name="Fal.ai FLUX.1-dev (28 steps)",
            category="visuals",
            unit_cost_usd=flux_rate,
            predicted_units=f"{est_images} keyframes",
            predicted_cost_usd=round(est_images * flux_rate, 4),
        ),
        ModelCostItem(
            component="Original Commercial Soundtrack" if getattr(episode.options, "enable_bgm", True) else "Soundtrack / BGM (Disabled)",
            model_name="Suno v3.5 Pro",
            category="soundtrack",
            unit_cost_usd=suno_rate,
            predicted_units="1 master soundtrack" if getattr(episode.options, "enable_bgm", True) else "0 tracks (disabled)",
            predicted_cost_usd=suno_rate if getattr(episode.options, "enable_bgm", True) else 0.0,
        ),
        ModelCostItem(
            component="Python Single-Pass FFmpeg Compositor",
            model_name="CPU FFmpeg Compositor",
            category="compute",
            unit_cost_usd=ffmpeg_rate,
            predicted_units=f"~{pred_render_s:.1f}s render",
            predicted_cost_usd=round(pred_render_s * ffmpeg_rate, 4),
        ),
    ]

    if getattr(episode.options, "enable_video_motion", False):
        items.append(
            ModelCostItem(
                component="Hero Action Motion Synthesis",
                model_name="Fal.ai Kling 1.5 Pro",
                category="motion",
                unit_cost_usd=kling_rate,
                predicted_units=f"{est_scenes} motion clips",
                predicted_cost_usd=round(est_scenes * kling_rate, 4),
            )
        )

    if getattr(episode.options, "enable_lipsync", False):
        items.append(
            ModelCostItem(
                component="Talking Avatar Lip-Sync",
                model_name="Fal.ai (LatentSync)",
                category="lipsync",
                unit_cost_usd=0.0120,
                predicted_units=f"{dur_sec:.1f}s active speech",
                predicted_cost_usd=round(dur_sec * 0.0120, 4),
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
    duration_seconds: float = 10.0,
) -> EpisodeCostRecord:
    """Update cost record in-place with measured execution actuals and calibrate future estimates."""
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

    # Feed actuals into the calibration model to refine future estimates
    update_cost_calibration(record, execution_metrics, duration_seconds=duration_seconds)

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
    "load_cost_calibration",
    "update_cost_calibration",
    "calculate_preflight_estimate",
    "actualize_production_cost",
    "save_cost_report",
]
