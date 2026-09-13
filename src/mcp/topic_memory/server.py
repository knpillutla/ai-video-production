"""Topic Memory MCP Server for topic, metadata, and story deduplication."""

from __future__ import annotations
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from src.mcp.base import MCPServerBase
from src.scripts.youtube_ingest import compute_text_cosine_similarity

server = MCPServerBase(server_name="mcp-topic-memory", version="1.0.0")

# Persistent in-memory & file-backed topic, metadata, and story vault
_TOPIC_VAULT: List[Dict[str, Any]] = [
    {
        "topic": "IT Employee Remote Work Confusions and Standup Comedy",
        "show_slug": "delhi_wfh_confusions",
        "episode_id": "ep_seed_001",
        "metadata": {"genre": "comedy", "tags": ["wfh", "corporate", "remote"]},
        "final_story": "A techie struggles through endless 9am agile standups while wearing pajamas.",
        "created_at": "2026-09-10T12:00:00Z",
    },
    {
        "topic": "Traffic Jam Excuses and Office Commute Horror Stories",
        "show_slug": "delhi_wfh_confusions",
        "episode_id": "ep_seed_002",
        "metadata": {"genre": "comedy", "tags": ["traffic", "delhi", "commute"]},
        "final_story": "Hilarious monsoon traffic blockages in Silk Board and Cyber City.",
        "created_at": "2026-09-11T12:00:00Z",
    },
]


def _format_metadata_str(meta: Optional[Dict[str, Any]]) -> str:
    """Flatten metadata dictionary into a searchable text string."""
    if not meta:
        return ""
    tags = " ".join(meta.get("tags", [])) if isinstance(meta.get("tags"), list) else ""
    genre = str(meta.get("genre", ""))
    target = str(meta.get("target_audience", ""))
    return f"{genre} {tags} {target}".strip()


async def check_topic_duplicate(
    topic: str,
    metadata: Optional[Dict[str, Any]] = None,
    final_story: Optional[str] = None,
    threshold: float = 0.80,
) -> Dict[str, Any]:
    """Check if proposed video topic, metadata, or story duplicates existing productions."""
    highest_sim = 0.0
    conflicting_entry: Optional[Dict[str, Any]] = None
    candidate_meta_str = _format_metadata_str(metadata)

    for entry in _TOPIC_VAULT:
        # 1. Topic cosine similarity (60% weight)
        topic_sim = compute_text_cosine_similarity(topic, entry["topic"])

        # 2. Metadata similarity (20% weight if provided)
        entry_meta_str = _format_metadata_str(entry.get("metadata"))
        meta_sim = (
            compute_text_cosine_similarity(candidate_meta_str, entry_meta_str)
            if candidate_meta_str and entry_meta_str else 0.0
        )

        # 3. Final story similarity (20% weight if provided)
        entry_story = entry.get("final_story", "")
        story_sim = (
            compute_text_cosine_similarity(final_story, entry_story)
            if final_story and entry_story else 0.0
        )

        # Composite score
        if candidate_meta_str or final_story:
            sim = (topic_sim * 0.6) + (meta_sim * 0.2) + (story_sim * 0.2)
            # Direct topic match override
            if topic_sim > sim:
                sim = topic_sim
        else:
            sim = topic_sim

        if sim > highest_sim:
            highest_sim = sim
            conflicting_entry = entry

    is_duplicate = highest_sim >= threshold
    alert_msg = None
    if is_duplicate and conflicting_entry:
        alert_msg = (
            f"DUPLICATE CONTENT ALERT: Video generation blocked! The proposed topic '{topic}' "
            f"has {highest_sim * 100:.1f}% similarity with existing episode '{conflicting_entry['topic']}' "
            f"(Episode ID: {conflicting_entry.get('episode_id', 'unknown')}). "
            f"Creating duplicate content is blocked to avoid demonetization and channel audience cannibalization."
        )

    return {
        "candidate_topic": topic,
        "max_similarity_score": round(highest_sim, 4),
        "threshold": threshold,
        "is_duplicate": is_duplicate,
        "conflicting_topic": conflicting_entry["topic"] if is_duplicate and conflicting_entry else None,
        "conflicting_episode_id": conflicting_entry.get("episode_id") if is_duplicate and conflicting_entry else None,
        "alert_message": alert_msg,
        "recommendation": alert_msg if is_duplicate else "Approved: Fresh and original concept",
    }


async def remember_topic(
    topic: str,
    metadata: Optional[Dict[str, Any]] = None,
    final_story: str = "",
    episode_id: str = "",
    show_slug: str = "default",
) -> Dict[str, Any]:
    """Record an approved topic, its metadata, and final synthesized story into memory vault."""
    record = {
        "topic": topic.strip(),
        "metadata": metadata or {},
        "final_story": final_story.strip(),
        "episode_id": episode_id,
        "show_slug": show_slug,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    _TOPIC_VAULT.append(record)
    return {
        "status": "memorized",
        "total_topics_tracked": len(_TOPIC_VAULT),
        "recorded_topic": record["topic"],
        "has_metadata": bool(metadata),
        "has_story": bool(final_story),
    }


server.register_tool(
    name="mcp_check_topic_duplicate",
    description="Check if candidate topic, metadata, and story duplicate existing productions using cosine similarity",
    input_schema={
        "type": "object",
        "properties": {
            "topic": {"type": "string", "description": "Candidate topic or video thesis statement"},
            "metadata": {"type": "object", "description": "Optional metadata dictionary (genre, tags, target audience)"},
            "final_story": {"type": "string", "description": "Optional draft or finalized story text"},
            "threshold": {"type": "number", "default": 0.80, "description": "Maximum allowed similarity score"},
        },
        "required": ["topic"],
    },
    handler=check_topic_duplicate,
)

server.register_tool(
    name="mcp_remember_topic",
    description="Commit an approved episode topic, metadata, and final story into the topic memory vault",
    input_schema={
        "type": "object",
        "properties": {
            "topic": {"type": "string", "description": "Approved episode topic text"},
            "metadata": {"type": "object", "description": "Episode metadata dictionary"},
            "final_story": {"type": "string", "description": "Final story synthesized from script"},
            "episode_id": {"type": "string", "default": ""},
            "show_slug": {"type": "string", "default": "default"},
        },
        "required": ["topic"],
    },
    handler=remember_topic,
)

if __name__ == "__main__":
    server.run_cli()
