"""Retention Scriptwriting & Scene Storyboard Director Agent."""

from typing import Any
from src.compliance.ypp_safety import evaluate_ypp_safety
from src.core.telemetry import logger
from src.mcp.model_selector.cultural_catalog import lookup_art_style
from src.mcp.model_selector.server import select_best_model
from src.mcp.prompt_director import get_directorial_prompt
from src.mcp.topic_memory.server import check_topic_duplicate
from src.providers.llm.gemini_adapter import GeminiLLMAdapter


class ScriptAgent:
    """Specialized Agent responsible for audience retention hooks and structured scene drafting."""

    def __init__(self):
        self.llm = GeminiLLMAdapter()

    def _build_genre_monetization_prompt(self, **kwargs) -> tuple[str, str]:
        """Backward compatible helper delegating to directorial prompt router."""
        from src.mcp.prompt_director.directorial_router import build_directorial_prompt
        return build_directorial_prompt(**kwargs)

    async def draft_episode_storyboard(
        self,
        topic: str,
        genre: str = "comedy",
        target_duration_seconds: int = 480,
        video_format: str = "",
        art_style: str = "",
        language: str = "en",
    ) -> dict[str, Any]:
        """Draft a complete high-retention video script and scene storyboard with built-in monetization safety.

        Coordinates with:
        - mcp-topic-memory to ensure concept originality
        - mcp-model-selector to choose optimal scripting LLM and inject art style intelligence
        """
        logger.info(f"script_agent_drafting: topic='{topic}', genre='{genre}', style='{art_style}'")

        # 1. Check Topic Originality
        topic_check = await check_topic_duplicate(topic)
        if topic_check["is_duplicate"]:
            logger.warning(f"topic_near_duplicate: similarity={topic_check['max_similarity_score']}")

        # 2. Query MCP Model Selector for primary script model
        model_meta = await select_best_model(category="script_creative")

        # 3. Retrieve Art Style Directorial Anchors
        style_info = lookup_art_style(art_style or video_format or topic)
        style_name = style_info.get("display_name", "Broadcast 4K Photorealistic Cinematic")
        decorations = style_info.get("prompt_decorations", "")
        lighting = style_info.get("lighting_scheme", "")
        palette = style_info.get("color_palette", "")
        guidance = style_info.get("directorial_guidance", "")

        # 4. Generate Structured Storyboard Plan via Contextual Prompt Director MCP
        prompt_res = await get_directorial_prompt(
            topic=topic,
            genre=genre,
            video_format=video_format,
            style_name=style_name,
            decorations=decorations,
            lighting=lighting,
            palette=palette,
            guidance=guidance,
            target_duration_seconds=target_duration_seconds,
            language=language,
        )
        prompt = prompt_res["prompt"]
        mode = prompt_res["mode"]

        storyboard = await self.llm.generate_structured(prompt)

        # 5. Automated Pre-Flight Monetization & AdSense Audit
        scenes = storyboard.get("scenes", [])
        full_dialogue = " ".join(s.get("dialogue", "") for s in scenes)
        opening_dialogue = scenes[0].get("dialogue", "") if scenes else ""
        originality = 1.0 - float(topic_check.get("max_similarity_score", 0.0))
        ypp_audit = evaluate_ypp_safety(
            script_text=full_dialogue,
            opening_text=opening_dialogue,
            originality_score=originality,
        )

        if not ypp_audit["is_monetization_safe"]:
            logger.warning(
                f"script_ypp_safety_warning: risk={ypp_audit['risk_level']}, "
                f"adsense_violations={ypp_audit['adsense_violations']}, "
                f"opening_profanity={ypp_audit['opening_profanity_violations']}"
            )

        return {
            "title": storyboard.get("title", topic),
            "hook_thesis": storyboard.get("hook_thesis", "The hidden reality that nobody talks about"),
            "target_duration_seconds": storyboard.get("target_duration_seconds", target_duration_seconds),
            "scenes": scenes,
            "art_style": style_name,
            "lighting_scheme": lighting,
            "color_palette": palette,
            "production_mode": mode,
            "topic_memory_score": topic_check["max_similarity_score"],
            "script_model_used": model_meta["selected_model"],
            "provider": model_meta["provider"],
            "recommended_fps": storyboard.get("recommended_fps", 30 if mode == "music_dance" else (60 if mode == "scenic_narrative" else 24)),
            "vocal_gender": storyboard.get("vocal_gender", "female" if "female" in topic.lower() or "woman" in topic.lower() or "girl" in topic.lower() else "male"),
            "vocal_delivery_type": storyboard.get("vocal_delivery_type", "lead_lip_sync" if mode == "music_dance" else "voiceover_narration"),
            "ypp_monetization_safety": ypp_audit,
        }


script_agent = ScriptAgent()

__all__ = ["ScriptAgent", "script_agent"]

