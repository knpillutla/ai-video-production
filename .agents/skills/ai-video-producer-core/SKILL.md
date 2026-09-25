---
name: ai-video-producer-core
description: Core foundation skill for AI video production across all genres (dance, comedy, blue-chip nature, drama, walking tours). Enforces the 4-Stage Progressive Quality Gate, pre-flight topic deduplication, YPP monetization safety, universal artifact caching, broadcast audio/video standards, and dynamic model routing.
---

# AI Video Producer Core Skill

Universal foundation skill and operational cheat-sheet for all studio agents, generation pipelines, and subagents in the Antigravity AI Video Production Studio.

---

## 1. Non-Negotiable Core Directives

Every agent and pipeline must adhere to these foundational engineering standards:

1. **Consultative Alignment & Feedback First (Directive 21):**
   - Provide engineering feedback, trade-off analysis, and professional advice BEFORE executing code or configuration changes.
   - Align with the user on intent and final design before action.
2. **Universal Artifact Caching & Idempotency Mandate (Directive 3):**
   - Universal across ALL categories & ALL channels: images, references, backgrounds, scripts, songs, videos, audio stems, lipsync, thumbnails, and composite renders.
   - **Tier 1 (Disk Check):** If an artifact exists on disk and is non-empty (>1000 bytes), **NEVER** recreate or re-invoke external paid models.
   - **Tier 2 (In-Flight Resumption):** Persist remote request IDs (`fal_req_p*.json`, `suno_req.json`) to disk. On restart, resume polling existing remote tasks before issuing a new paid call.
   - **Tier 3 (AudioVault):** Check AudioVault / local stem caches for matching musical moods before calling Suno.
   - **Tier 4 (Idempotent `--id` Resume):** All studio agents and channel scripts must support `--id <episode_id>` to resume interrupted jobs and only render missing artifacts.
3. **Pre-Flight Cost Transparency (Directive 7):**
   - Calculate and display the itemized cost breakdown (tokens, voice chars, keyframe images, video motion, compute) before dispatching generation jobs.
4. **Model Testing Safety Guard & Bulk Test Ban (Directive 8):**
   - **STRICT BAN ON BULK TESTS:** **NEVER, EVER automatically run all tests.** Full test suite runs (`pytest tests/`) are strictly prohibited unless explicitly requested by the user.
   - When verifying a code change, run **ONLY the single specific test file or function** modified.
   - Automated test suite runs 100% locally with offline deterministic mocks ($0.00 cost).
   - Live external model tests must run **only ONE test only** capped at a **maximum duration of 10 seconds**.
5. **Pre-Flight Topic Deduplication & User Alerting (Directive 10):**
   - Save topic, genre, tags, and synthesized story into `TopicMemory`.
   - If cosine similarity $\ge 0.80$ or heavy metadata overlap is detected, block generation (HTTP 409 Conflict) and alert the user immediately.
6. **YouTube Partner Program (YPP) Monetization Standards (Directive 11):**
   - **Anti-Demonetization Narrative Guard:** Prohibit silent/uncurated ambient video loops; mandate scripted voiceover commentary or cultural storytelling.
   - **100% Commercial Master Rights:** Zero copyrighted third-party tracks. Composed via Suno v3.5 Pro or procedural DSP stems.
   - **AdSense Advertiser-Friendly Screening:** All scripts screened via `local_compliance.py`.
   - **Synthetic Media Disclosure:** Set `has_synthetic_media=True` on upload.

---

## 2. Mandatory 4-Stage Progressive Quality Gate

All generation pipelines and production scripts must execute through 4 distinct verification stages:

```
[ Stage 1: Storyboard & Topic Gate ]  --> Pre-flight dedup (cos >= 0.80), cost forecast, Gemini story beats
                |
                v
[ Stage 2: Keyframe Image Gate ]      --> FLUX 1.1 Pro Ultra keyframes; inspect & allow single-scene recreation ($0.06)
                |
                v
[ Stage 3: Audio & Soundtrack Gate ]  --> Semantic AudioVault cache check ($0.00) or Suno v3.5 Pro stem generation
                |
                v
[ Stage 4: Video Motion & 4K Master ] --> Kling v3 Pro / Wan 2.1 motion + single-pass Lanczos FFmpeg 4K mastering
```

