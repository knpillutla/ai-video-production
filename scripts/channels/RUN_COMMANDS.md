# AI Video Production Studio: Multi-Channel CLI & Stretch Cheatsheet

This cheatsheet contains all production and stretching commands for the automated YouTube channels, covering the 3-stage Human-in-the-Loop review workflow, Kling v3 4K Native diffusion, custom mood prompting (`--prompt "..."`), `--shots 1`, native video audio (`--no-bgm`), and ultra-fast long-play broadcast stretching.

---

## 📋 Channel Overview & Defaults

| Channel Name | Focus / Archetype | Master Set | Long-Play Target | Stretch Mode | Default Motion Model |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1. Earth Serenade** | 4K Scenic Nature Sanctuaries (`swiss_alps`, `mountains`, `ocean_world`) | 60s – 120s | 1.0 – 3.0 Hours | Direct Copy (~10s) | Kling v3 4K Native (`kling_v3`) |
| **2. Silent Hearth** | Deep Sleep & Insomnia (`blizzard`, `camp_fire`, `rain`) | 90s (3 shots min) | 8.0 Hours | Direct Copy (or `--sleep` for 2h fade) | Kling v3 4K Native (`kling_v3`) |
| **3. Rain & Quill** | Study, Focus & Ambience (`beach_house`, `cafe`, `rain`) | 90s (3 shots) | 3.0 Hours | Direct Copy (~10s) | Kling v3 4K Native (`kling_v3`) |

---

## 🪵 Natural Audio Living Wallpapers (`--shots 1 --no-bgm --prompt "..."`)

Preserves the **100% natural, organic audio synthesized directly in the Kling video** (such as real crackling campfire logs, gentle rainfall, or wind) without overlaying external Suno music ($2.10 total API spend):

```powershell
# Example 1: Natural Crackling Fireplace (No BGM, 100% Native Video Audio)
python scripts/channels/deep_sleep_sanctuary_pipeline.py --primary blizzard --secondary camp_fire --shots 1 --no-bgm --prompt "Rustic stone fireplace with burning oak logs, crackling flames and glowing orange charcoal embers" --photos-only
python scripts/channels/deep_sleep_sanctuary_pipeline.py --id <episode_id> --shots 1 --no-bgm

# Example 2: Natural Rain on Cabin Window (No BGM)
python scripts/channels/study_focus_cafe_pipeline.py --primary beach_house --secondary rain --shots 1 --no-bgm --prompt "Cozy library window with gentle raindrops trickling down glass, warm glowing reading lamp" --photos-only
python scripts/channels/study_focus_cafe_pipeline.py --id <episode_id> --shots 1 --no-bgm

# Optional: Preserve Uncompressed High-Bitrate Size (--keep-uncompressed)
# By default, all stretch broadcasts encode with optimized CRF 22 (~14-18 GB for 3 hours, 50% faster upload).
# To force uncompressed CRF 16 high-bitrate (~28.5 GB), pass --keep-uncompressed:
python scripts/channels/nature_sanctuary_pipeline.py --id <episode_id> --auto-stretch --hours 3.0 --keep-uncompressed
```

---

## 1. Complete 3-Stage Human-in-the-Loop Workflow

### A. Channel 1: Earth Serenade (@EarthSerenade4K)

```powershell
# Stage 1: Generate 4K Keyframe Photos only ($0.20):
python scripts/channels/nature_sanctuary_pipeline.py --archetype swiss_alps --photos-only
# Output: Episode ID: ep_swiss_alps_1790365543

# Stage 2: After reviewing photos, synthesize Kling v3 4K Motion & Binaural Master:
python scripts/channels/nature_sanctuary_pipeline.py --id ep_swiss_alps_1790365543
# Output: 60s/120s master_4k_ambient.mp4 + review notification

# Stage 3: Instant 3-Hour Long-Play Stretch (~10 seconds, $0.00 spend):
python scripts/channels/nature_sanctuary_pipeline.py --id ep_swiss_alps_1790365543 --auto-stretch --hours 3.0
```

---

### B. Channel 2: Silent Hearth (@SilentHearthSleep)

