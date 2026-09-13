"""MCP Decision Auditor for capturing and persisting AI model selection traces."""

import json
from pathlib import Path
from typing import Any
from datetime import datetime, timezone
from src.core.telemetry import logger


class MCPDecisionAuditor:
    """Collects and audits model selection decisions made by the Model Selector MCP Server."""

    def __init__(self):
        self.decisions: list[dict[str, Any]] = []

    def record_decision(self, decision: dict[str, Any]) -> None:
        """Record an MCP model selection event."""
        record = dict(decision)
        record["timestamp"] = datetime.now(timezone.utc).isoformat()
        self.decisions.append(record)

    def save_decision_log(
        self,
        output_dir: Path,
        metadata: dict[str, Any] | None = None,
    ) -> Path:
        """Persist structured mcp_decision_log.json into episode directory."""
        output_dir.mkdir(parents=True, exist_ok=True)
        log_path = output_dir / "mcp_decision_log.json"

        bundle = {
            "version": "1.0.0",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "metadata": metadata or {},
            "total_decisions": len(self.decisions),
            "decisions": self.decisions,
        }

        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(bundle, f, indent=2)

        logger.info(f"mcp_decision_log_saved: path={log_path}, decisions_count={len(self.decisions)}")
        return log_path

    def get_summary(self) -> list[dict[str, str]]:
        """Return formatted summary list for CLI and reporting."""
        summary = []
        for d in self.decisions:
            summary.append({
                "category": d.get("category", "unknown"),
                "model": f"{d.get('provider', '')} {d.get('selected_model', '')}".strip(),
                "reasoning": d.get("selection_reasoning", d.get("status_reason", "")),
                "cost": f"${d.get('unit_cost_usd', 0.0):.6f}/{d.get('unit_name', 'unit')}",
                "fallback": "Yes" if d.get("fallback_triggered") else "No",
            })
        return summary


async def audit_pipeline_models(
    language: str = "en",
    budget_tier: str = "balanced",
    output_dir: Path | None = None,
    metadata: dict[str, Any] | None = None,
) -> MCPDecisionAuditor:
    """Evaluate and audit MCP model choices across all video production pipeline stages."""
    from src.mcp.model_selector.server import select_best_model

    auditor = MCPDecisionAuditor()
    for cat in ("script_creative", "visual_image", "voice_tts", "music_bgm"):
        dec = await select_best_model(category=cat, language=language, budget_tier=budget_tier)
        auditor.record_decision(dec)

    if output_dir:
        auditor.save_decision_log(output_dir, metadata=metadata)

    return auditor


__all__ = ["MCPDecisionAuditor", "audit_pipeline_models"]
