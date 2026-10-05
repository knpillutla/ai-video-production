"""Persistent Semantic Audio Vault & Ambient Sound Cache (Directives 3, 11 & 15).

Caches and dynamically retrieves audio stems by semantic theme, genre, and concept
overlap (>= 0.75 similarity) with a mandatory 10-Video Anti-Repetition Cooldown.
"""

import json
import shutil
import time
from pathlib import Path
from typing import Any, Optional
from src.core.telemetry import logger

VAULT_DIR = Path("storage/audio_vault")
INDEX_FILE = VAULT_DIR / "vault_index.json"


def _tokenize(text: str) -> set[str]:
    """Tokenize text into lowercase keywords for fast deterministic semantic matching."""
    clean = "".join(c if c.isalnum() else " " for c in (text or "").lower())
    stop_words = {"the", "a", "an", "and", "or", "in", "on", "at", "to", "for", "with", "of", "is", "video", "track", "music"}
    return {w for w in clean.split() if w and w not in stop_words and len(w) > 2}


class AudioVaultService:
    """Manages persistent catalog of reusable ambient, nature, and instrumental stems with 10-video cooldown."""

    def __init__(self, vault_dir: Path = VAULT_DIR):
        self.vault_dir = vault_dir
        self.vault_dir.mkdir(parents=True, exist_ok=True)
        self.index_file = self.vault_dir / "vault_index.json"
        self._ensure_index()

    def _ensure_index(self) -> None:
        if not self.index_file.exists():
            self.index_file.write_text(json.dumps({"stems": [], "production_history": []}, indent=2), encoding="utf-8")

    def _load_data(self) -> dict[str, Any]:
        try:
            return json.loads(self.index_file.read_text(encoding="utf-8"))
        except Exception:
            return {"stems": [], "production_history": []}

    def _save_data(self, data: dict[str, Any]) -> None:
        self.index_file.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def find_matching_stem(
        self,
        genre: str = "",
        theme: str = "",
        concept: str = "",
        tags: str = "",
        vocal_gender: str = "none",
        min_similarity: float = 0.70,
        current_episode_id: Optional[str] = None,
        min_cooldown: int = 10,
    ) -> Path | None:
        """Find a cached audio stem matching the requested theme, respecting the 10-video cooldown window."""
        query_text = f"{genre} {theme} {concept} {tags}"
        query_tokens = _tokenize(query_text)
        if not query_tokens:
            return None

        data = self._load_data()
        stems = data.get("stems", [])
        history = data.get("production_history", [])

        best_match: dict[str, Any] | None = None
        best_score = 0.0

        # Tier 0: Direct Same-Episode Stem Lookup ($0.00 spend)
        if current_episode_id:
            for entry in stems:
                if entry.get("episode_id") == current_episode_id:
                    stem_path = self.vault_dir / entry.get("filename", "")
                    if stem_path.is_file() and stem_path.stat().st_size > 1000:
                        logger.info(f"audio_vault_episode_match: found stem '{entry.get('title')}' registered for episode '{current_episode_id}'")
                        print(f"[DECISION - AUDIO VAULT EPISODE HIT] Reusing episode '{current_episode_id}' registered stem '{entry.get('title')}' ($0.00 spend).")
                        return stem_path

        for entry in stems:
            stem_path = self.vault_dir / entry.get("filename", "")
            if not (stem_path.is_file() and stem_path.stat().st_size > 1000):
                continue

            entry_gender = entry.get("vocal_gender", "none").lower()
            req_gender = (vocal_gender or "none").lower()
            if req_gender in ("male", "female") and entry_gender != req_gender:
                continue

            # Anti-Repetition 10-Video Cooldown Guard (exempts same-episode resumptions)
            filename = entry.get("filename", "")
            is_same_episode = bool(current_episode_id and (
                entry.get("episode_id") == current_episode_id or
                any(h.get("filename") == filename and h.get("episode_id") == current_episode_id for h in history)
            ))
            if not is_same_episode:
                last_used_indices = [idx for idx, h in enumerate(history) if h.get("filename") == filename]
                if last_used_indices:
                    last_used_offset = len(history) - 1 - last_used_indices[-1]
                    if last_used_offset < min_cooldown:
                        logger.info(f"audio_vault_cooldown_active: Stem '{entry.get('title')}' was used {last_used_offset} videos ago (< {min_cooldown}). Skipping to ensure musical variety.")
                        print(f"[DECISION - AUDIO COOLDOWN] Stem '{entry.get('title')}' used in the last {last_used_offset} videos (< {min_cooldown} video limit). Generating fresh music.")
                        continue

            entry_tokens = _tokenize(f"{entry.get('genre', '')} {entry.get('theme', '')} {entry.get('concept', '')} {entry.get('tags', '')}")
            if not entry_tokens:
                continue

            intersection = query_tokens.intersection(entry_tokens)
            union = query_tokens.union(entry_tokens)
            jaccard_score = len(intersection) / len(union) if union else 0.0
            primary_overlap = len(intersection) / len(query_tokens) if query_tokens else 0.0
            combined_score = max(0.4 * jaccard_score + 0.6 * primary_overlap, primary_overlap)

            if combined_score > best_score:
                best_score = combined_score
                best_match = entry

        if best_match and best_score >= min_similarity:
            matched_path = self.vault_dir / best_match["filename"]
            logger.info(f"decision_audio_vault_cache_hit: Matched '{best_match.get('title')}' (score={best_score:.2f} >= {min_similarity}) -> {matched_path.name}.")
            print(f"[DECISION - AUDIO CACHE HIT] Matched existing vault stem '{best_match.get('title')}' (similarity: {best_score:.2f} >= {min_similarity}, cooldown: OK). Reusing asset ($0.00 spend).")
            self.record_usage(best_match["filename"], current_episode_id or f"ep_{int(time.time())}")
            return matched_path

        logger.info(f"decision_audio_vault_cache_miss: Best match was '{best_match.get('title') if best_match else 'None'}' score={best_score:.2f} (< {min_similarity}). Generating fresh music.")
        print(f"[DECISION - AUDIO CACHE MISS] Highest audio vault similarity is {best_score:.2f} (< threshold {min_similarity}). Invoking Suno v3.5 Pro for fresh audio composition.")
        return None

    def record_usage(self, filename: str, episode_id: str) -> None:
        """Record stem usage in the global production history for cooldown tracking."""
        data = self._load_data()
        history = data.setdefault("production_history", [])
        history.append({"filename": filename, "episode_id": episode_id, "timestamp": time.time()})
        if len(history) > 200:
            data["production_history"] = history[-200:]
        self._save_data(data)

    def register_stem(
        self,
        source_path: Path | str,
        genre: str,
        theme: str = "",
        concept: str = "",
        tags: str = "",
        title: str = "",
        vocal_gender: str = "none",
        episode_id: Optional[str] = None,
    ) -> Path:
        """Store newly generated Suno track into the persistent vault and register its initial usage."""
        src = Path(source_path)
        if not (src.is_file() and src.stat().st_size > 1000):
            return src

        slug = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in (title or genre).lower().replace(" ", "_"))[:40]
        filename = f"{slug}_{abs(hash(f'{genre}_{theme}_{concept}')) % 100000}{src.suffix}"
        dest = self.vault_dir / filename

        if not dest.exists():
            shutil.copy2(src, dest)

        data = self._load_data()
        stems = data.setdefault("stems", [])
        matched_entry = next((s for s in stems if s.get("filename") == filename), None)
        if not matched_entry:
            stems.append({
                "filename": filename,
                "title": title or genre,
                "genre": genre,
                "theme": theme,
                "concept": concept,
                "tags": tags,
                "vocal_gender": vocal_gender or "none",
                "file_size": dest.stat().st_size,
                "episode_id": episode_id,
            })
            logger.info(f"audio_vault_stem_registered: {filename} in vault index ({len(stems)} total stems)")
        elif episode_id and not matched_entry.get("episode_id"):
            matched_entry["episode_id"] = episode_id
        self._save_data(data)

        self.record_usage(filename, episode_id or f"ep_{int(time.time())}")
        return dest


audio_vault = AudioVaultService()
__all__ = ["AudioVaultService", "audio_vault"]
