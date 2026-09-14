"""Tests for Topic, Metadata & Final Story Deduplication & User Duplicate Alerting."""

from pathlib import Path
from uuid import UUID, uuid4
import pytest
from httpx import ASGITransport, AsyncClient
from src.api.main import app
from src.domain.creative import Episode, Show
from src.domain.repo import repo
from src.domain.user import SubscriptionTier, User
from src.mcp.topic_memory.server import check_topic_duplicate, remember_topic


@pytest.mark.asyncio
async def test_remember_topic_saves_metadata_and_final_story():
    """Verify that every created video records topic, metadata, and final story in the vault."""
    unique_topic = f"Bangalore Traffic Silk Board Flyover Chronicles - {uuid4().hex[:6]}"
    metadata = {
        "genre": "comedy",
        "tags": ["bangalore", "traffic", "flyover", "silk_board"],
        "target_audience": "tech_professionals",
    }
    final_story = (
        "Ravi sits in his car for three hours staring at the half-constructed metro pillar. "
        "He orders biryani directly to his car window."
    )
    episode_id = f"ep_{uuid4().hex[:8]}"

    # Save to vault
    res = await remember_topic(
        topic=unique_topic,
        metadata=metadata,
        final_story=final_story,
        episode_id=episode_id,
        show_slug="bengaluru_confusions",
    )

    assert res["status"] == "memorized"
    assert res["has_metadata"] is True
    assert res["has_story"] is True
    assert res["recorded_topic"] == unique_topic


@pytest.mark.asyncio
async def test_duplicate_topic_and_metadata_blocks_and_alerts_user():
    """Verify system blocks similar topic/metadata, prevents duplicate content, and alerts user."""
    seed_topic = f"Ancient Rome Colosseum Gladiator Architecture - {uuid4().hex[:6]}"
    metadata = {
        "genre": "documentary",
        "tags": ["rome", "gladiators", "colosseum", "history"],
        "target_audience": "history_buffs",
    }
    final_story = "Exploration of the hypogeum and underground elevator mechanisms of the Roman Colosseum."
    ep_id = f"ep_hist_{uuid4().hex[:8]}"

    # First save the original production
    await remember_topic(
        topic=seed_topic,
        metadata=metadata,
        final_story=final_story,
        episode_id=ep_id,
        show_slug="ancient_history",
    )

    # Now simulate user attempting to create very similar topic with similar metadata
    duplicate_candidate = seed_topic.replace("Ancient Rome", "Rome")
    candidate_meta = {
        "genre": "documentary",
        "tags": ["colosseum", "gladiators", "rome"],
        "target_audience": "history_buffs",
    }

    check_res = await check_topic_duplicate(
        topic=duplicate_candidate,
        metadata=candidate_meta,
        threshold=0.75,
    )

    # System must block and alert user
    assert check_res["is_duplicate"] is True
    assert check_res["max_similarity_score"] >= 0.75
    assert check_res["conflicting_topic"] == seed_topic
    assert check_res["conflicting_episode_id"] == ep_id

    # Alert message must clearly inform the user
    alert = check_res["alert_message"]
    assert "DUPLICATE CONTENT ALERT" in alert
    assert "Video generation blocked" in alert
    assert "demonetization" in alert