```powershell
# Stage 1: Generate 3 Keyframe Photos only ($0.15):
python scripts/channels/deep_sleep_sanctuary_pipeline.py --primary blizzard --secondary camp_fire --photos-only
# Output: Episode ID: ep_blizzard_1790363895

# Stage 2: After reviewing photos, synthesize Kling v3 4K Motion & 432Hz Delta Audio (3 shots min):
python scripts/channels/deep_sleep_sanctuary_pipeline.py --id ep_blizzard_1790363895
# Output: 90s master_4k_ambient.mp4 + review notification

# Stage 3 Option 1: Ultra-Fast Direct Copy Stretch to 8 Hours (~10 seconds, video loops entire 8h):
python scripts/channels/deep_sleep_sanctuary_pipeline.py --id ep_blizzard_1790363895 --auto-stretch --hours 8.0

# Stage 3 Option 2: Circadian Sleep Stretch with --sleep (Fades to OLED Pure Black after 2.0h):
python scripts/channels/deep_sleep_sanctuary_pipeline.py --id ep_blizzard_1790363895 --auto-stretch --hours 8.0 --sleep
```

---

### C. Channel 3: Rain & Quill (@RainAndQuill)

```powershell
# Stage 1: Generate 3 Focus Keyframe Photos only:
python scripts/channels/study_focus_cafe_pipeline.py --primary beach_house --secondary rain --photos-only
# Output: Episode ID: ep_beach_house_1790365123

# Stage 2: Synthesize Kling v3 4K Motion & Felt Piano Master:
python scripts/channels/study_focus_cafe_pipeline.py --id ep_beach_house_1790365123
# Output: 90s master_4k_ambient.mp4 + review notification

# Stage 3: Instant 3-Hour Long-Play Stretch (~10 seconds):
python scripts/channels/study_focus_cafe_pipeline.py --id ep_beach_house_1790365123 --auto-stretch --hours 3.0
```

---

## 2. Standalone Long-Play Stretcher Commands

To stretch any pre-rendered `master_4k_ambient.mp4` directly without re-running pipeline scripts:

```powershell
# Fast Direct-Copy Stretch to 3 Hours (~10 seconds):
python src/services/long_play_stretcher.py --input storage/channels/earth_serenade/ep_swiss_alps_1790365543/master_4k_ambient.mp4 --hours 3.0

# Fast Direct-Copy Stretch to 8 Hours (~10 seconds):
python src/services/long_play_stretcher.py --input storage/channels/silent_hearth/ep_blizzard_1790363895/master_4k_ambient.mp4 --hours 8.0

# Sleep Mode with 2-Hour Circadian Fade-to-Black:
python src/services/long_play_stretcher.py --input storage/channels/silent_hearth/ep_blizzard_1790363895/master_4k_ambient.mp4 --hours 8.0 --fade-black 2.0
```

---

## 3. Multi-Channel Network Manager (Run All in Parallel)

```powershell
python scripts/channels/channel_network_manager.py --channel all
```

---

## 4. Channel-Specific YouTube Upload Commands

Each channel uploads directly to its dedicated YouTube Brand Account using its isolated token in `config/tokens/` and automatically publishes **both the Music Broadcast and the Pure Nature ASMR Broadcast** with tailored titles, tags, and synthetic media disclosures:

```powershell
# Channel 1: Earth Serenade (@EarthSerenade4K)
python scripts/channels/upload_earth_serenade.py --id ep_swiss_alps_1790365543 --privacy unlisted
# (Add --dry-run to simulate upload payload first)

# Channel 2: Silent Hearth (@SilentHearthSleep)
python scripts/channels/upload_silent_hearth.py --id ep_blizzard_1790363895 --privacy unlisted

# Channel 3: Rain & Quill (@RainAndQuill)
python scripts/channels/upload_rain_and_quill.py --id ep_beach_house_1790365123 --privacy unlisted
```

---

## 5. 🎙️ Blue-Chip Documentary Studio CLI

Produces 4K 24fps cinematic documentaries with authoritative natural history voiceover (Western Male default, `--female-voice`, multilingual `--lang te/hi`, and fatigue-free ducking).

```powershell
# Example 1: Wildlife Documentary (Stage 1 Photos Review -> Stage 2 Master):
python scripts/channels/documentary_pipeline.py --genre wildlife --photos-only
python scripts/channels/documentary_pipeline.py --id <episode_id>

# Example 2: Ancient Structures with Female Narrator:
python scripts/channels/documentary_pipeline.py --genre ancient_structures --female-voice --prompt "Giza Pyramids and astronomical alignments"

# Example 3: Ocean Documentary with Subtle Background Orchestral Score (-26dB):
python scripts/channels/documentary_pipeline.py --genre ocean --bgm --prompt "Bioluminescent coral trenches of the deep Pacific"

# Example 4: Mountains in Telugu / Hindi:
python scripts/channels/documentary_pipeline.py --genre mountains --lang te
```


