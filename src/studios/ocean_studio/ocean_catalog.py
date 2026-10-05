"""Ocean Studio Diurnal Atmospheric Archetypes Catalog.

Specialized exclusively in 4K Living Wallpapers across 6 diurnal ocean perspectives:
1. Daytime Coastal Haven (5500K turquoise lagoon, overwater villa, rhythmic surf)
2. Ocean Sunrise & Dawn Mist (3800K pastel rose/gold, first sun rays, glassy swells)
3. Sunset Ocean Horizon (3000K molten gold reflections, rolling swells, evening peace)
4. Bioluminescent Starlit Ocean (2200K dark indigo tide, glowing blue waves, zero fire)
5. Ocean Shoreline Campfire (2000K beach driftwood hearth, pulsing embers, night surf)
6. Tropical Ocean Rain (4500K gentle coastal shower on turquoise sea, rain on canvas/teak ASMR)
"""

from typing import Dict, List
from pydantic import BaseModel, Field


class AtmosphericArchetype(BaseModel):
    """Detailed visual, motion, and acoustic profile for an ocean environment."""
    key: str
    display_name: str
    cluster: str = "ocean"
    wide_visual_prompt: str
    intimate_visual_prompt: str
    wide_motion_prompt: str
    intimate_motion_prompt: str
    acoustic_tags: str
    default_domain: str = "water_fluid"
    tags: List[str] = Field(default_factory=list)


