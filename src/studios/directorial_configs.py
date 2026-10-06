"""Multi-model image and video diffusion configuration generators."""
from __future__ import annotations

from typing import Any, Dict


def build_default_image_model_configs(prompt: str, landmark_name: str = "Landmark") -> Dict[str, Any]:
    """Universal multi-model image configurations for FLUX Dev, FLUX Pro Ultra, and Z-Image Turbo."""
    clean_p = prompt.strip()
    return {
        "flux_dev": {
            "model": "fal-ai/flux/dev",
            "prompt": f"A photorealistic, symmetrical 16:9 cinematic landscape view of {landmark_name}. Shot on locked tripod. {clean_p}. Pristine natural wilderness, zero buildings, zero tourists, zero vehicles.",
            "aspect_ratio": "16:9",
            "guidance_scale": 3.5,
            "num_inference_steps": 28,
        },
        "flux_pro": {
            "model": "fal-ai/flux-pro/v1.1-ultra",
            "prompt": f"Ultra-photorealistic 8K UHD shot on Hasselblad H6D-100c with prime 24mm f/5.6 lens. Symmetrical 16:9 cinematic framing, shot on a locked tripod. {clean_p}. Pristine untouched wilderness, strictly zero humans, zero modern structures, zero vehicles.",
            "aspect_ratio": "16:9",
            "raw": True,
        },
        "zimage": {
            "model": "fal-ai/z-image/turbo",
            "prompt": f"Stunning photorealistic panoramic landscape of {landmark_name}, 16:9 locked tripod framing, {clean_p}, pristine nature, 8k, sharp focus.",
            "aspect_ratio": "16:9",
            "num_inference_steps": 8,
        },
    }


def build_default_video_model_configs(fluid_motion: str, static_elements: str = "Rock cliffs and landscape structure") -> Dict[str, Any]:
    """Universal multi-model video diffusion directives for Wan 2.1 and Kling Pro."""
    return {
        "wan_2_1": {
            "model": "fal-ai/wan-i2v",
            "prompts": {
                "positive_prompt": f"Living wallpaper cinemagraph, completely stationary static frame. {static_elements} remain 100% frozen and unmoving. {fluid_motion}, tranquil rising vapor mist. Stable uniform illumination, seamless loop compatible.",
                "negative_prompt": "camera movement, camera pan, panning, tilt, zoom, morphing landscape, changing environment, hallucinating objects, appearing trees, shifting rocks, altering cliff structures, structural drift, changing perspective, flickering, temporal jump, sunny sky, rainbow, changing lighting, parched, frozen ice, stagnant water, artifacts, humans, tourist, boat, railings, buildings",
            },
            "settings": {
                "guide_scale": 5.0,
                "num_inference_steps": 30,
                "aspect_ratio": "16:9",
            },
        },
        "kling_v1_6_pro": {
            "model": "fal-ai/kling-video/v1.6/pro/image-to-video",
            "prompts": {
                "positive_prompt": f"Cinemagraph style, living wallpaper. Strictly locked stationary camera with zero movement. {static_elements} remain 100% frozen and static. {fluid_motion}, soft rising vapor mist, seamless cyclic motion, pristine untouched nature, zero humans.",
                "negative_prompt": "camera movement, camera pan, panning, tilt, zoom, morphing landscape, changing environment, hallucinating objects, appearing trees, shifting rocks, altering cliff structures, structural drift, changing perspective, flickering, temporal jump, sunny sky, rainbow, changing lighting, sunlight shifts, altering colors, parched, frozen ice, stagnant water",
            },
            "settings": {
                "mode": "pro",
                "duration": "5",
                "aspect_ratio": "16:9",
            },
        },
    }
