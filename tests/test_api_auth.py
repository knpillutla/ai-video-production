"""Integration tests for FastAPI health check and authentication endpoints."""

import pytest
from httpx import ASGITransport, AsyncClient
from src.api.main import app


@pytest.mark.asyncio
async def test_health_check():
    """Verify global health check endpoint."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "video-studio-api"
    assert data["version"] == "2.0.0"


@pytest.mark.asyncio
async def test_auth_test_token_and_me():
    """Verify login and /api/auth/me profile retrieval."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Issue test token
        login_resp = await ac.post(
            "/api/auth/test-token",
            json={"email": "alice@studio.com", "display_name": "Alice Studio"},
        )
        assert login_resp.status_code == 200
        auth_data = login_resp.json()
        token = auth_data["token"]
        user = auth_data["user"]
        assert user["email"] == "alice@studio.com"
        assert "user-" in user["storage_container_name"]

        # Access /api/auth/me
        headers = {"Authorization": f"Bearer {token}"}
        me_resp = await ac.get("/api/auth/me", headers=headers)
        assert me_resp.status_code == 200
        me_data = me_resp.json()
        assert me_data["id"] == user["id"]
        assert me_data["email"] == "alice@studio.com"


@pytest.mark.asyncio
async def test_unauthorized_access_blocked():
    """Verify 401 when accessing protected route without credentials."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get("/api/auth/me")
    assert resp.status_code == 401
