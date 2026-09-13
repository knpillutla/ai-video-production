"""Tests for Phase 6: Autonomous Daily Theme Scheduler and Multi-Channel YouTube Publishing."""

import pytest
from httpx import ASGITransport, AsyncClient
from uuid import uuid4

from src.api.main import app
from src.domain.creative import Episode, Show
from src.domain.distribution import Channel, ScheduleJob
from src.domain.generation import MediaFormat, ThemeGenre, VisualStyle
from src.domain.repo import repo
from src.domain.user import User
from src.mcp.topic_memory.server import check_topic_duplicate, remember_topic
from src.scheduling.daily_scheduler import daily_scheduler


@pytest.fixture
def auth_user():
    """Create test user and return headers."""
    user = User(
        id=uuid4(),
        google_sub=f"sub_{uuid4().hex[:10]}",
        email=f"phase6_{uuid4().hex[:6]}@studio.com",
        display_name="Phase 6 Director",
        storage_container_name="user-phase6-test",
    )
    repo.save_user(user)
    return user


@pytest.fixture
def user_show(auth_user):
    """Create a parent show for the user."""
    show = Show(
        user_id=auth_user.id,
        title="Delhi WFH Confusions Universe",
        slug="delhi-wfh-confusions",
        genre="comedy",
    )
    return repo.save_show(show)


@pytest.mark.asyncio
async def test_channel_crud_and_listing(auth_user):
    """Test channel registration and retrieval via API."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Generate token
        auth_res = await client.post(
            "/api/auth/test-token",
            json={"email": auth_user.email, "display_name": auth_user.display_name},
        )
        headers = {"Authorization": f"Bearer {auth_res.json()['token']}"}

        # 1. Create channel
        create_res = await client.post(
            "/api/channels",
            headers=headers,
            json={
                "platform": "youtube",
                "channel_name": "Telugu Comedy Hub",
                "channel_handle": "@telugucomedyhub",
                "default_tags": ["TeluguComedy", "WFH", "Shorts"],
            },
        )
        assert create_res.status_code == 201
        channel_data = create_res.json()
        assert channel_data["channel_name"] == "Telugu Comedy Hub"
        assert channel_data["channel_handle"] == "@telugucomedyhub"

        # 2. List channels
        list_res = await client.get("/api/channels", headers=headers)
        assert list_res.status_code == 200
        channels = list_res.json()
        assert len(channels) >= 1
        assert any(c["channel_name"] == "Telugu Comedy Hub" for c in channels)


@pytest.mark.asyncio
async def test_schedule_crud_operations(auth_user, user_show):
    """Test creating, listing, and deleting autonomous daily schedules."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        auth_res = await client.post(
            "/api/auth/test-token",
            json={"email": auth_user.email, "display_name": auth_user.display_name},
        )
        headers = {"Authorization": f"Bearer {auth_res.json()['token']}"}

        # 1. Create schedule
        sched_res = await client.post(
            "/api/schedules",
            headers=headers,
            json={
                "show_id": str(user_show.id),
                "theme": "telugu_comedy",
                "format": "web_series",
                "visual_style": "realistic",
                "cadence": "daily",
                "time_of_day_utc": "06:00",
                "target_languages": ["te", "hi", "en"],
                "auto_publish": False,
            },
        )
        assert sched_res.status_code == 201
        sched_data = sched_res.json()
        assert sched_data["theme"] == "telugu_comedy"
        assert sched_data["cadence"] == "daily"
        schedule_id = sched_data["id"]

        # 2. List schedules
        list_res = await client.get("/api/schedules", headers=headers)
        assert list_res.status_code == 200
        sched_list = list_res.json()
        assert any(s["id"] == schedule_id for s in sched_list)

        # 3. Delete schedule
        del_res = await client.delete(f"/api/schedules/{schedule_id}", headers=headers)
        assert del_res.status_code == 204

        # 4. Verify deletion
        list_res_after = await client.get("/api/schedules", headers=headers)
        assert not any(s["id"] == schedule_id for s in list_res_after.json())


@pytest.mark.asyncio
async def test_autonomous_scheduler_execution_with_dedup(auth_user, user_show):
    """Test full execution of scheduled job: deduplication guard, rendering, and stats."""
    # Pre-seed topic memory with one existing topic
    await remember_topic(
        topic="IT Employee Secret Second Job Confusions",
        metadata={"genre": "telugu_comedy", "show_slug": user_show.slug},
        final_story="Existing comedy episode.",
    )

    job = ScheduleJob(
        user_id=auth_user.id,
        show_id=user_show.id,
        theme="telugu_comedy",
        format="web_series",
        visual_style="realistic",
        cadence="daily",
        target_languages=["te", "en"],
        auto_publish=False,
    )
    saved_job = repo.save_schedule(job)

    # Trigger run via daily_scheduler
    result = await daily_scheduler.trigger_schedule_job(saved_job.id, auth_user.id)
    assert result["schedule_id"] == saved_job.id
    assert result["theme"] == "telugu_comedy"
    assert "IT Employee Secret Second Job Confusions" != result["title"]  # Must pick non-duplicate topic
    assert result["total_videos_created"] == 1

    # Verify episode was created in repository
    created_ep = repo.get_episode(auth_user.id, result["episode_id"])
    assert created_ep is not None
    assert created_ep.theme == ThemeGenre.TELUGU_COMEDY
    assert created_ep.format == MediaFormat.WEB_SERIES


@pytest.mark.asyncio
async def test_youtube_publish_pipeline_and_audit(auth_user, user_show):
    """Test manual 1-click YouTube publish route with synthetic disclosure and audit ledger."""
    # Setup channel
    channel = Channel(
        user_id=auth_user.id,
        platform="youtube",
        channel_name="Telugu Comedy Hub",
        default_tags=["Comedy", "Telugu"],
    )
    saved_channel = repo.save_channel(channel)

    # Setup completed episode
    episode = Episode(
        user_id=auth_user.id,
        show_id=user_show.id,
        title="WFH Weekend Standup Confusions",
        duration_seconds=480,
        status="completed",
    )
    saved_ep = repo.save_episode(episode)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        auth_res = await client.post(
            "/api/auth/test-token",
            json={"email": auth_user.email, "display_name": auth_user.display_name},
        )
        headers = {"Authorization": f"Bearer {auth_res.json()['token']}"}

        # Publish to channel
        pub_res = await client.post(
            f"/api/channels/{saved_channel.id}/publish",
            headers=headers,
            json={
                "episode_id": str(saved_ep.id),
                "privacy_status": "public",
                "selected_language_thumbnail": "te",
                "custom_title": "They Lied About Remote Work! | Episode 01",
            },
        )
        assert pub_res.status_code == 200
        pub_data = pub_res.json()
        assert pub_data["channel_id"] == str(saved_channel.id)
        assert pub_data["status"] == "published"
        assert pub_data["synthetic_media_disclosed"] is True
        assert pub_data["monetization_cleared"] is True
        assert pub_data["platform_video_id"].startswith("yt_")

        # Check publication ledger API
        ledger_res = await client.get("/api/channels/publications", headers=headers)
        assert ledger_res.status_code == 200
        ledger = ledger_res.json()
        assert len(ledger) >= 1
        assert any(p["episode_id"] == str(saved_ep.id) for p in ledger)
