"""National Musical DNA Acoustic Profiles for Educational & Country Documentaries.

Maps nations and geographic cultural identities to authentic traditional and symphonic
instrumentation, modal tunings, resting tempos, and rich directorial Suno v3.5 Pro prompts.
Delivers genuine BBC Natural History / National Geographic / Ken Burns sonic immersion.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple
from src.services.cultural_acoustic_profiles import CulturalAcousticProfile


NATIONAL_ACOUSTIC_PROFILES: Dict[str, Dict[str, str]] = {
    "france": {
        "culture_key": "national_france",
        "lead_instrument": "Noble French Horn & Romantic Parisian Musette Accordion Harmonics",
        "secondary_textures": "Concert harp arpeggios, lyrical cello solo, gentle oboe, lush Debussy impressionist strings",
        "scale_and_tuning": "432Hz French Symphonic Impressionism & Warm Major Modal Resonance",
        "rhythm_and_tempo": "54 BPM noble, measured cinematic tempo",
        "emotional_purpose": "Cultural prestige, poetic elegance, architectural grandeur, evocative historical lore",
        "suno_tags": "cinematic documentary, french orchestral score, french horn, accordion musette, cello solo, harp, debussy aesthetic, lush strings, 48khz, zero vocals, -21 LUFS",
        "suno_prompt": (
            "[Instrumental French National Symphonic Documentary Score]\n"
            "[Tempo: 54 BPM - Noble Measured Pacing]\n"
            "[Tuning: 432Hz Symphonic Impressionist Bed]\n"
            "[Lead Melody: Noble French Horn Fanfares & Romantic Parisian Musette Accordion Harmonics]\n"
            "[Accompaniment: Sweeping Debussy-Style Impressionist Strings & Flowing Concert Harp]\n"
            "[Texture: Lyrical Acoustic Cello Solo & Subtle Parisian Cathedral Carillon Chimes]\n"
            "[Atmosphere: Grand Architectural Majesty, French Heritage Prestige, BBC Natural History Aesthetic]\n"
            "[Emotion: Poetic Wonder, Historical Grandeur, Educational Immersion]\n"
            "[Outro: Soft Lingering French Horn & Harp Resonance]"
        ),
    },
    "spain": {
        "culture_key": "national_spain",
        "lead_instrument": "Classical Spanish Nylon Guitar & Andalusian Violin",
        "secondary_textures": "Warm cello drone, subtle wooden cajón pulse, castanet whispers, soaring Iberian orchestral strings",
        "scale_and_tuning": "432Hz Phrygian Andalusian Modal Harmony",
        "rhythm_and_tempo": "56 BPM proud Mediterranean cadence",
        "emotional_purpose": "Passionate pride, sun-drenched coastlines, historic Moorish architecture, epic Iberian legacy",
        "suno_tags": "cinematic documentary, spanish classical nylon guitar, andalusian strings, warm cello, subtle cajon rhythm, iberian orchestral, 48khz, zero vocals, -21 LUFS",
        "suno_prompt": (
            "[Instrumental Spanish Classical & Andalusian Heritage Score]\n"
            "[Tempo: 56 BPM - Proud Iberian Cadence]\n"
            "[Tuning: 432Hz Phrygian Andalusian Modal Harmony]\n"
            "[Lead Melody: Virtuosic Classical Spanish Nylon Guitar Arpeggios & Passionate Violin]\n"
            "[Accompaniment: Resonant Cello Drone & Lyrical Orchestral Viola Harmonics]\n"
            "[Texture: Subtle Wooden Cajón Heartbeat & Distant Castanet Echoes, Zero Drums]\n"
            "[Atmosphere: Sun-Drenched Alhambra Terraces, Historic Madrid Plazas, Mediterranean Scale]\n"
            "[Emotion: Noble Pride, Timeless Passion, Cinematic Grandeur]\n"
            "[Outro: Resonant Spanish Nylon Guitar Dissolve]"
        ),
    },
    "italy": {
        "culture_key": "national_italy",
        "lead_instrument": "Expressive Plucked Mandolin & Operatic Solo Violin",
        "secondary_textures": "Warm chamber cello, lyrical oboe, distant Venetian cathedral carillon bells, lush Renaissance strings",
        "scale_and_tuning": "432Hz Italian Renaissance & Vivaldian Harmonic Resonance",
        "rhythm_and_tempo": "54 BPM lyrical Italian cantabile tempo",
        "emotional_purpose": "Timeless Renaissance grandeur, Italian romance, Venetian reflection, ancient Roman scale",
        "suno_tags": "cinematic documentary, italian orchestral score, plucked mandolin, operatic solo violin, warm cello, cathedral bells, cinematic drama, 48khz, zero vocals, -21 LUFS",
        "suno_prompt": (
            "[Instrumental Italian Renaissance & Cinema Symphonic Score]\n"
            "[Tempo: 54 BPM - Lyrical Cantabile Pacing]\n"
            "[Tuning: 432Hz Italian Renaissance Resonance]\n"
            "[Lead Melody: Expressive Plucked Mandolin & Operatic Solo Violin Phrasing]\n"
            "[Accompaniment: Warm Chamber Acoustic Strings & Lyrical Cello Solo]\n"
            "[Texture: Distant Venetian Carillon Bells & Gentle Mediterranean Harbor Ambience]\n"
            "[Atmosphere: Grand Italian Heritage, Florence Renaissance Romance, Timeless Cinematic Majesty]\n"
            "[Emotion: Lyrical Beauty, Ancient Splendor, Deep Educational Wonder]\n"
            "[Outro: Lingering Mandolin & Cathedral Bell Echo]"
        ),
    },
    "germany": {
        "culture_key": "national_germany",
        "lead_instrument": "Majestic Symphonic Brass Fanfare & French Horn Ensemble",
        "secondary_textures": "Sweeping romantic orchestral strings, acoustic zither harmonics, gentle woodwinds, grand cathedral organ swell",
        "scale_and_tuning": "432Hz Romantic Germanic Symphonic Tuning (Beethoven / Brahms)",
        "rhythm_and_tempo": "52 BPM stately, authoritative orchestral pulse",
        "emotional_purpose": "Architectural majesty, deep historic heritage, engineering precision, monumental grandeur",
        "suno_tags": "cinematic documentary, germanic symphonic score, french horn fanfare, sweeping orchestral strings, acoustic zither, cathedral brass, 48khz, zero vocals, -21 LUFS",
        "suno_prompt": (
            "[Instrumental Germanic Symphonic Documentary Score]\n"
            "[Tempo: 52 BPM - Stately Orchestral Pulse]\n"
            "[Tuning: 432Hz Romantic Germanic Symphonic Resonance]\n"
            "[Lead Melody: Majestic French Horn Fanfare & Lyrical Woodwind Motifs]\n"
            "[Accompaniment: Sweeping Romantic Orchestral Strings & Resonant Double Bass Drone]\n"
            "[Texture: Acoustic Bavarian Zither Harmonics & Distant Cathedral Bell Foley]\n"
            "[Atmosphere: Black Forest Mist, Rhine Valley Castles, Monumental Historic Depth]\n"
            "[Emotion: Authoritative Grandeur, Timeless Heritage, Majestic Wonder]\n"
            "[Outro: Noble French Horn & String Fade]"
        ),
    },
    "uk_celtic": {
        "culture_key": "national_celtic",
        "lead_instrument": "Highland Uilleann Pipes, Tin Whistle Air & Celtic Acoustic Harp",
        "secondary_textures": "Gentle bodhrán drum pulse, soaring acoustic fiddle, warm cello drone, misty heather breeze",
        "scale_and_tuning": "432Hz Celtic Modal Air & Dorian Resonance",
        "rhythm_and_tempo": "52 BPM rolling green highland cadence",
        "emotional_purpose": "Ancient rolling highlands, emerald cliffs, misty Atlantic lore, heartfelt poetic nostalgia",
        "suno_tags": "cinematic documentary, celtic score, uilleann pipes, tin whistle, celtic harp, bodhran pulse, soaring highland strings, 48khz, zero vocals, -21 LUFS",
        "suno_prompt": (
            "[Instrumental Highland Celtic Documentary Score]\n"
            "[Tempo: 52 BPM - Rolling Highland Cadence]\n"
            "[Tuning: 432Hz Celtic Modal Harmonic Air]\n"
            "[Lead Melody: Hauntingly Beautiful Tin Whistle & Highland Uilleann Pipes Air]\n"
            "[Accompaniment: Flowing Celtic Acoustic Harp Arpeggios & Deep Cello Drone]\n"
            "[Texture: Soft Bodhrán Drum Heartbeat & Soaring Highland Fiddle Harmonics]\n"
            "[Atmosphere: Mist Over Emerald Cliffs, Ancient Hebrides Coastline, Royal Castles]\n"
            "[Emotion: Heartfelt Nostalgia, Poetic Lore, Monumental Ancient Beauty]\n"
            "[Outro: Whispering Tin Whistle Dissolve]"
        ),
    },
    "greece": {
        "culture_key": "national_greece",
        "lead_instrument": "Plucked Bouzouki & Expressive Santur",
        "secondary_textures": "Warm Mediterranean nylon guitar, Aegean lyre, ancient wooden shepherd flute, rolling sea swells",
        "scale_and_tuning": "432Hz Ancient Aegean Modal Dromoi Tuning",
        "rhythm_and_tempo": "54 BPM sunlit Aegean coastal rhythm",
        "emotional_purpose": "Sunlit antiquity, Aegean mythology, Homeric seas, philosophy and democratic heritage",
        "suno_tags": "cinematic documentary, greek mediterranean score, bouzouki, santur, acoustic nylon guitar, warm strings, ancient aegean breeze, 48khz, zero vocals, -21 LUFS",
        "suno_prompt": (
            "[Instrumental Aegean Hellenic Documentary Score]\n"
            "[Tempo: 54 BPM - Sunlit Aegean Coastal Pacing]\n"
            "[Tuning: 432Hz Ancient Aegean Modal Harmony]\n"
            "[Lead Melody: Plucked Lyrical Bouzouki & Shimmering Santur Solos]\n"
            "[Accompaniment: Warm Mediterranean Nylon Guitar & Gentle Chamber Strings]\n"
            "[Texture: Breathy Shepherd Wooden Flute & Subtle Aegean Wave Swell Foley]\n"
            "[Atmosphere: Sunlit Acropolis Marble, Cobalt Blue Aegean Sea, Ancient Olive Groves]\n"
            "[Emotion: Timeless Wisdom, Homeric Wonder, Mythic Immersion]\n"
            "[Outro: Lingering Santur Tremolo Fade]"
        ),
    },
    "nordic": {
        "culture_key": "national_nordic",
        "lead_instrument": "Traditional Hardanger Fiddle & Nyckelharpa",
        "secondary_textures": "Crystal glass harp, breathy Nordic wooden flute, deep bowed cello drone, arctic wind foley",
        "scale_and_tuning": "432Hz Lydian Nordic Modal Resonance",
        "rhythm_and_tempo": "48 BPM deep glacial breathing tempo",
        "emotional_purpose": "Majestic fjords, aurora borealis, monumental glacial mystery, Nordic cinematic scale",
        "suno_tags": "cinematic documentary, nordic cinematic score, hardanger fiddle, nyckelharpa, crystal glass harp, deep cello drone, fjord atmosphere, 48khz, zero vocals, -21 LUFS",
        "suno_prompt": (
            "[Instrumental Nordic Glacial Documentary Score]\n"
            "[Tempo: 48 BPM - Glacial Breathing Cadence]\n"
            "[Tuning: 432Hz Lydian Nordic Modal Tuning]\n"
            "[Lead Melody: Soaring Lyrical Hardanger Fiddle & Resonant Nyckelharpa Themes]\n"
            "[Accompaniment: Deep Bowed Cello Harmonics & Breathy Nordic Wooden Flute]\n"
            "[Texture: Ethereal Crystal Glass Harp & Subtle Arctic Glacial Wind Whisper]\n"
            "[Atmosphere: Monumental Norwegian Fjords, Midnight Sun, Pristine Alpine Tundra]\n"
            "[Emotion: Breathtaking Solitude, Timeless Serenity, Epic Natural Scale]\n"
            "[Outro: Soft Arctic Wind & Fiddle Dissolve]"
        ),
    },
    "slavic": {
        "culture_key": "national_slavic",
        "lead_instrument": "Lyrical Chopin-esque Acoustic Piano & Melancholic Solo Violin",
        "secondary_textures": "Warm resonant cello, sweeping Slavic orchestral strings, subtle hammered dulcimer (cimbalom)",
        "scale_and_tuning": "432Hz Slavic Romantic Minor Harmony",
        "rhythm_and_tempo": "50 BPM poetic, reflective orchestral cadence",
        "emotional_purpose": "Poetic resilience, deep historical memory, romantic melancholy, grand cultural legacy",
        "suno_tags": "cinematic documentary, slavic orchestral score, chopinesque piano, melancholic solo violin, warm cello, sweeping strings, 48khz, zero vocals, -21 LUFS",
        "suno_prompt": (
            "[Instrumental Slavic Historical Documentary Score]\n"
            "[Tempo: 50 BPM - Poetic Reflective Cadence]\n"
            "[Tuning: 432Hz Slavic Romantic Minor Harmony]\n"
            "[Lead Melody: Expressive Chopin-Style Lyrical Piano & Melancholic Solo Violin]\n"
            "[Accompaniment: Sweeping Slavic Orchestral Strings & Resonant Acoustic Cello]\n"
            "[Texture: Delicate Hammered Dulcimer Shimmer & Soft Cathedral Ambience]\n"
            "[Atmosphere: Historic Central European Capitals, Ancient Castles, Forest Lore]\n"
            "[Emotion: Poetic Resilience, Soulful Beauty, Deep Cultural Memory]\n"
            "[Outro: Lingering Piano Chord & Violin Dissolve]"
        ),
    },
    "japan": {
        "culture_key": "national_japan",
        "lead_instrument": "Breathy Japanese Shakuhachi Bamboo Flute & Plucked Koto",
        "secondary_textures": "Resonant Biwa plucks, bronze temple singing bowls, soft taiko heartbeat pulse, bamboo chimes",
        "scale_and_tuning": "432Hz In-sen & Yo Traditional Pentatonic Scales",
        "rhythm_and_tempo": "48 BPM deep zen meditative cadence",
        "emotional_purpose": "Ancient imperial history, zen gardens, cherry blossoms, samurai honor, tranquil contemplation",
        "suno_tags": "cinematic documentary, traditional japanese orchestral, shakuhachi flute, plucked koto, temple bells, cinematic strings, 48khz, zero vocals, -21 LUFS",
        "suno_prompt": (
            "[Instrumental Japanese Heritage Documentary Score]\n"
            "[Tempo: 48 BPM - Meditative Imperial Cadence]\n"
            "[Tuning: 432Hz In-sen & Yo Traditional Pentatonic Scales]\n"
            "[Lead Melody: Breathy Shakuhachi Bamboo Flute Solos & Delicate Plucked Koto Harp]\n"
            "[Accompaniment: Resonant Biwa Plucks & Subtle Taiko Heartbeat Pulse]\n"
            "[Texture: Bronze Temple Singing Bowls & Delicate Bamboo Wind Chime Foley]\n"
            "[Atmosphere: Kyoto Ancient Shrines, Cherry Blossom Canopies, Imperial Tranquility]\n"
            "[Emotion: Sacred Reverence, Zen Clarity, Poetic Timelessness]\n"
            "[Outro: Reverberating Temple Bell Dissolve]"
        ),
    },
    "global_epic": {
        "culture_key": "national_global_epic",
        "lead_instrument": "BBC Earth Grand Symphonic French Horn & Lyrical Cello Solo",
        "secondary_textures": "Sweeping cinematic strings, concert harp arpeggios, noble woodwinds, majestic orchestral brass",
        "scale_and_tuning": "432Hz Natural History Grand Symphonic Harmony",
        "rhythm_and_tempo": "54 BPM sweeping cinematic cadence",
        "emotional_purpose": "Authoritative educational documentary grandeur, global scale, monumental natural history",
        "suno_tags": "cinematic documentary, bbc earth style orchestral score, sweeping strings, french horn fanfare, majestic cello, orchestral brass, 48khz, zero vocals, -21 LUFS",
        "suno_prompt": (
            "[Instrumental BBC Earth Style Symphonic Documentary Score]\n"
            "[Tempo: 54 BPM - Sweeping Cinematic Cadence]\n"
            "[Tuning: 432Hz Natural History Symphonic Harmony]\n"
            "[Lead Melody: Majestic French Horn Fanfare & Lyrical Solo Cello Themes]\n"
            "[Accompaniment: Sweeping Cinematic String Ensemble & Concert Harp Arpeggios]\n"
            "[Texture: Noble Woodwinds (Oboe/Flute) & Subtle Timpani Swells, Zero Modern Distortion]\n"
            "[Atmosphere: Monumental Earth Landscapes, Ancient Civilization, BBC Natural History Scale]\n"
            "[Emotion: Authoritative Wonder, Monumental Grandeur, Deep Educational Immersion]\n"
            "[Outro: Grand Symphonic Brass & String Dissolve]"
        ),
    },
}

COUNTRY_KEY_MAPPINGS: List[Tuple[List[str], str]] = [
    (["france", "french", "paris", "versailles", "normandy", "provence", "marseille", "lyon", "bordeaux", "cote d'azur"], "france"),
    (["spain", "spanish", "madrid", "barcelona", "andalusia", "seville", "valencia", "granada", "catalonia", "toledo"], "spain"),
    (["italy", "italian", "rome", "florence", "venice", "milan", "naples", "tuscany", "amalfi", "sicily", "pompeii"], "italy"),
    (["germany", "german", "berlin", "munich", "bavaria", "rhine", "austria", "vienna", "salzburg", "innsbruck"], "germany"),
    (["scotland", "scottish", "edinburgh", "highlands", "ireland", "irish", "dublin", "britain", "uk", "london", "wales"], "uk_celtic"),
    (["greece", "greek", "athens", "santorini", "mykonos", "crete", "aegean", "olympia", "rhodes", "corfu"], "greece"),
    (["norway", "norwegian", "oslo", "fjord", "iceland", "reykjavik", "sweden", "stockholm", "nordic", "finland", "helsinki"], "nordic"),
    (["poland", "polish", "warsaw", "krakow", "prague", "czech", "hungary", "budapest", "slavic"], "slavic"),
    (["japan", "japanese", "tokyo", "kyoto", "osaka", "fuji"], "japan"),
]


def resolve_national_acoustic_profile(text: str) -> Optional[CulturalAcousticProfile]:
    """Inspect topic, title, prompt, or archetype to match National Musical DNA."""
    cleaned = (text or "").lower()
    for keywords, profile_key in COUNTRY_KEY_MAPPINGS:
        if any(k in cleaned for k in keywords):
            raw = NATIONAL_ACOUSTIC_PROFILES[profile_key]
            return CulturalAcousticProfile(
                culture_key=raw["culture_key"],
                lead_instrument=raw["lead_instrument"],
                secondary_textures=raw["secondary_textures"],
                scale_and_tuning=raw["scale_and_tuning"],
                rhythm_and_tempo=raw["rhythm_and_tempo"],
                emotional_purpose=raw["emotional_purpose"],
                suno_tags=raw["suno_tags"],
                suno_prompt=raw["suno_prompt"],
            )

    # Check if this is a general country dossier or nations documentary
    normalized = cleaned.replace("_", " ")
    generic_keywords = [
        "country dossier", "country profile", "geo nations", "top 10 cities",
        "top places to visit", "bucket list", "nations", "documentary", "country"
    ]
    if any(k in normalized or k in cleaned for k in generic_keywords):
        raw = NATIONAL_ACOUSTIC_PROFILES["global_epic"]
        return CulturalAcousticProfile(
            culture_key=raw["culture_key"],
            lead_instrument=raw["lead_instrument"],
            secondary_textures=raw["secondary_textures"],
            scale_and_tuning=raw["scale_and_tuning"],
            rhythm_and_tempo=raw["rhythm_and_tempo"],
            emotional_purpose=raw["emotional_purpose"],
            suno_tags=raw["suno_tags"],
            suno_prompt=raw["suno_prompt"],
        )

    return None
