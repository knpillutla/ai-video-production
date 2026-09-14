
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
    """Verify composed Studio UI includes 3-tier cards, sidebar selector, and JS handlers."""
    from src.api.ui_composer import render_studio_html

    content = render_studio_html()
    js_content = "\n".join(f.read_text(encoding="utf-8") for f in Path("src/static/js").glob("*.js"))
    full_content = content + "\n" + js_content

    assert 'id="tier-card-low_cost"' in content
    assert 'id="tier-card-balanced"' in content
    assert 'id="tier-card-cinematic"' in content

    assert 'id="tier-radio-low_cost"' in content
    assert 'id="tier-radio-balanced"' in content
    assert 'id="tier-radio-cinematic"' in content

    assert 'id="studio-tier-select"' in content
    assert 'id="sidebar-tier-price-pill"' in content

    # Guided workflow inputs & controls
    assert 'id="youtube-url-input"' in content
    assert 'id="youtube-prompt-input"' in content
    assert 'id="btn-analyze-youtube"' in content
    assert 'id="guided-card-low_cost"' in content
    assert 'id="guided-card-balanced"' in content
    assert 'id="guided-card-cinematic"' in content
    assert 'id="btn-guided-generate"' in content

    assert "selectProductionTier" in full_content
    assert "onStudioTierChange" in full_content
    assert "analyzeReferenceConcept" in full_content
    assert "quickTestProduceFromPrompt" in full_content
    assert "PRODUCTION_TIERS" in full_content


def test_ui_video_studio_history_table_and_wizard_modal():
    """Verify Video Studio shows current videos status table desc and guided wizard modal."""
    from src.api.ui_composer import render_studio_html

    content = render_studio_html()
    js_content = "\n".join(f.read_text(encoding="utf-8") for f in Path("src/static/js").glob("*.js"))
    full_content = content + "\n" + js_content

    # Top button to create new video
    assert 'id="btn-top-create-video"' in content
    assert "Create New Video" in content

    # Current videos status table (Date/Time DESC, Option Selected, Cost, YouTube Status)
    assert 'id="studio-video-history-rows"' in content
    assert "Date / Time (DESC)" in content
    assert "Option Selected" in content
    assert "Published to YouTube" in content
    assert 'id="studio-filter-status"' in content
    assert 'id="studio-filter-tier"' in content
    assert 'id="studio-filter-youtube"' in content

    # Modal 10: Guided Create New Video Wizard
    assert 'id="create-video-wizard-modal"' in content
    assert 'id="wizard-step-1-container"' in content
    assert 'id="wizard-step-2-container"' in content
    assert 'id="wizard-step-3-container"' in content
    assert 'id="btn-wizard-analyze"' in content
    assert 'id="wizard-card-low_cost"' in content
    assert 'id="wizard-card-balanced"' in content
    assert 'id="wizard-card-cinematic"' in content
    assert 'id="btn-wizard-confirm"' in content

    # Modal 9: Professional Studio Guidance Modal
    assert 'id="studio-popup-modal"' in content
    assert 'id="popup-title"' in content
    assert 'id="popup-message"' in content
    assert 'id="popup-next-step-box"' in content
    assert 'id="popup-confirm-btn"' in content

    # JavaScript controller functions
    assert "openCreateVideoWizardModal" in full_content
    assert "closeCreateVideoWizardModal" in full_content
    assert "wizardGoToStep" in full_content
    assert "wizardAnalyzeConcept" in full_content
    assert "wizardSelectTier" in full_content
    assert "wizardConfirmAndProduce" in full_content
    assert "renderStudioVideoHistory" in full_content
    assert "showStudioModal" in full_content
    assert "closeStudioModal" in full_content
    assert "onStudioModalConfirm" in full_content


@pytest.mark.asyncio
async def test_ui_route_and_static_files_serving():
    """Verify FastAPI serves composed UI at / and static assets at /static/."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        ui_resp = await ac.get("/")
        assert ui_resp.status_code == 200
        assert "text/html" in ui_resp.headers.get("content-type", "")
        assert 'id="tab-studio"' in ui_resp.text
        assert 'id="create-video-wizard-modal"' in ui_resp.text

        css_resp = await ac.get("/static/css/styles.css")
        assert css_resp.status_code == 200
        assert "--bg:" in css_resp.text

        js_resp = await ac.get("/static/js/wizard_ui.js")
        assert js_resp.status_code == 200
        assert "openCreateVideoWizardModal" in js_resp.text

