"""Authoritative provider/model registry for every production artifact."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Literal


ProfileName = Literal["local", "development", "production"]


@dataclass(frozen=True)
class ArtifactModel:
    """Provider and model contract for one generated artifact type."""

    provider: str
    model: str
    endpoint: str | None = None
    allow_fallback: bool = False


@dataclass(frozen=True)
class ArtifactProfile:
    """Complete artifact stack for one execution profile."""

    name: ProfileName
    script: ArtifactModel
    image: ArtifactModel
    motion_video: ArtifactModel
    lipsync: ArtifactModel
    tts: ArtifactModel
    music: ArtifactModel
    bgm: ArtifactModel
    subtitles: ArtifactModel
    render: ArtifactModel


_LOCAL = ArtifactModel("Local", "deterministic-mock", allow_fallback=True)
_LOCAL_TTS = ArtifactModel("Local", "synthetic-wav", allow_fallback=True)
_LOCAL_AUDIO = ArtifactModel("LocalDSP", "procedural-audio", allow_fallback=True)
_LOCAL_RENDER = ArtifactModel("FFmpeg", "local-single-pass", allow_fallback=True)


ARTIFACT_PROFILES: dict[ProfileName, ArtifactProfile] = {
    "local": ArtifactProfile(
        name="local", script=_LOCAL, image=_LOCAL, motion_video=_LOCAL,
        lipsync=_LOCAL, tts=_LOCAL_TTS, music=_LOCAL_AUDIO, bgm=_LOCAL_AUDIO,
        subtitles=ArtifactModel("Local", "deterministic-subtitles", allow_fallback=True),
        render=_LOCAL_RENDER,
    ),
    "development": ArtifactProfile(
        name="development",
        script=ArtifactModel("Google", "gemini-1.5-pro", allow_fallback=True),
        image=ArtifactModel("Fal.ai", "FLUX.1-dev", "https://queue.fal.run/fal-ai/flux/dev", True),
        motion_video=ArtifactModel("Fal.ai", "Kling 1.5 Pro", "https://queue.fal.run/fal-ai/kling-video/v1.5/pro/image-to-video", True),
        lipsync=ArtifactModel("Fal.ai", "LatentSync", "https://queue.fal.run/fal-ai/latentsync", True),
        tts=ArtifactModel("Microsoft", "Azure Speech Neural HD", allow_fallback=True),
        music=ArtifactModel("MusicAPI.ai", "Suno Sonic v5", "https://api.musicapi.ai/api/v1/sonic/create", True),
        bgm=ArtifactModel("MusicAPI.ai", "Suno Sonic v5", "https://api.musicapi.ai/api/v1/sonic/create", True),
        subtitles=ArtifactModel("Local", "deterministic-subtitles", allow_fallback=True),
        render=_LOCAL_RENDER,
    ),
    "production": ArtifactProfile(
        name="production",
        script=ArtifactModel("Google", "gemini-1.5-pro"),
        image=ArtifactModel("Fal.ai", "FLUX.1-dev", "https://queue.fal.run/fal-ai/flux/dev"),
        motion_video=ArtifactModel("Fal.ai", "Kling 1.5 Pro", "https://queue.fal.run/fal-ai/kling-video/v1.5/pro/image-to-video"),
        lipsync=ArtifactModel("Fal.ai", "LatentSync", "https://queue.fal.run/fal-ai/latentsync"),
        tts=ArtifactModel("Microsoft", "Azure Speech Neural HD"),
        music=ArtifactModel("MusicAPI.ai", "Suno Sonic v5", "https://api.musicapi.ai/api/v1/sonic/create"),
        bgm=ArtifactModel("MusicAPI.ai", "Suno Sonic v5", "https://api.musicapi.ai/api/v1/sonic/create"),
        subtitles=ArtifactModel("Local", "deterministic-subtitles"),
        render=_LOCAL_RENDER,
    ),
}


import json
from pathlib import Path

_MATRIX_FILE = Path(__file__).parent / "model_routing_matrix.json"


def load_model_routing_matrix() -> dict:
    """Load the declarative model routing matrix JSON."""
    if _MATRIX_FILE.is_file():
        try:
            return json.loads(_MATRIX_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"profiles": {}}


def get_scenario_config(scenario: str = "general_default", profile: str | None = None) -> dict:
    """Return model and parameter config for a specific genre scenario under an execution profile."""
    prof_name = (profile or os.getenv("APP_ENV", "development")).lower()
    if prof_name in ("test", "testing", "dev"): prof_name = "development" if prof_name == "dev" else "local"
    if prof_name in ("live", "prod"): prof_name = "production"

    matrix = load_model_routing_matrix()
    p_data = matrix.get("profiles", {}).get(prof_name, {})
    scenarios = p_data.get("scenarios", {})
    return scenarios.get(scenario, scenarios.get("general_default", {}))


def get_artifact_profile(profile: str | None = None) -> ArtifactProfile:
    """Return the configured profile, defaulting to APP_ENV."""
    selected = (profile or os.getenv("APP_ENV", "development")).lower()
    if selected in ("test", "testing", "local"):
        selected = "local"
    elif selected in ("prod", "live", "production"):
        selected = "production"
    else:
        selected = "development"

    if selected not in ARTIFACT_PROFILES:
        raise ValueError(f"Unsupported artifact profile: {selected}")
    return ARTIFACT_PROFILES[selected]  # type: ignore[return-value]


__all__ = [
    "ArtifactModel",
    "ArtifactProfile",
    "ARTIFACT_PROFILES",
    "get_artifact_profile",
    "get_scenario_config",
    "load_model_routing_matrix",
]