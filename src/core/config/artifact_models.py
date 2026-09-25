"""Authoritative provider/model registry and declarative JSON router."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
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

    @property
    def profile_name(self) -> str:
        return self.name


_CONF_PATHS = [
    Path(__file__).parent.parent.parent.parent / "model_selection_config.json",
    Path(__file__).parent / "model_selection_config.json",
    Path(__file__).parent / "model_routing_matrix.json",
]


def load_model_selection_config() -> dict:
    """Load declarative model selection configuration JSON."""
    for p in _CONF_PATHS:
        if p.is_file():
            try:
                return json.loads(p.read_text(encoding="utf-8"))
            except Exception:
                pass
    return {"profiles": {}}


def load_model_routing_matrix() -> dict:
    """Alias for load_model_selection_config."""
    return load_model_selection_config()


def get_scenario_config(scenario: str = "general_default", profile: str | None = None) -> dict:
    """Return model configuration for an execution profile."""
    prof_name = (profile or os.getenv("APP_ENV", "development")).lower()
    if prof_name in ("test", "testing", "dev"): prof_name = "development" if prof_name == "dev" else "local"
    if prof_name in ("live", "prod"): prof_name = "production"

    matrix = load_model_selection_config()
    p_data = matrix.get("profiles", {}).get(prof_name, {})
    scenarios = p_data.get("scenarios", {})
    if scenarios:
        return scenarios.get(scenario, scenarios.get("general_default", p_data))
    return p_data


def get_artifact_profile(profile: str | None = None) -> ArtifactProfile:
    """Return the configured profile dynamically constructed from model_selection_config.json."""
    selected = (profile or os.getenv("APP_ENV", "development")).lower()
    if selected in ("test", "testing", "local"): selected = "local"
    elif selected in ("prod", "live", "production"): selected = "production"
    else: selected = "development"

    cfg = get_scenario_config(profile=selected)
    allow_fb = selected in ("local", "development")

    def _am(key: str, def_p: str, def_m: str, def_ep: str | None = None) -> ArtifactModel:
        item = cfg.get(key, {})
        return ArtifactModel(
            provider=item.get("provider", def_p),
            model=item.get("model", def_m),
            endpoint=item.get("endpoint", def_ep),
            allow_fallback=allow_fb,
        )

    if selected == "local":
        return ArtifactProfile(
            name="local",
            script=_am("script", "Local", "deterministic-mock"),
            image=_am("image", "Local", "pil-procedural-keyframe"),
            motion_video=_am("video_motion", "LocalFFmpeg", "optical-pan-zoom-2.5d"),
            lipsync=_am("lipsync", "None", "none"),
            tts=_am("tts", "Local", "synthetic-wav"),
            music=_am("music", "LocalDSP", "procedural-audio"),
            bgm=_am("music", "LocalDSP", "procedural-audio"),
            subtitles=ArtifactModel("Local", "deterministic-subtitles", allow_fallback=True),
            render=_am("render", "FFmpeg", "local-single-pass"),
        )

    return ArtifactProfile(
        name=selected,  # type: ignore[arg-type]
        script=_am("script", "Google", "gemini-1.5-pro"),
        image=_am("image", "Fal.ai", "FLUX 1.1 Pro Ultra", "https://queue.fal.run/fal-ai/flux-pro/v1.1-ultra"),
        motion_video=_am(
            "video_motion", "Fal.ai",
            "Tencent Hunyuan Video 1080p",
            "https://queue.fal.run/fal-ai/hunyuan-video-image-to-video",
        ),
        lipsync=_am("lipsync", "Fal.ai", "LatentSync", "https://queue.fal.run/fal-ai/latentsync"),
        tts=_am("tts", "Microsoft", "Azure Speech Neural HD"),
        music=_am("music", "MusicAPI.ai", "Suno v3.5 Pro", "https://api.musicapi.ai/api/v1/sonic/create"),
        bgm=_am("music", "MusicAPI.ai", "Suno v3.5 Pro", "https://api.musicapi.ai/api/v1/sonic/create"),
        subtitles=ArtifactModel("Local", "deterministic-subtitles", allow_fallback=allow_fb),
        render=_am("render", "FFmpeg", "single-pass-4k-lanczos"),
    )


ARTIFACT_PROFILES: dict[ProfileName, ArtifactProfile] = {
    "local": get_artifact_profile("local"),
    "development": get_artifact_profile("development"),
    "production": get_artifact_profile("production"),
}

__all__ = [
    "ArtifactModel", "ArtifactProfile", "ARTIFACT_PROFILES",
    "get_artifact_profile", "get_scenario_config",
    "load_model_selection_config", "load_model_routing_matrix",
]