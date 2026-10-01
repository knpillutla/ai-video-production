"""Waterfall Studio Directorial Prompt Engineering.

Specialized exclusively in monumental cascades, cataracts, and plunge waterfalls
with wall-to-wall eye-level framing, dense spray mist, and brown noise foley.
"""

from __future__ import annotations
from typing import Optional


WATERFALL_LANDMARK_POOL = [
    "Niagara Falls, Horseshoe Falls & American Falls",
    "Victoria Falls (Mosi-oa-Tunya), Zambia & Zimbabwe",
    "Iguazu Falls (Devil's Throat), Argentina & Brazil",
    "Angel Falls (Salto Angel), Canaima Venezuela",
    "Plitvice Lakes Great Waterfall & Cascades, Croatia",
    "Gullfoss Golden Falls, Iceland",
    "Skogafoss Glacial Waterfall, Iceland",
    "Multnomah Falls, Columbia River Gorge Oregon",
    "Snoqualmie Falls, Washington Cascades",
    "Dettifoss Roaring Chasm, Iceland",
]


def build_waterfall_prompt(
    custom_prompt: str,
    duration_seconds: float,
    num_shots: int,
    camera_motion: str = "locked_tripod",
    excluded_topics: Optional[list[str]] = None,
    image_model: str = "flux_1_1_pro_ultra",
) -> str:
    """Build dedicated waterfall directorial prompt for Gemini."""
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

    return f"""You are the Lead Waterfall Cinematographer for CineAI Studio.
Your mission is to synthesize an 8K broadcast-grade master directorial screenplay for a MONUMENTAL WATERFALL SOUNDSCAPE production conforming strictly to the RelaxScreenplay JSON schema.

======================================================================
WATERFALL DIRECTORIAL RULES & FRAMING:
======================================================================
1. EYE-LEVEL WALL-TO-WALL CASCADE FRAMING:
   - Frame the waterfall confronting the plunging water wall directly.
   - Symmetrical 16:9 cinematic landscape framing, shot on a locked tripod.
   - The falling cataract water curtain spans wall-to-wall across 100% of the horizontal screen into a churning turquoise or emerald basin.
   - Billowing vapor mist rises steadily from the plunge basin under moody overcast skies.
   - Strictly zero humans, zero tourists, zero boats, zero railings, zero bridges, zero buildings.

2. ACOUSTIC SOUNDSCAPE DIRECTIVE:
   - Suno tags: "432Hz ambient brown noise, powerful roaring waterfall foley, continuous water plunge, deep bass rumble, -14 LUFS".

3. CINEMAGRAPH KINETICS (Wan 2.1 & Kling v1.6 Pro):
   - Rock cliffs and horizon remain 100% frozen, rigid, and static.
   - Continuous downward flowing water cascades into the turbulent basin.
   - Domain: "water_fluid".
{exclusion_block}
PRODUCTION SPECIFICATIONS:
- User Prompt / Concept Anchor: "{custom_prompt or 'Monumental world-famous plunging waterfall cascade'}"
- Genre: relax/waterfall
- Sub-genre: waterfall_gorge
- Total Duration: {duration_seconds} seconds
- Shot Count: {num_shots} shots ({per_shot_dur}s per shot)
- Target Image Model: {image_model}

CRITICAL SCHEMA ENFORCEMENT:
Return ONLY a valid JSON object matching RelaxScreenplay:
{{
  "production_id": "EP-WATERFALL-001",
  "title": "Monumental Waterfall Plunge | Location Name",
  "story_topic": "Direct eye-level encounter with the monumental roaring waterfall wall",
  "genre": "relax/waterfall",
  "sub_genre": "waterfall_gorge",
  "recommended_fps": 24,
  "aspect_ratio": "16:9",
  "total_duration_seconds": {duration_seconds},
  "cast": [],
  "scenes": [
    {{
      "scene_index": 1,
      "location_hub": "Waterfall Plunge Basin",
      "shot_type": "wide_panoramic_picturesque",
      "camera_rig": "{camera_motion}",
      "color_temp_kelvin": 5500,
      "visual_prompt": "A photorealistic, eye-level frontal view directly confronting the monumental roaring waterfall wall of [Landmark Name]. Symmetrical 16:9 cinematic landscape framing, shot on a locked tripod. The powerful cascading cataract spans wall-to-wall across 100% of the screen into a churning turquoise basin with soft rising mist under moody diffused overcast skies. Pristine natural wilderness, strictly zero buildings, zero boats, zero tourists, and zero modern structures.",
      "image_model_configs": {{
        "{image_model}": {{
          "model": "fal-ai/flux-pro/v1.1-ultra",
          "prompt": "A photorealistic, eye-level frontal view directly confronting the monumental roaring waterfall wall of [Landmark Name]. Symmetrical 16:9 cinematic landscape framing, shot on a locked tripod. The powerful cascading cataract spans wall-to-wall across 100% of the screen into a churning turquoise basin with soft rising mist. Pristine natural wilderness, strictly zero buildings, zero boats, zero tourists, and zero modern structures.",
          "aspect_ratio": "16:9",
          "raw": true
        }}
      }},
      "motion_prompt": "Living wallpaper cinemagraph style. Completely stationary locked frame, absolute zero camera movement. Rock cliffs and horizon remain 100% frozen and static. Only the water moves: continuous downward flowing cataract curtains into the churning basin below, with soft vapor mist steadily rising.",
      "motion_negative_prompt": "camera movement, pan, tilt, zoom, moving rocks, morphing landscape, humans, boats",
      "model_configs": {{
        "wan_2_1": {{
          "model": "fal-ai/wan-i2v",
          "prompts": {{
            "positive_prompt": "Living wallpaper cinemagraph, static camera. Continuous laminar water cascades flowing downward into the basin, rising mist, zero humans.",
            "negative_prompt": "camera movement, morphing, humans"
          }},
          "settings": {{
            "guide_scale": 5.0,
            "num_inference_steps": 30,
            "aspect_ratio": "16:9"
          }}
        }}
      }},
      "domain": "water_fluid",
      "duration_seconds": {per_shot_dur}
    }}
  ]
}}
Do NOT output markdown backticks or preamble. Output raw JSON only.
"""
