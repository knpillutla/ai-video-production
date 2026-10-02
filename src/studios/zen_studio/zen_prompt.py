"""Zen Studio Directorial Prompt Engineering.

Specialized exclusively in 432Hz Zen rock gardens, Kyoto temple grounds,
ancient moss sanctuaries, sacred lotus ponds, and raked gravel courtyards.
Conforms strictly to the unified global RelaxScreenplay schema.
"""

from __future__ import annotations
from typing import Optional


ZEN_LANDMARK_POOL = [
    "Daitoku-ji Zuiho-in Raked Rock Garden, Kyoto, Japan",
    "Tenryu-ji Temple Sogenchi Reflection Pond, Arashiyama, Kyoto, Japan",
    "Ryoan-ji Temple Dry Landscape Rock Garden, Kyoto, Japan",
    "Ginkaku-ji Silver Pavilion Moss Garden & Sand Cone, Kyoto, Japan",
    "Kenkoku-ji Zen Temple Bamboo Grove & Stone Lanterns, Kamakura, Japan",
    "Byodoin Phoenix Temple Sacred Lotus Pond & Reflecting Waters, Uji, Japan",
    "Saiho-ji Kokedera Ancient Moss Temple Sanctuary, Kyoto, Japan",
    "Nanzen-ji Hojo Stone Garden & Cedar Veranda, Kyoto, Japan",
    "Kennin-ji Temple Twin Dragon Courtyard & Pebble Wave Garden, Kyoto, Japan",
    "Tofuku-ji Hojo Checkerboard Moss & Slate Garden, Kyoto, Japan",
]


