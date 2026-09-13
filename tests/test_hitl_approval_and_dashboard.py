"""Tests for Human-in-the-Loop Video Approval and Executive Creator Dashboard."""

from uuid import uuid4
import pytest
from httpx import ASGITransport, AsyncClient

from src.api.main import app
from src.domain.creative import Episode, GenerationOptions, Show
from src.domain.distribution import Channel, ScheduleJob
from src.domain.generation import AspectRatio, MediaFormat, ThemeGenre
from src.domain.repo import repo
from src.domain.user import User
from src.scheduling.daily_scheduler import daily_scheduler
from src.services.notification import notification_service


@pytest.fixture
def clean_services():
    """Clear in-memory notification and token stores."""
    notification_service.clear()
    repo.clear()
    yield
    notification_service.clear()
    repo.clear()


@pytest.fixture
def creator_user(clean_services):
    """Fixture creating and saving a verified creator user."""
    user = User(
        id=uuid4(),
        google_sub=f"sub_{uuid4().hex[:8]}",
        email="director.krishna@cineai.studio",
        display_name="Krishna Director",
        storage_container_name="user-director-test",
    )
    return repo.save_user(user)


@pytest.fixture
def creator_show(creator_user):
    """Create parent show universe for creator."""
    return repo.save_show(
        Show(user_id=creator_user.id, title="Delhi WFH Universe", slug="delhi-wfh", genre="comedy")
    )


@pytest.fixture
def creator_channel(creator_user):
    """Create connected YouTube channel."""
    return repo.save_channel(
        Channel(
            user_id=creator_user.id,
            platform="youtube",
            channel_name="Telugu Comedy Hub",
            channel_id_or_handle="@telugucomedyhub",
        )
    )


@pytest.mark.asyncio
async def test_user_persistence_and_email_retrieval(creator_user):
    """Validate user profile and email address are accurately stored and retrievable."""
    by_id = repo.get_user(creator_user.id)
    assert by_id and by_id.email == "director.krishna@cineai.studio"
    assert by_id.display_name == "Krishna Director"

    by_email = repo.get_user_by_email("director.krishna@cineai.studio")
    assert by_email and by_email.id == creator_user.id


@pytest.mark.asyncio
async def test_scheduled_pipeline_dispatches_approval_email(creator_user, creator_show, creator_channel):
    """Validate scheduled job pauses at pending_approval and sends email with magic token."""
    job = repo.save_schedule(
        ScheduleJob(
            user_id=creator_user.id,
            show_id=creator_show.id,
            channel_id=creator_channel.id,
            name="Daily Comedy",
            theme_genre=ThemeGenre.TELUGU_COMEDY,
            target_languages=["te", "en"],
        )
    )

    result = await daily_scheduler.trigger_schedule_job(job.id, creator_user.id)
    assert result["status"] == "pending_approval"

    notifs = notification_service.list_notifications(creator_user.email)
    assert len(notifs) == 1
    assert "magic_review_" in notifs[0].magic_approval_token
    assert "/api/approvals/quick-confirm?token=" in notifs[0].direct_confirm_url
    assert "/ui?approval_id=" in notifs[0].studio_review_url


@pytest.mark.asyncio
async def test_quick_confirm_via_token_without_login_json(creator_user, creator_show, creator_channel):
    """Validate 1-click confirmation from email button succeeds without login."""
    ep = repo.save_episode(
        Episode(
            user_id=creator_user.id,
            show_id=creator_show.id,
            title="Secret Second Job (EP 03)",
            episode_number=3,
            duration_seconds=480,
            status="pending_approval",
            options=GenerationOptions(target_languages=["te"]),
        )
    )
    notif = await notification_service.send_approval_request_email(creator_user, ep)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post(f"/api/approvals/quick-confirm?token={notif.magic_approval_token}")
        assert res.status_code == 200
        assert res.json()["decision"] == "approved"
        assert res.json()["status"] == "published"
        assert res.json()["publication_id"] is not None

    assert repo.get_episode(creator_user.id, ep.id).status == "published"


@pytest.mark.asyncio
async def test_quick_confirm_via_token_html_response(creator_user, creator_show, creator_channel):
    """Validate browser click from email displays success page without login."""
    ep = repo.save_episode(
        Episode(
            user_id=creator_user.id,
            show_id=creator_show.id,
            title="Rebel Commander (EP 01)",
            episode_number=1,
            duration_seconds=480,
            status="pending_approval",
            options=GenerationOptions(target_languages=["te"]),
        )
    )
    notif = await notification_service.send_approval_request_email(creator_user, ep)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get(
            f"/api/approvals/quick-confirm?token={notif.magic_approval_token}",
            headers={"Accept": "text/html"},
        )
        assert res.status_code == 200
        assert "text/html" in res.headers["content-type"]
        assert "Episode Approved" in res.text


