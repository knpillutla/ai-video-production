
"""Unit Tests for 3 Production Tiers (Low-Cost Quick Test, Balanced, High-Fidelity)."""

from pathlib import Path
from uuid import UUID
import pytest
from httpx import ASGITransport, AsyncClient

from src.api.main import app
from src.domain.repo import repo


@pytest.fixture(autouse=True)
def clean_repo():
    """Reset repo before and after each test."""
    repo.clear()
    yield
    repo.clear()


@pytest.mark.asyncio
async def test_estimate_cost_returns_three_production_tiers():
    """Verify estimate-cost endpoint returns available_tiers containing low_cost, balanced, and cinematic."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        auth_resp = await ac.post(
            "/api/auth/test-token",
            json={"email": "tier_creator@studio.com", "display_name": "Tier Creator"},
        )
        token = auth_resp.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}

        show_resp = await ac.post("/api/shows", headers=headers, json={"title": "Tier Show", "genre": "comedy"})
        show_id = show_resp.json()["id"]

        ep_resp = await ac.post(
            "/api/projects",
            headers=headers,
            json={"show_id": show_id, "title": "WFH Confusions EP 1", "duration_seconds": 60},
        )
        assert ep_resp.status_code == 201
        ep_id = ep_resp.json()["id"]

        est_resp = await ac.post(f"/api/projects/{ep_id}/estimate-cost", headers=headers)
        assert est_resp.status_code == 200
        data = est_resp.json()

        assert data["selected_tier"] == "balanced"
        tiers = data["available_tiers"]

        assert "low_cost" in tiers
        assert "balanced" in tiers
        assert "cinematic" in tiers

        low = tiers["low_cost"]
        bal = tiers["balanced"]
        cine = tiers["cinematic"]

        assert low["tier_key"] == "low_cost"
        assert bal["tier_key"] == "balanced"
        assert cine["tier_key"] == "cinematic"

        assert low["total_cost_usd"] < bal["total_cost_usd"] < cine["total_cost_usd"]
        assert low["total_cost_usd"] <= 0.05
        assert cine["total_cost_usd"] >= 0.20


@pytest.mark.asyncio
async def test_confirm_production_with_low_cost_tier():
    """Verify selecting low_cost tier charges minimal spend and enqueues with low_cost tier."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        auth_resp = await ac.post(
            "/api/auth/test-token",
            json={"email": "low_tester@studio.com", "display_name": "Low Tester"},
        )
        token = auth_resp.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}

        show_resp = await ac.post("/api/shows", headers=headers, json={"title": "Low Show", "genre": "comedy"})
        show_id = show_resp.json()["id"]

        ep_resp = await ac.post(
            "/api/projects",
            headers=headers,
            json={"show_id": show_id, "title": "Low Cost Video", "duration_seconds": 30},
        )
        assert ep_resp.status_code == 201
        ep_id = ep_resp.json()["id"]

        await ac.post(f"/api/projects/{ep_id}/estimate-cost", headers=headers)

        conf_resp = await ac.post(
            f"/api/projects/{ep_id}/confirm-production",
            headers=headers,
            json={"tier": "low_cost", "force_proceed": True},
        )
        assert conf_resp.status_code == 200
        conf_data = conf_resp.json()

        assert conf_data["status"] == "queued"
        assert conf_data["deducted_usd"] <= 0.05
        assert conf_data["remaining_balance_usd"] == round(10.0 - conf_data["deducted_usd"], 4)


@pytest.mark.asyncio
async def test_confirm_production_tier_insufficient_funds():
    """Verify user with low balance can afford low_cost but gets 402 on cinematic tier."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        auth_resp = await ac.post(
            "/api/auth/test-token",
            json={"email": "budget_user@studio.com", "display_name": "Budget User"},
        )
        token = auth_resp.json()["token"]
        user_id = auth_resp.json()["user"]["id"]
        headers = {"Authorization": f"Bearer {token}"}

        user = repo.get_user(UUID(user_id))
        user.api_credit_balance_usd = 0.03
        repo.save_user(user)

        show_resp = await ac.post("/api/shows", headers=headers, json={"title": "Budget Show", "genre": "comedy"})
        show_id = show_resp.json()["id"]

        ep_resp = await ac.post(
            "/api/projects",
            headers=headers,
            json={"show_id": show_id, "title": "Budget Episode", "duration_seconds": 30},
        )
        assert ep_resp.status_code == 201
        ep_id = ep_resp.json()["id"]

        await ac.post(f"/api/projects/{ep_id}/estimate-cost", headers=headers)

        cine_resp = await ac.post(
            f"/api/projects/{ep_id}/confirm-production",
            headers=headers,
            json={"tier": "cinematic", "force_proceed": True},
        )
        assert cine_resp.status_code == 402
        assert "Insufficient credits" in cine_resp.json()["detail"]

        low_resp = await ac.post(
            f"/api/projects/{ep_id}/confirm-production",
            headers=headers,
            json={"tier": "low_cost", "force_proceed": True},
        )
        assert low_resp.status_code == 200
        assert low_resp.json()["status"] == "queued"


def test_ui_html_tier_elements_and_javascript():
    """Verify index.html includes the 3-tier cards, sidebar selector, and JS handlers."""
    html_path = Path("src/static/index.html")
    assert html_path.exists(), "src/static/index.html not found"

    content = html_path.read_text(encoding="utf-8")

    assert 'id="tier-card-low_cost"' in content
    assert 'id="tier-card-balanced"' in content
    assert 'id="tier-card-cinematic"' in content

    assert 'id="tier-radio-low_cost"' in content
    assert 'id="tier-radio-balanced"' in content
    assert 'id="tier-radio-cinematic"' in content

    assert 'id="studio-tier-select"' in content
    assert 'id="sidebar-tier-price-pill"' in content

    assert "selectProductionTier" in content
    assert "onStudioTierChange" in content
    assert "PRODUCTION_TIERS" in content
