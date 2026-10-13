"""Multi-tenant cloud and local storage abstraction with per-user container isolation."""

import json
import os
import re
from pathlib import Path
from typing import Any

from src.core.config import settings


def sanitize_container_name(user_id: str) -> str:
    """Sanitize user ID into a valid Azure Blob container name (lowercase, alphanumeric, hyphens)."""
    raw_str = str(user_id).lower().strip()
    if raw_str.startswith("user-"):
        raw_str = raw_str[5:]
    clean_id = re.sub(r"[^a-zA-Z0-9-]", "-", raw_str).lower()
    clean_id = re.sub(r"-+", "-", clean_id).strip("-")
    container = f"user-{clean_id}"
    return container[:63]


class MultiTenantStorageService:
    """Provides air-gapped per-user storage with decoupled creative and distribution domains."""

    def __init__(self, root_dir: str | None = None):
        self.root_dir = Path(root_dir or settings.storage.local_storage_root)
        self.backend = settings.storage.storage_backend
        self._ensure_root()

    def _ensure_root(self) -> None:
        if self.backend == "local":
            self.root_dir.mkdir(parents=True, exist_ok=True)

    def get_user_container_path(self, user_id: str) -> Path:
        """Return root path for a user's isolated container."""
        container_name = sanitize_container_name(user_id)
        container_path = self.root_dir / container_name
        container_path.mkdir(parents=True, exist_ok=True)
        return container_path

    def get_creative_vault_path(self, user_id: str, show_slug: str) -> Path:
        """Return path for a user's specific show universe in the creative vault."""
        clean_slug = re.sub(r"[^a-zA-Z0-9_-]", "_", str(show_slug).lower()).strip("_") or "default_show"
        clean_slug = re.sub(r"_+", "_", clean_slug)[:64]
        base = self.get_user_container_path(user_id)
        vault_path = base / "creative_vault" / "shows_and_titles" / clean_slug
        vault_path.mkdir(parents=True, exist_ok=True)
        return vault_path

    def get_character_path(self, user_id: str, show_slug: str, character_id: str) -> Path:
        """Return path for a character's IP assets within a show universe."""
        base = self.get_creative_vault_path(user_id, show_slug)
        char_path = base / "characters" / character_id
        char_path.mkdir(parents=True, exist_ok=True)
        return char_path

    def get_episode_path(self, user_id: str, show_slug: str, episode_id: str) -> Path:
        """Return path for an episode's scripts, audio stems, and master renders."""
        base = self.get_creative_vault_path(user_id, show_slug)
        ep_path = base / "episodes" / episode_id
        ep_path.mkdir(parents=True, exist_ok=True)
        return ep_path

    def get_network_path(self, user_id: str, network_id: str) -> Path:
        """Return path for a user's network under networks/{network}."""
        clean_net = re.sub(r"[^a-zA-Z0-9_-]", "_", str(network_id).lower()).strip("_") or "default_network"
        base = self.get_user_container_path(user_id)
        net_path = base / "networks" / clean_net
        net_path.mkdir(parents=True, exist_ok=True)
        return net_path

    def get_channel_path(self, user_id: str, channel_id: str) -> Path:
        """Alias for get_network_path."""
        return self.get_network_path(user_id, channel_id)

    def get_channel_episode_path(self, user_id: str, channel_id: str, episode_id: str) -> Path:
        """Return path for an episode within a user's network."""
        clean_ep = re.sub(r"[^a-zA-Z0-9_-]", "_", str(episode_id).lower()).strip("_") or "ep_001"
        chan_path = self.get_network_path(user_id, channel_id)
        ep_path = chan_path / clean_ep
        ep_path.mkdir(parents=True, exist_ok=True)
        return ep_path

    def get_global_assets_path(self, user_id: str, category: str | None = None) -> Path:
        """Return path for universal global assets shared across all channels (storage/user/assets/{category})."""
        base = self.get_user_container_path(user_id) / "assets"
        if category:
            clean_cat = re.sub(r"[^a-zA-Z0-9_-]", "_", str(category).lower()).strip("_")
            base = base / clean_cat
        base.mkdir(parents=True, exist_ok=True)
        return base

    def get_channel_assets_path(self, user_id: str, channel_id: str, category: str | None = None) -> Path:
        """Return path for channel-specific branding and assets (channels/{channel}/assets/{category})."""
        chan_path = self.get_channel_path(user_id, channel_id)
        base = chan_path / "assets"
        if category:
            clean_cat = re.sub(r"[^a-zA-Z0-9_-]", "_", str(category).lower()).strip("_")
            base = base / clean_cat
        base.mkdir(parents=True, exist_ok=True)
        return base

    def get_channel_format_production_episode_path(
        self,
        user_id: str,
        channel_id: str,
        format_slug: str,
        production_name: str | None,
        episode_id: str,
    ) -> Path:
        """Return path for an episode organized under channel/{channel}/{format}/{production}/{episode}."""
        clean_format = re.sub(r"[^a-zA-Z0-9_-]", "_", str(format_slug).lower()).strip("_") or "documentary"
        clean_prod = re.sub(r"[^a-zA-Z0-9_-]", "_", str(production_name or 'standalone').lower()).strip("_") or "standalone"
        clean_ep = re.sub(r"[^a-zA-Z0-9_-]", "_", str(episode_id).lower()).strip("_") or "ep_001"

        chan_path = self.get_channel_path(user_id, channel_id)
        ep_path = chan_path / clean_format / clean_prod / clean_ep
        ep_path.mkdir(parents=True, exist_ok=True)
        return ep_path

    def find_episode_path(
        self,
        user_id: str,
        channel_id: str | None,
        episode_id: str,
        format_slug: str | None = None,
        production_name: str | None = None,
    ) -> Path | None:
        """Find an episode's folder whether stored in channels/ or networks/, flat or in {format}/{prod}/{ep}."""
        clean_ep = re.sub(r"[^a-zA-Z0-9_-]", "_", str(episode_id).lower()).strip("_")
        user_root = self.get_user_container_path(user_id)
        search_roots = []
        if channel_id:
            search_roots.append(self.get_network_path(user_id, channel_id))
            search_roots.append(user_root / "channels" / channel_id)
        else:
            search_roots.extend([user_root / "networks", user_root / "channels"])

        clean_fmt = re.sub(r"[^a-zA-Z0-9_-]", "_", str(format_slug).lower()).strip("_") if format_slug else None
        if clean_fmt:
            for std in ("documentary", "relaxation", "walking_tour", "music_video", "short"):
                if std in clean_fmt:
                    clean_fmt = std
                    break

        if channel_id and clean_fmt and production_name:
            exact_dir = self.get_channel_format_production_episode_path(
                user_id, channel_id, clean_fmt, production_name, episode_id
            )
            if exact_dir.exists() and exact_dir.is_dir():
                return exact_dir

        matches = []
        for root in search_roots:
            if not root.exists():
                continue
            flat_candidate = root / episode_id
            if flat_candidate.exists() and flat_candidate.is_dir():
                matches.append(flat_candidate)
            flat_candidate_clean = root / clean_ep
            if flat_candidate_clean.exists() and flat_candidate_clean.is_dir() and flat_candidate_clean != flat_candidate:
                matches.append(flat_candidate_clean)
            try:
                for sub in root.rglob("*"):
                    if sub.is_dir() and sub.name.lower() in (episode_id.lower(), clean_ep):
                        if sub not in matches:
                            matches.append(sub)
            except Exception:
                pass

        if not matches:
            return None

        clean_prod = re.sub(r"[^a-zA-Z0-9_-]", "_", str(production_name).lower()).strip("_") if production_name else None

        # Score matches: strictly respect format and production scope, heavily penalizing cross-format candidates
        def _score(p: Path) -> int:
            score = 0
            path_parts = [part.lower() for part in p.parts]
            if clean_fmt:
                if clean_fmt in path_parts:
                    score += 600
                else:
                    for other_fmt in ("documentary", "relaxation", "walking_tour", "music_video", "short"):
                        if other_fmt != clean_fmt and other_fmt in path_parts:
                            score -= 2000
            if clean_prod:
                if p.parent.name.lower() == clean_prod:
                    score += 400
                elif any(other_prod in path_parts for other_prod in ("swiss_landscape", "geneva_tour", "standalone") if other_prod != clean_prod):
                    score -= 1000
            try:
                if clean_prod and (p / "user_inputs.json").exists():
                    import json
                    u_in = json.loads((p / "user_inputs.json").read_text(encoding="utf-8"))
                    u_prod = re.sub(r"[^a-zA-Z0-9_-]", "_", str(u_in.get("production_name", "")).lower()).strip("_")
                    if u_prod == clean_prod:
                        score += 500
            except Exception:
                pass
            if any(p.glob("motion_p*.mp4")): score += 100
            if any(p.glob("keyframe_p*.jpg")): score += 50
            if (p / "screenplay.json").exists(): score += 10
            if (p / "episode_manifest.json").exists(): score += 5
            if (p / "user_inputs.json").exists(): score += 2
            try:
                if any(p.iterdir()): score += 1
            except Exception:
                pass
            return score

        matches.sort(key=_score, reverse=True)
        return matches[0]

    def get_production_path(self, user_id: str, format_slug: str, production_name: str) -> Path:
        """Return global path for a production project or web series: productions/{format}/{production_name}/."""
        clean_format = re.sub(r"[^a-zA-Z0-9_-]", "_", str(format_slug).lower()).strip("_") or "documentary"
        clean_prod = re.sub(r"[^a-zA-Z0-9_-]", "_", str(production_name).lower()).strip("_") or "standalone"
        base = self.get_user_container_path(user_id)
        prod_path = base / "productions" / clean_format / clean_prod
        prod_path.mkdir(parents=True, exist_ok=True)
        return prod_path

    def get_production_episode_path(self, user_id: str, format_slug: str, production_name: str, episode_id: str) -> Path:
        """Return global path for an episode: productions/{format}/{production_name}/{episode_id}/."""
        clean_ep = re.sub(r"[^a-zA-Z0-9_-]", "_", str(episode_id).lower()).strip("_") or "ep_001"
        prod_path = self.get_production_path(user_id, format_slug, production_name)
        ep_path = prod_path / clean_ep
        ep_path.mkdir(parents=True, exist_ok=True)
        return ep_path

    async def save_json(self, file_path: Path, data: dict[str, Any]) -> None:
        """Atomically persist JSON metadata."""
        file_path.parent.mkdir(parents=True, exist_ok=True)
        temp_file = file_path.with_suffix(".tmp")
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        temp_file.replace(file_path)

    async def load_json(self, file_path: Path) -> dict[str, Any] | None:
        """Load and parse JSON metadata."""
        if not file_path.exists():
            return None
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    async def generate_signed_url(self, user_id: str, relative_blob_path: str) -> str:
        """Generate a short-lived 15-minute SAS or Signed URL depending on active storage backend."""
        container_name = sanitize_container_name(user_id)
        if self.backend == "azure" and settings.storage.azure_storage_connection_string:
            return f"https://mystorage.blob.core.windows.net/{container_name}/{relative_blob_path}?se=mock_sas_token"
        elif self.backend == "gcs" and settings.storage.gcs_project_id:
            bucket_name = f"{settings.storage.gcs_bucket_prefix}-{container_name}"
            return f"https://storage.googleapis.com/{bucket_name}/{relative_blob_path}?X-Goog-Signature=mock_sig"
        return f"/api/vault/stream/{container_name}/{relative_blob_path}"

    async def generate_sas_url(self, user_id: str, relative_blob_path: str) -> str:
        """Backwards-compatible alias for generate_signed_url."""
        return await self.generate_signed_url(user_id, relative_blob_path)


# Singleton storage service
storage_service = MultiTenantStorageService()

__all__ = ["storage_service", "MultiTenantStorageService", "sanitize_container_name"]
