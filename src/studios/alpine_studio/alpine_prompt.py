"""Alpine Nature Studio Directorial Prompt Engineering.

Specialized exclusively in panoramic mountain landscapes, Swiss Alps, Dolomites,
snow-capped peaks, wildflower meadows, and crystal-clear glacial streams.
"""

from __future__ import annotations
from typing import Optional


ALPINE_LANDMARK_POOL = [
    "Lauterbrunnen Valley & Eiger, Jungfrau Peaks, Swiss Alps",
    "Matterhorn & Zermatt Alpine Meadows, Switzerland",
    "Dolomites Val di Funes & Tre Cime di Lavaredo, Italian Alps",
    "Banff National Park & Moraine Lake, Canadian Rockies",
    "Lake Bled & Julian Alps, Slovenia",
    "Mount Fuji & Lake Kawaguchi Spring Meadows, Japan",
    "Hallstatt & Dachstein Mountain Range, Austrian Alps",
    "Yosemite Valley & Half Dome Granite Peaks, California",
    "Grand Teton Cathedral Group & Snake River Valley, Wyoming",
    "Milford Sound & Mitre Peak Alpine Fjord, New Zealand",
]


def build_alpine_prompt(
    custom_prompt: str,
    duration_seconds: float,
    num_shots: int,
    camera_motion: str = "locked_tripod",
    excluded_topics: Optional[list[str]] = None,
    image_model: str = "flux_1_1_pro_ultra",
) -> str:
    """Build dedicated alpine nature directorial prompt for Gemini."""
    per_shot_dur = round(duration_seconds / max(1, num_shots), 1)

    exclusion_block = ""
    if excluded_topics:
        cleaned_excl = "\n".join(f"- {t}" for t in excluded_topics if t)
        if cleaned_excl:
            exclusion_block = f"""
======================================================================
PREVIOUSLY PRODUCED TOPICS (STRICT DO-NOT-REPEAT EXCLUSION LIST):
======================================================================
{cleaned_excl}
"""

    return f"""You are the Lead Alpine Nature Cinematographer for CineAI Studio.
Your mission is to synthesize an 8K broadcast-grade master directorial screenplay for a MAJESTIC ALPINE NATURE & MOUNTAIN SOUNDSCAPE production conforming strictly to the RelaxScreenplay JSON schema.

======================================================================
ALPINE NATURE DIRECTORIAL RULES & FRAMING:
======================================================================
1. WIDE PANORAMIC ALPINE LANDSCAPE FRAMING:
   - Frame majestic wide 16:9 panoramic landscape vistas shot on a locked tripod.
   - In the background: Towering snow-capped jagged alpine mountain peaks rising into a crisp clear or gentle alpine morning sky.
   - In the foreground/midground: Lush green rolling alpine meadows dotted with colorful wildflowers, framed by a tranquil crystal-clear glacial mountain stream gently flowing over rounded river pebbles.
   - Crisp, balanced natural daylight illumination (5500K-6000K) with soft alpine glow.
   - STRICTLY PROHIBIT: Close-up waterfall plunge walls, dark desaturated rainy clouds, gray mist walls, buildings, tourists, vehicles, ski lifts, roads, and human structures.

2. ACOUSTIC SOUNDSCAPE DIRECTIVE:
   - Suno tags: "432Hz ambient soundscape, gentle mountain breeze, distant acoustic folk strings, crystal glacial stream murmur, deep relaxation, -14 LUFS".

3. CINEMAGRAPH KINETICS (Wan 2.1 & Kling v1.6 Pro):
   - Snow peaks, granite cliffs, mountain ridgelines, and meadows remain 100% frozen, rigid, and static.
   - Animate ONLY the gentle crystal stream water and subtle drifting clouds in the distant sky.
   - Domain: "landscape_solid" or "water_fluid" for stream.
{exclusion_block}
PRODUCTION SPECIFICATIONS:
- User Prompt / Concept Anchor: "{custom_prompt or 'Majestic Swiss Alps panoramic peaks and wildflower meadows'}"
- Genre: relax/nature
- Sub-genre: alpine_mountains
- Total Duration: {duration_seconds} seconds
- Shot Count: {num_shots} shots ({per_shot_dur}s per shot)
- Target Image Model: {image_model}

CRITICAL SCHEMA ENFORCEMENT:
Return ONLY a valid JSON object matching RelaxScreenplay:
{{
  "production_id": "EP-ALPINE-001",
  "title": "Majestic Alpine Peaks & Wildflower Meadows | Location Name",
  "story_topic": "Detailed sensory synopsis of the panoramic alpine mountains",
  "genre": "relax/nature",
  "sub_genre": "alpine_mountains",
  "recommended_fps": 24,
  "aspect_ratio": "16:9",
  "total_duration_seconds": {duration_seconds},
  "cast": [],
  "scenes": [
    {{
      "scene_index": 1,
      "location_hub": "Alpine Vista Name",
      "shot_type": "wide_panoramic_picturesque",
      "camera_rig": "{camera_motion}",
      "color_temp_kelvin": 5800,
      "visual_prompt": "A photorealistic, wide panoramic landscape view of [Landmark Name]. Symmetrical 16:9 cinematic framing, shot on a locked tripod. In the majestic background, towering snow-dusted jagged mountain peaks rise into a crisp clear sky; in the foreground, lush green rolling alpine meadows dotted with wildflowers frame a tranquil crystal-clear glacial stream. Pristine natural wilderness, strictly zero buildings, zero tourists, zero vehicles, and zero modern structures.",
      "image_model_configs": {{
        "{image_model}": {{
          "model": "fal-ai/flux-pro/v1.1-ultra",
          "prompt": "A photorealistic, wide panoramic landscape view of [Landmark Name]. Symmetrical 16:9 cinematic framing, shot on a locked tripod. In the majestic background, towering snow-dusted jagged mountain peaks rise into a crisp clear sky; in the foreground, lush green rolling alpine meadows dotted with wildflowers frame a tranquil crystal-clear glacial stream. Pristine natural wilderness, strictly zero buildings, zero tourists, zero vehicles, and zero modern structures.",
          "aspect_ratio": "16:9",
          "raw": true
        }}
      }},
      "motion_prompt": "Living wallpaper cinemagraph style. Completely stationary locked frame, absolute zero camera movement. Mountain peaks, cliffs, meadows, and horizon line remain 100% frozen and static. Only the crystal glacial stream water gently flows over stones with subtle soft clouds drifting in the distant sky.",
      "motion_negative_prompt": "camera movement, pan, tilt, zoom, moving mountains, morphing landscape, humans, vehicles, buildings",
      "model_configs": {{
        "wan_2_1": {{
          "model": "fal-ai/wan-i2v",
          "prompts": {{
            "positive_prompt": "Living wallpaper cinemagraph, static camera. Mountain peaks and meadows remain frozen, gentle stream water flows smoothly, zero humans.",
            "negative_prompt": "camera movement, morphing, humans"
          }},
          "settings": {{
            "guide_scale": 5.0,
            "num_inference_steps": 30,
            "aspect_ratio": "16:9"
          }}
        }}
      }},
      "domain": "landscape_solid",
      "duration_seconds": {per_shot_dur}
    }}
  ]
}}
Do NOT output markdown backticks or preamble. Output raw JSON only.
"""
