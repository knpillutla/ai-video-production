"""Atmospheric Archetypes Catalog for Ambient Relaxation & Sleep Productions.

Maps 14 ambient archetypes across 5 master atmospheric clusters with optimized
photographic prompts, tranquil motion dynamics, and Velvet acoustic tags.
"""

from typing import Dict, List, Optional
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


ARCHETYPES: Dict[str, AtmosphericArchetype] = {
    "swiss_alps": AtmosphericArchetype(
        key="swiss_alps",
        display_name="Swiss Alps Mountain Sanctuary",
        cluster="alpine",
        wide_visual_prompt=(
            "Masterpiece 4K panoramic photograph of the Swiss Alps in Lauterbrunnen valley at morning. "
            "Majestic snow-capped alpine peaks towering in the background, emerald green flower meadows with yellow wildflowers, "
            "quaint traditional Swiss wooden chalets, crystal mountain stream, natural 5400K daylight, 35mm Arri cinematography, zero humans."
        ),
        intimate_visual_prompt=(
            "Close-up 50mm portrait perspective of delicate alpine edelweiss and wild gentian flowers with morning dew, "
            "wooden timber chalet balcony, soft warm mountain sunrise bokeh, deep tranquil atmosphere, zero humans."
        ),
        wide_motion_prompt=(
            "Very gentle alpine breeze swaying mountain wildflowers, ultra-slow tranquil cloud drift across distant snow peaks, "
            "smooth stationary camera with subtle steadycam sway."
        ),
        intimate_motion_prompt=(
            "Soft mountain wind gently brushing floral petals, glistening morning dew in soft sunrise light, calm stationary camera."
        ),
        acoustic_tags=(
            "[velvet acoustic ambient], gentle Swiss mountain breeze, distant soft alpine cowbells, peaceful acoustic guitar and flute, "
            "soothing 432Hz sleep tuning, -21 LUFS anti-fatigue master, zero harsh hiss"
        ),
        default_domain="landscape_solid",
        tags=["swiss_alps", "mountains", "chalet", "peaceful", "nature"],
    ),
    "himalayas": AtmosphericArchetype(
        key="himalayas",
        display_name="Sacred Himalayan Monastery & Peaks",
        cluster="alpine",
        wide_visual_prompt=(
            "Masterpiece 4K photograph of sacred Himalayan snow peaks piercing ethereal golden dawn clouds. "
            "Ancient serene Tibetan stone monastery perched on mountain ridge, colorful prayer flags fluttering, vast transcendent silence, "
            "crisp 5500K natural sunlight, 35mm lens, 8k resolution, zero humans."
        ),
        intimate_visual_prompt=(
            "Close-up 50mm framing of hand-carved Tibetan prayer wheels and weathered wooden temple beam, "
            "warm butter lamp glowing gently, distant snowy mountain backdrop in soft creamy bokeh, serene spirituality."
        ),
        wide_motion_prompt=(
            "Tranquil prayer flags gently fluttering in high-altitude mountain air, slow ethereal mist rolling between Himalayan peaks, "
            "meditative stationary perspective."
        ),
        intimate_motion_prompt=(
            "Soft flickering warmth of sacred butter lamp flame, subtle mist drift outside temple window, peaceful stationary camera."
        ),
        acoustic_tags=(
            "[velvet acoustic ambient], sacred Tibetan singing bowls, resonant Himalayan monastery flute, gentle high-altitude wind, "
            "432Hz deep meditative drone, anti-fatigue sleep master, zero treble spikes"
        ),
        default_domain="landscape_solid",
        tags=["himalayas", "monastery", "meditation", "spiritual", "zen"],
    ),
    "ocean_world": AtmosphericArchetype(
        key="ocean_world",
        display_name="Crystalline Ocean World & Coral Haven",
        cluster="aquatic",
        wide_visual_prompt=(
            "Masterpiece 4K photograph of a serene tropical lagoon and crystalline turquoise ocean waters. "
            "Sunlight caustics dancing gracefully on white sandy seabed, vibrant living coral reef gardens with soft sea fans, "
            "gentle rolling surface swells, crystal clarity, natural underwater daylight, 35mm lens, zero humans."
        ),
        intimate_visual_prompt=(
            "Close-up 50mm portrait perspective of glowing sea anemone and pastel coral branches bathed in soft turquoise light, "
            "delicate dancing underwater sun rays, pure aquatic peace, zero humans."
        ),
        wide_motion_prompt=(
            "Tranquil underwater sunlight caustics shifting across soft sand, gentle slow fluid current swaying coral fans, "
            "smooth floating drift, zero rapid motion."
        ),
        intimate_motion_prompt=(
            "Delicate organic sway of sea anemone tentacles in calm laminar current, shimmering turquoise light glints, soothing flow."
        ),
        acoustic_tags=(
            "[velvet acoustic ambient], deep soothing oceanic swell, gentle underwater ambiance, soft ambient piano and warm synth pad, "
            "low-frequency oceanic grounding, -21 LUFS sleep master, zero harsh splash"
        ),
        default_domain="water_fluid",
        tags=["ocean", "underwater", "coral", "aquatic", "calm"],
    ),
    "mountains": AtmosphericArchetype(
        key="mountains",
        display_name="Misty Mountain Ranges at Dawn",
        cluster="alpine",
        wide_visual_prompt=(
            "Masterpiece 4K landscape photograph of endless layered mountain ridges shrouded in golden morning fog. "
            "Warm sunrise illuminating rocky granite peaks, deep green pine valleys below, sweeping monumental scale, 35mm Arri cinema, zero humans."
        ),
        intimate_visual_prompt=(
            "Close-up 50mm framing of a solitary pine bonsai rooted in weathered granite rock, morning dew drops, soft mountain dawn glow."
        ),
        wide_motion_prompt=(
            "Slow majestic sea of clouds floating through mountain passes, golden sunrise light gradually warming peaks, steady camera."
        ),
        intimate_motion_prompt=(
            "Delicate morning mist brushing pine needles, soft sunrise reflections on rock crystals, serene stationary shot."
        ),
        acoustic_tags=(
            "[velvet acoustic ambient], expansive atmospheric mountain wind, distant cello and warm ambient pads, 432Hz sleep resonance, "
            "smooth anti-fatigue master, zero hiss"
        ),
        default_domain="landscape_solid",
        tags=["mountains", "mist", "sunrise", "peace", "nature"],
    ),
    "rain": AtmosphericArchetype(
        key="rain",
        display_name="Forest River Rain & Water Droplets",
        cluster="forest_seasonal",
        wide_visual_prompt=(
            "Masterpiece 4K photograph of gentle tranquil rain falling over a lush emerald forest and glassy river. "
            "Soft concentric ripples spreading across the water, vibrant mossy banks, weeping willows, soft diffused overcast daylight, zero humans."
        ),
        intimate_visual_prompt=(
            "Close-up 50mm macro perspective of translucent raindrops hitting a broad emerald lotus leaf and dripping into clear pool, "
            "glistening water spheres, soft creamy green bokeh, pure calming ASMR."
        ),
        wide_motion_prompt=(
            "Gentle steady raindrops creating smooth expanding ripples across glassy river, soft misty precipitation, calm stationary camera."
        ),
        intimate_motion_prompt=(
            "Raindrops gently sliding down glistening leaf surface, slow hypnotic water droplet drip, serene macro motion."
        ),
        acoustic_tags=(
            "[velvet acoustic ambient], soft gentle forest rain on leaves, velvet low-pass rain sound, warm brown noise, acoustic piano, "
            "anti-fatigue sleep master, zero treble frying hiss, -21 LUFS"
        ),
        default_domain="water_fluid",
        tags=["rain", "water", "forest", "asmr", "sleep"],
    ),
    "lake": AtmosphericArchetype(
        key="lake",
        display_name="Placid Mountain Lake & Morning Mist",
        cluster="aquatic",
        wide_visual_prompt=(
            "Masterpiece 4K photograph of a mirror-smooth alpine lake surrounded by pine forests and misty mountains. "
            "Perfect crystal reflection of sky and trees in glassy water, wooden boat dock stretching into calm water, peaceful dawn, zero humans."
        ),
        intimate_visual_prompt=(
            "Close-up 50mm perspective of calm lake water gently lapping against weathered wooden dock posts, morning dew on wood grain."
        ),
        wide_motion_prompt=(
            "Ultra-slow tranquil morning mist skimming lake surface, microscopic water ripples, mirror reflections, stationary camera."
        ),
        intimate_motion_prompt=(
            "Gentle rhythmic rise and fall of calm water against dock, soft golden morning light glints, soothing stationary shot."
        ),
        acoustic_tags=(
            "[velvet acoustic ambient], gentle lap of water against dock, soft distant loon call, acoustic guitar and warm Rhodes piano, "
            "calm 432Hz tuning, anti-fatigue sleep master"
        ),
        default_domain="landscape_solid",
        tags=["lake", "reflection", "mist", "peaceful", "nature"],
    ),
    "beach": AtmosphericArchetype(
        key="beach",
        display_name="Tropical Beach & Sunset Surf",
        cluster="aquatic",
        wide_visual_prompt=(
            "Masterpiece 4K photograph of a pristine secluded tropical beach at golden sunset. "
            "Gentle foaming turquoise waves washing over smooth white sand, silhouette of coconut palm trees swaying, pastel orange sky, zero humans."
        ),
        intimate_visual_prompt=(
            "Close-up 50mm perspective of gentle ocean foam receding over wet seashell sand, reflecting warm sunset colors."
        ),
        wide_motion_prompt=(
            "Smooth rhythmic rolling waves breaking softly on shore, gentle palm fronds swaying in tropical sea breeze, calm camera."
        ),
        intimate_motion_prompt=(
            "Soft wave surge gliding over fine sand, glistening sunset reflections in receding tide, hypnotic rhythmic motion."
        ),
        acoustic_tags=(
            "[velvet acoustic ambient], rhythmic gentle ocean waves, soft warm sea breeze, acoustic harp and ambient synth pad, "
            "low-frequency wave surge, anti-fatigue master, -21 LUFS"
        ),
        default_domain="water_fluid",
        tags=["beach", "ocean", "waves", "sunset", "tropical"],
    ),
    "camp_fire": AtmosphericArchetype(
        key="camp_fire",
        display_name="Starlit Campfire & Glowing Embers",
        cluster="cozy_hearth",
        wide_visual_prompt=(
            "Masterpiece 4K photograph of a warm crackling campfire in a stone ring under a breathtaking starry night sky. "
            "Glowing golden embers, pine forest silhouette, deep indigo Milky Way galaxy above, rustic timber bench, cozy warmth, zero humans."
        ),
        intimate_visual_prompt=(
            "Close-up 50mm framing of glowing orange charcoal embers and dancing soft yellow flames in stone hearth, warm bokeh."
        ),
        wide_motion_prompt=(
            "Gentle dancing campfire flames, subtle glowing sparks rising into starlit night sky, calm stationary camera."
        ),
        intimate_motion_prompt=(
            "Hypnotic pulsing glow of warm embers, soft lick of fire flame, cozy soothing stationary perspective."
        ),
        acoustic_tags=(
            "[velvet acoustic ambient], gentle de-popped campfire crackle, soft night crickets, warm acoustic guitar picking, "
            "comforting sleep foley, -21 LUFS master, zero loud pop spikes"
        ),
        default_domain="landscape_solid",
        tags=["campfire", "hearth", "stars", "night", "cozy"],
    ),
    "forest": AtmosphericArchetype(
        key="forest",
        display_name="Ancient Pine Forest & Sunbeam Canopy",
        cluster="forest_seasonal",
        wide_visual_prompt=(
            "Masterpiece 4K photograph of an ancient pine and oak forest with golden morning sunbeams streaming through canopy (Komorebi). "
            "Lush moss-covered boulders, fern carpet, tranquil woodland path, crisp clean air, natural 5400K daylight, zero humans."
        ),
        intimate_visual_prompt=(
            "Close-up 50mm portrait of sunlit green ferns and wild wood sorrel on velvety moss bark, glowing dust motes in soft light."
        ),
        wide_motion_prompt=(
            "Sunbeams slowly shifting through pine canopy, gentle rustle of leaves in the woodland breeze, calm stationary camera."
        ),
        intimate_motion_prompt=(
            "Soft breathing of fern fronds in morning air, shimmering sunbeam highlights on green moss, peaceful stationary view."
        ),
        acoustic_tags=(
            "[velvet acoustic ambient], gentle forest breeze in pine needles, soft distant woodland birds, gentle acoustic piano, "
            "432Hz nature tuning, anti-fatigue sleep master"
        ),
        default_domain="landscape_solid",
        tags=["forest", "trees", "sunbeams", "moss", "nature"],
    ),
    "beach_house": AtmosphericArchetype(
        key="beach_house",
        display_name="Coastal Beach House & Ocean Terrace",
        cluster="aquatic",
        wide_visual_prompt=(
            "Masterpiece 4K photograph of an open-air luxury beach house terrace overlooking the tranquil ocean. "
            "White sheer linen curtains billowing in warm ocean breeze, teak wooden lounge chairs, ceramic coffee mug, sunset horizon, zero humans."
        ),
        intimate_visual_prompt=(
            "Close-up 50mm framing of sheer linen curtains swaying by open terrace window, soft ocean sunset bokeh outside."
        ),
        wide_motion_prompt=(
            "Soft breeze fluttering white terrace curtains, gentle rolling ocean waves visible in distance, tranquil stationary camera."
        ),
        intimate_motion_prompt=(
            "Graceful flowing movement of sheer curtains in sea air, warm golden sunset light glinting on teak wood, calm shot."
        ),
        acoustic_tags=(
            "[velvet acoustic ambient], distant muted ocean surf, gentle breeze through window, soft Rhodes piano and acoustic guitar, "
            "cozy seaside sleep master, -21 LUFS"
        ),
        default_domain="landscape_solid",
        tags=["beach_house", "terrace", "ocean", "cozy", "sunset"],
    ),
    "night_sleep": AtmosphericArchetype(
        key="night_sleep",
        display_name="Celestial Night Sky & Moonlit Clouds",
        cluster="deep_sleep",
        wide_visual_prompt=(
            "Masterpiece 4K photograph of a luminous full moon illuminating soft ethereal clouds and starry night sky. "
            "Deep velvet indigo atmosphere, distant mountain silhouette bathed in silvery moonlight, serene cosmos, zero humans."
        ),
        intimate_visual_prompt=(
            "Close-up 50mm perspective of cozy candle lantern glowing on dark wooden windowsill looking out into starlit night."
        ),
        wide_motion_prompt=(
            "Ultra-slow graceful drift of silvery clouds across luminous moon, subtle twinkling stars, hypnotic tranquil camera."
        ),
        intimate_motion_prompt=(
            "Soft warm flicker of candle flame, gentle moonlight reflection on window glass, deeply peaceful stationary view."
        ),
        acoustic_tags=(
            "[velvet acoustic ambient], deep delta wave sleep music, 432Hz solfeggio drone, warm ambient synth pads, soft night foley, "
            "deep sleep master, -22 LUFS anti-fatigue"
        ),
        default_domain="landscape_solid",
        tags=["night", "sleep", "moon", "stars", "delta_waves"],
    ),
    "blizzard": AtmosphericArchetype(
        key="blizzard",
        display_name="Cozy Timber Cabin in Mountain Blizzard",
        cluster="cozy_hearth",
        wide_visual_prompt=(
            "Masterpiece 4K photograph from inside a warm timber cabin looking out large bay window at snowstorm blizzard. "
            "Frost crystals on window corners, swirling snow outside, warm stone fireplace glowing inside, knitted blanket on chair, zero humans."
        ),
        intimate_visual_prompt=(
            "Close-up 50mm framing of delicate frost lace on double-pane glass with warm glowing fireplace reflection inside."
        ),
        wide_motion_prompt=(
            "Swirling blizzard snow outside cabin window, steady warm amber firelight glowing inside, calm stationary perspective."
        ),
        intimate_motion_prompt=(
            "Soft dancing firelight flickering across window frost, gentle outside snow drift, deeply comforting stillness."
        ),
        acoustic_tags=(
            "[velvet acoustic ambient], muted arctic blizzard wind outside, cozy stone fireplace crackle inside, warm acoustic cello, "
            "comforting sleep master, -21 LUFS"
        ),
        default_domain="landscape_solid",
        tags=["blizzard", "cabin", "snow", "fireplace", "cozy"],
    ),
    "winter": AtmosphericArchetype(
        key="winter",
        display_name="Pristine Winter Forest & Snowfall",
        cluster="forest_seasonal",
        wide_visual_prompt=(
            "Masterpiece 4K photograph of a serene winter forest with heavy pristine snow on pine boughs and frozen crystalline brook. "
            "Soft gentle snowflakes falling peacefully through crisp winter air, soft blue-white winter light, zero humans."
        ),
        intimate_visual_prompt=(
            "Close-up 50mm portrait of perfect hexagonal snowflakes resting on deep green pine needles, glistening ice crystals."
        ),
        wide_motion_prompt=(
            "Slow hypnotic vertical drift of fluffy snowflakes through winter pines, tranquil stillness, stationary camera."
        ),
        intimate_motion_prompt=(
            "Gentle snowflakes settling on pine bough, delicate winter sparkle in soft daylight, calm stationary view."
        ),
        acoustic_tags=(
            "[velvet acoustic ambient], soft gentle snowfall stillness, muted winter atmosphere, warm acoustic piano and crystal chimes, "
            "432Hz sleep tuning, anti-fatigue master"
        ),
        default_domain="landscape_solid",
        tags=["winter", "snow", "forest", "peaceful", "silence"],
    ),
    "autumn": AtmosphericArchetype(
        key="autumn",
        display_name="Golden Autumn Foliage & River Stream",
        cluster="forest_seasonal",
        wide_visual_prompt=(
            "Masterpiece 4K photograph of a vibrant autumn forest with golden yellow, amber, and crimson maple trees along a clear river. "
            "Fallen autumn leaves floating on clear water surface, mossy rocks, warm golden afternoon sunlight, 35mm lens, zero humans."
        ),
        intimate_visual_prompt=(
            "Close-up 50mm perspective of crisp golden and red maple leaf resting on smooth wet river pebble with clear water flowing by."
        ),
        wide_motion_prompt=(
            "Gentle autumn leaves slowly drifting down from maple trees, tranquil river current carrying floating leaves, calm camera."
        ),
        intimate_motion_prompt=(
            "Delicate water ripple parting around fallen autumn leaf, golden sunlight sparkle on clear stream, peaceful motion."
        ),
        acoustic_tags=(
            "[velvet acoustic ambient], gentle autumn breeze rustling dry leaves, soft flowing brook, acoustic guitar and Celtic harp, "
            "warm biophilic grounding, -21 LUFS sleep master"
        ),
        default_domain="water_fluid",
        tags=["autumn", "leaves", "river", "golden", "nature"],
    ),
}
