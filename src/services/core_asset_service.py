"""Core Tiered Universal Asset Service.

Manages studio assets across three hierarchical scopes:
1. Global Scope: storage/user/assets/{category} (fonts, universal audio, LUTs)
2. Network Scope: storage/user/networks/{network}/assets/{category} (character LoRAs, channel logos)
3. Episode Scope: storage/.../episodes/{episode_id} (specific keyframes, isolated stems)
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
import json
from pathlib import Path
import re
from typing import Any
from pydantic import BaseModel, Field

from src.core.storage import storage_service
from src.core.telemetry import logger


class AssetScope(str, Enum):
    GLOBAL = "global"
    NETWORK = "network"
    EPISODE = "episode"


class AssetRecord(BaseModel):
    """Canonical registry record for any managed asset in the studio."""

    asset_id: str
    category: str
    name: str
    path_or_url: str
    scope: AssetScope = AssetScope.NETWORK
    network: str | None = None
    episode_id: str | None = None
    file_size_bytes: int = 0
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: dict[str, Any] = Field(default_factory=dict)


class CoreAssetService:
    """Universal hierarchical asset engine for Studio UI, API, and CLI."""

    MANIFEST_NAME = "asset_manifest.json"

    def get_asset_dir(
        self,
        user_id: str,
        category: str,
        scope: AssetScope = AssetScope.NETWORK,
        network: str | None = None,
        episode_id: str | None = None,
    ) -> Path:
        """Resolve directory path for a scoped asset category."""
        clean_cat = re.sub(r"[^a-zA-Z0-9_-]", "_", category.lower()).strip("_") or "general"
        if scope == AssetScope.GLOBAL:
            target = storage_service.get_global_assets_path(user_id, clean_cat)
        elif scope == AssetScope.NETWORK:
            clean_net = re.sub(r"[^a-zA-Z0-9_-]", "_", str(network or "default").lower()).strip("_")
            target = storage_service.get_network_path(user_id, clean_net) / "assets" / clean_cat
        else:
            clean_net = re.sub(r"[^a-zA-Z0-9_-]", "_", str(network or "default").lower()).strip("_")
            target = storage_service.get_channel_episode_path(user_id, clean_net, str(episode_id or "ep_001")) / "assets" / clean_cat

        target.mkdir(parents=True, exist_ok=True)
        return target

    def _load_manifest(self, directory: Path) -> dict[str, Any]:
        manifest_file = directory / self.MANIFEST_NAME
        if manifest_file.is_file() and manifest_file.stat().st_size > 10:
            try:
                return json.loads(manifest_file.read_text(encoding="utf-8"))
            except Exception as e:
                logger.warning(f"asset_manifest_read_error: {e}")
        return {"assets": {}}

    def _save_manifest(self, directory: Path, data: dict[str, Any]) -> None:
        manifest_file = directory / self.MANIFEST_NAME
        try:
            manifest_file.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        except Exception as e:
            logger.warning(f"asset_manifest_write_error: {e}")

    def register_asset(
        self,
        user_id: str,
        category: str,
        name: str,
        path_or_url: str,
        scope: AssetScope = AssetScope.NETWORK,
        network: str | None = None,
        episode_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> AssetRecord:
        """Register or update an asset in its target scope manifest."""
        target_dir = self.get_asset_dir(user_id, category, scope=scope, network=network, episode_id=episode_id)
        asset_id = f"{category}_{re.sub(r'[^a-zA-Z0-9_-]', '_', name.lower())}"

        size = 0
        p = Path(path_or_url)
        if p.is_file():
            size = p.stat().st_size

        record = AssetRecord(
            asset_id=asset_id,
            category=category,
            name=name,
            path_or_url=str(path_or_url),
            scope=scope,
            network=network,
            episode_id=episode_id,
            file_size_bytes=size,
            metadata=metadata or {},
        )

        manifest = self._load_manifest(target_dir)
        manifest["assets"][asset_id] = record.model_dump()
        self._save_manifest(target_dir, manifest)
        logger.info(f"core_asset_registered: id={asset_id}, scope={scope.value}, cat={category}")
        return record

    def list_assets(
        self,
        user_id: str,
        category: str,
        scope: AssetScope = AssetScope.NETWORK,
        network: str | None = None,
    ) -> list[AssetRecord]:
        """List all assets registered within a scope and category."""
        target_dir = self.get_asset_dir(user_id, category, scope=scope, network=network)
        manifest = self._load_manifest(target_dir)
        return [AssetRecord(**rec) for rec in manifest.get("assets", {}).values()]

    def resolve_asset(
        self,
        user_id: str,
        category: str,
        name: str,
        network: str | None = None,
    ) -> AssetRecord | None:
        """Resolve an asset checking Network scope first, then falling back to Global scope."""
        asset_id = f"{category}_{re.sub(r'[^a-zA-Z0-9_-]', '_', name.lower())}"
        if network:
            net_dir = self.get_asset_dir(user_id, category, scope=AssetScope.NETWORK, network=network)
            net_manifest = self._load_manifest(net_dir)
            if asset_id in net_manifest.get("assets", {}):
                return AssetRecord(**net_manifest["assets"][asset_id])

        global_dir = self.get_asset_dir(user_id, category, scope=AssetScope.GLOBAL)
        global_manifest = self._load_manifest(global_dir)
        if asset_id in global_manifest.get("assets", {}):
            return AssetRecord(**global_manifest["assets"][asset_id])

        return None


core_asset_service = CoreAssetService()

__all__ = ["AssetScope", "AssetRecord", "CoreAssetService", "core_asset_service"]