OCEAN_ARCHETYPES: Dict[str, AtmosphericArchetype] = {
    "ocean_daytime_shore": AtmosphericArchetype(
        key="ocean_daytime_shore",
        display_name="Overwater Villa & Daytime Turquoise Lagoon",
        cluster="ocean",
        wide_visual_prompt=(
            "Masterpiece 4K photograph looking outward from the shaded teak deck of an ultra-luxury overwater villa "
            "onto a vast turquoise lagoon and rolling white ocean waves under brilliant 5500K natural daylight. "
            "Sheer white linen drapes flutter gently at the wooden columns framing the shot. "
            "Polished teak lounge daybed with plush sand-colored cushions and a low driftwood table with chilled coconut water in a crystal glass. "
            "In the background, pristine crystal-clear turquoise waters gradient into deep sapphire ocean, "
            "with gentle rhythmic swells and white sea-foam crests breaking along a distant coral reef under a spotless cerulean blue sky. "
            "Symmetrical 16:9 cinematic framing, shot on a locked tripod, 35mm Arri cinematography, zero tourists, zero boats, zero modern clutter."
        ),
        intimate_visual_prompt=(
            "Close-up 50mm portrait perspective of chilled coconut water with a bamboo straw in a crystal glass on a weathered teak deck table. "
            "In the soft-focus optical bokeh background (f/1.4), radiant turquoise lagoon water and shimmering sunlit ripples lap gently against wooden villa stilts, "
            "sheer white linen curtains swaying in the sea breeze, serene luxury tropical stillness."
        ),
        wide_motion_prompt=(
            "Ultra-subtle living wallpaper cinemagraph motion. Completely stationary locked tripod framing. "
            "Continuous smooth laminar ocean wave swells rolling rhythmically across the turquoise lagoon toward the shore. "
            "Sheer white linen drapes flutter and sway in the coastal sea breeze. Specular sunlight caustics dancing on the crystal clear water surface. "
            "The wooden villa deck, furniture, and sky remain 100% rigid, frozen, and temporally stable, zero camera movement, zero panning, zero morphing."
        ),
        intimate_motion_prompt=(
            "Gentle sway of white linen curtains in the ocean breeze, subtle dancing sunbeam reflections across the glass and teak wood, "
            "calm stationary camera, peaceful tropical living wallpaper cadence."
        ),
        acoustic_tags=(
            "[peaceful & joyful meditation], gentle rhythmic turquoise ocean surf, uplifting resonant handpan in major pentatonic mode, "
            "soft Hawaiian slack-key guitar harmonics, crystalline sea shell chimes, warm 432Hz velvet pads, deep stress relief, -21 LUFS"
        ),
        default_domain="water_fluid",
        tags=["ocean", "daytime", "turquoise_lagoon", "overwater_villa", "tropical", "linen_drapes", "432hz", "asmr"],
    ),
    "ocean_sunrise_coast": AtmosphericArchetype(
        key="ocean_sunrise_coast",
        display_name="Coastal Veranda & Pastel Dawn Sunrise",
        cluster="ocean",
        wide_visual_prompt=(
            "Masterpiece 4K photograph looking outward through the open arched colonnade of a luxury Mediterranean coastal veranda at early morning dawn. "
            "The radiant rising sun crests over the open ocean horizon, casting shimmering golden sun-shaft caustics across calm glassy water. "
            "The sky transitions from soft lavender and pastel blush-pink to radiant amber (3800K). "
            "Inside the veranda, a whitewashed stone ledge with a steaming porcelain cup of morning coffee, a small vase of coastal wildflowers, "
            "and sheer ivory draperies gently stirring in the cool dawn sea air. In the background, calm rhythmic ocean waves roll smoothly toward the shore. "
            "Locked tripod, symmetrical 16:9 framing, 35mm cinematic lens, zero humans."
        ),
        intimate_visual_prompt=(
            "Close-up 50mm portrait perspective of a steaming ceramic coffee mug on a rustic stone balcony balustrade. "
            "In the background through creamy optical bokeh (f/1.4), the radiant rising sun shines across the glassy pastel ocean surface, "
            "soft dawn sea haze, sheer ivory fabric stirring in the morning breeze, tranquil awakening."
        ),
        wide_motion_prompt=(
            "Stationary locked tripod framing. Gentle glassy ocean swells rolling peacefully toward the coastline. "
            "Shimmering golden sunlight reflections dancing on the water surface as dawn breaks. "
            "Delicate steam rises from the coffee cup. Sheer ivory curtains billow softly in the cool sea breeze. "
            "Architectural arches, balcony, and horizon remain 100% rock-solid and stable."
        ),
        intimate_motion_prompt=(
            "Delicate wisps of steam curling from the coffee cup, soft golden dawn ripples shimmering in background bokeh, "
            "gentle fabric flutter, stationary camera."
        ),
        acoustic_tags=(
            "[morning renewal & gratitude], soft melodic Mediterranean bouzouki harmonics, Spanish nylon-string guitar, "
            "gentle glassy ocean swell foley, warm 528Hz Solfeggio heart-opening resonance, restorative dawn calm, -21 LUFS"
        ),
        default_domain="water_fluid",
        tags=["ocean", "sunrise", "mediterranean", "dawn", "pastel_sky", "balcony_view", "528hz", "relaxation"],
    ),
    "ocean_sunset_horizon": AtmosphericArchetype(
        key="ocean_sunset_horizon",
        display_name="Cliffside Sanctuary & Golden Hour Ocean Sunset",
        cluster="ocean",
        wide_visual_prompt=(
            "Masterpiece 4K photograph looking out from a private stone cliffside terrace high above the Pacific Ocean during golden hour sunset. "
            "The sinking sun forms a fiery molten gold ball on the horizon, bathing the undulating ocean swells in rich terracotta, crimson, and amber light (3000K). "
            "On the flagstone terrace, a plush woven daybed with linen throws, a warm brass hurricane lantern with a glowing pillar candle, and olive trees in terracotta urns. "
            "Below, long majestic ocean waves roll smoothly into a secluded cove, their foam glowing in warm amber sunset reflections. "
            "Locked tripod, 16:9 wide cinematic landscape, zero tourists, zero power lines, pure coastal sanctuary."
        ),
        intimate_visual_prompt=(
            "Close-up 50mm portrait perspective of a glowing glass hurricane lantern on a stone terrace wall at golden hour. "
            "In the background through lush optical bokeh (f/1.4), the molten crimson sunset reflects across rolling ocean surf, "
            "soft evening sea mist, warm amber caustics, peaceful dusk unwinding."
        ),
        wide_motion_prompt=(
            "Completely stationary locked tripod framing. Continuous rhythmic rolling ocean waves surging gently into the cove. "
            "Molten golden sunset light shimmering across the moving wave crests. "
            "Subtle candle flame flicker protected inside the glass lantern. Olive branches sway lightly in the evening offshore breeze. "
            "Cliffside stone terrace and horizon remain completely rigid and stable."
        ),
        intimate_motion_prompt=(
            "Subtle candle flame dance inside the lantern glass, glowing sunset ripples shimmering in soft background bokeh, "
            "stationary camera, peaceful sunset cadence."
        ),
        acoustic_tags=(
            "[evening unwinding & stress relief], rich warm cello drone, gentle fingerpicked acoustic guitar, "
            "rhythmic Pacific ocean surf, 6Hz theta-wave relaxation, soothing amber twilight soundbed, -21 LUFS"
        ),
        default_domain="water_fluid",
        tags=["ocean", "sunset", "cliffside", "golden_hour", "ambient_waves", "theta_wave", "stress_relief"],
    ),
    "ocean_night_bioluminescent": AtmosphericArchetype(
        key="ocean_night_bioluminescent",
        display_name="Starlit Beach Pavilion & Bioluminescent Waves",
        cluster="ocean",
        wide_visual_prompt=(
            "Masterpiece 4K night photograph looking outward from an open-air beachfront cabana onto a tranquil midnight ocean under a brilliant starlit sky. "
            "The Milky Way galaxy arcs majestically across a deep indigo night canopy (2200K). "
            "Along the dark wet shoreline, gentle rolling ocean wave swells naturally glow with electric-blue bioluminescent phytoplankton illumination, "
            "creating ribbons of soft cyan light along each breaking wave crest. "
            "Inside the shaded cabana, dark teak wood framing, sheer navy linen curtains, and a soft warm candle lantern on a low driftwood table. "
            "Strictly zero campfire, zero smoke, zero bonfire. Locked tripod, symmetrical 16:9 framing, 35mm long-exposure cinematography, zero humans."
        ),
        intimate_visual_prompt=(
            "Close-up 50mm perspective of a low brass candle lantern casting a warm golden glow on a weathered driftwood table in an open cabana. "
            "In the background through creamy optical bokeh (f/1.4), dark midnight ocean waves glow with vibrant electric-blue bioluminescent light "
            "under a crystalline star-filled sky, pure celestial tranquility, zero humans."
        ),
        wide_motion_prompt=(
            "Stationary locked tripod framing. Continuous gentle ocean waves rolling ashore, their crests glowing with hypnotic ribbons of electric-blue bioluminescence. "
            "Sheer navy drapes stir gently in the cool midnight sea air. A steady warm candle glow inside the lantern. "
            "Cabana architecture, driftwood table, and starlit sky remain completely rigid, stable, and static, zero camera jitter."
        ),
        intimate_motion_prompt=(
            "Gentle steady candle flame glow inside glass lantern, soft electric-blue bioluminescent wave pulses glowing in background bokeh, "
            "calm stationary camera, deep sleep cadence."
        ),
        acoustic_tags=(
            "[deep sleep & insomnia relief], hypnotic 432Hz velvet delta-wave sleep soundbath (2Hz entrainment), "
            "soft nocturnal ocean tide lapping, celestial singing bowl resonance, deep restorative peace, zero drums, -21 LUFS"
        ),
        default_domain="water_fluid",
        tags=["ocean", "night", "bioluminescence", "starlight", "milky_way", "deep_sleep", "delta_waves", "asmr"],
    ),
    "ocean_campfire_hearth": AtmosphericArchetype(
        key="ocean_campfire_hearth",
        display_name="Open-Air Beach Shoreline Campfire & Night Waves",
        cluster="ocean",
        wide_visual_prompt=(
            "Masterpiece 4K photograph of a cozy open-air driftwood campfire in a rustic stone pit on a pristine coastal sandy beach at dark twilight. "
            "In the foreground, warm glowing campfire flames and pulsing orange wood embers illuminate the golden sand and weathered river stones (2000K). "
            "In the immediate background, continuous rhythmic ocean waves roll and surge along the dark coastline under an indigo night sky filled with faint stars. "
            "100% open-air outdoor beach, strictly zero indoor rooms, zero sofas, zero modern furniture. "
            "Symmetrical 16:9 framing, locked tripod, 35mm Arri cinematography, zero humans, pure coastal solitude."
        ),
        intimate_visual_prompt=(
            "Close-up 50mm portrait perspective of crackling driftwood embers and glowing orange coals in a beach stone hearth. "
            "In the soft-focus optical bokeh background (f/1.4), dark rhythmic ocean surf breaks along the sandy shore under a deep twilight sky, "
            "warm ember sparks rising into the cool evening breeze, cozy beach campfire tranquility."
        ),
        wide_motion_prompt=(
            "Stationary locked tripod framing. Animate ONLY the crackling campfire flames, glowing embers, and rolling ocean surf. "
            "Flames flicker and dance gently in the sea breeze while background ocean waves roll continuously ashore. "
            "The stone hearth, beach sand, and twilight sky remain 100% rigid, frozen, and temporally stable."
        ),
        intimate_motion_prompt=(
            "Gentle hypnotic dance of orange campfire embers and delicate floating sparks, dark ocean waves rolling in background bokeh, "
            "stationary camera, tranquil hearth cadence."
        ),
        acoustic_tags=(
            "[cozy grounding & warmth], crystal-clear crackling driftwood campfire foley, rhythmic ocean surf surges, "
            "warm 432Hz ambient drone, comforting acoustic bed, binaural relaxation, -21 LUFS"
        ),
        default_domain="water_fluid",
        tags=["ocean", "campfire", "beach", "hearth", "embers", "rolling_surf", "asmr", "relaxation"],
    ),
    "ocean_tropical_rain": AtmosphericArchetype(
        key="ocean_tropical_rain",
        display_name="Sheltered Teak Balcony & Tropical Ocean Rain",
        cluster="ocean",
        wide_visual_prompt=(
            "Masterpiece 4K photograph looking outward from a covered teak balcony of a tropical coastal sanctuary during a soothing warm ocean rain shower. "
            "Gentle raindrops fall diagonally through the cool coastal air, creating delicate concentric ripples across the calm turquoise ocean surface (4500K). "
            "Overhead, deep overhanging teak eaves shelter the balcony. Lush wet palm fronds and flowering hibiscus frame the perimeter with glistening water droplets. "
            "On the balcony, a hand-woven rattan chair with waterproof linen cushions and a small cedar table. "
            "In the background, the vast tropical sea stretches to a misty soft-gray horizon under gentle overcast clouds. "
            "Locked tripod, symmetrical 16:9 cinematic framing, 35mm cinematography, zero humans."
        ),
        intimate_visual_prompt=(
            "Close-up 50mm perspective of glistening rainwater droplets beading on a dark green tropical palm leaf overhanging a covered teak balcony railing. "
            "In the background through creamy optical bokeh (f/1.4), gentle raindrops fall across the turquoise sea with rhythmic ripples, "
            "fresh petrichor ambiance, peaceful rain shelter tranquility."
        ),
        wide_motion_prompt=(
            "Stationary locked tripod framing. Gentle vertical raindrops falling smoothly through the air, creating continuous micro-ripples across the turquoise sea. "
            "Delicate rain droplets dripping from palm leaves at the edges. Distant calm ocean swells rolling smoothly. "
            "Balcony eaves, deck floor, and furniture remain 100% solid, static, and stable."
        ),
        intimate_motion_prompt=(
            "Subtle trembling of the wet palm leaf as water droplets drip from its tip, gentle rain streaks in soft bokeh background, "
            "stationary camera, restorative ASMR rain cadence."
        ),
        acoustic_tags=(
            "[restorative rain ASMR & calm], gentle tropical rain falling on ocean water, soft water drops on palm leaves, "
            "distant soothing ocean surf rumble, 432Hz velvet acoustic pads, anti-anxiety soundbath, -21 LUFS"
        ),
        default_domain="water_fluid",
        tags=["ocean", "rain", "tropical", "balcony_shelter", "water_ripples", "rain_asmr", "stress_relief"],
    ),
}

# Aliases for backward compatibility and intuitive routing
OCEAN_ARCHETYPES["ocean_daytime"] = OCEAN_ARCHETYPES["ocean_daytime_shore"]
OCEAN_ARCHETYPES["ocean_villa"] = OCEAN_ARCHETYPES["ocean_daytime_shore"]
OCEAN_ARCHETYPES["ocean_sunrise"] = OCEAN_ARCHETYPES["ocean_sunrise_coast"]
OCEAN_ARCHETYPES["ocean_sunset"] = OCEAN_ARCHETYPES["ocean_sunset_horizon"]
OCEAN_ARCHETYPES["ocean_night"] = OCEAN_ARCHETYPES["ocean_night_bioluminescent"]
OCEAN_ARCHETYPES["ocean_bioluminescent"] = OCEAN_ARCHETYPES["ocean_night_bioluminescent"]
OCEAN_ARCHETYPES["ocean_campfire"] = OCEAN_ARCHETYPES["ocean_campfire_hearth"]
OCEAN_ARCHETYPES["ocean_rain"] = OCEAN_ARCHETYPES["ocean_tropical_rain"]
OCEAN_ARCHETYPES["ocean"] = OCEAN_ARCHETYPES["ocean_daytime_shore"]
