"""Tests for MCP Decision-Making Engine, Decision Auditor, and Telemetry File Logging."""

import json
from pathlib import Path
import pytest

from src.core.telemetry import logger
from src.mcp.model_selector.audit import MCPDecisionAuditor, audit_pipeline_models
from src.mcp.model_selector.server import select_best_model


@pytest.mark.asyncio
async def test_mcp_select_best_model_decision_reasoning():
    """Verify select_best_model returns selection_reasoning, alternatives, and factors."""
    decision = await select_best_model(category="script_creative", language="te")
    assert decision["selected_model"] == "gemini-1.5-pro"
    assert "selection_reasoning" in decision
    assert "Indic" in decision["selection_reasoning"] or "multilingual" in decision["selection_reasoning"]
    assert "alternatives_evaluated" in decision
    assert "decision_factors" in decision
    assert decision["fallback_triggered"] is False


@pytest.mark.asyncio
async def test_mcp_decision_auditor_persistence(tmp_path: Path):
    """Verify MCPDecisionAuditor saves structured mcp_decision_log.json to disk."""
    auditor = await audit_pipeline_models(
        language="en",
        budget_tier="balanced",
        output_dir=tmp_path,
        metadata={"title": "Test Title", "episode_id": "test-ep-01"},
    )
    assert len(auditor.decisions) == 4
    summary = auditor.get_summary()
    assert len(summary) == 4
    assert any(s["category"] == "script_creative" for s in summary)

    log_file = tmp_path / "mcp_decision_log.json"
    assert log_file.exists()
    with open(log_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["version"] == "1.0.0"
    assert data["metadata"]["title"] == "Test Title"
    assert len(data["decisions"]) == 4


def test_telemetry_file_logging():
    """Verify that logger writes to disk in logs/studio.log."""
    log_path = Path("logs") / "studio.log"
    logger.info("telemetry_file_logging_verification_probe")
    assert log_path.exists()
    with open(log_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "telemetry_file_logging_verification_probe" in content
