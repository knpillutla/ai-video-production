---
name: blizzard-studio
description: Studio-grade 4K Alpine Blizzard, Cozy Cabin Windows & Winter Snowstorms with ASMR acoustic mastering and ultra-low cost ($1.80-$2.20).
---

# Blizzard Studio Skill

Specialized studio skill for directing and producing 4K broadcast-grade **Alpine Blizzards, Frosted Cabin Windows, Mountain Hearths, and Winter ASMR Wallpapers**. Built on and strictly adhering to the [ai-video-producer-core](file:///c:/neel-1/projects/content-generation/.agents/skills/ai-video-producer-core/SKILL.md) skill.

---

## 1. Directorial Aesthetics & Archetypes

1. **Inside-Out Warmth vs. Cold Framing**:
   - 16:9 panoramic compositions on locked tripod contrasting warm, cozy timber cabin interiors with ferocious howling winter blizzards outside panoramic glass.
   - Elements: Steaming ceramic cocoa mug, frosted glass borders, glowing rustic stone hearth, thick wool blankets.
   - Purity Guard: Strictly zero modern snowmobiles, zero ski lift towers, zero industrial equipment.

2. **The 4 Archetypes**:
   - `blizzard_cozy_cabin_window` (2700K int / 6500K ext): Warm timber cabin interior, panoramic window overlooking raging whiteout blizzard.
   - `blizzard_frosted_pine_forest` (6500K): Swirling snowstorm sweeping through dense frosted evergreen pine forest, deep snowdrifts.
   - `blizzard_alpine_hearth_shelter` (2200K int): Glowing stone hearth fire inside rustic mountain refuge, blizzard howling outside.
   - `blizzard_twilight_snowfall` (4500K): Peaceful heavy snowflakes drifting gently down at deep blue twilight on snowy cabin roof.

3. **Acoustic Mastering & Kinetics**:
   - Howling sub-zero mountain wind, gentle windowpane tickle, crackling hearth embers, deep sub-bass wind drones (-21 LUFS).
   - Interior cabin architecture remains rigid; animate swirling blizzard snowflakes, window frost caustics, and hearth embers.

---

## 2. CLI Execution

```bash
python -m src.studios.blizzard_studio.blizzard_director --genre relax/blizzard --archetype blizzard_cozy_cabin_window --duration 60
```
