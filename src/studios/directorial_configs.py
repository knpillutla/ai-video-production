"""Multi-model image and video diffusion configuration generators."""
from __future__ import annotations

from typing import Any, Dict


def build_default_image_model_configs(prompt: str, landmark_name: str = "Landmark") -> Dict[str, Any]:
    """Universal multi-model image configurations for FLUX Dev, FLUX Pro Ultra, and Z-Image Turbo."""
    clean_p = prompt.strip()
    return {
        "flux_dev": {
            "model": "fal-ai/flux/dev",
            "prompt": f"A hyper-realistic, colorful 16:9 cinematic vista of {landmark_name}. {clean_p}. Vibrant natural colors, rich textures, warm golden sidelight, crystalline atmospheric depth, pristine composition.",
            "aspect_ratio": "16:9",
            "guidance_scale": 3.5,
            "num_inference_steps": 28,
        },
        "flux_pro": {
            "model": "fal-ai/flux-pro/v1.1-ultra",
            "prompt": f"Ultra-photorealistic 8K UHD shot on Hasselblad H6D-100c with prime 24mm f/5.6 lens. 16:9 panoramic cinematic framing. {clean_p}. Saturated natural jewel tones, rich architectural and environmental relief, deep dynamic range, raw texture, pristine clarity.",
            "aspect_ratio": "16:9",
            "raw": True,
        },
        "zimage": {
            "model": "fal-ai/z-image/turbo",
            "prompt": f"A hyper-realistic 4K UHD panoramic vista of {landmark_name}, shot on Hasselblad H6D-100c with prime lens. {clean_p}. Vibrant saturated natural colors, sun-drenched golden amber light, rich environmental textures, deep cobalt sky, crystalline atmospheric depth, razor-sharp edge-to-edge optical clarity, 16:9.",
            "aspect_ratio": "16:9",
            "num_inference_steps": 8,
        },
    }


def build_default_video_model_configs(fluid_motion: str, static_elements: str = "Rock cliffs and landscape structure") -> Dict[str, Any]:
    """Universal multi-model video diffusion directives for Wan 2.1 and Kling Pro."""
    is_rain = any(k in fluid_motion.lower() for k in ("rain", "downpour", "storm", "eaves", "torrent"))
    if is_rain:
        kling_pos = f"Cinematic masterpiece, locked camera. A blinding torrential rainstorm, thick solid white sheets of heavy downpour obscuring the view, intense splashing water exploding off timber eaves. Wet, glistening wooden railings dripping with water. Heavy fog and a dense wall of rain completely blurring the distant mountains. High-contrast dramatic storm atmosphere, {fluid_motion}, photorealistic 8k."
        kling_4k_pos = f"Cinematic masterpiece, locked stationary camera. A blinding torrential rainstorm, thick solid white sheets of heavy downpour obscuring the view, intense splashing water exploding off timber eaves. Wet, glistening wooden railings dripping with water. Heavy fog and a dense wall of rain completely blurring the distant mountains. Native 4K UHD atmospheric depth, high-contrast dramatic mood, {fluid_motion}, photorealistic 8k."
    else:
        kling_pos = f"Cinematic visual grandeur, locked stationary camera. {static_elements} remain 100% frozen and static. {fluid_motion}, soft rising vapor mist, seamless cyclic motion, pristine untouched nature, zero humans."
        kling_4k_pos = f"Cinematic visual grandeur, locked stationary camera. {static_elements} remain 100% frozen and static. {fluid_motion}, soft rising vapor mist, seamless cyclic motion, native 4K UHD atmospheric depth, pristine untouched nature, zero humans."

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
        "kling_v3_4k": {
            "model": "fal-ai/kling-video/v3/4k/image-to-video",
            "prompts": {
                "positive_prompt": kling_4k_pos,
                "negative_prompt": "camera movement, camera pan, panning, tilt, zoom, morphing landscape, changing environment, hallucinating objects, appearing trees, shifting rocks, altering cliff structures, structural drift, changing perspective, flickering, temporal jump, sunny sky, rainbow, changing lighting, sunlight shifts, altering colors, parched, frozen ice, stagnant water",
            },
            "settings": {
                "mode": "pro",
                "duration": "5",
                "aspect_ratio": "16:9",
            },
        },
        "kling_v1_6_pro": {
            "model": "fal-ai/kling-video/v1.6/pro/image-to-video",
            "prompts": {
                "positive_prompt": kling_pos,
                "negative_prompt": "camera movement, camera pan, panning, tilt, zoom, morphing landscape, changing environment, hallucinating objects, appearing trees, shifting rocks, altering cliff structures, structural drift, changing perspective, flickering, temporal jump, sunny sky, rainbow, changing lighting, sunlight shifts, altering colors, parched, frozen ice, stagnant water",
            },
            "settings": {
                "mode": "pro",
                "duration": "5",
                "aspect_ratio": "16:9",
            },
        },
        "h3_max": {
            "model": "fal-ai/minimax/h3-max-turbo/image-to-video",
            "prompts": {
                "positive_prompt": f"Subtle atmospheric movement, locked stationary camera. {static_elements} remain 100% structurally frozen and unmoving. {fluid_motion}, gentle atmospheric drift, zero camera movement, realistic natural lighting.",
                "negative_prompt": "camera movement, camera pan, panning, tilt, zoom, camera shake, jitter, rapid motion, morphing architecture, changing scenery, structural drift, distortion, cartoon, 3d render, plastic skin, artifacts, humans",
            },
            "settings": {
                "mode": "turbo",
                "duration": "5",
                "aspect_ratio": "16:9",
            },
        },
        "local_drone": {
            "model": "local_perspective_drone",
            "movement": "stay",
            "start_pan": "center",
            "start_zoom": "normal",
            "start_tilt": "center",
            "curve": "cosine",
            "speed_factor": 1.0,
            "rationale": "Pure locked stationary tripod living wallpaper framing with zero camera movement ($0.00 compute)",
        },
    }
