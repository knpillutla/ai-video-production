"""Comprehensive Test Suite for Pre-Flight Cost Prediction and Post-Execution Actuals Governance."""

import json
from pathlib import Path
from uuid import uuid4
import pytest
from httpx import ASGITransport, AsyncClient

from src.api.main import app
from src.billing.cost_tracker import (
    actualize_production_cost,
    calculate_preflight_estimate,
    save_cost_report,
)
from src.compositor.pipeline import pipeline_coordinator
from src.domain.cost import EpisodeCostRecord, ModelCostItem
from src.domain.creative import Episode, Show
from src.domain.generation import GenerationOptions
from src.domain.repo import repo
from src.domain.user import User


@pytest.fixture(autouse=True)
def clean_repo():
    """Reset repo before and after each test."""
    repo.clear()
    yield
    repo.clear()


def test_preflight_cost_estimation_calculation():
    """Verify pre-flight estimation builds itemized breakdown across all planned models."""
    ep_id = uuid4()
    user_id = uuid4()
    show_id = uuid4()

    episode = Episode(
        id=ep_id,
        user_id=user_id,
        show_id=show_id,
        title="Test Budget Episode",
        duration_seconds=480,
    )

    cost_rec = calculate_preflight_estimate(episode)
    assert isinstance(cost_rec, EpisodeCostRecord)
    assert cost_rec.episode_id == ep_id
    assert cost_rec.status == "estimated"
    assert cost_rec.predicted_total_usd > 0
    assert cost_rec.actual_total_usd is None

    # Verify model categories present
    cats = {item.category for item in cost_rec.items}
    assert {"scripting", "voice", "visuals", "soundtrack", "compute"}.issubset(cats)

    for item in cost_rec.items:
        assert isinstance(item, ModelCostItem)
        assert item.predicted_cost_usd > 0
        assert item.predicted_units != ""
        assert item.actual_cost_usd is None


def test_actualize_production_cost_updates_same_record():
    """Verify post-execution actualization updates the exact same record in-place."""
    ep_id = uuid4()
    episode = Episode(
        id=ep_id,
        user_id=uuid4(),
        show_id=uuid4(),
        title="Test Actuals Episode",
        duration_seconds=480,
    )

    record = calculate_preflight_estimate(episode)
    initial_record_id = record.id
    initial_estimated_at = record.estimated_at
    initial_pred_total = record.predicted_total_usd

    metrics = {
        "tokens_used": 13420,
        "voice_characters": 1450,
        "images_generated": 3,
        "music_tracks": 1,
        "render_seconds": 11.5,
    }

    actualized = actualize_production_cost(record, metrics)

    # 1. Exact same record verified (immutable identity)
    assert actualized.id == initial_record_id
    assert actualized.estimated_at == initial_estimated_at
    assert actualized.status == "actualized"
    assert actualized.actualized_at is not None

    # 2. Predicted vs Actual totals and variance verified
    assert actualized.predicted_total_usd == initial_pred_total
    assert actualized.actual_total_usd is not None
    assert actualized.actual_total_usd > 0
    expected_var = round(actualized.actual_total_usd - actualized.predicted_total_usd, 4)
    assert actualized.total_variance_usd == expected_var
    assert 0.0 <= actualized.accuracy_pct <= 100.0

    # 3. Model-by-model actuals verified
    for item in actualized.items:
        assert item.actual_units is not None
        assert item.actual_cost_usd is not None
        assert item.variance_usd is not None
        assert item.variance_pct is not None
        assert item.variance_usd == round(item.actual_cost_usd - item.predicted_cost_usd, 4)


def test_cost_report_serialization_and_persistence(tmp_path: Path):
    """Verify cost report JSON is properly structured and persisted to disk."""
    ep_id = uuid4()
    episode = Episode(
        id=ep_id,
        user_id=uuid4(),
        show_id=uuid4(),
        title="Test Report Episode",
        duration_seconds=120,
    )

    record = calculate_preflight_estimate(episode)
    actualize_production_cost(record, {"tokens_used": 10000, "voice_characters": 800, "render_seconds": 8.0})

    out_file = save_cost_report(record, tmp_path)
    assert out_file.exists()
    assert out_file.name == "cost_report.json"

    data = json.loads(out_file.read_text(encoding="utf-8"))
    assert data["episode_id"] == str(ep_id)
    assert data["status"] == "actualized"
    assert "accuracy_pct" in data
    assert len(data["items"]) >= 5


@pytest.mark.asyncio
async def test_api_cost_estimation_and_drilldown_endpoints():
    """Verify FastAPI routes for pre-flight cost estimation and model drilldown."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Create user & auth token
        auth_resp = await ac.post("/api/auth/test-token", json={"email": "costuser@studio.com", "display_name": "Cost User"})
        token = auth_resp.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create show & episode
        show_resp = await ac.post("/api/shows", headers=headers, json={"title": "Tech Comedy", "genre": "comedy"})
        show_id = show_resp.json()["id"]

        ep_resp = await ac.post(
            "/api/projects",
            headers=headers,
            json={"show_id": show_id, "title": "Episode 1 Budget Test", "duration_seconds": 480},
        )
        ep_id = ep_resp.json()["id"]

        # 1. Pre-flight estimate API
        est_resp = await ac.post(f"/api/projects/{ep_id}/estimate-cost", headers=headers)
        assert est_resp.status_code == 200
        est_data = est_resp.json()
        assert est_data["total_cost_usd"] > 0

        # 2. Cost drilldown API
        drill_resp = await ac.get(f"/api/projects/{ep_id}/cost-breakdown", headers=headers)
        assert drill_resp.status_code == 200
        drill_data = drill_resp.json()
        assert drill_data["episode_id"] == ep_id
        assert drill_data["status"] == "estimated"
        assert len(drill_data["items"]) >= 5
        assert drill_data["predicted_total_usd"] > 0


@pytest.mark.asyncio
async def test_pipeline_actualizes_episode_cost_record():
    """Verify end-to-end production pipeline updates episode cost_record with measured actuals."""
    user = User(
        email="pipeline_cost@studio.com",
        display_name="Pipeline Cost Creator",
        google_sub="sub_pipeline_cost",
        storage_container_name="user-pipeline-cost",
        api_credit_balance_usd=50.0,
    )
    repo.save_user(user)

    show = Show(user_id=user.id, title="Cost Pipeline Show", slug="cost_pipeline_show")
    repo.save_show(show)

    episode = Episode(
        user_id=user.id,
        show_id=show.id,
        title="Episode Cost Pipeline Run",
        episode_number=1,
        duration_seconds=12,
        options=GenerationOptions(target_languages=["te"]),
    )
    repo.save_episode(episode)

    # Execute pipeline in dry_run mode
    final_video = await pipeline_coordinator.produce_episode_master(
        user_id=user.id,
        episode_id=episode.id,
        dry_run=True,
        language="te",
    )
    assert final_video.exists()

    # Verify updated episode in repo
    updated_ep = repo.get_episode(user.id, episode.id)
    assert updated_ep is not None
    assert updated_ep.cost_record is not None
    assert updated_ep.cost_record.status == "actualized"
    assert updated_ep.cost_record.actual_total_usd is not None
    assert updated_ep.cost_record.actual_total_usd > 0
    assert updated_ep.actual_spend_usd == updated_ep.cost_record.actual_total_usd
    assert updated_ep.cost_record.accuracy_pct is not None
    assert 0.0 <= updated_ep.cost_record.accuracy_pct <= 100.0
