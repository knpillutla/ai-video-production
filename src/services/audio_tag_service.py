"""Shared normalization for audio tags returned by creative models."""

from typing import Any


def normalize_audio_tags(value: Any) -> str:
    """Convert model-produced audio tag values into the pipeline's string contract."""
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, (list, tuple, set)):
        return ", ".join(
            normalized
            for item in value
            if (normalized := normalize_audio_tags(item))
        )
    return str(value)