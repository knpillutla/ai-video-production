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

---

## 6. 🎵 Music Video Studio & Telugu Rhythms Channel (`produce_music_video.py`)

Produces broadcast-grade 4K Telugu musical releases, soulful pastoral melodies, romantic duets, and mass folk dances with kinetic subtitles, multi-scene keyframes, and Suno master audio.

```powershell
# Example 1: Lyrical Pastoral Melody (Inspired by "Aakulo Aakunai" from Meghasandesam)
# Soft bansuri flute, resonant sitar, gentle tabla, 35mm misty Nilgiri forest photography
python scripts/produce_music_video.py `
  --title "Aakulo Aakunai" `
  --language te `
  --duration 280s `
  --solo-female `
  --genre "soulful_acoustic" `
  --similar-to "Aakulo Aakunai (Meghasandesam, Ramesh Naidu)" `
  --style "poetic bhavageetham melody, raga mohanam, acoustic bansuri flute, resonant sitar, gentle tabla, tanpura drone, lush vintage strings, contemplative, 72 bpm" `
  --theme "Bhavageetham poetic communion with nature, blending into leaves, flowers, and gentle forest rain as a free soul in love" `
  --art-style "Classic 35mm film photograph, soft natural overcast daylight, misty Nilgiri pine forest, emerald canopy, gentle cascading mountain brook, dewdrops on leaves, poetic painterly composition, muted organic film grade" `
  --costume "Traditional South Indian handloom saree in forest emerald green and turmeric gold border, jasmine flowers in long braided hair, graceful modest classical look" `
  --vfx `
  --images 12 `
  --network telugu_rhythms `
  --live

# Example 2: Romantic Melodic Duet (Lead Pair Chemistry)
python scripts/produce_music_video.py `
  --title "Madhura Bhavame" `
  --language te `
  --duration 240s `
  --duet `
  --genre "music/duet_romance" `
  --theme "Soulful romantic rain melody by a lakeside gazebo" `
  --images 12 `
  --network telugu_rhythms `
  --live

# Example 3: High-Energy Mass Folk Dance (Teenmaar & Dappu Beats)
python scripts/produce_music_video.py `
  --title "Dappu Debba" `
  --language te `
  --duration 180s `
  --mass `
  --solo-male `
  --theme "Festive village Jathara celebration with thumping dappu drums" `
  --images 12 `
  --network telugu_rhythms `
  --live
```

---

## 7. 🎭 Character LoRA 3D Turnaround & Virtual Artists (Lara Aredo Style)

Locks 100% facial bone structure, eyes, and skin texture across multiple episodes and outfits using a custom-trained FLUX portrait LoRA ($1.80 one-time, ~$0.035/image inference thereafter).

```powershell
# Step 1: Pre-train a Character LoRA using 3D Head Turnaround
# Automatically generates a hero portrait, 3D turnaround video, extracts 15 decoupled angle crops, and trains LoRA
python scripts/train_character_lora.py `
  --name "Kavitha" `
  --network "telugu_rhythms" `
  --gender "female" `
  --language "te" `
  --live

# Step 2: Use the LoRA in Production (--loras)
# Pass --loras to produce_music_video.py. If the LoRA exists in the network vault, it is loaded for $0.00.
# If missing, it will automatically call the 3D turnaround synthesizer, train the LoRA, and use it!
python scripts/produce_music_video.py `
  --title "Aakulo Aakunai" `
  --language te `
  --duration 280s `
  --solo-female `
  --character "Kavitha" `
  --loras `
  --network telugu_rhythms `
  --live
```

---

## 8. 🎙️ Virtual Artist Music Videos (Lara Aredo Style)

Gemini autonomously directs setting-matched scenic backdrops or live concert stages, elegant modest context-matched outfits ([Rule 12](file:///c:/neel-1/projects/content-generation/AGENTS.md)), signature instrument handling, and natural singer performance kinematics (subtle rhythm sway, hair in breeze, guitar strumming, expressive eyes, and LatentSync lip-sync):

### A. Solo Male Live Concert (Using Existing `kalyan` LoRA)
Performs on a live concert arena stage with acoustic guitar, overhead lighting trusses, volumetric spot beams, backing orchestra, multi-camera orchestra cutaways, and beat-synchronized vocal lip-sync:

```powershell
python scripts/produce_music_video.py `
  --title "Kalyan Live Unplugged" `
  --language te `
  --duration 90s `
  --chars kalyan `
  --solo-male `
  --loras `
  --network telugu_rhythms `
  --virtual-artist `
  --artist-mode concert `
  --instrument acoustic_guitar `
  --orchestra `
  --continuous-motion `
  --live
```

