"""Topic Memory MCP Server for topic deduplication and vector cosine uniqueness."""

from typing import Any
from src.mcp.base import MCPServerBase
from src.scripts.youtube_ingest import compute_text_cosine_similarity

server = MCPServerBase(server_name="mcp-topic-memory", version="1.0.0")

# In-memory vector topic store (can synchronize to SQLite/Chroma)
_TOPIC_VAULT: list[dict[str, Any]] = [
    {
        "topic": "IT Employee Remote Work Confusions and Standup Comedy",
        "show_slug": "delhi_wfh_confusions",
        "episode_id": "ep_seed_001",
    },
    {
        "topic": "Traffic Jam Excuses and Office Commute Horror Stories",
        "show_slug": "delhi_wfh_confusions",
        "episode_id": "ep_seed_002",
    },
]


async def check_topic_duplicate(topic: str, threshold: float = 0.80) -> dict[str, Any]:
    """Check whether a proposed video topic duplicates previously produced content."""
    highest_sim = 0.0
    conflicting_topic = None

    for entry in _TOPIC_VAULT:
        sim = compute_text_cosine_similarity(topic, entry["topic"])
        if sim > highest_sim:
            highest_sim = sim
            conflicting_topic = entry["topic"]

    is_duplicate = highest_sim >= threshold
    return {
        "candidate_topic": topic,
        "max_similarity_score": round(highest_sim, 4),
        "threshold": threshold,
        "is_duplicate": is_duplicate,
        "conflicting_topic": conflicting_topic if is_duplicate else None,
        "recommendation": "Reject: Idea already produced in channel universe" if is_duplicate else "Approved: Fresh and original concept",
    }


async def remember_topic(topic: str, episode_id: str = "", show_slug: str = "default") -> dict[str, Any]:
    """Record an approved topic into the historical memory vault."""
    record = {
        "topic": topic.strip(),
        "episode_id": episode_id,
        "show_slug": show_slug,
    }
    _TOPIC_VAULT.append(record)
    return {
        "status": "memorized",
        "total_topics_tracked": len(_TOPIC_VAULT),
        "recorded_topic": record["topic"],
    }


server.register_tool(
    name="mcp_check_topic_duplicate",
    description="Check if a candidate video topic duplicates existing episodes using vector cosine similarity",
    input_schema={
        "type": "object",
        "properties": {
            "topic": {"type": "string", "description": "Candidate topic or video thesis statement"},
            "threshold": {"type": "number", "default": 0.80, "description": "Maximum allowed similarity score"},
        },
        "required": ["topic"],
    },
    handler=check_topic_duplicate,
)

server.register_tool(
    name="mcp_remember_topic",
    description="Commit an approved episode concept into the long-term topic memory vault",
    input_schema={
        "type": "object",
        "properties": {
            "topic": {"type": "string", "description": "Approved episode topic text"},
            "episode_id": {"type": "string", "default": ""},
            "show_slug": {"type": "string", "default": "default"},
        },
        "required": ["topic"],
    },
    handler=remember_topic,
)

if __name__ == "__main__":
    server.run_cli()
