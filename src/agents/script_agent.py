"""Retention Scriptwriting & Scene Storyboard Director Agent."""

from typing import Any
from src.core.telemetry import logger
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
    ) -> dict[str, Any]:
        """Draft a complete high-retention video script and scene storyboard.

        Coordinates with:
        - mcp-topic-memory to ensure concept originality
        - mcp-model-selector to choose the optimal scripting LLM
        """
        logger.info(f"script_agent_drafting: topic='{topic}', genre='{genre}'")

        # 1. Check Topic Originality
        topic_check = await check_topic_duplicate(topic)
        if topic_check["is_duplicate"]:
            logger.warning(f"topic_near_duplicate: similarity={topic_check['max_similarity_score']}")

        # 2. Query MCP Model Selector for primary script model
        model_meta = await select_best_model(category="script_creative")

        # 3. Generate Structured 3-Scene Storyboard
        prompt = (
            f"Act as broadcast director. Write a high-retention {genre} storyboard on '{topic}'. "
            f"Include an opening 5-second hook, escalation scenes, and punchline. Duration: {target_duration_seconds}s."
        )
        storyboard = await self.llm.generate_structured(prompt)

        return {
            "title": storyboard.get("title", topic),
            "hook_thesis": storyboard.get("hook_thesis", "The hidden reality that nobody talks about"),
            "target_duration_seconds": storyboard.get("target_duration_seconds", target_duration_seconds),
            "scenes": storyboard.get("scenes", []),
            "topic_memory_score": topic_check["max_similarity_score"],
            "script_model_used": model_meta["selected_model"],
            "provider": model_meta["provider"],
        }


script_agent = ScriptAgent()

__all__ = ["ScriptAgent", "script_agent"]