### B. Solo Female Live Concert (Stand Mic, Arena Rigging & Orchestra with LoRA)
Live concert performance with lead vocalist at centerstage with a vintage stand microphone, backing musicians in optical bokeh, and orchestra cutaways:

```powershell
python scripts/produce_music_video.py `
  --title "Echoes in the Spotlight" `
  --language en `
  --duration 90s `
  --chars Kavitha `
  --solo-female `
  --loras `
  --network telugu_rhythms `
  --virtual-artist `
  --artist-mode concert `
  --instrument mic `
  --orchestra `
  --continuous-motion `
  --live
```

### C. Grand Piano Acoustic Concert (Intimate Stage with LoRA)
Intimate live performance seated at a grand acoustic piano with strings accompaniment:

```powershell
python scripts/produce_music_video.py `
  --title "Moonlight Sonata Live" `
  --language en `
  --duration 90s `
  --chars kalyan `
  --solo-male `
  --loras `
  --network telugu_rhythms `
  --virtual-artist `
  --artist-mode concert `
  --instrument piano `
  --orchestra `
  --continuous-motion `
  --live
```

### D. Scenic Open-Air Acoustic (Lush Meadows / Mountain Peaks / Landmarks with LoRA)
Natural scenic performance in undulating wildflower meadows overlooking alpine peaks:

```powershell
python scripts/produce_music_video.py `
  --title "Whispers of the Meadow" `
  --language en `
  --duration 60s `
  --chars Kavitha `
  --solo-female `
  --loras `
  --network telugu_rhythms `
  --virtual-artist `
  --artist-mode scenic `
  --instrument acoustic_guitar `
  --scenic meadows `
  --landmark swiss_alps `
  --continuous-motion `
  --live
```

---

## 4. 4K Live Virtual Artist Concert Broadcast (`scripts/produce_concert_video.py`)

A state-of-the-art production pipeline for **4K Multi-Camera Live Stadium Concerts**, engineered around:
1. **3 Master Eye-Level Stage Plates**:
   - `singer_orchestra_stage`: Single unified master plate — Lead Singer at centerstage stand microphone with the live backing band (guitarist, drummer on riser, bassist, keys) together on the wooden stage deck strictly at stage eye level.
   - `stadium_audience_crowd`: Ecstatic stadium crowd viewing the glowing stage at eye level with synchronized lightsticks.
   - `overall_stage_vista`: Grand wide concert arena view of the stage, overhead trusses, and laser atmosphere at stage eye level.
2. **Autonomous Directorial Wardrobe & Accessories (No Hardcoding)**:
   - Gemini autonomously derives attractive, beautiful, elegant, and cute stage attire tailored to the song and cultural genre.
   - Dignified natural neckline contour accented with delicate jewelry/choker; completely non-exposing (zero cleavage, covered chest and collarbones, long fitted sleeves).
3. **Smooth Seamless Directorial Rhythm (Zero Looping & Zero Jump Cuts)**:
   - Enforces a continuous, non-repetitive flow:
     $$\text{Motion (Wan 2.1 / Kling)} \longleftrightarrow \text{Local Drone (Pans/Zooms)} \longleftrightarrow \text{Lip-Sync (LatentSync)} \longleftrightarrow \text{Motion}$$
   - Dynamic local perspective drone flights (`zoom_in_singer`, `pan_to_guitarist`, `pan_to_drummer`, `wide_stage_pullback`, `steady_eye_level`) connect stage elements seamlessly.
4. **Dynamic Model Routing by Flag**:
   - `--image-model`: `flux` (Flux Dev), `flux-pro-ultra`, `z-image`.
   - `--motion-model`: `wan` (Wan 2.1), `kling`, `kling-4k`, `drone` (Local Perspective Drone).

---

### A. Standard Production (Wan 2.1 Motion + Flux Dev)
Produce a full 60s concert anthem with Ashwini in Hindi:
```powershell
python scripts/produce_concert_video.py `
  --chars Ashwini `
  --language hi `
  --prompt "High energy live stadium concert anthem with driving rhythm and roaring guitar" `
  --image-model flux `
  --motion-model wan `
  --live `
  -y
