"""Silent Hearth & Campfire Studio Directorial Prompt Engineering.

Specialized exclusively in 100% open-air outdoor beach campfires, ocean shore stone hearths,
glowing wood embers, rhythmic rolling ocean surf, and deep sleep ASMR.
Strictly prohibits indoor rooms, sofas, living room furniture, walls, and ceilings.
"""

from __future__ import annotations
from typing import Optional


HEARTH_LANDMARK_POOL = [
    "Big Sur Secluded Pebble Beach Cove, California",
    "Cannon Beach Ocean Shoreline & Sea Stacks, Oregon",
    "Rialto Beach Driftwood Coastline, Washington",
    "Amalfi Coastline Secluded Pebble Cove, Italy",
    "Black Sand Beach & Basalt Shoreline, Vik Iceland",
    "Kailua Ocean Shoreline Twilight Breeze, Hawaii",
    "Cape Kiwanda Pacific Sand Dunes & Ocean Waves, Oregon",
]


def build_hearth_prompt(
    custom_prompt: str,
    duration_seconds: float,
    num_shots: int,
    camera_motion: str = "locked_tripod",
    excluded_topics: Optional[list[str]] = None,
    image_model: str = "flux_1_1_pro_ultra",
) -> str:
    """Build dedicated silent hearth & beach campfire directorial prompt for Gemini."""
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

    return f"""You are the Lead Hearth & Ocean Soundscape Cinematographer for CineAI Studio.
Your mission is to synthesize an 8K broadcast-grade master directorial screenplay for an OPEN-AIR BEACH CAMPFIRE & OCEAN SOUNDSCAPE production conforming strictly to the RelaxScreenplay JSON schema.

======================================================================
SILENT HEARTH & BEACH CAMPFIRE DIRECTORIAL RULES:
======================================================================
1. 100% OPEN-AIR OUTDOOR BEACH SHORELINE FRAMING:
   - Symmetrical 16:9 cinematic landscape framing, shot on a locked tripod at eye level.
   - In the foreground: A cozy natural stone campfire / rock fire ring burning with rich glowing wood logs and crackling amber embers sitting directly on the wet sand / smooth pebble shore.
   - In the immediate background: Gentle rhythmic ocean waves roll and surge along the coastline under a dark indigo twilight or night sky with soft coastal mist.
   - STRICT NEGATIVE DIRECTIVE (CRITICAL): Strictly prohibit indoor rooms, living rooms, interior walls, ceilings, indoor sofas, couches, cushions, rugs, indoor tables, and glass window frames.

2. ACOUSTIC SOUNDSCAPE DIRECTIVE:
   - Suno tags: "432Hz ambient soundscape, deep crackling oak campfire foley, gentle rhythmic ocean surf, soft acoustic drone, velvety low-frequency resonance, binaural relaxation, -14 LUFS".

3. CINEMAGRAPH KINETICS (Wan 2.1 & Kling v1.6 Pro):
   - Beach sand, surrounding rocks, and coastline remain 100% frozen, rigid, and static.
   - Animate ONLY the realistic flickering wood flames, glowing embers, and the continuous rolling ocean waves in the background.
   - Domain: "water_fluid" or "cozy_hearth".
{exclusion_block}
PRODUCTION SPECIFICATIONS:
- User Prompt / Concept Anchor: "{custom_prompt or 'Gentle night rain on cozy stone campfire burning directly on wet pebble beach by ocean'}"
- Genre: relax/cozy_hearth
- Sub-genre: coastal_campfire
- Total Duration: {duration_seconds} seconds
- Shot Count: {num_shots} shots ({per_shot_dur}s per shot)
- Target Image Model: {image_model}

CRITICAL SCHEMA ENFORCEMENT:
Return ONLY a valid JSON object matching RelaxScreenplay:
{{
  "production_id": "EP-HEARTH-001",
  "title": "Cozy Oceanfront Campfire & Twilight Waves | Location Name",
  "story_topic": "Serene open-air beach campfire with glowing wood embers and rhythmic ocean waves",
  "genre": "relax/cozy_hearth",
  "sub_genre": "coastal_campfire",
  "recommended_fps": 24,
  "aspect_ratio": "16:9",
  "total_duration_seconds": {duration_seconds},
  "cast": [],
  "scenes": [
    {{
      "scene_index": 1,
      "location_hub": "Beach Campfire Shoreline",
      "shot_type": "wide_panoramic_picturesque",
      "camera_rig": "{camera_motion}",
      "color_temp_kelvin": 3200,
      "visual_prompt": "A photorealistic, eye-level frontal view of a cozy natural stone campfire burning directly on the wet pebble sand at [Landmark Name]. Symmetrical 16:9 cinematic framing, shot on a locked tripod. Warm glowing wood logs crackle with rich amber embers under an open twilight sky while gentle rhythmic ocean waves roll and surge along the shoreline. 100% open-air outdoor beach, strictly zero indoor rooms, zero sofas, zero living room furniture, zero interior walls, zero ceilings, zero glass windows.",
      "image_model_configs": {{
        "{image_model}": {{
          "model": "fal-ai/flux-pro/v1.1-ultra",
          "prompt": "A photorealistic, eye-level frontal view of a cozy natural stone campfire burning directly on the wet pebble beach at [Landmark Name]. Symmetrical 16:9 cinematic framing, shot on a locked tripod. Warm glowing wood logs crackle under an open twilight sky while gentle rhythmic ocean waves surge in the background. 100% open-air outdoor beach, strictly zero indoor rooms, zero sofas, zero furniture.",
          "aspect_ratio": "16:9",
          "raw": true
        }}
      }},
      "motion_prompt": "Living wallpaper cinemagraph style. Completely stationary locked frame, absolute zero camera movement. Pebble beach, shoreline rocks, and horizon remain 100% frozen and static. Only the hypnotic glowing wood fire flickers and crackles in the stone pit while continuous gentle ocean waves roll in the background.",
      "motion_negative_prompt": "camera movement, pan, tilt, zoom, moving beach, indoor room, sofas, furniture, humans",
      "model_configs": {{
        "wan_2_1": {{
          "model": "fal-ai/wan-i2v",
          "prompts": {{
            "positive_prompt": "Living wallpaper cinemagraph, static camera. Realistic crackling fire flames in fire pit, gentle ocean waves rolling in background, zero humans.",
            "negative_prompt": "camera movement, indoor, sofas, furniture, humans"
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
