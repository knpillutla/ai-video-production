"""Network-Level Character LoRA Asset Service.

Delegates to CoreLoraService and CoreAssetService for unified character consistency.
Maintains backward compatibility for network-scoped calls across CLI and Studio.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.services.core_asset_service import AssetScope, core_asset_service
from src.services.core_lora_service import CharacterLoraProfile, core_lora_service


def get_network_lora_dir(user_id: str, network: str) -> Path:
    """Return storage directory for network-level LoRA assets."""
    return core_asset_service.get_asset_dir(
        user_id=user_id, category="loras", scope=AssetScope.NETWORK, network=network
    )


def load_network_loras(user_id: str, network: str) -> dict[str, Any]:
    """Load character LoRAs registered under the given network."""
    profiles = core_lora_service.list_character_loras(user_id=user_id, network=network)
    return {
        "network": network,
        "characters": {p.name: p.model_dump() for p in profiles},
    }


def save_network_lora(
    user_id: str,
    network: str,
    character_key: str,
    lora_data: dict[str, Any],
) -> Path:
    """Register or update a character LoRA at the network level."""
    profile = CharacterLoraProfile(
        name=lora_data.get("name", character_key),
        gender=lora_data.get("gender", "female"),
        lora_url=lora_data.get("lora_url") or lora_data.get("path", ""),
        trigger_word=lora_data.get("trigger_word", f"{character_key.upper()}_TRIGGER"),
        scale=float(lora_data.get("scale", 1.0)),
        body_composition=lora_data.get("body_composition", "graceful medium-thin build with natural feminine curves"),
    )
    rec = core_lora_service.register_character_lora(
        user_id=user_id, network=network, character_key=character_key, profile=profile
    )
    return Path(rec.path_or_url)


def resolve_effective_loras(
    user_id: str,
    network: str | None,
    explicit_loras: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Resolve effective LoRAs prioritizing explicit overrides, otherwise loading network assets."""
    return core_lora_service.resolve_character_loras(
        user_id=user_id, network=network, explicit_loras=explicit_loras
    )


__all__ = [
    "get_network_lora_dir",
    "load_network_loras",
    "save_network_lora",
    "resolve_effective_loras",
]