```

### B. Studio Master Production (4K Flux Pro Ultra + Kling 4K)
Maximum cinema-grade resolution and broadcast motion fidelity:
```powershell
python scripts/produce_concert_video.py `
  --chars Ashwini `
  --language hi `
  --prompt "Epic rock concert anthem with soaring vocal hooks and pyrotechnics" `
  --image-model flux-pro-ultra `
  --motion-model kling-4k `
  --live `
  -y
```

### C. Pure Local Perspective Drone ($0.00 Motion Cost, Fast CPU Render)
Uses subpixel optical homography for all camera sweeps, pushes, and lateral pans:
```powershell
python scripts/produce_concert_video.py `
  --chars Ashwini `
  --language hi `
  --image-model flux `
  --motion-model drone `
  --live `
  -y
```

### D. Studio Master Production with Sync-Lipsync v2 (`--prod`)
Production broadcast quality utilizing Sync Labs 2.0 (`fal-ai/sync-lipsync/v2`) for premium mouth synchronization:
```powershell
python scripts/produce_concert_video.py `
  --chars Ashwini `
  --language hi `
  --prompt "Grand stadium rock anthem with roaring guitars and electrifying vocal delivery" `
  --image-model flux `
  --motion-model wan `
  --prod `
  --live `
  -y
```

### E. Custom Lipsync Model Selection (`--lipsync-model`)
Pass any specific lipsync model explicitly:
```powershell
python scripts/produce_concert_video.py `
  --id 4b923266-bdde-4e2b-9fa2-0d4743aaf51f `
  --lipsync-model fal-ai/sync-lipsync/v2 `
  --live `
  -y
```

### F. Idempotent Episode Resumption (Zero Duplicate Spend)
Resume an existing project folder, synthesizing only missing assets while preserving existing Suno audio and completed plates:
```powershell
python scripts/produce_concert_video.py `
  --id 4b923266-bdde-4e2b-9fa2-0d4743aaf51f `
  --image-model flux `
  --motion-model wan `
  --prod `
  --live `
  -y
```

---

### 🔑 Concert Studio CLI Flag Reference

| Flag | Purpose | Options | Default |
| :--- | :--- | :--- | :--- |
| `--chars` / `--artist-name` | Lead singer character identity (locked via FLUX LoRA) | `Ashwini`, `Radha`, `Meera` | `Radha` |
| `--language` / `-l` | Language code for lyrics, title, and vocal delivery | `hi`, `te`, `ta`, `kn`, `pa`, `en`, `es`, etc. | `te` |
| `--prompt` / `-p` | Directorial theme & musical concept | Any narrative description | High-energy stadium anthem |
| `--image-model` / `--model` | 4K stage plate synthesis model | `flux`, `flux-dev`, `flux-pro-ultra`, `z-image` | `flux` |
| `--motion-model` | Stage motion & camera flight engine | `wan`, `wan2.1`, `kling`, `kling-4k`, `drone` | `wan` |
| `--prod` | Enable production-tier models (switches lipsync to `fal-ai/sync-lipsync/v2`) | Flag | `False` (defaults to `fal-ai/latentsync`) |
| `--lipsync-model` | Explicitly choose vocal lipsync engine | `fal-ai/sync-lipsync/v2`, `sync-lipsync`, `latentsync` | Auto-derived from `--prod` |
| `--id` | Resume existing episode folder without duplicate paid calls | e.g. `--id 4b923266-bdde-4e2b-9fa2-0d4743aaf51f` | Auto-generated from title |
| `--duration` / `-d` | Song duration | `60s`, `90s`, `120s` | `60s` |
| `--instrument` | Staging instrument for lead performer | `mic`, `acoustic_guitar`, `violin`, `sitar` | `mic` |
| `--no-orchestra` | Disable live backing rock band/orchestra | Flag | Enabled by default |
| `--no-lipsync` | Disable lipsync on singing cuts | Flag | Enabled by default |
| `--live` | Enable paid remote APIs (FLUX, Wan, Suno, Sync-Lipsync) | Flag | Offline test mode |
| `-y` / `--yes` | Auto-confirm pre-flight script validation gate | Flag | Prompts `[Y/n]` |
