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
        user_id: Optional[str] = None,
        channel_id: Optional[str] = None,
    ) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """Check if topic is duplicate (> threshold similarity) via MCP topic memory."""
        try:
            res = await check_topic_duplicate(
                topic,
                metadata={"genre": genre, "tags": tags or [], "user_id": user_id, "channel_id": channel_id},
                threshold=threshold,
                user_id=user_id,
                channel_id=channel_id,
            )
            is_dup = res.get("is_duplicate", False)
            conflict = res.get("conflicting_topic")
            return is_dup, res if is_dup else None
        except Exception as exc:
            logger.warning(f"topic_memory_check_fallback: {exc}")
            return False, None

    async def remember_topic(
        self,
        topic: str,
        genre: str,
        tags: List[str],
        story_synopsis: str,
        episode_id: str,
        user_id: Optional[str] = None,
        channel_id: Optional[str] = None,
    ) -> None:
        """Persist topic, metadata, and story synopsis to Topic Memory scoped to user channel."""
        try:
            await mcp_remember_topic(
                topic=topic,
                metadata={"genre": genre, "tags": tags, "episode_id": episode_id, "user_id": user_id, "channel_id": channel_id},
                final_story=story_synopsis,
                episode_id=episode_id,
                user_id=user_id,
                channel_id=channel_id,
            )
            logger.info(f"topic_remembered: topic='{topic}' ep={episode_id} chan={channel_id}")
        except Exception as exc:
            logger.warning(f"topic_memory_save_fallback: {exc}")

    async def record_production(
        self,
        topic: str,
        genre: str,
        tags: List[str],
        episode_id: str,
        story_synopsis: str = "",
        user_id: Optional[str] = None,
        channel_id: Optional[str] = None,
    ) -> None:
        """Alias for remember_topic to persist completed productions."""
        await self.remember_topic(
            topic=topic,
            genre=genre,
            tags=tags,
            story_synopsis=story_synopsis or topic,
            episode_id=episode_id,
            user_id=user_id,
            channel_id=channel_id,
        )

    def get_recent_topics(
        self,
        user_id: Optional[str] = None,
        channel_id: Optional[str] = None,
        language: str = "en",
        limit: int = 15,
    ) -> List[str]:
        """Retrieve recent topics to inject into LLM prompts as negative exclusions for channel."""
        try:
            return recent_topic_context(user_id=user_id, channel_id=channel_id, language=language, limit=limit)
        except Exception as exc:
            logger.warning(f"get_recent_topics_failed: {exc}")
            return []


topic_memory = TopicMemoryService()

__all__ = ["topic_memory", "TopicMemoryService"]
