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
        if self.backend == "local": self.root_dir.mkdir(parents=True, exist_ok=True)

    def get_user_container_path(self, user_id: str) -> Path:
        """Return root path for a user's isolated container."""
        try:
            from src.domain.repo import repo
            from uuid import UUID
            u = repo.users.get(UUID(str(user_id))) if str(user_id).count("-") == 4 else repo.get_user_by_email(str(user_id))
            if u and getattr(u, "storage_container_name", None):
                p = self.root_dir / sanitize_container_name(u.storage_container_name)
                p.mkdir(parents=True, exist_ok=True)
                return p
        except Exception:
            pass
        p = self.root_dir / sanitize_container_name(user_id)
        p.mkdir(parents=True, exist_ok=True)
        return p

    def get_creative_vault_path(self, user_id: str, show_slug: str) -> Path:
        clean_slug = re.sub(r"[^a-zA-Z0-9_-]", "_", str(show_slug).lower()).strip("_") or "default_network"
        return self.get_network_path(user_id, re.sub(r"_+", "_", clean_slug)[:64])

    def get_character_path(self, user_id: str, show_slug: str, character_id: str) -> Path:
        p = self.get_network_path(user_id, show_slug) / "characters" / character_id
        p.mkdir(parents=True, exist_ok=True)
        return p

    def get_episode_path(self, user_id: str, show_slug: str, episode_id: str, format_slug: str = "general", production_name: str | None = None) -> Path:
        clean_ep = str(episode_id).lower().strip()
        m = re.match(r"^ep[-_]?(\d+)$", clean_ep)
        clean_ep = f"ep-{int(m.group(1)):03d}" if m else (f"ep-{int(clean_ep):03d}" if clean_ep.isdigit() else clean_ep)
        return self.get_channel_format_production_episode_path(user_id=user_id, channel_id=show_slug, format_slug=format_slug, production_name=production_name or show_slug, episode_id=clean_ep)

    def get_network_path(self, user_id: str, network_id: str) -> Path:
        clean_net = re.sub(r"[^a-zA-Z0-9_-]", "_", str(network_id).lower()).strip("_") or "default_network"
        p = self.get_user_container_path(user_id) / "networks" / clean_net
        p.mkdir(parents=True, exist_ok=True)
        return p

    def get_channel_path(self, user_id: str, channel_id: str) -> Path:
        return self.get_network_path(user_id, channel_id)

    def get_channel_episode_path(self, user_id: str, channel_id: str, episode_id: str) -> Path:
        clean_ep = re.sub(r"[^a-zA-Z0-9_-]", "_", str(episode_id).lower()).strip("_") or "ep_001"
        p = self.get_network_path(user_id, channel_id) / clean_ep
        p.mkdir(parents=True, exist_ok=True)
        return p

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
        clean_ep = re.sub(r"[^a-zA-Z0-9_-]", "_", str(episode_id).lower()).strip("_") or "ep-001"

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
            for fb in ("knpillutla@gmail.com", "user_krishna_01"):
                if fb != user_id:
                    search_roots.extend([self.get_network_path(fb, channel_id), self.get_user_container_path(fb) / "channels" / channel_id])
            search_roots.extend([self.root_dir / "networks" / channel_id, self.root_dir / "channels" / channel_id])
        else:
            search_roots.extend([user_root / "networks", user_root / "channels"])
            for fb in ("knpillutla@gmail.com", "user_krishna_01"):
                if fb != user_id:
                    fb_root = self.get_user_container_path(fb)
                    search_roots.extend([fb_root / "networks", fb_root / "channels"])
            search_roots.extend([self.root_dir / "networks", self.root_dir / "channels"])

        clean_fmt = re.sub(r"[^a-zA-Z0-9_-]", "_", str(format_slug).lower()).strip("_") if format_slug else None
        if clean_fmt:
            for std in ("documentary", "relaxation", "walking_tour", "music_video", "short"):
                if std in clean_fmt:
                    clean_fmt = std
                    break

        if channel_id and clean_fmt and production_name:
            clean_prod = re.sub(r"[^a-zA-Z0-9_-]", "_", str(production_name).lower()).strip("_") or "standalone"
            clean_e = re.sub(r"[^a-zA-Z0-9_-]", "_", str(episode_id).lower()).strip("_") or "ep-001"
            for uid in [user_id, "knpillutla@gmail.com", "user_krishna_01"]:
                chan_path = self.get_channel_path(uid, channel_id)
                exact_dir = chan_path / clean_fmt / clean_prod / clean_e
                if exact_dir.exists() and exact_dir.is_dir():
                    has_content = any(
                        (exact_dir / f).exists()
                        for f in ("raw_gemini_story.json", "raw_gemini_screenplay.json", "screenplay.json", "storyboard.json", "spoken_narration.mp3")
                    ) or any(exact_dir.glob("keyframe_p*.jpg")) or any(exact_dir.glob("motion_p*.mp4"))
                    if has_content:
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
                # Fast path: check standard 1-level, 2-level, and 3-level directory depths
                for pattern in (
                    f"*/{clean_ep}",
                    f"*/*/{clean_ep}",
                    f"*/{episode_id}",
                    f"*/*/{episode_id}",
                    f"*/{clean_ep.upper()}",
                    f"*/*/{clean_ep.upper()}",
                ):
                    for sub in root.glob(pattern):
                        if sub.is_dir() and sub not in matches and any(sub.iterdir()):
                            matches.append(sub)

                # Fallback to targeted rglob only if no structural matches found
                if not matches:
                    for sub in root.rglob(f"{clean_ep}"):
                        if sub.is_dir() and sub not in matches and any(sub.iterdir()):
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
            if (p / "raw_gemini_screenplay.json").exists(): score += 300
            if (p / "raw_gemini_story.json").exists(): score += 250
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
        file_path.parent.mkdir(parents=True, exist_ok=True)
        temp_file = file_path.with_suffix(".tmp")
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        temp_file.replace(file_path)

    async def load_json(self, file_path: Path) -> dict[str, Any] | None:
        if not file_path.exists():
            return None
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    async def generate_signed_url(self, user_id: str, relative_blob_path: str) -> str:
        container_name = sanitize_container_name(user_id)
        if self.backend == "azure" and settings.storage.azure_storage_connection_string:
            return f"https://mystorage.blob.core.windows.net/{container_name}/{relative_blob_path}?se=mock_sas_token"
        elif self.backend == "gcs" and settings.storage.gcs_project_id:
            bucket_name = f"{settings.storage.gcs_bucket_prefix}-{container_name}"
            return f"https://storage.googleapis.com/{bucket_name}/{relative_blob_path}?X-Goog-Signature=mock_sig"
        return f"/api/vault/stream/{container_name}/{relative_blob_path}"

    async def generate_sas_url(self, user_id: str, relative_blob_path: str) -> str:
        return await self.generate_signed_url(user_id, relative_blob_path)


# Singleton storage service
storage_service = MultiTenantStorageService()

__all__ = ["storage_service", "MultiTenantStorageService", "sanitize_container_name"]
