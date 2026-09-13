"""Retention Scriptwriting & Scene Storyboard Director Agent."""

from typing import Any
from src.core.telemetry import logger
from src.mcp.model_selector.cultural_catalog import lookup_art_style
from src.mcp.model_selector.server import select_best_model
from src.mcp.topic_memory.server import check_topic_duplicate
from src.providers.llm.gemini_adapter import GeminiLLMAdapter


class ScriptAgent:
    """Specialized Agent responsible for audience retention hooks and structured scene drafting."""

    def __init__(self):
        self.llm = GeminiLLMAdapter()

    async def draft_episode_storyboard(
        self,
        topic: str,
        genre: str = "comedy",
        target_duration_seconds: int = 480,
        video_format: str = "",
        art_style: str = "",
        language: str = "en",
    ) -> dict[str, Any]:
        """Draft a complete high-retention video script and scene storyboard.

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

        # 4. Generate Structured Storyboard Plan
        combined_cues = f"{genre} {video_format} {topic}".lower()
        if any(k in combined_cues for k in ("scenic", "walk", "drive", "relaxation", "lounge", "nature", "alps", "rain")):
            prompt = (
                f"Act as world-class cinematography director. Write an immersive {style_name} storyboard on '{topic}'. "
                f"Aesthetic: {decorations}. Lighting: {lighting}. Color Palette: {palette}. "
                f"Directorial Guidance: {guidance}. Format: {video_format or 'Scenic Relaxation'}. "
                f"Include 4K visual scene prompts with steady camera motion, authentic ambient foley ASMR cues, "
                f"and soothing narration or atmospheric titles. Duration: {target_duration_seconds}s. Language: {language}."
            )
        else:
            prompt = (
                f"Act as broadcast director. Write a high-retention {genre} storyboard on '{topic}' in {style_name} style. "
                f"Visual Style: {decorations}. Lighting: {lighting}. Guidance: {guidance}. "
                f"Include an opening 5-second hook, escalation scenes, and punchline. Duration: {target_duration_seconds}s. Language: {language}."
            )

        storyboard = await self.llm.generate_structured(prompt)

        return {
            "title": storyboard.get("title", topic),
            "hook_thesis": storyboard.get("hook_thesis", "The hidden reality that nobody talks about"),
            "target_duration_seconds": storyboard.get("target_duration_seconds", target_duration_seconds),
            "scenes": storyboard.get("scenes", []),
            "art_style": style_name,
            "lighting_scheme": lighting,
            "color_palette": palette,
            "topic_memory_score": topic_check["max_similarity_score"],
            "script_model_used": model_meta["selected_model"],
            "provider": model_meta["provider"],
        }


script_agent = ScriptAgent()

__all__ = ["ScriptAgent", "script_agent"]