| Stage | Verification Checks | Cost Optimization Action |
| :--- | :--- | :--- |
| **Stage 1** | Storyboard structure, prompt fidelity ($\ge 130$ words), topic similarity $< 0.80$. | Abort before generating any visual assets if topic is duplicate. |
| **Stage 2** | Image sharpness, character build/wardrobe consistency, natural 5500K daylight. | Re-generate only flawed keyframes ($0.06/img) instead of re-rendering full video ($1.40/clip). |
| **Stage 3** | 48 kHz stereo, -14.0 LUFS, zero procedural hiss, matching lead vocal gender. | Reuse matching cached stem from `AudioVault` for $0.00 spend. |
| **Stage 4** | Downbeat scene snapping, dynamic FPS (24/30/60), single-pass Lanczos 4K CRF 18. | Single-pass FFmpeg `-filter_complex` with zero intermediate re-encodings. |

---

## 3. Dynamic Model Selection & Kinematics Strategy

### A. Video Motion Kinematics Strategy
- **`water_impact_collision` $\rightarrow$ Kling v3 Pro ($0.280/s)$:** Heavy cascading waterfalls plunging over rocks, crashing ocean surf, violent rapids, splashing characters/wildlife.
- **`water_fluid` $\rightarrow$ Alibaba Wan 2.1 ($0.080/s)$:** Continuous smooth laminar rivers, gentle ocean swells, meandering streams, canal flows, light rain.
- **`landscape_solid` $\rightarrow$ Tencent Hunyuan Video 1080p ($0.075/s)$:** Calm glassy glacial lakes, mirror fjords, solid mountain peaks, architectural facades.
- **`human_action` / `dance_choreography` $\rightarrow$ Kling v3 Pro ($0.280/s)$:** High-energy choreography, foot-stomping hook steps, spinning fabrics.

### B. Story-Driven Dynamic FPS Standards
- **24 fps (Cinematic Drama & Blue-Chip Nature):** Natural cinematic motion blur; prevents the artificial "soap opera" effect.
- **30 fps (Music, Dance & Comedy):** Clean temporal sharpness for footwork, spinning fabrics, and facial expressions.
- **60 fps (POV Walking & Scenic Tours):** Eliminates pan judder and creates smooth physical presence.

---

## 4. Reusable Script Utilities Reference

Always prefer deterministic Python modules over redundant LLM calls:
- `src/services/topic_memory.py`: Semantic topic deduplication and vector cosine distance.
- `src/services/audio_vault.py`: Dynamic semantic audio caching and tag overlap search ($\ge 0.70$).
- `scripts/local_compliance.py`: YouTube AdSense advertiser-unfriendly category scanner.
- `scripts/local_beat_detector.py`: Librosa BPM, kick transients, and downbeat snap alignment.
- `scripts/local_subtitles.py`: Formatted `.srt`, `.vtt`, and kinetic subtitle generator.
- `scripts/local_audio_ducking.py`: Mathematical dynamic volume ducking (-18 dB speech).

---

## 5. UI Preview Panel Specification (6-Section Master Hierarchy)

When inspecting productions in the UI Right Preview Panel, always adhere to the 6-section structure:
- **Section 0:** Master 4K Video Player (Final composite 4K UHD with download).
- **Section 1:** Keyframe Images (Horizontal scroll with lightbox zoom and per-scene recreation trigger).
- **Section 2:** Raw Video Clips (Horizontal scroll with hover playback and model provenance badge).
- **Section 3:** Foley & Environmental Audio Stems (Waveform player & volume control).
- **Section 4:** BGM & Musical Score (Suno v3.5 Pro stem player with loop controls).
- **Section 5:** Voiceover & TTS Narration (Audio stem player).
- **Section 6:** Subtitles & Metadata (SRT/VTT display, YPP clearance badge, synthetic media status).