def build_zen_prompt(
    custom_prompt: str,
    duration_seconds: float,
    num_shots: int,
    camera_motion: str = "locked_tripod",
    excluded_topics: Optional[list[str]] = None,
    image_model: str = "flux_1_1_pro_ultra",
    sub_genre: str = "zen_healing",
) -> str:
    """Build dedicated Zen studio directorial prompt conforming to global RelaxScreenplay schema."""
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

    return f"""You are the Lead Zen & Japanese Garden Cinematographer for CineAI Studio.
Your mission is to synthesize an 8K broadcast-grade master directorial screenplay for a 432Hz ZEN GARDEN & SACRED LOTUS SANCTUARY production conforming strictly to the RelaxScreenplay JSON schema.

======================================================================
ZEN DIRECTORIAL RULES & CINEMATOGRAPHY:
======================================================================
1. AUTHENTIC JAPANESE GARDEN COMPOSITION & LIVING WALLPAPER:
   - Frame tranquil wide 16:9 compositions shot on a locked tripod with restrained asymmetry.
   - Foreground: Weathered dark cedar or cypress engawa veranda with rich wood grains, carved granite tsukubai water basin, or pristine raked gravel ripple patterns.
   - Midground: Meticulously sculpted Japanese black pines (niwaki), lush emerald moss mounds, and authentic granite toro lanterns with lichen.
   - Background: Weathered white clay temple walls, dark tiled eaves, or bamboo groves shrouded in soft dawn morning mist.
   - Illumination: Soft, ethereal morning sidelight (5400K daylight) with glowing dawn caustics on still reflective water.
   - PURE ZEN NATURE PURITY GUARD: Strictly mandate zero humans, zero tourists, zero monks, zero voices, zero modern buildings, zero vehicles, zero clutter, zero animals.

2. ACOUSTIC SOUNDSCAPE & 432Hz VELVET MASTERING:
   - Suno tags: "432Hz deep meditative soundscape, shakuhachi bamboo flute, warm singing bowl resonance, soft temple bell chime, gentle tsukubai water trickle, velvet -14 LUFS anti-fatigue master".
   - Set target_lufs: -14.0, ducking_db: -18.0.

3. CINEMAGRAPH KINETICS (Wan 2.1 & Kling v1.6 Pro):
   - Temple verandas, raked gravel patterns, granite boulders, and stone lanterns remain 100% frozen, rigid, and static.
   - Animate ONLY subtle micro-ripples across the glassy water surface and gentle pine needle whispers in the faint morning breeze.
   - Domain: "landscape_solid" (gravel courtyard) or "water_fluid" (lotus pond / tsukubai).

4. SPOKEN NARRATION & TIMED SUBTITLES:
   - Provide a poetic, contemplative narration script in "spoken_narration_script" exploring Zen philosophy, mind stillness, and nature harmony (~120 wpm).

5. MULTI-MODEL IMAGE PROMPTS ("image_model_configs"):
   - "flux_dev": 28-step photoreal prompt with Arri Alexa 35mm, 35mm f/4.0 lens, crisp textures.
   - "flux_pro": 8K Hasselblad H6D raw photorealistic prompt.
   - "zimage": High-contrast crisp prompt for Z-Image Turbo.

6. MODEL-SPECIFIC VIDEO DIFFUSION ("model_configs"):
   - "wan_2_1": Fluid cinemagraph kinetic prompt with guide_scale: 5.0, steps: 30.
   - "kling_v1_6_pro": Pro action cinemagraph prompt, stationary locked tripod.
{exclusion_block}
PRODUCTION SPECIFICATIONS:
- User Prompt / Concept Anchor: "{custom_prompt or 'Tranquil Kyoto Zen garden with raked gravel, mossy granite stones, and 432Hz bell resonance'}"
- Genre: relax/zen
- Sub-Genre: {sub_genre}
- Primary Archetype: zen_garden
- Total Duration: {duration_seconds}s across {num_shots} scenes ({per_shot_dur}s per shot)
- Target Image Engine: {image_model}

======================================================================
MANDATORY JSON OUTPUT SCHEMA (RelaxScreenplay):
======================================================================
{{
  "production_id": "EP-001",
  "title": "432Hz Kyoto Zen Garden Sanctuary • Deep Healing Meditation & Inner Peace (8K)",
  "story_topic": "A restorative dawn awakening at Kyoto's historic Zen sanctuary, showcasing raked gravel ocean ripples, ancient moss-covered granite boulders, and a tranquil stone water basin beneath weathered temple eaves.",
  "genre": "relax/zen",
  "sub_genre": "{sub_genre}",
  "primary_archetype": "zen_garden",
  "cluster": "Kyoto, Japan",
  "primary_language": "en",
  "target_dubbing_languages": ["en", "de", "fr", "ja", "es"],
  "recommended_fps": 24,
  "aspect_ratio": "16:9",
  "total_duration_seconds": {duration_seconds},
  "publishing": {{
    "seo_titles": [
      "432Hz Kyoto Zen Garden Sanctuary • Deep Healing Meditation (8K)",
      "Zen Temple Morning Stillness • 432Hz Soundscape for Inner Peace",
      "Kyoto Zen Rock Garden & Sacred Lotus Pond • 4K Living Wallpaper"
    ],
    "seo_description": "Immerse yourself in profound 432Hz healing resonance at Kyoto's ancient Zen temple gardens. Features masterfully raked gravel ocean ripples, mossy granite boulders, and peaceful morning mist.\\n\\n⏱ TIMESTAMPS:\\n00:00 - Tranquil Zen Courtyard\\n01:00 - Sacred Tsukubai Flow\\n\\n#Zen #432Hz #Meditation #Kyoto #Relaxation",
    "seo_tags": ["432Hz", "zen garden", "kyoto zen", "meditation soundscape", "deep healing", "inner peace", "japan ambient", "tenryu-ji", "shakuhachi", "living wallpaper", "relaxing nature", "4k zen", "binaural asmr", "stress relief", "mindfulness"],
    "thumbnail_prompts": {{
      "landscape_16_9": "Award-winning high-CTR YouTube thumbnail landscape photograph of Kyoto Zen garden at dawn. Raked gravel ripples, mossy boulders, glowing morning light, 8k, zero text.",
      "vertical_9_16": "Striking vertical 9:16 YouTube Short thumbnail photograph of authentic Japanese temple stone water basin and sculpted black pine. Deep cinematic depth, 8k, zero text."
    }}
  }},
  "audio_master": {{
    "audio_mode": "ambient_nature",
    "spoken_narration_script": "In the silent cradle of dawn, stillness settles over the ancient garden. Every grain of raked sand mirrors the vastness of the ocean, inviting the mind into tranquil equilibrium.",
    "singing_lyrics_spec": "",
    "suno_musical_tags": "432Hz deep meditative soundscape, shakuhachi bamboo flute, warm singing bowl resonance, soft temple bell chime, gentle tsukubai water trickle, velvet -14 LUFS anti-fatigue master",
    "vocal_gender": "female",
    "tempo_bpm": 60,
    "speech_cadence_wpm": 115,
    "traditional_instruments": ["shakuhachi", "singing_bowl", "temple_bell"],
    "target_lufs": -14.0,
    "ducking_db": -18.0
  }},
  "scenes": [
    {{
      "scene_index": 1,
      "location_hub": "Kyoto Zen Courtyard & Raked Gravel Terrace",
      "shot_type": "wide_panoramic_picturesque",
      "camera_rig": "{camera_motion}",
      "color_temp_kelvin": 5400,
      "visual_prompt": "Cinematic 8K UHD capture on Arri Alexa 35mm, 35mm f/4.0 lens. A wide panoramic view of authentic Kyoto Zen rock garden at tranquil early dawn. Crisp, raked dark river gravel patterns mimic undulating sea waves surrounding sculptural, moss-laden granite stones. Polished dark cedar engawa veranda in the foreground. Sculpted Japanese black pines, authentic white plaster wall with dark clay tiles. Rich slate, forest green, and burnished umber tones. Carved granite tsukubai holds glassy clear water. Strictly zero humans, zero people, zero modern structures, zero clutter.",
      "image_model_configs": {{
        "flux_dev": {{
          "model": "fal-ai/flux/dev",
          "prompt": "Photorealistic 8K wide landscape of Kyoto Zen garden at dawn, 35mm Arri Alexa, locked tripod, raked gravel sea waves, mossy granite boulders, dark cedar veranda, sculpted black pines, serene morning mist, zero humans.",
          "aspect_ratio": "16:9",
          "guidance_scale": 3.5,
          "num_inference_steps": 28
        }},
        "flux_pro": {{
          "model": "fal-ai/flux-pro/v1.1-ultra",
          "prompt": "Ultra-photorealistic 8K UHD shot on Hasselblad H6D-100c, 24mm f/5.6. Panoramic landscape of Kyoto Zen rock garden at dawn. Raked river gravel ripples, deep emerald moss banks, authentic stone lanterns, polished cypress veranda, natural 5400K dawn light, pristine wilderness, strictly zero humans.",
          "aspect_ratio": "16:9",
          "raw": true
        }},
        "zimage": {{
          "model": "fal-ai/z-image/turbo",
          "prompt": "Stunning photorealistic Kyoto Zen rock garden at dawn, raked sand waves, moss stones, cedar temple veranda, 8k sharp focus, zero humans.",
          "aspect_ratio": "16:9",
          "num_inference_steps": 8
        }}
      }},
      "motion_prompt": "Living wallpaper cinemagraph style. Completely stationary locked frame, absolute zero camera movement, zero panning, zero tilting, zero zooming. Temple veranda, stone lanterns, raked gravel, and granite boulders remain 100% frozen and static. Only the glassy water reflections breathe in quiet stillness with subtle morning mist slowly drifting.",
      "motion_negative_prompt": "camera movement, camera pan, panning, tilt, zoom, morphing landscape, changing environment, hallucinating objects, appearing trees, shifting rocks, altering cliff structures, structural drift, changing perspective, flickering, temporal jump, parched, frozen ice, stagnant water, artifacts, humans, tourist, boat, railings, buildings",
      "model_configs": {{
        "wan_2_1": {{
          "model": "fal-ai/wan-i2v",
          "prompts": {{
            "positive_prompt": "Living wallpaper cinemagraph, completely stationary static frame. Architectural structure and stones remain 100% frozen and unmoving. Subtle tranquil mist slowly drifting, glassy water micro-ripples. Stable uniform illumination, seamless loop compatible.",
            "negative_prompt": "camera movement, camera pan, panning, tilt, zoom, morphing, changing environment, flickering, temporal jump, artifacts, humans, tourist, buildings"
          }},
          "settings": {{
            "guide_scale": 5.0,
            "num_inference_steps": 30,
            "aspect_ratio": "16:9"
          }}
        }},
        "kling_v1_6_pro": {{
          "model": "fal-ai/kling-video/v1.6/pro/image-to-video",
          "prompts": {{
            "positive_prompt": "Cinemagraph style, living wallpaper. Strictly locked stationary camera with zero movement. Zen garden stones and gravel remain 100% frozen and static. Microscopic water surface movement, soft rising mist, seamless cyclic motion, zero humans.",
            "negative_prompt": "camera movement, camera pan, panning, tilt, zoom, morphing, flickering, temporal jump, artifacts, humans"
          }},
          "settings": {{
            "mode": "pro",
            "duration": "5",
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
