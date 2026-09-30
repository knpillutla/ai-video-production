"""Topic Memory MCP Server for topic, metadata, and story deduplication."""

from __future__ import annotations
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from src.mcp.base import MCPServerBase
from src.scripts.youtube_ingest import compute_text_cosine_similarity

server = MCPServerBase(server_name="mcp-topic-memory", version="1.0.0")

import json
import re
from pathlib import Path

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


def _get_channel_storage_folder(user_id: Optional[str] = None, channel_id: Optional[str] = None) -> Path:
    """Resolve the channel storage directory under storage/<user_container>/channels/<channel_id>/."""
    eff_uid = str(user_id or "knpillutla").strip()
    eff_chan = str(channel_id or "default_channel").strip()
    clean_chan = re.sub(r"[^a-zA-Z0-9_-]", "_", eff_chan).strip("_") or "default_channel"
    p_direct = Path(f"storage/{eff_uid}/channels/{clean_chan}")
    if p_direct.is_dir():
        return p_direct
    clean_id = re.sub(r"[^a-zA-Z0-9-]", "-", eff_uid).lower()
    clean_id = re.sub(r"-+", "-", clean_id).strip("-")
    container_name = clean_id if clean_id.startswith("user-") else f"user-{clean_id}"
    chan_dir = Path(f"storage/{container_name[:63]}/channels/{clean_chan[:64]}")
    chan_dir.mkdir(parents=True, exist_ok=True)
    return chan_dir


def _get_vault_file(user_id: Optional[str] = None, channel_id: Optional[str] = None) -> Path:
    """Get the channel-scoped topic memory vault file path."""
    folder = _get_channel_storage_folder(user_id, channel_id)
    return folder / "topic_memory_vault.json"


