"""Rigorous multi-tenant isolation tests verifying query, entity, and storage separation."""

import pytest
from httpx import ASGITransport, AsyncClient
from src.api.main import app
from src.domain.repo import repo


@pytest.mark.asyncio
async def test_strict_multi_tenant_isolation():
    """Verify that User 2 has zero access or visibility into User 1's shows, characters, or episodes."""
    repo.clear()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Login User 1
        resp1 = await ac.post(
            "/api/auth/test-token",
            json={"email": "user1@studio.com", "display_name": "User One"},
        )
        token1 = resp1.json()["token"]
        headers1 = {"Authorization": f"Bearer {token1}"}

        # 2. Login User 2
        resp2 = await ac.post(
            "/api/auth/test-token",
            json={"email": "user2@studio.com", "display_name": "User Two"},
        )
        token2 = resp2.json()["token"]
        headers2 = {"Authorization": f"Bearer {token2}"}

        # 3. User 1 creates Show 1
        show1_resp = await ac.post(
            "/api/shows",
            headers=headers1,
            json={
                "title": "Delhi WFH Confusions",
                "genre": "comedy",
                "synopsis": "Remote work comedy series",
            },
        )
        assert show1_resp.status_code == 201
        show1 = show1_resp.json()
        show1_id = show1["id"]

        # 4. User 1 adds Character Aaradhya to Show 1
        char1_resp = await ac.post(
            f"/api/shows/{show1_id}/characters",
            headers=headers1,
            json={
                "name": "Aaradhya",
                "age_bracket": "20s",
                "gender": "female",
                "backstory": "Frustrated software engineer working from home",
            },
        )
        assert char1_resp.status_code == 201
        char1 = char1_resp.json()

        # 5. User 2 creates Show 2
        show2_resp = await ac.post(
            "/api/shows",
            headers=headers2,
            json={
                "title": "Tollywood Action Universe",
                "genre": "action",
                "synopsis": "High-octane mass action series",
            },
        )
        assert show2_resp.status_code == 201
        show2 = show2_resp.json()

        # 6. VERIFY ISOLATION: User 1 only sees Show 1
        u1_shows = (await ac.get("/api/shows", headers=headers1)).json()
        assert len(u1_shows) == 1
        assert u1_shows[0]["title"] == "Delhi WFH Confusions"

        # 7. VERIFY ISOLATION: User 2 only sees Show 2
        u2_shows = (await ac.get("/api/shows", headers=headers2)).json()
        assert len(u2_shows) == 1
        assert u2_shows[0]["title"] == "Tollywood Action Universe"

        # 8. VERIFY ISOLATION: User 2 CANNOT read User 1's show directly
        u2_get_show1 = await ac.get(f"/api/shows/{show1_id}", headers=headers2)
        assert u2_get_show1.status_code == 404

        # 9. VERIFY ISOLATION: User 2 CANNOT read User 1's characters
        u2_get_chars = await ac.get(f"/api/shows/{show1_id}/characters", headers=headers2)
        assert u2_get_chars.status_code == 404

        # 10. User 1 creates Episode 1 under Show 1
        ep1_resp = await ac.post(
            "/api/projects",
            headers=headers1,
            json={
                "show_id": show1_id,
                "title": "Episode 1: The Endless Standup",
                "duration_seconds": 480,
                "format": "web_series",
                "visual_style": "realistic",
            },
        )
        assert ep1_resp.status_code == 201
        ep1 = ep1_resp.json()
        ep1_id = ep1["id"]

        # 11. VERIFY ISOLATION: User 2 lists projects -> 0 projects
        u2_projects = (await ac.get("/api/projects", headers=headers2)).json()
        assert len(u2_projects) == 0

        # 12. VERIFY ISOLATION: User 2 cannot fetch User 1's episode
        u2_get_ep = await ac.get(f"/api/projects/{ep1_id}", headers=headers2)
        assert u2_get_ep.status_code == 404

        # 13. VERIFY ISOLATION: User 2 cannot inject an episode into User 1's show
        u2_create_ep_in_show1 = await ac.post(
            "/api/projects",
            headers=headers2,
            json={
                "show_id": show1_id,
                "title": "Hacker Intrusion",
                "duration_seconds": 300,
            },
        )
        assert u2_create_ep_in_show1.status_code == 404
