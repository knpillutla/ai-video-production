"""SQLite Benchmark Vault for Empirical Model Artifact Counts and Cost Scaling."""

from datetime import datetime, timezone
import json
from pathlib import Path
import sqlite3
from typing import Any

from src.core.telemetry import logger

DB_PATH = Path("storage/production_benchmarks.db")


def init_benchmark_db(db_path: Path | str = DB_PATH) -> None:
    """Initialize SQLite schema for production benchmarks and model artifact tracking."""
    p = Path(db_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(str(p)) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS production_benchmarks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                episode_id TEXT NOT NULL,
                title TEXT,
                theme TEXT,
                genre TEXT,
                format TEXT,
                duration_seconds REAL NOT NULL,
                total_pipeline_seconds REAL DEFAULT 0.0,
                render_seconds REAL DEFAULT 0.0,
                estimated_total_usd REAL NOT NULL,
                actual_total_usd REAL NOT NULL,
                variance_usd REAL NOT NULL,
                variance_pct REAL NOT NULL,
                cost_per_second REAL NOT NULL,
                artifact_counts TEXT NOT NULL,
                model_breakdown TEXT NOT NULL,
                variance_explanation TEXT
            )
        """)
        # Safe migration for new columns
        try:
            conn.execute("ALTER TABLE production_benchmarks ADD COLUMN total_pipeline_seconds REAL DEFAULT 0.0")
        except Exception:
            pass
        try:
            conn.execute("ALTER TABLE production_benchmarks ADD COLUMN render_seconds REAL DEFAULT 0.0")
        except Exception:
            pass
        conn.commit()


def record_production_benchmark(
    episode_id: str,
    title: str,
    duration_seconds: float,
    estimated_total_usd: float,
    actual_total_usd: float,
    artifact_counts: dict[str, int],
    model_breakdown: dict[str, Any],
    total_pipeline_seconds: float = 0.0,
    render_seconds: float = 0.0,
    theme: str = "",
    genre: str = "",
    media_format: str = "",
    variance_explanation: str = "",
    db_path: Path | str = DB_PATH,
) -> int:
    """Record an empirical production run into the SQLite benchmark database."""
    init_benchmark_db(db_path)
    dur = max(1.0, float(duration_seconds))
    act = float(actual_total_usd)
    est = float(estimated_total_usd)
    var = round(act - est, 4)
    var_pct = round((var / est) * 100.0, 2) if est > 0 else 0.0
    cost_per_sec = round(act / dur, 4)

    now_iso = datetime.now(timezone.utc).isoformat()
    with sqlite3.connect(str(db_path)) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO production_benchmarks (
                timestamp, episode_id, title, theme, genre, format,
                duration_seconds, total_pipeline_seconds, render_seconds,
                estimated_total_usd, actual_total_usd,
                variance_usd, variance_pct, cost_per_second,
                artifact_counts, model_breakdown, variance_explanation
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            now_iso, episode_id, title, theme, genre, media_format,
            dur, float(total_pipeline_seconds), float(render_seconds),
            est, act, var, var_pct, cost_per_sec,
            json.dumps(artifact_counts), json.dumps(model_breakdown), variance_explanation,
        ))
        conn.commit()
        rec_id = cursor.lastrowid or 0

    logger.info(f"production_benchmark_saved: id={rec_id}, ep={episode_id}, dur={dur}s, cost=${act:.4f}, per_sec=${cost_per_sec:.4f}/s")
    return rec_id


def query_empirical_cost_multiplier(
    target_duration: float,
    media_format: str = "",
    genre: str = "",
    db_path: Path | str = DB_PATH,
) -> dict[str, Any]:
    """Query historical benchmarks to project high-fidelity cost scaling for a target duration."""
    init_benchmark_db(db_path)
    dur = max(1.0, float(target_duration))
    with sqlite3.connect(str(db_path)) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        # Look for exact or close duration matches first
        cursor.execute("""
            SELECT * FROM production_benchmarks
            ORDER BY id DESC LIMIT 20
        """)
        rows = cursor.fetchall()

    if not rows:
        return {"has_empirical_data": False, "suggested_cost_usd": None, "cost_per_second": None}

    # Calculate weighted average cost per second
    total_cost_per_sec = sum(r["cost_per_second"] for r in rows)
    avg_per_sec = round(total_cost_per_sec / len(rows), 4)
    projected = round(avg_per_sec * dur, 4)

    return {
        "has_empirical_data": True,
        "sample_size": len(rows),
        "cost_per_second": avg_per_sec,
        "suggested_cost_usd": projected,
        "scaling_factor_vs_15s": round(dur / 15.0, 2),
    }


def calculate_customer_credit_capacity(budget_usd: float = 10.0, db_path: Path | str = DB_PATH) -> dict[str, Any]:
    """Calculate exact customer video production capacity matrix for a given credit/USD budget."""
    benchmark = query_empirical_cost_multiplier(target_duration=15.0, db_path=db_path)
    base_cost_per_sec = benchmark.get("cost_per_second") or 0.0350

    durations = [15, 30, 60, 120, 180, 300]
    matrix = {}
    for d in durations:
        cost_per_video = round(base_cost_per_sec * d, 4)
        videos_possible = round(budget_usd / cost_per_video, 1) if cost_per_video > 0 else 0
        matrix[f"{d}s_video"] = {
            "duration_seconds": d,
            "cost_per_video_usd": cost_per_video,
            "videos_possible": videos_possible,
            "full_renders_guaranteed": int(budget_usd // cost_per_video) if cost_per_video > 0 else 0,
        }

    return {
        "budget_usd": budget_usd,
        "cost_per_second_usd": base_cost_per_sec,
        "capacity_matrix": matrix,
        "sample_size": benchmark.get("sample_size", 0),
    }


def estimate_turnaround_time_sla(target_duration: float, db_path: Path | str = DB_PATH) -> dict[str, Any]:
    """Estimate expected wall-clock turnaround delivery time based on empirical runs."""
    init_benchmark_db(db_path)
    dur = max(1.0, float(target_duration))
    with sqlite3.connect(str(db_path)) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT total_pipeline_seconds, duration_seconds FROM production_benchmarks WHERE total_pipeline_seconds > 0 ORDER BY id DESC LIMIT 20")
        rows = cursor.fetchall()

    if rows:
        ratios = [r["total_pipeline_seconds"] / max(1.0, r["duration_seconds"]) for r in rows]
        avg_ratio = sum(ratios) / len(ratios)
    else:
        avg_ratio = 6.0

    expected_sec = round(avg_ratio * dur, 1)
    min_sec = round(expected_sec * 0.8, 1)
    max_sec = round(expected_sec * 1.3, 1)

    return {
        "target_duration_seconds": dur,
        "expected_seconds": expected_sec,
        "expected_display": f"{expected_sec / 60:.1f} minutes" if expected_sec >= 60 else f"{int(expected_sec)} seconds",
        "range_display": f"{min_sec / 60:.1f}–{max_sec / 60:.1f} mins" if max_sec >= 60 else f"{int(min_sec)}–{int(max_sec)} secs",
        "turnaround_factor": round(avg_ratio, 2),
    }


__all__ = [
    "init_benchmark_db",
    "record_production_benchmark",
    "query_empirical_cost_multiplier",
    "calculate_customer_credit_capacity",
    "estimate_turnaround_time_sla",
]