def _get_vault(user_id: Optional[str] = None, channel_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieve in-memory seeds and disk-persisted topic memory entries for a user's channel."""
    entries = list(_SEED_VAULT)
    v_file = _get_vault_file(user_id, channel_id)
    if v_file.is_file():
        try:
            data = json.loads(v_file.read_text(encoding="utf-8"))
            if isinstance(data, list):
                seen = {(str(e.get("user_id", "")), e["topic"], (e.get("metadata") or {}).get("language", "en").lower()) for e in entries}
                for item in data:
                    key = (str(item.get("user_id", "")), item.get("topic"), (item.get("metadata") or {}).get("language", "en").lower())
                    if key not in seen:
                        entries.append(item)
                        seen.add(key)
        except Exception:
            pass
    return entries


def _persist_vault(record: Dict[str, Any], user_id: Optional[str] = None, channel_id: Optional[str] = None) -> None:
    """Append a newly remembered topic to channel's disk vault under storage/<user>/channels/<channel>/."""
    try:
        eff_uid = user_id or record.get("user_id")
        eff_chan = channel_id or record.get("channel_id")
        v_file = _get_vault_file(eff_uid, eff_chan)
        v_file.parent.mkdir(parents=True, exist_ok=True)
        current = []
        if v_file.is_file():
            try:
                current = json.loads(v_file.read_text(encoding="utf-8"))
            except Exception:
                current = []
        current.append(record)
        v_file.write_text(json.dumps(current, indent=2), encoding="utf-8")
    except Exception:
        pass


def _format_metadata_str(meta: Optional[Dict[str, Any]]) -> str:
    """Flatten metadata dictionary into a searchable text string."""
    if not meta:
        return ""
    tags = " ".join(meta.get("tags", [])) if isinstance(meta.get("tags"), list) else ""
    genre = str(meta.get("genre", ""))
    target = str(meta.get("target_audience", ""))
    return f"{genre} {tags} {target}".strip()


def recent_topic_context(
    user_id: Optional[str] = None,
    channel_id: Optional[str] = None,
    language: str = "en",
    limit: int = 15,
) -> List[str]:
    """Return recent same-language premises for creative-planner exclusions scoped to channel."""
    entries = _get_vault(user_id, channel_id)
    scoped = [
        entry for entry in entries
        if (not user_id or str(entry.get("user_id", "")) == str(user_id))
        and (entry.get("metadata") or {}).get("language", "en").lower() == language.lower()
    ]
    return [str(entry.get("topic", "")) for entry in scoped[-limit:] if entry.get("topic")]


async def check_topic_duplicate(
    topic: str,
    metadata: Optional[Dict[str, Any]] = None,
    final_story: Optional[str] = None,
    threshold: float = 0.80,
    user_id: Optional[str] = None,
    channel_id: Optional[str] = None,
    language: Optional[str] = None,
) -> Dict[str, Any]:
    """Check if proposed video topic duplicates existing productions for this user channel & language."""
    highest_sim = 0.0
    conflicting_entry: Optional[Dict[str, Any]] = None
    candidate_meta_str = _format_metadata_str(metadata)
    candidate_lang = language or (metadata.get("language") if metadata else None) or "en"

    eff_user_id = user_id or (metadata.get("user_id") if metadata else None)
    eff_channel_id = channel_id or (metadata.get("channel_id") if metadata else None)
    entries_to_check = _get_vault(eff_user_id, eff_channel_id)
    if eff_user_id is not None:
        entries_to_check = [
            e for e in entries_to_check
            if not e.get("user_id") or str(e.get("user_id")).strip() == str(eff_user_id).strip()
        ]

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

        sim = max((topic_sim * 0.6) + (meta_sim * 0.2) + (story_sim * 0.2), topic_sim) if (candidate_meta_str or final_story) else topic_sim

        entry_meta = entry.get("metadata") or {}
        entry_lang = entry_meta.get("language") or "en"
        if sim >= threshold and entry_lang.lower() == candidate_lang.lower():
            if sim > highest_sim:
                highest_sim = sim
                conflicting_entry = entry

    is_duplicate = conflicting_entry is not None
    alert_msg = None
    if is_duplicate and conflicting_entry:
        alert_msg = (
            f"DUPLICATE CONTENT ALERT: Video generation blocked! The proposed topic '{topic}' "
            f"already exists in this channel for language '{candidate_lang}' in episode '{conflicting_entry['topic']}' "
            f"(Episode ID: {conflicting_entry.get('episode_id', 'unknown')}). "
            f"Creating duplicate content on the same channel is blocked to avoid demonetization and channel audience cannibalization."
        )

    return {
        "candidate_topic": topic,
        "language": candidate_lang,
        "max_similarity_score": round(highest_sim, 4),
        "threshold": threshold,
        "is_duplicate": is_duplicate,
        "user_id": str(eff_user_id) if eff_user_id else None,
        "channel_id": str(eff_channel_id) if eff_channel_id else None,
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
    channel_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Record an approved topic, its metadata, and final story into channel memory vault."""
    eff_user_id = user_id or (metadata.get("user_id") if metadata else None)
    eff_channel_id = channel_id or (metadata.get("channel_id") if metadata else None)

    record = {
        "topic": topic.strip(),
        "metadata": metadata or {},
        "final_story": final_story,
        "episode_id": episode_id,
        "show_slug": show_slug,
        "user_id": str(eff_user_id) if eff_user_id else None,
        "channel_id": str(eff_channel_id) if eff_channel_id else None,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    _persist_vault(record, eff_user_id, eff_channel_id)
    vault_entries = _get_vault(eff_user_id, eff_channel_id)
    return {
        "status": "memorized",
        "total_topics_tracked": len(vault_entries),
        "recorded_topic": record["topic"],
        "user_id": record["user_id"],
        "channel_id": record["channel_id"],
        "has_metadata": bool(metadata),
        "has_story": bool(final_story),
    }


def clear_topic_vault(user_id: Optional[str] = None, channel_id: Optional[str] = None) -> int:
    """Clear topic memory vault file for specified channel under storage/<user>/channels/<channel>/."""
    v_file = _get_vault_file(user_id, channel_id)
    if v_file.is_file():
        try:
            data = json.loads(v_file.read_text(encoding="utf-8"))
            count = len(data) if isinstance(data, list) else 1
            v_file.unlink()
            return count
        except Exception:
            return 0
    return 0


server.register_tool(
    name="mcp_check_topic_duplicate",
    description="Check if candidate topic duplicates existing productions in a channel using cosine similarity",
    input_schema={
        "type": "object",
        "properties": {
            "topic": {"type": "string", "description": "Candidate topic or video thesis statement"},
            "metadata": {"type": "object", "description": "Optional metadata dictionary"},
            "final_story": {"type": "string", "description": "Optional story text"},
            "threshold": {"type": "number", "default": 0.80},
            "user_id": {"type": "string", "description": "User identifier"},
            "channel_id": {"type": "string", "description": "Channel identifier to scope deduplication to channel"},
        },
        "required": ["topic"],
    },
    handler=check_topic_duplicate,
)

server.register_tool(
    name="mcp_remember_topic",
    description="Commit an approved episode topic, metadata, and story into channel memory vault",
    input_schema={
        "type": "object",
        "properties": {
            "topic": {"type": "string"},
            "metadata": {"type": "object"},
            "final_story": {"type": "string"},
            "episode_id": {"type": "string", "default": ""},
            "show_slug": {"type": "string", "default": "default"},
            "user_id": {"type": "string", "description": "User identifier"},
            "channel_id": {"type": "string", "description": "Channel identifier"},
        },
        "required": ["topic"],
    },
    handler=remember_topic,
)

server.register_tool(
    name="mcp_clear_topic_memory",
    description="Clear remembered topics from vault, optionally scoped to a specific user channel",
    input_schema={
        "type": "object",
        "properties": {
            "user_id": {"type": "string", "description": "Optional user ID"},
            "channel_id": {"type": "string", "description": "Optional channel ID"},
        },
    },
    handler=lambda user_id=None, channel_id=None: {"cleared_count": clear_topic_vault(user_id, channel_id)},
)

if __name__ == "__main__":
    server.run_cli()
