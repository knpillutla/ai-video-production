"""Tests for Channel Management, Credential Encryption, YouTube Analytics Drilldown, and Recommendation."""

from uuid import UUID, uuid4
import pytest
from httpx import ASGITransport, AsyncClient

from src.api.main import app
from src.core.security import decrypt_secret
from src.domain.creative import Episode, Show
from src.domain.distribution import Channel, ChannelPublication
from src.domain.generation import MediaFormat, ThemeGenre, VisualStyle
from src.domain.repo import repo
from src.domain.user import User


@pytest.fixture
def channel_creator():
    """Create test creator."""
    user = User(
        id=uuid4(),
        google_sub=f"sub_{uuid4().hex[:10]}",
        email=f"channel_creator_{uuid4().hex[:6]}@cineai.studio",
        display_name="Executive Channel Manager",
        storage_container_name="user-channel-test",
    )
    repo.save_user(user)
    return user


@pytest.mark.asyncio
async def test_channel_credential_import_and_encryption(channel_creator):
    """Verify channel credentials are encrypted with AES-256-GCM and stored securely."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        auth_res = await client.post(
            "/api/auth/test-token",
            json={"email": channel_creator.email, "display_name": channel_creator.display_name},
        )
        headers = {"Authorization": f"Bearer {auth_res.json()['token']}"}

        import_payload = {
            "channel_name": "Mana Telugu Comedy Club",
            "channel_handle": "@manatelugucomedy",
            "primary_genre": "telugu_comedy",
            "primary_language": "te",
            "default_tags": ["Telugu", "Comedy", "AIStudio"],
            "client_id": "google_oauth_client_id_999",
            "client_secret": "super_secret_client_key",
            "refresh_token": "1//04test_refresh_token_xyz",
            "simulate_subscribers": 520000,
        }

        res = await client.post("/api/channels/import-credentials", headers=headers, json=import_payload)
        assert res.status_code == 201
        data = res.json()
        assert data["channel_name"] == "Mana Telugu Comedy Club"
        assert data["subscribers_count"] == 520000
        assert data["credentials_configured"] is True

        # Verify underlying repo entity has encrypted credentials (not plaintext)
        channel_id = data["channel_id"]
        stored_channel = repo.get_channel(channel_creator.id, UUID(channel_id))
        assert stored_channel is not None
        assert stored_channel.encrypted_credentials is not None
        assert "super_secret_client_key" not in stored_channel.encrypted_credentials

        # Verify decryption round-trip
        decrypted = decrypt_secret(stored_channel.encrypted_credentials)
        assert "super_secret_client_key" in decrypted


@pytest.mark.asyncio
async def test_channel_portfolio_overview_and_stats(channel_creator):
    """Verify aggregated portfolio metrics and single channel statistics."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        auth_res = await client.post(
            "/api/auth/test-token",
            json={"email": channel_creator.email, "display_name": channel_creator.display_name},
        )
        headers = {"Authorization": f"Bearer {auth_res.json()['token']}"}

        # Create 2 test channels
        ch1 = Channel(
            user_id=channel_creator.id,
            channel_name="Telugu Comedy Hub",
            primary_genre="telugu_comedy",
            subscribers_count=350000,
            total_views=1200000,
            total_revenue_usd=4140.0,
            total_likes=98000,
            credentials_configured=True,
        )
        ch2 = Channel(
            user_id=channel_creator.id,
            channel_name="Earth 4K Expeditions",
            primary_genre="nature_wildlife",
            subscribers_count=180000,
            total_views=650000,
            total_revenue_usd=2242.50,
            total_likes=52000,
            credentials_configured=True,
        )
        repo.save_channel(ch1)
        repo.save_channel(ch2)

        # 1. Overview
        ov_res = await client.get("/api/channels/overview", headers=headers)
        assert ov_res.status_code == 200
        ov_data = ov_res.json()
        assert ov_data["total_channels"] >= 2
        assert ov_data["total_subscribers"] >= 530000
        assert ov_data["total_views"] >= 1850000

        # 2. Stats for single channel
        st_res = await client.get(f"/api/channels/{ch1.id}/stats", headers=headers)
        assert st_res.status_code == 200
        st_data = st_res.json()
        assert st_data["channel_name"] == "Telugu Comedy Hub"
        assert st_data["total_views"] == 1200000


