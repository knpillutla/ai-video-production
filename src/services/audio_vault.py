"""Persistent Semantic Audio Vault & Ambient Sound Cache (Directive 3 & 15).

Caches and dynamically retrieves audio stems by semantic theme, genre, and concept
overlap (>= 0.75 similarity) before invoking external paid music APIs.
"""

import json
import shutil
from pathlib import Path
from typing import Any
from src.core.telemetry import logger

VAULT_DIR = Path("storage/audio_vault")
INDEX_FILE = VAULT_DIR / "vault_index.json"


def _tokenize(text: str) -> set[str]:
    """Tokenize text into lowercase keywords for fast deterministic semantic matching."""
    clean = "".join(c if c.isalnum() else " " for c in (text or "").lower())
    stop_words = {"the", "a", "an", "and", "or", "in", "on", "at", "to", "for", "with", "of", "is", "video", "track", "music"}
    return {w for w in clean.split() if w and w not in stop_words and len(w) > 2}


class AudioVaultService:
    """Manages persistent catalog of reusable ambient, nature, and instrumental stems."""

    def __init__(self, vault_dir: Path = VAULT_DIR):
        self.vault_dir = vault_dir
        self.vault_dir.mkdir(parents=True, exist_ok=True)
        self.index_file = self.vault_dir / "vault_index.json"
        self._ensure_index()

    def _ensure_index(self) -> None:
        if not self.index_file.exists():
            self.index_file.write_text(json.dumps({"stems": []}, indent=2), encoding="utf-8")

    def _load_index(self) -> list[dict[str, Any]]:
        try:
            return json.loads(self.index_file.read_text(encoding="utf-8")).get("stems", [])
        except Exception:
            return []

    def _save_index(self, stems: list[dict[str, Any]]) -> None:
        self.index_file.write_text(json.dumps({"stems": stems}, indent=2), encoding="utf-8")

    def find_matching_stem(
        self,
        genre: str = "",
        theme: str = "",
        concept: str = "",
        tags: str = "",
        vocal_gender: str = "none",
        min_similarity: float = 0.70,
    ) -> Path | None:
        """Find a cached audio stem matching the requested theme, genre, and concept."""
        query_text = f"{genre} {theme} {concept} {tags}"
        query_tokens = _tokenize(query_text)
        if not query_tokens:
            return None

        best_match: dict[str, Any] | None = None
        best_score = 0.0

        for entry in self._load_index():
            stem_path = self.vault_dir / entry.get("filename", "")
            if not (stem_path.is_file() and stem_path.stat().st_size > 1000):
                continue

            entry_gender = entry.get("vocal_gender", "none").lower()
            req_gender = (vocal_gender or "none").lower()
            if req_gender in ("male", "female") and entry_gender != req_gender:
                continue

            entry_tokens = _tokenize(f"{entry.get('genre', '')} {entry.get('theme', '')} {entry.get('concept', '')} {entry.get('tags', '')}")
            if not entry_tokens:
                continue

            intersection = query_tokens.intersection(entry_tokens)
            union = query_tokens.union(entry_tokens)
            jaccard_score = len(intersection) / len(union) if union else 0.0

            # Combined score weights query concept coverage heavily to identify relevant existing stems
            primary_overlap = len(intersection) / len(query_tokens) if query_tokens else 0.0
            combined_score = max(0.4 * jaccard_score + 0.6 * primary_overlap, primary_overlap)

            if combined_score > best_score:
                best_score = combined_score
                best_match = entry

        if best_match and best_score >= min_similarity:
            matched_path = self.vault_dir / best_match["filename"]
            logger.info(f"decision_audio_vault_cache_hit: Matched '{best_match.get('title')}' (score={best_score:.2f} >= threshold {min_similarity}) -> {matched_path.name}. Reusing cached stem ($0.00 spend).")
            print(f"[DECISION - AUDIO CACHE HIT] Matched existing vault stem '{best_match.get('title')}' (semantic similarity: {best_score:.2f} >= {min_similarity}). Reusing {matched_path.name} ($0.00 spend).")
            return matched_path

        logger.info(f"decision_audio_vault_cache_miss: Best match was '{best_match.get('title') if best_match else 'None'}' with score={best_score:.2f} (< threshold {min_similarity}). Calling Suno for fresh composition.")
        print(f"[DECISION - AUDIO CACHE MISS] Highest audio vault similarity is {best_score:.2f} (below required threshold {min_similarity}). Invoking Suno v3.5 Pro for fresh audio composition.")
        return None

    def register_stem(
        self,
        source_path: Path | str,
        genre: str,
        theme: str = "",
        concept: str = "",
        tags: str = "",
        title: str = "",
        vocal_gender: str = "none",
    ) -> Path:
        """Store newly generated Suno/DSP track into the persistent vault for future reuse."""
        src = Path(source_path)
        if not (src.is_file() and src.stat().st_size > 1000):
            return src

        slug = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in (title or genre).lower().replace(" ", "_"))[:40]
        filename = f"{slug}_{abs(hash(f'{genre}_{theme}_{concept}')) % 100000}{src.suffix}"
        dest = self.vault_dir / filename

        if not dest.exists():
            shutil.copy2(src, dest)

        stems = self._load_index()
        # Avoid duplicate index entries
        if not any(s.get("filename") == filename for s in stems):
            stems.append({
                "filename": filename,
                "title": title or genre,
                "genre": genre,
                "theme": theme,
                "concept": concept,
                "tags": tags,
                "vocal_gender": vocal_gender or "none",
                "file_size": dest.stat().st_size,
            })
            self._save_index(stems)
            logger.info(f"audio_vault_stem_registered: {filename} in vault index ({len(stems)} total stems)")

        return dest


audio_vault = AudioVaultService()
__all__ = ["AudioVaultService", "audio_vault"]
