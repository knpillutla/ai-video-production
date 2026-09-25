---
name: rain-retreat-studio
description: Studio-grade 4K Forest River Rainfall, Water Droplet Ripples, and ASMR Soundscapes producer with 2-perspective long-play architecture, binaural audio, and ultra-low cost ($1.80-$2.20).
---

# Rain Retreat Studio Skill

Specialized studio skill for directing and producing 4K broadcast-grade **Forest River Rainfall, Expanding Water Droplet Ripples, and River ASMR Soundscapes**. Built on and strictly adhering to the [ai-video-producer-core](file:///c:/neel-1/projects/content-generation/.agents/skills/ai-video-producer-core/SKILL.md) skill.

---

## 1. Directorial Aesthetics & Composition

1. **Natural Waterway & Rain Composition**:
   - Focus on ancient moss-covered granite boulders, deep lush pine canopy, and emerald forest streams under continuous steady rainfall.
   - 5500K crisp cool diffused daylight. Zero artificial flares.
2. **2-Perspective Long-Play Formula ($1.80 – $2.20 Cost)**:
   - **Perspective 1 (Wide Forest River, 0:00–0:30):** Panoramic 35mm view of emerald river with thousands of rain droplet ripples.
   - **Perspective 2 (Macro Water Ripples, 0:30–1:00):** Close-up 50mm portrait perspective of circular water ripples and dripping cedar leaves.
3. **Motion Kinematics Strategy**:
   - **Alibaba Wan 2.1 ($0.080/s)**: Continuous laminar river current + rain ripple physics (`water_fluid`).
   - Single-pass FFmpeg 1.5s cross-dissolve looping.
4. **Binaural Audio Design**:
   - Pristine natural rain on water surface + babbling brook white noise (48kHz stereo, -14.0 LUFS, zero synthetic hiss).

---

## 2. CLI Execution

```bash
# Generate 1-minute 4K Rain Retreat video
python -m src.studios.rain_retreat.rain_agent --theme "Lush Forest River in Gentle Rain" --duration 60
```
