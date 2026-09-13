"""Autonomous Swarm Coordinator orchestrating specialized agents and MCP microservices."""

import asyncio
from pathlib import Path
from typing import Any
from uuid import uuid4

from src.agents.audio_foley_agent import audio_foley_agent
from src.agents.growth_seo_agent import growth_seo_agent
from src.agents.qa_gate_agent import qa_gate_agent
from src.agents.script_agent import script_agent
from src.agents.transcreation_agent import transcreation_agent
from src.core.telemetry import logger
from src.mcp.compliance_guard.server import validate_compliance
from src.mcp.compositor_engine.server import compile_filter_complex
from src.mcp.model_selector.server import estimate_production_cost, select_best_model
from src.mcp.publisher.server import prepare_youtube_payload
from src.mcp.topic_memory.server import check_topic_duplicate, remember_topic


class SwarmCoordinator:
    """Orchestrates end-to-end multi-agent pipeline handoffs via MCP microservices."""

    async def run_pipeline_swarm(
        self,
        topic: str,
        genre: str = "comedy",
        language: str = "te",
        output_workspace: Path | str = "./storage/swarm_runs",
        simulate_model_failover: bool = False,
    ) -> dict[str, Any]:
        """Execute a full coordinated agent swarm generation run with failover recovery."""
        run_id = str(uuid4())[:8]
        ws = Path(output_workspace) / f"run_{run_id}"
        ws.mkdir(parents=True, exist_ok=True)
        logger.info(f"swarm_pipeline_started: run_id={run_id}, topic='{topic}'")

        # Step 1: Topic & Metadata Originality Check via MCP Topic Memory
        topic_check = await check_topic_duplicate(topic, metadata={"genre": genre, "language": language})
        if topic_check.get("is_duplicate"):
            logger.warning(f"swarm_duplicate_blocked: {topic_check.get('alert_message')}")
            return {
                "run_id": run_id,
                "status": "DUPLICATE_BLOCKED",
                "alert_message": topic_check.get("alert_message"),
                "topic_check": topic_check,
            }

        # Step 2: Model Selection & Pre-Flight Cost via MCP Model Selector
        model_selection = await select_best_model(
            category="script_creative",
            language=language,
            simulate_rate_limit=simulate_model_failover,
        )
        cost_est = await estimate_production_cost(scenes_count=3, duration_seconds=12.0)

        # Step 3: Script Agent Storyboard Drafting
        storyboard = await script_agent.draft_episode_storyboard(topic, genre=genre)
        full_dialogue = " ".join(s.get("dialogue", "") for s in storyboard["scenes"])

        # Step 4: Compliance Guard MCP Screening
        compliance = await validate_compliance(full_dialogue or topic)

        # Step 5: Transcreation Agent Subtitle Bundle
        base_segments = [
            {"start": 0.0, "end": 4.0, "text": storyboard["scenes"][0].get("dialogue", "Scene 1") if storyboard["scenes"] else "Scene 1"},
            {"start": 4.0, "end": 8.0, "text": storyboard["scenes"][1].get("dialogue", "Scene 2") if len(storyboard["scenes"]) > 1 else "Scene 2"},
            {"start": 8.0, "end": 12.0, "text": storyboard["scenes"][2].get("dialogue", "Scene 3") if len(storyboard["scenes"]) > 2 else "Scene 3"},
        ]
        sub_bundle = transcreation_agent.generate_multilingual_subtitle_bundle(
            base_segments=base_segments,
            output_dir=ws / "subtitles",
            primary_language=language,
        )

        # Step 6: Audio & Foley Agent Scoring & Stem Isolation
        bgm_path = ws / "soundtrack.wav"
        await audio_foley_agent.score_soundtrack(bgm_path, genre="cinematic comedy", duration_seconds=12.0)
        stems = await audio_foley_agent.separate_vocal_and_instrumental_stems(bgm_path, ws / "stems")

        # Step 7: Compositor Engine MCP Single-Pass Filter Complex
        filter_complex = await compile_filter_complex(
            scenes=storyboard["scenes"],
            output_mp4=str(ws / "master.mp4"),
        )

        # Step 8: Growth & SEO Agent Metadata Generation
        seo_meta = growth_seo_agent.generate_growth_metadata(
            title=storyboard["title"],
            topic=topic,
            genre=genre,
            language=language,
        )

        # Step 9: Publisher MCP Payload Preparation
        pub_payload = await prepare_youtube_payload(
            title=seo_meta["primary_title"],
            description=seo_meta["description"],
            tags=seo_meta["search_tags"],
            contains_synthetic_media=True,
        )

        # Step 10: Commit Approved Topic, Metadata & Final Story to Topic Memory
        await remember_topic(
            topic=topic,
            metadata={"genre": genre, "language": language, "tags": seo_meta.get("search_tags", [])},
            final_story=full_dialogue,
            episode_id=run_id,
            show_slug=genre,
        )

        logger.info(f"swarm_pipeline_completed: run_id={run_id}, status=SUCCESS")
        return {
            "run_id": run_id,
            "status": "completed",
            "topic": topic,
            "topic_uniqueness": topic_check,
            "model_routing": model_selection,
            "preflight_cost": cost_est,
            "compliance_guard": compliance,
            "storyboard": storyboard,
            "subtitle_bundle": sub_bundle,
            "audio_stems": {k: str(v) for k, v in stems.items()},
            "filter_complex_graph": filter_complex["filter_complex_graph"],
            "seo_metadata": seo_meta,
            "publisher_payload": pub_payload,
        }


swarm_coordinator = SwarmCoordinator()

__all__ = ["SwarmCoordinator", "swarm_coordinator"]
