"""Topic Memory MCP Server for topic, metadata, and story deduplication."""

from __future__ import annotations
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from src.mcp.base import MCPServerBase
from src.scripts.youtube_ingest import compute_text_cosine_similarity

server = MCPServerBase(server_name="mcp-topic-memory", version="1.0.0")

import json
from pathlib import Path

VAULT_FILE = Path("storage/topic_memory_vault.json")

_SEED_VAULT: List[Dict[str, Any]] = [
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


def _get_vault() -> List[Dict[str, Any]]:
    """Retrieve in-memory and disk-persisted topic memory entries."""
    entries = list(_SEED_VAULT)
    if VAULT_FILE.is_file():
        try:
            data = json.loads(VAULT_FILE.read_text(encoding="utf-8"))
            if isinstance(data, list):
                seen = {e["topic"] for e in entries}
                for item in data:
                    if item.get("topic") not in seen:
                        entries.append(item)
                        seen.add(item["topic"])
        except Exception:
            pass
    return entries


def _persist_vault(record: Dict[str, Any]) -> None:
    """Append a newly remembered topic to disk vault."""
    try:
        VAULT_FILE.parent.mkdir(parents=True, exist_ok=True)
        current = []
        if VAULT_FILE.is_file():
            try:
                current = json.loads(VAULT_FILE.read_text(encoding="utf-8"))
            except Exception:
                current = []
        current.append(record)
        VAULT_FILE.write_text(json.dumps(current, indent=2), encoding="utf-8")
    except Exception:
        pass


_TOPIC_VAULT = _get_vault()


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
    user_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Check if proposed video topic duplicates existing productions for this user."""
    highest_sim = 0.0
    conflicting_entry: Optional[Dict[str, Any]] = None
    candidate_meta_str = _format_metadata_str(metadata)

    global _TOPIC_VAULT
    _TOPIC_VAULT = _get_vault()

    eff_user_id = user_id or (metadata.get("user_id") if metadata else None)
    if eff_user_id is not None:
        entries_to_check = [
            e for e in _TOPIC_VAULT
            if e.get("user_id") and str(e.get("user_id")).strip() == str(eff_user_id).strip()
        ]
    else:
        entries_to_check = _TOPIC_VAULT

    for entry in entries_to_check:
        topic_sim = compute_text_cosine_similarity(topic, entry["topic"])
        entry_meta_str = _format_metadata_str(entry.get("metadata"))
        meta_sim = (
            compute_text_cosine_similarity(candidate_meta_str, entry_meta_str)
            if candidate_meta_str and entry_meta_str else 0.0
        )
        entry_story = entry.get("final_story", "")
        story_sim = (
            compute_text_cosine_similarity(final_story, entry_story)
            if final_story and entry_story else 0.0
        )

        if candidate_meta_str or final_story:
            sim = max((topic_sim * 0.6) + (meta_sim * 0.2) + (story_sim * 0.2), topic_sim)
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
            f"has {highest_sim * 100:.1f}% similarity with your existing episode '{conflicting_entry['topic']}' "
            f"(Episode ID: {conflicting_entry.get('episode_id', 'unknown')}). "
            f"Creating duplicate content is blocked to avoid demonetization and channel audience cannibalization."
        )

    return {
        "candidate_topic": topic,
        "max_similarity_score": round(highest_sim, 4),
        "threshold": threshold,
        "is_duplicate": is_duplicate,
        "user_id": str(eff_user_id) if eff_user_id else None,
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
    user_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Record an approved topic, its metadata, and final story into memory vault scoped to user."""
    eff_user_id = user_id or (metadata.get("user_id") if metadata else None)
    record = {
        "topic": topic.strip(),
        "metadata": metadata or {},
        "final_story": final_story.strip(),
        "episode_id": episode_id,
        "show_slug": show_slug,
        "user_id": str(eff_user_id) if eff_user_id else None,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    _TOPIC_VAULT.append(record)
    _persist_vault(record)
    return {
        "status": "memorized",
        "total_topics_tracked": len(_TOPIC_VAULT),
        "recorded_topic": record["topic"],
        "user_id": record["user_id"],
        "has_metadata": bool(metadata),
        "has_story": bool(final_story),
    }


def clear_topic_vault(user_id: Optional[str] = None) -> int:
    """Clear topic memory vault. If user_id is provided, only clear topics for that user."""
    global _TOPIC_VAULT
    current = _get_vault()
    if user_id:
        retained = [e for e in current if str(e.get("user_id", "")) != str(user_id)]
        cleared_count = len(current) - len(retained)
        _TOPIC_VAULT = retained
        VAULT_FILE.parent.mkdir(parents=True, exist_ok=True)
        disk_entries = [e for e in retained if e not in _SEED_VAULT]
        VAULT_FILE.write_text(json.dumps(disk_entries, indent=2), encoding="utf-8")
        return cleared_count
    else:
        cleared_count = len(current)
        _TOPIC_VAULT = list(_SEED_VAULT)
        VAULT_FILE.parent.mkdir(parents=True, exist_ok=True)
        VAULT_FILE.write_text("[]", encoding="utf-8")
        return cleared_count


server.register_tool(
    name="mcp_check_topic_duplicate",
    description="Check if candidate topic duplicates existing productions for a user using cosine similarity",
    input_schema={
        "type": "object",
        "properties": {
            "topic": {"type": "string", "description": "Candidate topic or video thesis statement"},
            "metadata": {"type": "object", "description": "Optional metadata dictionary"},
            "final_story": {"type": "string", "description": "Optional story text"},
            "threshold": {"type": "number", "default": 0.80},
            "user_id": {"type": "string", "description": "User identifier to scope deduplication to user"},
        },
        "required": ["topic"],
    },
    handler=check_topic_duplicate,
)

server.register_tool(
    name="mcp_remember_topic",
    description="Commit an approved episode topic, metadata, and story into user's memory vault",
    input_schema={
        "type": "object",
        "properties": {
            "topic": {"type": "string"},
            "metadata": {"type": "object"},
            "final_story": {"type": "string"},
            "episode_id": {"type": "string", "default": ""},
            "show_slug": {"type": "string", "default": "default"},
            "user_id": {"type": "string", "description": "User identifier"},
        },
        "required": ["topic"],
    },
    handler=remember_topic,
)

server.register_tool(
    name="mcp_clear_topic_memory",
    description="Clear remembered topics from vault, optionally scoped to a specific user",
    input_schema={
        "type": "object",
        "properties": {"user_id": {"type": "string", "description": "Optional user ID"}},
    },
    handler=lambda user_id=None: {"cleared_count": clear_topic_vault(user_id)},
)

if __name__ == "__main__":
    server.run_cli()
