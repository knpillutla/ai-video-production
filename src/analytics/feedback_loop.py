"""Closed-Loop YouTube Analytics Feedback Ingestion & Production Prior Calibration."""

from __future__ import annotations
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional
from src.core.telemetry import logger


@dataclass
class VideoPerformanceMetric:
    """Ingested YouTube Analytics metrics for a published video."""
    video_id: str
    views: int
    impressions_ctr: float
    average_view_duration_pct: float
    retention_at_30s: float
    hook_style_used: str = "curiosity_intrigue"
    scene_avg_duration_sec: float = 6.0
    copyright_claims: int = 0
    drop_off_timestamps: List[float] = field(default_factory=list)


@dataclass
class ProductionPriors:
    """Calibrated production hyperparameters tuned from audience analytics."""
    hook_weights: Dict[str, float] = field(default_factory=lambda: {
        "curiosity_intrigue": 0.35,
        "shock_fact": 0.25,
        "humor_relatable": 0.25,
        "direct_question": 0.15,
    })
    recommended_scene_duration_sec: float = 6.0
    recommended_words_per_minute: int = 145
    ducking_attenuation_db: float = -18.0
    samples_ingested: int = 0


class AnalyticsFeedbackLoop:
    """Ingests audience retention metrics and continuously calibrates script & pacing priors."""

    def __init__(self, persistence_file: Optional[Path | str] = None) -> None:
        self.persistence_file = Path(persistence_file) if persistence_file else None
        self.history: List[VideoPerformanceMetric] = []
        self.priors = ProductionPriors()
        self._load_state()

    def ingest_metrics(self, metric: VideoPerformanceMetric) -> ProductionPriors:
        """Ingest performance data and update Bayesian weights for hooks and scene pacing."""
        self.history.append(metric)
        self.priors.samples_ingested += 1

        # 1. Calibrate hook weights based on 30s retention and CTR performance
        hook = metric.hook_style_used
        if hook in self.priors.hook_weights:
            # Score combining 30s retention (70% weight) and impressions CTR (30% weight)
            performance_score = (metric.retention_at_30s * 0.7) + (min(metric.impressions_ctr * 10, 1.0) * 0.3)
            # Update weight using exponential moving average (alpha = 0.2)
            alpha = 0.2
            current_weight = self.priors.hook_weights[hook]
            updated_weight = (1 - alpha) * current_weight + alpha * performance_score
            self.priors.hook_weights[hook] = max(0.05, round(updated_weight, 4))

            # Normalize weights to sum to 1.0
            total_w = sum(self.priors.hook_weights.values())
            for k in self.priors.hook_weights:
                self.priors.hook_weights[k] = round(self.priors.hook_weights[k] / total_w, 4)

        # 2. Calibrate scene duration: shorten if early retention is low (<60%)
        if metric.retention_at_30s < 0.60 and self.priors.recommended_scene_duration_sec > 4.0:
            self.priors.recommended_scene_duration_sec = round(
                self.priors.recommended_scene_duration_sec - 0.5, 1
            )
            self.priors.recommended_words_per_minute = min(165, self.priors.recommended_words_per_minute + 5)
        elif metric.retention_at_30s >= 0.75 and self.priors.recommended_scene_duration_sec < 8.0:
            self.priors.recommended_scene_duration_sec = round(
                self.priors.recommended_scene_duration_sec + 0.2, 1
            )

        self._save_state()
        logger.info(
            f"feedback_loop_updated: video={metric.video_id}, samples={self.priors.samples_ingested}, "
            f"top_hook={max(self.priors.hook_weights, key=self.priors.hook_weights.get)}"
        )
        return self.priors

    def get_best_hook_style(self) -> str:
        """Return the highest-performing hook strategy based on ingested analytics."""
        return max(self.priors.hook_weights, key=lambda k: self.priors.hook_weights[k])

    def get_production_guidelines(self) -> Dict[str, Any]:
        """Provide calibrated directives for downstream script and compositor agents."""
        return {
            "top_hook_style": self.get_best_hook_style(),
            "hook_probabilities": self.priors.hook_weights,
            "target_scene_duration_sec": self.priors.recommended_scene_duration_sec,
            "target_wpm": self.priors.recommended_words_per_minute,
            "ducking_attenuation_db": self.priors.ducking_attenuation_db,
            "total_feedback_samples": self.priors.samples_ingested,
        }

    def _save_state(self) -> None:
        """Persist calibrated state to disk if path is provided."""
        if not self.persistence_file:
            return
        self.persistence_file.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "priors": asdict(self.priors),
            "history": [asdict(h) for h in self.history[-50:]],
        }
        self.persistence_file.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def _load_state(self) -> None:
        """Load calibrated state from disk if exists."""
        if not self.persistence_file or not self.persistence_file.exists():
            return
        try:
            raw = json.loads(self.persistence_file.read_text(encoding="utf-8"))
            priors_data = raw.get("priors", {})
            self.priors = ProductionPriors(**priors_data)
        except Exception as ex:
            logger.warning(f"Could not load feedback loop state: {ex}")


feedback_loop = AnalyticsFeedbackLoop()

__all__ = ["AnalyticsFeedbackLoop", "VideoPerformanceMetric", "ProductionPriors", "feedback_loop"]
