"""Cultural Acoustic Data Profiles, Archetype Matrices & Weather Modifiers."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CulturalAcousticProfile:
    """Acoustic specification tailored to a specific cultural and environmental landscape."""
    culture_key: str
    lead_instrument: str
    secondary_textures: str
    scale_and_tuning: str
    rhythm_and_tempo: str
    emotional_purpose: str
    suno_tags: str
    suno_prompt: str


WEATHER_ACOUSTIC_MODIFIERS: dict[str, dict[str, str]] = {
    "rain": {
        "tag_addon": "binaural raindrops on water, soft wet reflections, gentle rhodes piano, reflective warmth",
        "prompt_layer": "[Weather Foley: Continuous Soothing Binaural Rain ASMR on Water & Glass, Wet Surface Reflections]\n[Atmosphere: Cozy Overcast Rainy Sky, Reflective Melancholic Warmth]",
        "tempo_offset": -4,
    },
    "snow": {
        "tag_addon": "serene snowfall, muted winter stillness, delicate crystalline glass bells, warm cello harmonics",
        "prompt_layer": "[Weather Foley: Muffled Winter Silence, Gentle Wind Through Frosted Pines]\n[Atmosphere: Serene Frosted Stillness, Crystalline Glass Bells, Velvet Warming Pads]",
        "tempo_offset": -6,
    },
    "fog": {
        "tag_addon": "ethereal morning mist, breathy wooden flute, mysterious ambient drone, soft distant chime",
        "prompt_layer": "[Weather Foley: Distant Soft Coastal Foghorn Whisper, Delicate Dewdrop Foley]\n[Atmosphere: Ethereal Morning Mist, Breathy Flute Echo, Velvet Ambient Shroud]",
        "tempo_offset": -4,
    },
    "sunset": {
        "tag_addon": "warm sunset golden hour, spanish nylon guitar arpeggios, amber ambient synth pads, nostalgic peace",
        "prompt_layer": "[Lighting Atmosphere: Warm 2800K Golden Sunset Alpenglow, Long Dusk Shadows]\n[Music Texture: Nostalgic Nylon Guitar Chords & Golden Velvet Pads, Heartfelt Serenity]",
        "tempo_offset": 0,
    },
    "night": {
        "tag_addon": "deep delta sleep drone, 432Hz starlit night pads, nocturnal tranquility, zero percussive drums",
        "prompt_layer": "[Lighting Atmosphere: Deep Indigo Midnight Sky, Brilliant Celestial Milky Way]\n[Music Texture: 432Hz Delta Sleep Drone, Soft Ambient Night Pads, Deep Anxiety Dissolving Silence]",
        "tempo_offset": -8,
    },
}

CULTURAL_PROFILES: dict[str, dict[str, str]] = {
    "beach_lounge": {
        "culture_key": "beach_lounge",
        "lead_instrument": "Sophisticated Acoustic Nylon Guitar & Rhodes Piano",
        "secondary_textures": "Deep velvet chillout synth pads, warm downtempo bassline, glassy pool water caustics, subtle distant surf foley",
        "scale_and_tuning": "432Hz Modern Harmonic Resonance, Dorian / Major 7th chords",
        "rhythm_and_tempo": "85 BPM relaxed chic lounge downtempo pulse",
        "emotional_purpose": "Sophisticated luxury, effortless calm, modern poolside elegance, stress release",
        "suno_tags": "432hz, modern chillout lounge, acoustic nylon guitar, velvet rhodes piano, downtempo bass, glassy pool water caustics, distant ocean surf, -21 LUFS",
        "suno_prompt": "[Instrumental Modern Chillout Lounge]\n[Tempo: 85 BPM - Chic Downtempo Pulse]\n[Tuning: 432Hz Harmonic Velvet Bed]\n[Lead Melody: Sophisticated Spanish Nylon Guitar & Warm Rhodes Keys]\n[Accompaniment: Deep Velvet Ambient Synth Pads & Warm Sub-Bass]\n[Texture: Glassy Infinity Pool Water Ripples & Distant Ocean Surf]\n[Emotion: Ultra-Chic Luxury, Effortless Modern Peace, Cafe Del Mar Aesthetic]\n[Outro: Soft Twilight Pool Caustic Fade]",
    },
    "party_lounge": {
        "culture_key": "party_lounge",
        "lead_instrument": "Uplifting Acoustic Guitar Plucks & Warm Melodic Synth Chords",
        "secondary_textures": "Crisp rhythmic shakers, organic hand claps, rolling tropical sub-bass, vibrant summer ocean breeze",
        "scale_and_tuning": "Melodic Major 7th House Harmony",
        "rhythm_and_tempo": "120 BPM upbeat tropical beach club groove",
        "emotional_purpose": "Joyous celebration, uplifting summer vitality, chic sunset cocktail party energy",
        "suno_tags": "energetic tropical beach club, melodic house groove, rhythmic shakers, acoustic guitar plucks, uplifting summer beats, vibrant ocean ambiance, -18 LUFS",
        "suno_prompt": "[Instrumental Tropical Beach Club Groove]\n[Tempo: 120 BPM - Uplifting Melodic House Pulse]\n[Lead Melody: Joyous Acoustic Guitar Riffs & Sunny Synth Melodic Motifs]\n[Accompaniment: Rhythmic Crisp Shakers, Bongo Grooves & Warm Deep Bassline]\n[Atmosphere: Sun-Drenched Oceanfront Terrace Party, Sunset Cocktail Vibe]\n[Emotion: Exhilarating Joy, Carefree Summer Celebration, Vibrant Luxury Vibe]\n[Outro: Triumphant Sunset Ocean Fade]",
    },
    "desert": {
        "culture_key": "desert",
        "lead_instrument": "Airy Wooden Ney Flute in D-Minor",
        "secondary_textures": "Resonant acoustic Qanun, warm Oud harmonics, soft framed Daf heartbeat pulse, serene silence",
        "scale_and_tuning": "432Hz Solfeggio tuning, Maqam Bayati / Hijaz modal resonance",
        "rhythm_and_tempo": "54 BPM gentle hypnotic pulse (resting heart rate entrainment)",
        "emotional_purpose": "Mystical serenity, vast tranquility, deep stress relief, mind-calming meditation",
        "suno_tags": "432hz, airy wooden ney flute, qanun, warm oud harmonics, soft daf pulse, velvet pads, desert acoustic, hummable melody, studio master, zero hiss, -21 LUFS",
        "suno_prompt": "[Instrumental Ambient Meditation]\n[Tempo: 54 BPM - Hypnotic Heartbeat Pulse]\n[Tuning: 432Hz Solfeggio Velvet Resonance]\n[Lead Melody: Mesmerizing Hummable Airy Wooden Ney Flute]\n[Accompaniment: Plucked Acoustic Qanun & Soft Oud Harmonics]\n[Rhythm: Gentle Framed Daf Drum Soft Heartbeat Tap]\n[Atmosphere: Warm Velvet Ambient Pads & Singing Bowls, Studio Master, Zero Hiss, Zero Wind Noise]\n[Emotion: Enchanting, Joyful, Anxiety-Reducing, Restful Sleep Drone]\n[Outro: Infinite Peaceful Desert Night Fade]",
    },
    "swiss_alps": {
        "culture_key": "swiss_alps",
        "lead_instrument": "Warm Alpine Wooden Flute in Major Pentatonic",
        "secondary_textures": "Acoustic Zither, gentle Cello harmonics, crystalline glass bells, distant alpine breeze",
        "scale_and_tuning": "528Hz Transformation & 432Hz Harmonic Solfeggio",
        "rhythm_and_tempo": "56 BPM slow pastoral breathing rhythm",
        "emotional_purpose": "Soaring wonder, joyous pastoral peace, uplifting lightness, anxiety relief",
        "suno_tags": "528hz, alpine wooden flute, acoustic zither, cello harmonics, crystalline bells, velvet pads, pastoral ambient, joyful hummable melody, -21 LUFS",
        "suno_prompt": "[Instrumental Pastoral Meditation]\n[Tempo: 56 BPM - Slow Breathing Cadence]\n[Tuning: 528Hz Love Frequency & 432Hz Velvet Bed]\n[Lead Melody: Joyous Hummable Alpine Wooden Flute Solos]\n[Accompaniment: Plucked Acoustic Zither & Resonant Cello Drone]\n[Texture: Pure Crystalline Glass Bells & Distant Wind Chimes]\n[Atmosphere: Sunlit Alpine Wildflower Valley, Zero Distortion, Studio Master]\n[Emotion: Heartwarming, Uplifting, Majestic Peace, Restful Sleep]\n[Outro: Soft Glacial Wind Whisper Fade]",
    },
    "zen": {
        "culture_key": "zen",
        "lead_instrument": "Breathy Japanese Shakuhachi Bamboo Flute",
        "secondary_textures": "Plucked Koto strings, resonant bronze temple bells, bamboo water dripper (shishi-odoshi), pebble raking",
        "scale_and_tuning": "432Hz In-sen & Yo pentatonic meditative tuning",
        "rhythm_and_tempo": "48 BPM deep meditative breathing cadence (alpha/theta state)",
        "emotional_purpose": "Profound inner stillness, clarity of mind, tension release, sacred peace",
        "suno_tags": "432hz, breathy shakuhachi bamboo flute, plucked koto, bronze temple bell, bamboo water drip foley, zen ambient, tranquil melody, -21 LUFS",
        "suno_prompt": "[Instrumental Zen Garden Soundscape]\n[Tempo: 48 BPM - Deep Meditative Breath]\n[Tuning: 432Hz In-sen Sacred Pentatonic Tuning]\n[Lead Melody: Breathy Expressive Shakuhachi Flute Solos]\n[Accompaniment: Delicate Plucked Koto Harp Notes]\n[Texture: Distant Bronze Singing Bell & Subtle Bamboo Water Drip Foley]\n[Atmosphere: Velvet Mist Over Moss Garden, Pure Stillness]\n[Emotion: Transcendent Peace, Anxiety Erasing, Deep Sleep Induction]\n[Outro: Reverberating Temple Bell Dissolve]",
    },
    "himalayas": {
        "culture_key": "himalayas",
        "lead_instrument": "Breathy Indian Bansuri Bamboo Flute in E-Major",
        "secondary_textures": "Resonant Handpan (Pantam), Tibetan singing bowls, subtle Tampura drone, cedar wind chimes",
        "scale_and_tuning": "432Hz Raag Bhupali (uplifting major pentatonic) meditative resonance",
        "rhythm_and_tempo": "52 BPM steady resting heartbeat pulse",
        "emotional_purpose": "Spiritual elevation, sacred sanctuary calm, grounded serenity, meditative bliss",
        "suno_tags": "432hz, bansuri bamboo flute, resonant handpan, tibetan singing bowls, tampura drone, himalayan ambient, uplifting melody, -21 LUFS",
        "suno_prompt": "[Instrumental Himalayan Sanctuary]\n[Tempo: 52 BPM - Heartbeat Entrainment]\n[Tuning: 432Hz Raag Bhupali Sacred Frequency]\n[Lead Melody: Soaring Lyrical Bansuri Flute Solos]\n[Accompaniment: Resonant Handpan Plucks & Singing Bowl Harmonics]\n[Atmosphere: Mountain Sanctuary Velvet Drone, High Altitude Serenity]\n[Emotion: Deep Inner Joy, Sacred Reverence, Complete Physical Relaxation]\n[Outro: Lingering Bowl Resonance Fade]",
    },
    "ocean": {
        "culture_key": "ocean",
        "lead_instrument": "Melodic Steel Handpan (Pantam) in D-Kurd",
        "secondary_textures": "Gentle Kalimba (Thumb Piano), soft Rhodes electric piano, rolling ocean swell foley, sea spray whisper",
        "scale_and_tuning": "432Hz Oceanic Kurd Scale Harmonic resonance",
        "rhythm_and_tempo": "50 BPM tidal wave lullaby cadence",
        "emotional_purpose": "Soothing tidal flow, emotional release, gentle maternal calm, deep sleep entry",
        "suno_tags": "432hz, melodic handpan, kalimba, rhodes piano, gentle ocean swell foley, coastal ambient, soothing tidal melody, -21 LUFS",
        "suno_prompt": "[Instrumental Ocean Coastline Meditation]\n[Tempo: 50 BPM - Tidal Wave Cadence]\n[Tuning: 432Hz D-Kurd Harmonic Water Resonance]\n[Lead Melody: Hypnotic Plucked Handpan & Kalimba Harmonics]\n[Accompaniment: Warm Rhodes Electric Piano Velvet Chords]\n[Texture: Continuous Gentle Shoreline Ocean Swell Foley, Zero Harsh Waves]\n[Atmosphere: Sunlit Turquoise Lagoon, Warm Sea Spray Velvet Bed]\n[Emotion: Soothing Comfort, Drift Away Serenity, Insomnia Relief]\n[Outro: Soft Sea Foam Receding Fade]",
    },
    "forest": {
        "culture_key": "forest",
        "lead_instrument": "Warm Native American Cedar Flute",
        "secondary_textures": "Delicate Celtic Harp, gentle Cello warmth, whispering pine canopy wind, birdsong murmurs",
        "scale_and_tuning": "432Hz Minor Pentatonic Natural Forest tuning",
        "rhythm_and_tempo": "52 BPM leaf-sway breathing tempo",
        "emotional_purpose": "Grounding biophilic comfort, nature connection, nervous system reset, calming reassurance",
        "suno_tags": "432hz, cedar flute, celtic harp, warm cello, forest canopy wind foley, ancient woodland ambient, hummable melody, -21 LUFS",
        "suno_prompt": "[Instrumental Ancient Forest Soundscape]\n[Tempo: 52 BPM - Leaf-Sway Rhythm]\n[Tuning: 432Hz Nature Solfeggio Tuning]\n[Lead Melody: Warm Expressive Cedar Flute Themes]\n[Accompaniment: Flowing Celtic Harp Arpeggios & Cello Drone]\n[Texture: Soft Canopy Wind Whispers & Distant Spring Brook Foley]\n[Atmosphere: Sunbeams Through Ancient Mossy Oaks, Warm Biophilic Glow]\n[Emotion: Grounded Safe Sanctuary, Stress Dissolving, Deep Calm]\n[Outro: Lingering Woodland Flute Echo Fade]",
    },
    "hearth": {
        "culture_key": "hearth",
        "lead_instrument": "Intimate Soft Felted Upright Piano",
        "secondary_textures": "Warm Cello harmonics, subtle acoustic nylon guitar, crackling fireplace embers foley, cozy room tone",
        "scale_and_tuning": "432Hz Warm Major 7th Cozy Harmony",
        "rhythm_and_tempo": "46 BPM ember-glow ultra-slow tempo",
        "emotional_purpose": "Cozy shelter, nostalgic warmth, complete physical surrender, restful deep sleep",
        "suno_tags": "432hz, felted piano, warm cello, crackling fire foley, acoustic guitar, cozy hearth ambient, intimate lullaby melody, -21 LUFS",
        "suno_prompt": "[Instrumental Fireside Cabin Meditation]\n[Tempo: 46 BPM - Ember-Glow Slow Pulse]\n[Tuning: 432Hz Warm Velvet Tuning]\n[Lead Melody: Intimate Gentle Felted Piano Lullaby Motifs]\n[Accompaniment: Warm Cello Harmonics & Soft Nylon Guitar Chords]\n[Texture: Continuous Soft Crackling Hearth Fire ASMR, Gentle Wood Embers]\n[Atmosphere: Candlelit Cabin Sanctuary, Safe Warmth From Winter Wind]\n[Emotion: Deep Nourishing Comfort, Heart-Opening Peace, Sleep Induction]\n[Outro: Soft Fire Ember Dissolve]",
    },
    "rain": {
        "culture_key": "rain",
        "lead_instrument": "Gentle Crystal Handpan & Marimba",
        "secondary_textures": "Plucked acoustic harp, warm analog synth pads, continuous soothing rainfall on windowpane foley",
        "scale_and_tuning": "432Hz Water Droplet Lydian Mode",
        "rhythm_and_tempo": "54 BPM steady droplet rhythm",
        "emotional_purpose": "Wash away mental fatigue, introspective peace, anxiety release, rain-sleep bliss",
        "suno_tags": "432hz, crystal handpan, acoustic harp, soft marimba, continuous rainfall foley, rain retreat ambient, soothing melody, -21 LUFS",
        "suno_prompt": "[Instrumental Rainy Day Retreat]\n[Tempo: 54 BPM - Steady Raindrop Cadence]\n[Tuning: 432Hz Lydian Droplet Tuning]\n[Lead Melody: Hypnotic Plucked Crystal Handpan & Harp Patterns]\n[Accompaniment: Soft Warm Analog Synth Bed]\n[Texture: Continuous Soothing Rain On Leaves & Windowpane ASMR]\n[Atmosphere: Overcast Green Forest Canopy, Reflective Stillness]\n[Emotion: Calming Washed Clean Mind, Restorative Comfort, Sleep Aid]\n[Outro: Soft Rain Droplet Fade]",
    },
    "waterfall": {
        "culture_key": "waterfall",
        "lead_instrument": "Cascading Celtic Harp & Cello Harmonics",
        "secondary_textures": "Acoustic 12-string guitar, soft high-register flute, continuous roaring waterfall mist foley, brown noise bed",
        "scale_and_tuning": "432Hz Natural Waterfall Resonance",
        "rhythm_and_tempo": "58 BPM steady cataract surge",
        "emotional_purpose": "Brown noise acoustic masking, mental stillness, total relaxation",
        "suno_tags": "432hz, celtic harp, acoustic cello, cascading water foley, brown noise acoustics, waterfall ambient, -21 LUFS",
        "suno_prompt": "[Instrumental Monumental Waterfall Sanctuary]\n[Tempo: 58 BPM - Cascading Flow Cadence]\n[Tuning: 432Hz Natural Earth Flow]\n[Lead Melody: Flowing Celtic Harp Arpeggios & Cello Harmonics]\n[Texture: Continuous Gentle Roaring Water Mist Foley & Brown Noise Bed]\n[Atmosphere: Refreshing Mountain Cascade Velvet Pads]\n[Emotion: Profound Immersion, Anxiety Melting, Restful Serenity]\n[Outro: Soft Cascading Spray Fade]",
    },
}

MOTIF_VARIATIONS: dict[str, list[str]] = {
    "beach_lounge": [
        "Sensory nylon guitar 4-bar chillout phrase floating above warm rhodes chords",
        "Graceful Spanish guitar arpeggio echoing over gentle pool water caustics",
        "Warm downtempo keyboard motif pacing with distant evening ocean surf",
    ],
    "party_lounge": [
        "Catchy summer acoustic guitar hook over uplifting melodic house groove",
        "Joyful tropical pluck melody layered with bright rhythmic shakers",
    ],
    "desert": [
        "Gentle ascending 5-note Maqam Bayati motif with lingering breath pauses",
        "Tranquil descending Hijaz phrase resolving into warm desert drone",
    ],
    "swiss_alps": [
        "Luminous 4-note major pentatonic pastoral motif echoing across green meadows",
        "Gentle 6-note alpine lullaby phrasing pacing every 6 seconds",
    ],
    "zen": [
        "In-sen pentatonic Shakuhachi phrase opening into transcendent lotus stillness",
        "Subtle 3-note bamboo breath motif accompanied by soft bronze temple bell",
    ],
    "himalayas": [
        "Mesmerizing 5-note Bansuri phrase echoing over deep Tibetan singing bowls",
        "Ascending meditative flute melody with gentle handpan heartbeat cadence",
    ],
    "ocean": [
        "5-note handpan circular motif rolling with gentle shoreline waves",
        "Plucked kalimba melodic lullaby intertwined with warm rhodes electric piano",
    ],
    "forest": [
        "Serene 4-note cedar flute melody floating on morning canopy breeze",
        "Gentle harp arpeggios embracing a slow, hummable woodland flute theme",
    ],
    "hearth": [
        "Soft felted piano 4-note lullaby motif resting on warm cello harmonics",
        "Intimate descending piano arpeggio melting into crackling fireplace embers",
    ],
    "rain": [
        "4-bar crystal handpan melody descending like gentle falling rain drops",
        "Slow steady rain lullaby melody pacing with rhythmic droplet ripples",
    ],
    "waterfall": [
        "Sweeping Celtic harp ascending motif gliding over roaring cataract spray",
        "Restorative cello melodic phrase grounded in continuous brown noise stream",
    ],
}
