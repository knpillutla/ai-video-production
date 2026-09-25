"""Topic Memory service facade for persistent topic deduplication."""

from typing import Any, Dict, List, Optional, Tuple
from src.core.telemetry import logger
from src.mcp.topic_memory.server import (
    check_topic_duplicate,
    remember_topic as mcp_remember_topic,
    recent_topic_context,
)


class TopicMemoryService:
    """Unified service for pre-flight topic deduplication and story persistence."""

    async def is_duplicate_topic(
        self,
        topic: str,
        genre: str = "general",
        tags: Optional[List[str]] = None,
        threshold: float = 0.80,
    ) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """Check if topic is duplicate (> threshold similarity) via MCP topic memory."""
        try:
            res = await check_topic_duplicate(topic, metadata={"genre": genre, "tags": tags or []}, threshold=threshold)
            is_dup = res.get("is_duplicate", False)
            conflict = res.get("conflict")
            return is_dup, conflict
        except Exception as exc:
            logger.warning(f"topic_memory_check_fallback: {exc}")
            return False, None

    def remember_topic(
        self,
        topic: str,
        genre: str,
        tags: List[str],
        story_synopsis: str,
        episode_id: str,
    ) -> None:
        """Persist topic, metadata, and story synopsis to Topic Memory."""
        try:
            mcp_remember_topic(
                topic=topic,
                metadata={"genre": genre, "tags": tags, "episode_id": episode_id},
                story=story_synopsis,
            )
            logger.info(f"topic_remembered: topic='{topic}' ep={episode_id}")
        except Exception as exc:
            logger.warning(f"topic_memory_save_fallback: {exc}")


topic_memory = TopicMemoryService()

__all__ = ["topic_memory", "TopicMemoryService"]
