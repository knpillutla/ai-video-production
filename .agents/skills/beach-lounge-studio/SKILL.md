---
name: beach-lounge-studio
description: Studio-grade 4K Luxury Beach Lounge, Cabanas & Coastal Terraces with 432Hz acoustic mastering and ultra-low cost ($1.80-$2.20).
---

# Beach Lounge Studio Skill

Specialized studio skill for directing and producing 4K broadcast-grade **Luxury Beach Lounges, Private Cabanas, Coastal Terraces, and Sunset Pergolas**. Built on and strictly adhering to the [ai-video-producer-core](file:///c:/neel-1/projects/content-generation/.agents/skills/ai-video-producer-core/SKILL.md) skill.

---

## 1. Directorial Aesthetics & Archetypes

1. **Inside-Out Luxury Cabana Framing**:
   - 16:9 panoramic compositions on locked tripod looking from inside a luxury beachfront cabana or teak terrace onto turquoise ocean surf.
   - Luxury elements: Billowing sheer white linen drapes, teak daybed with plush canvas cushions, weathered driftwood table, gentle sea breeze.
   - Purity Guard: Strictly zero crowds, zero plastic beach chairs, zero commercial watercraft.

2. **The 4 Archetypes**:
   - `beach_luxury_cabana_day` (5500K): Crisp natural daylight, sheer linen drapes billowing, gentle turquoise waves washing on white sand.
   - `beach_sunset_terrace` (2800K): Golden hour sunset over ocean horizon from private teak terrace with warm glowing lanterns.
   - `beach_twilight_pergola` (2200K): Deep violet dusk under open-air wooden pergola, soft amber candlelight, soothing tide lullaby.
   - `beach_starlit_hammock` (2000K): Starlit beachfront hammock between swaying coconut palms, bioluminescent waves in dark turquoise surf.

3. **Acoustic Mastering & Kinetics**:
   - Binaural rhythmic ocean wave wash, palm frond rustle, warm nylon acoustic guitar, 432Hz ambient pads (-21 LUFS).
   - Furniture and architecture remain rock-solid; animate only gentle linen drapery flutter, palm sway, and rolling wave wash.

---

## 2. CLI Execution

```bash
python -m src.studios.beach_lounge_studio.beach_lounge_director --genre relax/beach_lounge --archetype beach_luxury_cabana_day --duration 60
```
