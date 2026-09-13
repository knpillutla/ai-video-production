"""Tests for Commercial SaaS Subscriptions, Stripe Billing, and Pre-Flight Cost Governance."""

import pytest
from httpx import ASGITransport, AsyncClient
from src.api.main import app
from src.domain.repo import repo


@pytest.mark.asyncio
async def test_saas_billing_and_production_lifecycle():
    """Complete end-to-end test of SaaS subscriptions, wallet top-ups, cost estimation, and confirmation."""
    repo.clear()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Login Creator User
        auth_resp = await ac.post(
            "/api/auth/test-token",
            json={"email": "procreator@studio.com", "display_name": "Pro Creator"},
        )
        assert auth_resp.status_code == 200
        token = auth_resp.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Check Subscription Overview
        sub_resp = await ac.get("/api/billing/subscription", headers=headers)
        assert sub_resp.status_code == 200
        sub_data = sub_resp.json()
        assert sub_data["subscription_tier"] == "creator"
        assert sub_data["credit_balance_usd"] == 10.00
        assert sub_data["quota_limits"]["storage_gb"] == 50

        # 3. Create Stripe Checkout Session to upgrade to PRO_STUDIO
        checkout_resp = await ac.post(
            "/api/billing/create-checkout-session",
            headers=headers,
            json={"plan_tier": "pro_studio"},
        )
        assert checkout_resp.status_code == 200
        session_data = checkout_resp.json()
        assert "cs_test_" in session_data["session_id"]
        assert "checkout.stripe.com" in session_data["checkout_url"]

        # 4. Instant Credit Top-Up (+$25 USD)
        topup_resp = await ac.post(
            "/api/billing/topup-credits",
            headers=headers,
            json={"amount_usd": 25.0},
        )
        assert topup_resp.status_code == 200
        assert topup_resp.json()["credit_balance_usd"] == 35.00

        # 5. Create Show Universe and Episode 1
        show_resp = await ac.post(
            "/api/shows",
            headers=headers,
            json={"title": "Delhi WFH Confusions", "genre": "comedy"},
        )
        show_id = show_resp.json()["id"]

        ep_resp = await ac.post(
            "/api/projects",
            headers=headers,
            json={
                "show_id": show_id,
                "title": "Episode 1: The Endless Standup",
                "episode_number": 1,
                "duration_seconds": 480,
            },
        )
        assert ep_resp.status_code == 201
        ep_id = ep_resp.json()["id"]

        # 6. MANDATORY STEP 1: Pre-Flight Cost Estimation
        cost_resp = await ac.post(
            f"/api/projects/{ep_id}/estimate-cost",
            headers=headers,
        )
        assert cost_resp.status_code == 200
        cost_data = cost_resp.json()
        assert cost_data["total_cost_usd"] > 0
        assert len(cost_data["items"]) == 7  # All 7 itemized components
        assert cost_data["can_afford"] is True

        estimated_total = cost_data["total_cost_usd"]

        # 7. MANDATORY STEP 2: Explicit Confirmation & Deduction
        confirm_resp = await ac.post(
            f"/api/projects/{ep_id}/confirm-production",
            headers=headers,
        )
        assert confirm_resp.status_code == 200
        confirm_data = confirm_resp.json()
        assert confirm_data["status"] == "queued"
        assert confirm_data["deducted_usd"] == estimated_total
        assert round(confirm_data["remaining_balance_usd"] + estimated_total, 2) == 35.00

        # 8. Render Episodic Thumbnail with Top-Left Badge
        thumb_resp = await ac.post(
            f"/api/projects/{ep_id}/thumbnail",
            headers=headers,
            json={"language": "te", "style": "pill", "headline": "వర్క్ ఫ్రమ్ హోమ్ గోల!"},
        )
        assert thumb_resp.status_code == 200
        thumb_data = thumb_resp.json()
        assert thumb_data["status"] == "generated"
        assert thumb_data["position"] == "top_left"
        assert thumb_data["episode_number"] == 1