@pytest.mark.asyncio
async def test_token_reuse_and_invalid_token_protection(creator_user, creator_show):
    """Validate consumed tokens cannot be reused and invalid tokens fail fast."""
    ep = repo.save_episode(
        Episode(
            user_id=creator_user.id,
            show_id=creator_show.id,
            title="One Time Token Test",
            episode_number=1,
            duration_seconds=120,
            status="pending_approval",
        )
    )
    notif = await notification_service.send_approval_request_email(creator_user, ep)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res1 = await client.post(f"/api/approvals/quick-confirm?token={notif.magic_approval_token}")
        assert res1.status_code == 200
        res2 = await client.post(f"/api/approvals/quick-confirm?token={notif.magic_approval_token}")
        assert res2.status_code == 400
        res3 = await client.post("/api/approvals/quick-confirm?token=fake_random_token")
        assert res3.status_code == 400


@pytest.mark.asyncio
async def test_token_info_and_authenticated_approval_flow(creator_user, creator_show):
    """Validate token inspection and authenticated director review endpoints."""
    ep = repo.save_episode(
        Episode(
            user_id=creator_user.id,
            show_id=creator_show.id,
            title="Interactive Review Episode",
            episode_number=2,
            duration_seconds=300,
            status="pending_approval",
        )
    )
    notif = await notification_service.send_approval_request_email(creator_user, ep)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        info_res = await client.get(f"/api/approvals/token-info?token={notif.magic_approval_token}")
        assert info_res.status_code == 200
        assert info_res.json()["recipient_email"] == creator_user.email

        auth_res = await client.post(
            "/api/auth/test-token",
            json={"email": creator_user.email, "display_name": creator_user.display_name},
        )
        headers = {"Authorization": f"Bearer {auth_res.json()['token']}"}

        list_res = await client.get("/api/approvals", headers=headers)
        assert list_res.status_code == 200 and len(list_res.json()) >= 1

        reject_res = await client.post(
            f"/api/approvals/{ep.id}/reject",
            headers=headers,
            json={"reason": "Audio leveling needs revision"},
        )
        assert reject_res.status_code == 200 and reject_res.json()["decision"] == "rejected"

    assert repo.get_episode(creator_user.id, ep.id).status == "rejected"


@pytest.mark.asyncio
async def test_dashboard_stats_first_time_user(creator_user):
    """Validate first-time user receives sample showcase videos."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        auth_res = await client.post(
            "/api/auth/test-token",
            json={"email": creator_user.email, "display_name": creator_user.display_name},
        )
        headers = {"Authorization": f"Bearer {auth_res.json()['token']}"}

        res = await client.get("/api/dashboard/stats", headers=headers)
        assert res.status_code == 200
        stats = res.json()
        assert stats["is_first_time_user"] is True
        assert stats["total_videos_created"] == 0
        assert len(stats["sample_showcase_videos"]) == 3


@pytest.mark.asyncio
async def test_dashboard_stats_returning_user_breakdowns(creator_user, creator_show):
    """Validate format (long vs short) and genre breakdown calculations."""
    repo.save_episode(
        Episode(
            user_id=creator_user.id,
            show_id=creator_show.id,
            title="Long Ep 1",
            episode_number=1,
            duration_seconds=480,
            theme=ThemeGenre.TELUGU_COMEDY,
            status="published",
        )
    )
    repo.save_episode(
        Episode(
            user_id=creator_user.id,
            show_id=creator_show.id,
            title="Long Ep 2",
            episode_number=2,
            duration_seconds=360,
            theme=ThemeGenre.EPIC_ACTION,
            status="pending_approval",
        )
    )
    repo.save_episode(
        Episode(
            user_id=creator_user.id,
            show_id=creator_show.id,
            title="Short Reel 1",
            episode_number=3,
            duration_seconds=45,
            theme=ThemeGenre.TELUGU_COMEDY,
            status="published",
        )
    )

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        auth_res = await client.post(
            "/api/auth/test-token",
            json={"email": creator_user.email, "display_name": creator_user.display_name},
        )
        headers = {"Authorization": f"Bearer {auth_res.json()['token']}"}

        res = await client.get("/api/dashboard/stats", headers=headers)
        assert res.status_code == 200
        stats = res.json()

        assert stats["is_first_time_user"] is False
        assert stats["total_videos_created"] == 3
        assert stats["total_videos_published"] == 2
        assert stats["pending_approval_count"] == 1

        fb = stats["format_breakdown"]
        assert fb["long_form_count"] == 2 and fb["short_form_count"] == 1
        assert fb["long_form_pct"] == 66.7

        gb = stats["genre_breakdown"]
        assert gb["telugu_comedy"]["created"] == 2 and gb["telugu_comedy"]["published"] == 2
        assert gb["epic_action"]["created"] == 1 and gb["epic_action"]["published"] == 0
