"""Tests for User Settings, Multi-Theme Preferences, and Profile Customization."""

from uuid import uuid4
import pytest
from httpx import ASGITransport, AsyncClient

from src.api.main import app
from src.domain.repo import repo
from src.domain.user import User


@pytest.fixture
def test_creator():
    """Create test creator."""
    user = User(
        id=uuid4(),
        google_sub=f"sub_{uuid4().hex[:10]}",
        email=f"settings_creator_{uuid4().hex[:6]}@cineai.studio",
        display_name="Kling Runway Director",
        storage_container_name="user-settings-test",
        preferred_theme="white",
    )
    repo.save_user(user)
    return user


@pytest.mark.asyncio
async def test_user_theme_preference_persistence(test_creator):
    """Verify selecting a theme persists to user profile."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        auth_res = await client.post(
            "/api/auth/test-token",
            json={"email": test_creator.email, "display_name": test_creator.display_name},
        )
        headers = {"Authorization": f"Bearer {auth_res.json()['token']}"}

        # Update theme to cyberpunk
        patch_res = await client.patch(
            "/api/auth/preferences",
            headers=headers,
            json={"preferred_theme": "cyberpunk"},
        )
        assert patch_res.status_code == 200
        data = patch_res.json()
        assert data["preferred_theme"] == "cyberpunk"

        # Verify repo entity updated
        stored_user = repo.users.get(test_creator.id)
        assert stored_user is not None
        assert stored_user.preferred_theme == "cyberpunk"


@pytest.mark.asyncio
async def test_user_settings_display_name_update(test_creator):
    """Verify updating display name in user settings."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        auth_res = await client.post(
            "/api/auth/test-token",
            json={"email": test_creator.email, "display_name": test_creator.display_name},
        )
        headers = {"Authorization": f"Bearer {auth_res.json()['token']}"}

        patch_res = await client.patch(
            "/api/auth/preferences",
            headers=headers,
            json={"display_name": "Senior Executive Director", "preferred_theme": "obsidian"},
        )
        assert patch_res.status_code == 200
        data = patch_res.json()
        assert data["display_name"] == "Senior Executive Director"
        assert data["preferred_theme"] == "obsidian"


@pytest.mark.asyncio
async def test_all_theme_palette_options(test_creator):
    """Verify all 5 theme options (white, dark, cyberpunk, warm, obsidian) can be saved."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        auth_res = await client.post(
            "/api/auth/test-token",
            json={"email": test_creator.email, "display_name": test_creator.display_name},
        )
        headers = {"Authorization": f"Bearer {auth_res.json()['token']}"}

        themes = ["white", "dark", "cyberpunk", "warm", "obsidian"]
        for theme in themes:
            res = await client.patch(
                "/api/auth/preferences",
                headers=headers,
                json={"preferred_theme": theme},
            )
            assert res.status_code == 200
            assert res.json()["preferred_theme"] == theme


@pytest.mark.asyncio
async def test_user_preferences_requires_auth():
    """Verify unauthenticated requests are rejected."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.patch("/api/auth/preferences", json={"preferred_theme": "dark"})
        assert res.status_code == 401