@pytest.mark.asyncio
async def test_api_production_estimate_cost_blocks_duplicate_topic():
    """Verify POST /api/projects/{id}/estimate-cost returns HTTP 409 Conflict on duplicate topic."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Login to get JWT
        login_res = await client.post(
            "/api/auth/test-token",
            json={"email": "dup@studio.com", "display_name": "Duplicate Tester"},
        )
        assert login_res.status_code == 200
        auth_data = login_res.json()
        token = auth_data["token"]
        user_id = auth_data["user"]["id"]
        auth_headers = {"Authorization": f"Bearer {token}"}

        uid = UUID(user_id)
        # Create Show
        show = Show(user_id=uid, title="IT Comedy Universe", slug="it_comedy_universe", genre="comedy")
        repo.save_show(show)

        # Seed an existing topic for this user
        existing_title = f"Chai Break Standup Gossip - {uuid4().hex[:6]}"
        await remember_topic(
            topic=existing_title,
            metadata={"genre": "comedy"},
            final_story="Engineers discussing sprint deadlines by the tea stall.",
            episode_id="ep_tea_001",
            user_id=user_id,
        )

        # Create Episode with duplicate title
        dup_title = existing_title
        episode = Episode(
            user_id=uid,
            show_id=show.id,
            title=dup_title,
            duration_seconds=300,
        )
        repo.save_episode(episode)

        # Call estimate-cost -> Returns HTTP 200 with prominent warning and can_force_proceed=True
        resp = await client.post(
            f"/api/projects/{episode.id}/estimate-cost",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        est_data = resp.json()
        assert est_data["has_duplicate_warning"] is True
        assert "DUPLICATE CONTENT ALERT" in est_data["duplicate_warning_message"]
        assert est_data["can_force_proceed"] is True

        # Call confirm-production without force_proceed -> Returns 409 warning
        conf_resp = await client.post(
            f"/api/projects/{episode.id}/confirm-production",
            headers=auth_headers,
            json={"force_proceed": False},
        )
        assert conf_resp.status_code == 409
        err = conf_resp.json()["detail"]
        assert err["error"] == "DUPLICATE_TOPIC_WARNING"
        assert err["can_force_proceed"] is True

        # Call confirm-production with force_proceed=True -> Succeeds with 200
        conf_force_resp = await client.post(
            f"/api/projects/{episode.id}/confirm-production",
            headers=auth_headers,
            json={"force_proceed": True},
        )
        assert conf_force_resp.status_code == 200
        assert conf_force_resp.json()["status"] == "queued"


@pytest.mark.asyncio
async def test_youtube_trending_topics_and_selection():
    """Verify YouTube trending topics feed and 1-click transformative episode creation."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        login_res = await client.post(
            "/api/auth/test-token",
            json={"email": "trend@studio.com", "display_name": "Trend Explorer"},
        )
        auth_headers = {"Authorization": f"Bearer {login_res.json()['token']}"}
        uid = UUID(login_res.json()["user"]["id"])

        # 1. Fetch trending YouTube topics
        res = await client.get("/api/trending/youtube?region=IN", headers=auth_headers)
        assert res.status_code == 200
        topics = res.json()
        assert len(topics) > 0
        first = topics[0]
        assert "title" in first
        assert "views_count" in first
        assert "suggested_angle" in first

        # 2. Select a trending topic and instantiate project
        show = Show(user_id=uid, title="Trending Breakdown", slug="trending_show", genre="comedy")
        repo.save_show(show)

        sel_res = await client.post(
            "/api/trending/select-topic",
            headers=auth_headers,
            json={"trending_id": first["id"], "show_id": str(show.id), "target_duration_seconds": 300},
        )
        assert sel_res.status_code == 201
        data = sel_res.json()
        assert data["status"] == "created"
        assert data["source_trend"] == first["title"]
        assert "abstract_theme" in data


def test_terraform_only_iac_verification():
    """Verify that only Terraform scripts exist for all platforms, with zero Bicep files."""
    azure_tf = Path("deploy/azure/terraform/main.tf")
    azure_root_tf = Path("deploy/azure/main.tf")
    gcp_tf = Path("deploy/gcp/terraform/cloud_run.tf")
    gcp_root_tf = Path("deploy/gcp/main.tf")
    cloudflare_tf = Path("deploy/multi_cloud/cloudflare_failover.tf")

    # All Terraform scripts must exist
    assert azure_tf.exists() or azure_root_tf.exists()
    assert gcp_tf.exists() or gcp_root_tf.exists()
    assert cloudflare_tf.exists()

    # Zero Bicep files must exist anywhere in deploy/
    deploy_dir = Path("deploy")
    bicep_files = list(deploy_dir.rglob("*.bicep"))
    assert len(bicep_files) == 0, f"Found prohibited Bicep files: {bicep_files}"


@pytest.mark.asyncio
async def test_user_scoped_topic_deduplication_and_vault_clearing():
    """Verify deduplication checks user's existing topics only, not across all users."""
    from src.mcp.topic_memory.server import clear_topic_vault
    # 1. Clear vault for clean test isolation
    clear_topic_vault()

    topic_name = f"Wild Safari Serengeti Predators - {uuid4().hex[:6]}"
    user_a = "user_alpha_01"
    user_b = "user_beta_02"

    # User A records a topic
    await remember_topic(
        topic=topic_name,
        metadata={"genre": "documentary", "tags": ["wildlife", "safari"]},
        final_story="Cheetah chasing gazelle across golden African savannah.",
        episode_id="ep_user_a_001",
        user_id=user_a,
    )

    # User A proposes duplicate topic -> BLOCKED (similarity >= 0.80)
    check_a = await check_topic_duplicate(
        topic=topic_name,
        user_id=user_a,
        threshold=0.80,
    )
    assert check_a["is_duplicate"] is True
    assert check_a["conflicting_topic"] == topic_name

    # User B proposes SAME topic -> NOT BLOCKED (deduplication scoped to user's existing topics)
    check_b = await check_topic_duplicate(
        topic=topic_name,
        user_id=user_b,
        threshold=0.80,
    )
    assert check_b["is_duplicate"] is False
    assert check_b["conflicting_topic"] is None

    # Clear vault for User A only
    cleared = clear_topic_vault(user_id=user_a)
    assert cleared >= 1

    # User A can now re-propose the topic cleanly
    check_a_after = await check_topic_duplicate(
        topic=topic_name,
        user_id=user_a,
        threshold=0.80,
    )
    assert check_a_after["is_duplicate"] is False