@pytest.mark.asyncio
async def test_channel_video_drilldown(channel_creator):
    """Verify video list drilldown for a specific channel with video-level analytics."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        auth_res = await client.post(
            "/api/auth/test-token",
            json={"email": channel_creator.email, "display_name": channel_creator.display_name},
        )
        headers = {"Authorization": f"Bearer {auth_res.json()['token']}"}

        test_show = Show(user_id=channel_creator.id, title="Universe Show", slug="universe-show")
        repo.save_show(test_show)

        ch = Channel(
            user_id=channel_creator.id,
            channel_name="Action Flix World",
            primary_genre="epic_action",
        )
        repo.save_channel(ch)

        ep1 = Episode(
            user_id=channel_creator.id,
            show_id=test_show.id,
            title="Midnight Fortress Siege",
            episode_number=1,
            duration_seconds=540,
            format=MediaFormat.MOVIE_CINEMATIC,
            theme=ThemeGenre.EPIC_ACTION,
            visual_style=VisualStyle.REALISTIC,
        )
        repo.save_episode(ep1)

        pub1 = ChannelPublication(
            user_id=channel_creator.id,
            episode_id=ep1.id,
            channel_id=ch.id,
            platform_video_id="yt_action_001",
            status="published",
        )
        repo.save_publication(pub1)

        drill_res = await client.get(f"/api/channels/{ch.id}/videos", headers=headers)
        assert drill_res.status_code == 200
        vids = drill_res.json()
        assert len(vids) == 1
        assert vids[0]["title"] == "Midnight Fortress Siege"
        assert vids[0]["video_id"] == "yt_action_001"
        assert vids[0]["views"] > 0
        assert vids[0]["ctr_pct"] > 0.0
        assert vids[0]["estimated_revenue_usd"] > 0.0


@pytest.mark.asyncio
async def test_channel_recommendation_based_on_metadata(channel_creator):
    """Verify auto-selection of the matching channel based on episode genre & language."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        auth_res = await client.post(
            "/api/auth/test-token",
            json={"email": channel_creator.email, "display_name": channel_creator.display_name},
        )
        headers = {"Authorization": f"Bearer {auth_res.json()['token']}"}

        test_show = Show(user_id=channel_creator.id, title="Recommendation Show", slug="rec-show")
        repo.save_show(test_show)

        comedy_ch = Channel(
            user_id=channel_creator.id,
            channel_name="Hyderabad Comedy Laughs",
            primary_genre="telugu_comedy",
            primary_language="te",
        )
        nature_ch = Channel(
            user_id=channel_creator.id,
            channel_name="Wild World UHD",
            primary_genre="nature_wildlife",
            primary_language="en",
        )
        repo.save_channel(comedy_ch)
        repo.save_channel(nature_ch)

        # Episode A: Telugu Comedy
        ep_comedy = Episode(
            user_id=channel_creator.id,
            show_id=test_show.id,
            title="WFH Confusion Comedy",
            episode_number=1,
            format=MediaFormat.WEB_SERIES,
            theme=ThemeGenre.TELUGU_COMEDY,
            visual_style=VisualStyle.REALISTIC,
        )
        repo.save_episode(ep_comedy)

        rec_res1 = await client.get(f"/api/channels/recommend/{ep_comedy.id}", headers=headers)
        assert rec_res1.status_code == 200
        rec_data1 = rec_res1.json()
        assert rec_data1["recommended_channel_id"] == str(comedy_ch.id)
        assert rec_data1["matched_genre"] is True

        # Episode B: Nature Wildlife
        ep_nature = Episode(
            user_id=channel_creator.id,
            show_id=test_show.id,
            title="Snow Leopard Stalk",
            episode_number=1,
            format=MediaFormat.MOVIE_CINEMATIC,
            theme=ThemeGenre.NATURE_WILDLIFE,
            visual_style=VisualStyle.REALISTIC,
        )
        repo.save_episode(ep_nature)

        rec_res2 = await client.get(f"/api/channels/recommend/{ep_nature.id}", headers=headers)
        assert rec_res2.status_code == 200
        rec_data2 = rec_res2.json()
        assert rec_data2["recommended_channel_id"] == str(nature_ch.id)
        assert rec_data2["matched_genre"] is True


@pytest.mark.asyncio
async def test_channel_deletion(channel_creator):
    """Verify deleting a channel."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        auth_res = await client.post(
            "/api/auth/test-token",
            json={"email": channel_creator.email, "display_name": channel_creator.display_name},
        )
        headers = {"Authorization": f"Bearer {auth_res.json()['token']}"}

        temp_ch = Channel(user_id=channel_creator.id, channel_name="Temporary Channel")
        repo.save_channel(temp_ch)

        del_res = await client.delete(f"/api/channels/{temp_ch.id}", headers=headers)
        assert del_res.status_code == 200
        assert del_res.json()["status"] == "deleted"
        assert repo.get_channel(channel_creator.id, temp_ch.id) is None
