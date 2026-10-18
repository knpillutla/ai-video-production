"""Core Studio Assets & LoRA API Routes.

Exposes REST endpoints for Studio UI, background producers, and API clients
to list, register, and query network-level and global character LoRA assets.
"""

from __future__ import annotations

from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from src.api.deps import get_current_user
from src.domain.user import User
from src.services.core_asset_service import AssetRecord, AssetScope, core_asset_service
from src.services.core_lora_service import CharacterLoraProfile, core_lora_service

router = APIRouter(tags=["Studio Assets & Character LoRAs"])


class RegisterLoraRequest(BaseModel):
    character_key: str
    name: str
    gender: str = "female"
    role: str = "protagonist"
    age_bracket: str = "mid-20s (ages 23-26)"
    body_composition: str = "graceful medium-thin build with natural feminine curves, defined waistline, neither bony nor chubby"
    lora_url: str
    trigger_word: str
    scale: float = 1.0
    base_model: str = "flux"
    metadata: dict[str, Any] = Field(default_factory=dict)


@router.get("/api/networks/{network}/loras", response_model=list[CharacterLoraProfile])
async def list_network_loras(
    network: str,
    current_user: User = Depends(get_current_user),
):
    """List all character LoRAs registered under the given network."""
    return core_lora_service.list_character_loras(user_id=current_user.email, network=network)


@router.post("/api/networks/{network}/loras", response_model=CharacterLoraProfile)
async def register_network_lora(
    network: str,
    req: RegisterLoraRequest,
    current_user: User = Depends(get_current_user),
):
    """Register or update a character LoRA asset under the network."""
    profile = CharacterLoraProfile(
        name=req.name,
        gender=req.gender,
        role=req.role,
        age_bracket=req.age_bracket,
        body_composition=req.body_composition,
        lora_url=req.lora_url,
        trigger_word=req.trigger_word,
        scale=req.scale,
        base_model=req.base_model,
        metadata=req.metadata,
    )
    core_lora_service.register_character_lora(
        user_id=current_user.email,
        network=network,
        character_key=req.character_key,
        profile=profile,
    )
    return profile


@router.get("/api/networks/{network}/assets", response_model=list[AssetRecord])
async def list_network_assets(
    network: str,
    category: str = "loras",
    current_user: User = Depends(get_current_user),
):
    """List all scoped assets for a network."""
    return core_asset_service.list_assets(
        user_id=current_user.email,
        category=category,
        scope=AssetScope.NETWORK,
        network=network,
    )


@router.get("/api/assets/global", response_model=list[AssetRecord])
async def list_global_assets(
    category: str = "fonts",
    current_user: User = Depends(get_current_user),
):
    """List all global studio-wide assets."""
    return core_asset_service.list_assets(
        user_id=current_user.email,
        category=category,
        scope=AssetScope.GLOBAL,
    )
