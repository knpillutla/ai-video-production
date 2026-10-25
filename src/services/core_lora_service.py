"""Core Character LoRA Engine.

Provides unified LoRA registration, hierarchical resolution, prompt trigger injection,
and training orchestration for Studio Web UI, API, and production CLI.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
from pydantic import BaseModel, Field

from src.core.telemetry import logger
from src.providers.visual.fal_flux_lora import FalFluxLoraAdapter
from src.services.core_asset_service import AssetRecord, AssetScope, core_asset_service


class CharacterLoraProfile(BaseModel):
    """Character identity specification bound to a custom diffusion LoRA."""

    name: str
    gender: str = "female"
    role: str = "protagonist"
    age_bracket: str = "mid-20s (ages 23-26)"
    body_composition: str = "graceful medium-thin build with natural feminine curves, defined waistline, neither bony nor chubby"
    lora_url: str
    trigger_word: str
    scale: float = 0.82
    base_model: str = "z-image"
    metadata: dict[str, Any] = Field(default_factory=dict)


class CoreLoraService:
    """Universal Character LoRA management engine."""

    CATEGORY = "loras"

    def register_character_lora(
        self,
        user_id: str,
        network: str,
        character_key: str,
        profile: CharacterLoraProfile,
    ) -> AssetRecord:
        """Register a character LoRA profile as a network asset."""
        meta = profile.model_dump()
        return core_asset_service.register_asset(
            user_id=user_id,
            category=self.CATEGORY,
            name=character_key,
            path_or_url=profile.lora_url,
            scope=AssetScope.NETWORK,
            network=network,
            metadata=meta,
        )

    def list_character_loras(self, user_id: str, network: str) -> list[CharacterLoraProfile]:
        """List all character LoRAs available for a given network."""
        records = core_asset_service.list_assets(
            user_id=user_id, category=self.CATEGORY, scope=AssetScope.NETWORK, network=network
        )
        profiles = []
        for rec in records:
            meta = rec.metadata
            meta.setdefault("lora_url", rec.path_or_url)
            meta.setdefault("name", rec.name)
            meta.setdefault("trigger_word", f"{rec.name.upper()}_TRIGGER")
            profiles.append(CharacterLoraProfile(**meta))
        return profiles

    def resolve_character_loras(
        self,
        user_id: str,
        network: str | None,
        explicit_loras: list[dict[str, Any]] | None = None,
    ) -> list[dict[str, Any]]:
        """Resolve effective LoRAs prioritizing explicit overrides, otherwise loading network assets."""
        if explicit_loras:
            logger.info(f"core_loras_using_explicit_override: count={len(explicit_loras)}")
            return explicit_loras

        if not network:
            return []

        profiles = self.list_character_loras(user_id=user_id, network=network)
        resolved = []
        for p in profiles:
            resolved.append({
                "path": p.lora_url,
                "scale": p.scale,
                "trigger_word": p.trigger_word,
                "character_name": p.name,
                "gender": p.gender,
                "base_model": p.base_model,
                "body_composition": p.body_composition,
            })

        if resolved:
            logger.info(f"core_loras_resolved_from_network: network={network}, count={len(resolved)}")
        return resolved

    def inject_lora_prompt_cues(self, prompt: str, loras: list[dict[str, Any]]) -> str:
        """Inject character trigger words into the visual diffusion prompt."""
        triggers = [str(l["trigger_word"]).strip() for l in loras if l.get("trigger_word")]
        if not triggers:
            return prompt
        prefix = " ".join(triggers)
        return f"{prefix}, {prompt}".strip(", ")

    async def train_and_register_lora(
        self,
        user_id: str,
        network: str,
        character_key: str,
        images_zip_path: Path | str,
        trigger_word: str,
        name: str,
        gender: str = "female",
        body_composition: str | None = None,
        base_model: str = "z-image",
    ) -> CharacterLoraProfile:
        """Train a character portrait LoRA and automatically register it under the network."""
        eff_base = (base_model or "z-image").lower().strip()
        if eff_base in ("z-image", "zimage"):
            from src.providers.visual.fal_zimage_lora import FalZImageLoraAdapter
            adapter = FalZImageLoraAdapter()
        else:
            adapter = FalFluxLoraAdapter()

        lora_dir = core_asset_service.get_asset_dir(
            user_id=user_id, category=self.CATEGORY, scope=AssetScope.NETWORK, network=network
        )
        meta_out = lora_dir / f"{character_key}_lora.json"

        lora_url = await adapter.train_portrait_lora(
            images_zip_path=images_zip_path,
            trigger_word=trigger_word,
            output_meta_path=meta_out,
        )

        eff_body = body_composition or (
            "graceful medium-thin build with natural feminine curves, defined waistline, neither bony nor chubby"
            if gender == "female" else "lean-athletic fit medium build, sculpted jawline"
        )
        profile = CharacterLoraProfile(
            name=name,
            gender=gender,
            lora_url=lora_url,
            trigger_word=trigger_word,
            body_composition=eff_body,
            base_model=eff_base,
        )
        self.register_character_lora(user_id=user_id, network=network, character_key=character_key, profile=profile)
        return profile


core_lora_service = CoreLoraService()

__all__ = ["CharacterLoraProfile", "CoreLoraService", "core_lora_service"]
