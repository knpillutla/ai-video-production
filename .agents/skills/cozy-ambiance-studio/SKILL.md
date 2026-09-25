---
name: cozy-ambiance-studio
description: Studio-grade 4K Cozy Ambiance, Biophilic Living Spaces, Fireplace Terraces, and ASMR Soundscapes producer with 2-perspective long-play architecture, binaural audio, and ultra-low cost ($1.80-$2.50).
---

# Cozy Ambiance Studio Skill

Specialized studio skill for directing and producing 4K broadcast-grade **Cozy Living Spaces, Oceanfront Fireplace Terraces, Rainy Cabins, and Biophilic Ambiance** videos. Built on and strictly adhering to the [ai-video-producer-core](file:///c:/neel-1/projects/content-generation/.agents/skills/ai-video-producer-core/SKILL.md) skill.

---

## 1. Directorial Aesthetics & Composition

1. **Architectural & Biophilic Pairing**:
   - Every scene must pair a **Warm Cozy Sanctuary Foreground/Midground** (stone fireplace, modern firepit, cedar patio, teak loungers, steaming tea/coffee) with an **Expansive Natural Window/Vista** (rolling turquoise ocean waves, forest rain on glass, blizzard outside alpine chalet).
2. **The 2-Perspective Long-Play Formula ($1.80 – $2.50 Cost)**:
   - **Perspective 1 (Wide Architectural Anchor, 0:00–0:30):** Full 24mm wide angle capturing the entire luxury room/terrace, glowing hearth, and rolling nature vista.
   - **Perspective 2 (Intimate Hearth & Ambiance, 0:30–1:00):** Closer 50mm portrait perspective focusing on the crackling fire embers, cozy seating, and steaming cup with nature in soft background bokeh.
3. **Motion Kinematics Strategy**:
   - **Alibaba Wan 2.1 ($0.080/s)** or **Kling v3 Pro ($0.280/s)**: Animate 10s–15s of fluid rolling ocean swells / rain drips + gentle fire flame flickering.
   - Single-pass FFmpeg 1.5s–2.0s cross-dissolve loops extending seamlessly to 60s, 3 mins, or long-form.
4. **Binaural Audio Design (48kHz Stereo, -14.0 LUFS)**:
   - Layer authentic wood crackles/embers with ocean surf or gentle rainfall. Commercially cleared via Suno v3.5 Pro or cached in `AudioVault`.

---

## 2. CLI Execution

```bash
# Generate 1-minute 4K Cozy Oceanfront Terrace Fireplace video
python -m src.studios.cozy_ambiance.cozy_agent --theme "Cozy Oceanfront Terrace Fireplace & Ocean Waves" --duration 60

# Generate Rainy Forest Cabin Ambiance
python -m src.studios.cozy_ambiance.cozy_agent --theme "Rainy Glass Cabin Fireplace & Misty Pine Woods" --duration 60
```
