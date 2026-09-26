"""Atmospheric Archetype Model Definition."""

from typing import List
from pydantic import BaseModel, Field


class AtmosphericArchetype(BaseModel):
    """Detailed visual, motion, and acoustic profile for an ambient environment."""
    key: str
    display_name: str
    cluster: str  # alpine, aquatic, forest_seasonal, cozy_hearth, deep_sleep
    wide_visual_prompt: str
    intimate_visual_prompt: str
    wide_motion_prompt: str
    intimate_motion_prompt: str
    acoustic_tags: str
    default_domain: str = "landscape_solid"
    tags: List[str] = Field(default_factory=list)
