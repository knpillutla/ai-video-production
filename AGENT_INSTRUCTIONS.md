# AI Agent Instructions & Engineering Guidelines
# Project: Professional AI Video Producer Studio

> **Scope:** Mandatory guidelines for all AI agents, engineers, and subagents contributing to this codebase.  
> **Core Mandate:** High performance, extreme token efficiency, reusable deterministic scripts over LLMs, modular functional design, performance optimization, and a strict 300-line limit per file.

---

## 1. Golden Rules (Non-Negotiable)

1. **Token Economy First:** Minimize LLM calls and context size. If a task can be calculated, parsed, or formatted with deterministic code, **never call an LLM**.
2. **Deterministic Script Reusability & Universal Artifact Caching (All Media Categories):** Build standalone, reusable scripts and utilities for recurring operations. Reuse created artifacts as much as possible; the entire production pipeline must be strictly idempotent. This rule applies universally across **ALL categories—images, references, backgrounds, scripts, songs, video, audio, lipsync, thumbnails, and composite renders**. If an artifact file already exists on disk and is non-empty for that project/episode/task, **NEVER invoke external AI models or re-synthesize**. If an artifact is deleted or does not exist, then and only then create it again as required for improvements.
3. **Hard 300-Line File Limit:** **No code file may exceed 300 lines.** If a file approaches 250 lines, refactor immediately into focused sub-modules.
4. **Functional & Modular Design:** Favor pure functions, explicit dependency injection, clear interface contracts, and zero hidden side effects.
5. **High-Performance Architecture:** Enforce asynchronous non-blocking I/O, streaming media transfers (zero RAM bloat), connection pooling, single-pass FFmpeg filter graphs, and vectorized math.
6. **Zero Duplication & Single Source of Truth:** Never create or keep duplicate code, redundant helpers, or overlapping documentation files. Maintain exactly one authoritative source file per domain. Delete superseded drafts immediately.
7. **Fail-Fast & Idempotent (Zero Redundant Spends):** Every pipeline step must be replayable and idempotent. Never regenerate existing media assets or duplicate external paid API expenditures during iterative video improvements.
8. **Pre-Flight Cost Transparency & Explicit Confirmation:** UI submissions must NEVER immediately trigger generation. The pipeline must first calculate and display an itemized cost breakdown (LLM tokens, TTS characters, visual assets, cloud compute) and require explicit user confirmation before executing billable jobs.
9. **Model Testing Safety & Cost Guard (Automated Tests Mandate):** When testing models as part of automated tests, **only run one test only with 10 sec duration**; ensure we do not call more than one test, to save on costs. The standard automated test suite (`pytest`) must ALWAYS run 100% locally with offline deterministic mocks/fallbacks even if model keys are present in `.env`.
10. **Terraform-Only IaC:** Always create Terraform scripts only for all cloud platforms (Azure, GCP, AWS, Multi-Cloud). Never use Bicep, ARM, CloudFormation, or platform-specific template languages.
11. **Topic, Metadata & Story Deduplication & User Alerting:** Every time a video is created, save the topic, metadata information (genre, tags, target audience, format), and the final story created from the script into the persistent Topic Memory vault. When the user creates for similar metadata or topic (cosine similarity $\ge 0.80$ or heavy metadata overlap), do not create duplicate content; block generation immediately and alert the user with a descriptive duplicate alert.
12. **Mandatory YPP Monetization Standards (Anti-Demonetization Guard):** Never generate uncurated, silent ambient or scenic loops without substantive human/scripted narrative. All productions must incorporate meaningful voiceover commentary, educational trivia, or cultural storytelling (via TTS narration and timed subtitles) to avoid YouTube's "Reused / Repetitive Content" rejections. Ensure 100% commercial master rights for audio/music (Suno v3.5 Pro or local procedural DSP) to prevent Content ID strikes, strictly enforce AdSense advertiser-friendly safety (`local_compliance.py`), and declare synthetic media flags on upload.
13. **Mandatory Character Physicality & Autonomous Contextual Wardrobe/Aesthetics Derivation:** All main characters (both male and female) must have a balanced, naturally fit medium-slender build (neither too skinny/bony nor too chubby, graceful feminine curves with toned midriff for women, lean-athletic fit build for men), strikingly beautiful/handsome, and in their mid-20s (ages 23–27) by default unless explicitly specified. The user must never be required to manually specify clothing, background aesthetics, or set designs; the system must autonomously derive background aesthetics, lighting, color palettes, and scene-matched outfits directly from the narrative beats and cultural context synthesized by Gemini.
14. **Broadcast Video, Audio & Story-Driven Dynamic FPS Standards:** Deliveries must adhere to broadcast mastering specs: 4K UHD (3840×2160 or 2160×3840), CRF 18–20 visually lossless, 48 kHz 24-bit stereo audio, 256–320 kbps AAC, -14.0 LUFS integrated loudness, and dynamic story-driven FPS selection (24 fps for cinematic drama, 30 fps for music/dance/comedy, 60 fps for POV walking/scenic tours) autonomously directed by Gemini.
15. **Mandatory Beat-Driven Choreographic Progression & Lyrics/Beat Architecture:** Every dance production must dynamically evolve its visual choreography in lockstep with the song's musical shifts (Phase 1: Swagger walk/shoulder shrugs; Phase 2: Lyrical acting/half-spins; Phase 3: Explosive synchronized hook step on the beat drop). Gemini MUST write the structured rhyming lyrics, and Suno MUST compose the music and beats based on those lyrics with matching vocal gender (male dancer = male vocals; female dancer = female vocals). On-screen singing scenes must be processed through avatar lip-sync (`fal-ai/sync-lipsync`). Audio reuse or hardcoding is strictly banned. Snap all editorial cuts deterministically to downbeats via `LocalBeatDetector`.
16. **Mandatory Multi-Location Progression & Camera-Matched Background Depth:** For full songs (2–3+ mins), rotate across 3–4 distinct location hubs derived from lyrics (e.g., bazaar, paddy fields, banyan tree, twilight fairgrounds). Enforce optical background depth per camera angle (wide = deep environmental panorama; closeup = creamy f/1.4 bokeh blur for facial focus; low-angle = upward ground view).


---

## 2. Token Optimization & Model Tiering Strategy

### 2.1 The Three-Tier Model Routing Hierarchy
Never use an expensive flagship model when a lightweight model or local script suffices.

| Tier | Model Types | Allowed Tasks | Disallowed Tasks |
| :--- | :--- | :--- | :--- |
| **Tier 0: Local Script** | Pure Python, Regex, NumPy, FFmpeg | Token cost calculation, profanity filtering, SRT formatting, cosine similarity, audio ducking math, YouTube upload payloads. | Creative writing, cultural transcreation. |
| **Tier 1: Lightweight** | `gemini-1.5-flash`, `gpt-4o-mini`, `flash_lite` | Text summarization, JSON schema extraction, keyword/tag generation, transcription cleanup, title variations. | Complex humor adaptation, long-form scriptwriting. |
| **Tier 2: Flagship** | `gemini-1.5-pro`, `claude-3-5-sonnet`, `gpt-4o` | Core retention scriptwriting, cultural transcreation (Telugu comedic timing, Hindi idioms), sensitive monetization arbitration. | Parsing JSON, formatting subtitles, regex searches. |

### 2.2 Token Minimization Tactics
* **Minified Structured Output:** Instruct models to return raw minified JSON. Do not tolerate conversational preamble (e.g., *"Here is the script you requested:"*).
* **Context Pruning:** Never pass entire conversation transcripts, raw video transcripts, or large historical files into the prompt. Slice and pass only the exact context required (e.g., passing only the 1-sentence hook and scene index).
* **Prompt Caching:** Keep system prompts static and structured at the head of requests to leverage LLM API prompt caching discounts.
* **Hash-Based Caching:** Hash prompt inputs (`hashlib.sha256(prompt.encode()).hexdigest()`). If the output exists in local cache or Azure, reuse it rather than re-querying the model.

### 2.3 Dynamic Model Selection via MCP Server
* Never hardcode arbitrary model IDs across production services.
* Always query the dedicated Model Selector MCP server (`mcp_select_best_model`) to dynamically resolve the best model per category (`script_creative`, `script_fast`, `voice_tts`, `visual_image`, `video_motion`, `lipsync`, `music_bgm`, `sfx_audio`).
* The MCP server evaluates token pricing, real-time benchmarks, latency limits, language compatibility (e.g., Telugu/Hindi phonetics), and commercial license compliance before dispatching tasks.
* **Isolated Provider Adapters:** Every model integration must live in its own dedicated, modular adapter file under `src/providers/<category>/<model>_adapter.py` (under 200 lines) adhering to standard typed protocols (`LLMProviderInterface`, `TTSProviderInterface`, etc.).

---

## 3. Reusable Deterministic Scripts Over LLMs

Whenever a capability is needed, first ask: **"Can this be a deterministic Python function or utility script?"**

### Mandated Reusable Script Modules:
* **`scripts/local_compliance.py`:** Fast regex dictionary scanner checking YouTube's 11 advertiser-unfriendly categories. Only call LLM if ambiguous context requires nuanced safety judgment.
* **`scripts/local_beat_detector.py`:** Pure Python Librosa analysis computing BPM, downbeats, kicks, and drops for millisecond dance/music cuts.
* **`scripts/local_audio_ducking.py`:** Math utility computing volume curves (-18dB speech, -6dB pause) and FFmpeg filter chains without LLM intervention.
* **`scripts/local_subtitles.py`:** Converts timestamped word arrays into formatted `.srt`, `.vtt`, and kinetic subtitle SVG chunks.
* **`scripts/local_vector_math.py`:** Local NumPy cosine similarity function to compare topic embeddings against vector memory.
* **`scripts/local_pan_zoom.py`:** Executes 2.5D camera parallax/zoom on 4K static images via FFmpeg, saving $0.20–$0.50 per scene over full video AI models.
* **`scripts/local_thumbnail.py`:** PIL/Canvas script rendering high-contrast text overlays, borders, dropshadows, and regional font rendering (Telugu, Devanagari) deterministically from templates.
* **`scripts/youtube_builder.py`:** Pure Python script assembling YouTube Data API v3 upload structures, synthetic media flags, and chapter timestamps.

---

## 4. Code Performance Optimization

### 4.1 Asynchronous Non-Blocking Execution
* All network I/O (Azure Blob Storage, YouTube API, external LLM/TTS endpoints) must use `async`/`await` (e.g., `httpx.AsyncClient`, `aiofiles`).
* Execute independent asset jobs concurrently using `asyncio.gather()` or `TaskGroup`:
  ```python
  # Good: Parallel multilingual audio stem generation
  await asyncio.gather(
      tts_service.generate("te", te_script),
      tts_service.generate("hi", hi_script),
      tts_service.generate("en", en_script)
  )
  ```

### 4.2 Streaming & Zero-Memory-Bloat Media Handling
* Media files (1080p/4K video, audio stems) are large. **Never read entire video files into memory** via `file.read()`.
* Stream data using chunks, memory-mapped files (`mmap`), or pipeline iterators (`shutil.copyfileobj`, Azure chunked upload streams).

### 4.3 FFmpeg Pipeline Performance
* **Single-Pass Encoding:** Never execute multiple sequential re-encodings of intermediate video files. Combine scaling, transitions, audio ducking, and subtitle overlays in a single `-filter_complex` execution.
* **Stream Copying:** Use `-c copy` whenever muxing audio tracks into a master video without touching the video stream.
* **Hardware Acceleration:** Configure FFmpeg with multithreading (`-threads 0`) and GPU acceleration (`h264_nvenc`, `cuda`, or `qsv`) when available.

### 4.4 Connection Pooling & In-Memory Caching
* Reuse persistent `httpx.AsyncClient` instances with connection pooling across all services. Do not instantiate a new HTTP client per request.
* Pre-compile regular expressions (`re.compile`) at module initialization.
* Use NumPy vectorized array math for all embedding cosine distance calculations instead of pure Python loops.

---

## 5. Modular Code Standards & The 300-Line Rule

### 5.1 The 300-Line Limit
* **Strict Ceiling:** 300 lines of code (including docstrings and imports).
* **Target Size:** 120–220 lines per file.
* **Action Trigger:** When a file reaches 250 lines:
  1. Identify distinct responsibilities (e.g., parsing vs. network requests vs. business logic).
  2. Extract helper functions into a dedicated sub-package module.
  3. Re-export clean public APIs in `__init__.py`.

### 5.2 Module Decomposition Pattern

❌ **Anti-Pattern (Monolithic file):**
```
services/
└── video_service.py          # 1,200 lines (Compositing, ducking, subtitles, upload)
```

✅ **Mandated Architecture (Modular sub-packages):**
```
services/
└── video/
    ├── __init__.py           # Clean facade (< 50 lines)
    ├── compositor.py         # Main pipeline orchestration (< 200 lines)
    ├── audio_ducking.py      # Ducking and audio filter chains (< 180 lines)
    ├── subtitle_burner.py    # Kinetic captions and typography (< 190 lines)
    └── transition_engine.py  # Visual transitions & cut pacing (< 160 lines)
```

---

## 6. Functional & Reusable Code Conventions

1. **Pure Functions Wherever Feasible:**
   * Given the same inputs, a pure function must always return the same output with no side effects on external state.
   ```python
   # Good: Pure, testable, reusable
   def calculate_ducking_volume(speech_active: bool, duck_db: float = -18.0) -> float:
       return duck_db if speech_active else -6.0
   ```

2. **Explicit Interfaces & Pydantic Schemas:**
   * Every function accepting structured data must use explicit Pydantic models or typed dataclasses. No arbitrary untyped `dict` payloads across service boundaries.

3. **Dependency Injection:**
   * Inject storage clients, LLM clients, and file paths into classes/functions. Never hardcode singleton network connections inside business logic.
   ```python
   # Good: Injectable, mockable for testing
   class RetentionScriptService:
       def __init__(self, llm_client: LLMProviderInterface, cache: CacheInterface):
           self.llm = llm_client
           self.cache = cache
   ```

4. **Error Handling & Graceful Degradation:**
   * Catch specific exceptions. Never use bare `except:`.
   * When an external API fails (e.g., voice synthesis timeout), fall back gracefully to secondary providers or cached assets without crashing the entire pipeline.

---

## 7. Directory & Code Organization Blueprint

```
content-generation/
├── AGENTS.md                  # Project rules loaded by Antigravity
├── AGENT_INSTRUCTIONS.md      # Detailed engineering instructions (this file)
├── MASTER_DESIGN_AND_REQUIREMENTS.md  # System specification & architecture
├── project-requirements.txt   # Original customer requirements
│
├── core/                      # Shared configuration & base types
│   ├── config.py              # Environment variables & constants (< 120 lines)
│   ├── exceptions.py          # Custom domain exceptions (< 80 lines)
│   └── logger.py              # Structured logging utility (< 70 lines)
│
├── schemas/                   # Pydantic data contracts
│   ├── project.py             # Project & channel definitions (< 150 lines)
│   ├── scene.py               # Storyboard & scene models (< 120 lines)
│   ├── compliance.py          # YPP & AdSense audit schemas (< 90 lines)
│   └── publishing.py          # YouTube & multi-channel metadata (< 100 lines)
│
├── scripts/                   # Reusable deterministic automation scripts
│   ├── filter_keywords.py     # Regex compliance & profanity checker (< 180 lines)
│   ├── ducking_math.py        # FFmpeg audio filter generator (< 140 lines)
│   ├── srt_builder.py         # Subtitle parsing & kinetic formatter (< 160 lines)
│   ├── vector_dedup.py        # Cosine similarity calculation (< 120 lines)
│   └── thumbnail_layout.py    # Localized PIL typography renderer (< 220 lines)
│
├── agents/                    # LLM orchestration agents (Tier 1 & Tier 2)
│   ├── script_agent.py        # Retention & hook writing (< 240 lines)
│   ├── compliance_agent.py    # YPP safety auditor (< 180 lines)
│   ├── transcreation_agent.py # Cultural translation (Telugu, Hindi) (< 220 lines)
│   └── seo_agent.py           # Titles, chapters & descriptions (< 160 lines)
│
├── services/                  # Business logic & external service integrations
│   ├── storage/               # Azure Blob Storage client (< 200 lines)
│   ├── audio/                 # TTS, BGM mixing & ducking (< 220 lines)
│   ├── visual/                # Image/video provider routing (< 220 lines)
│   ├── compositor/            # FFmpeg/Remotion video assembler (< 240 lines)
│   └── youtube/               # YouTube Data API v3 publisher (< 250 lines)
│
└── tests/                     # Unit & integration test suite
    ├── test_compliance.py
    ├── test_ducking.py
    ├── test_scripts.py
    └── test_schemas.py
```

---

## 8. Agent Pre-Commit Self-Audit Checklist

Before completing any task, every agent must verify:
* [ ] **Line Count Check:** Did any created or modified file exceed 300 lines? (`Get-Content <file> | Measure-Object -Line`)
* [ ] **Performance Check:** Are network and file operations asynchronous? Are media files streamed rather than loaded entirely into memory? Is FFmpeg executing in single-pass filter graphs?
* [ ] **Token Check:** Did I avoid calling an LLM for deterministic math, regex, formatting, or parsing?
* [ ] **Script Reusability:** Did I extract reusable logic into a script under `scripts/` or a service module?
* [ ] **Schema Compliance:** Are all data contracts backed by typed Pydantic models?
* [ ] **Modularity:** Is code decomposed into single-responsibility functions with clean inputs and outputs?
* [ ] **Zero Duplication:** Did I avoid duplicate code, redundant helpers, or duplicate markdown documentation files?
* [ ] **Cost Confirmation:** Does the UI flow enforce pre-flight cost calculation and explicit confirmation before dispatching rendering/generation jobs?
* [ ] **Model Testing Safety (Automated Tests):** Did I ensure the automated test suite runs 100% locally with offline mocks? When testing models as part of automated tests, did I verify that only ONE test only was called with a maximum 10-second duration to save on costs?
* [ ] **Terraform-Only IaC Check:** Did I ensure all infrastructure as code scripts are declared exclusively in Terraform (`.tf`) with zero Bicep/ARM files?
* [ ] **Topic, Metadata & Story Deduplication Check:** Does the pipeline save the topic, metadata, and final story, and alert/block duplicate content attempts?
* [ ] **YPP Monetization & Rights Compliance Check:** Did I ensure no silent/ambient-only video loops are produced without narrative voiceover? Are all soundtracks 100% commercially cleared (zero Content ID risks)? Did the script pass AdSense compliance screening (`local_compliance.py`)?
* [ ] **Character Physicality & Contextual Outfits Check:** Are all main characters defaulted to a balanced, naturally fit medium-slender build (neither too skinny/bony nor too chubby, graceful curves for women, lean-athletic for men), beautiful/handsome, mid-20s (23–27)? Are outfits, lighting, and background aesthetics autonomously derived and matched to the specific scene context without requiring manual user input?
* [ ] **Natural Lighting & Walking Cadence Check:** Do outdoor productions enforce crisp, natural daylight (5400K–5600K) with zero artificial yellow flares? Are POV walking tours paced at a gentle, leisurely 3 km/h cadence?
* [ ] **Broadcast Video, Audio & Dynamic FPS Check:** Did Gemini directorially specify `recommended_fps` matching the narrative tempo (24 fps drama, 30 fps dance, 60 fps walking)? Is audio muxed at 48,000 Hz, 256 kbps AAC, normalized to -14.0 LUFS with BGM ducking? Is video rendered at 4K UHD CRF 18–20?
* [ ] **Beat-Driven Choreography Check:** Does dance choreography dynamically evolve across song phases (intro tease -> lyrical verse -> explosive hook step on beat drop)? Are video cuts snapped to downbeats via `LocalBeatDetector`?
* [ ] **Multi-Location & Angle-Depth Check:** For full songs, did Gemini architect 3–4 location hubs? Do closeups feature creamy optical bokeh while wide shots show environmental depth?

---

## 9. Mandatory Character Physicality & Contextual Wardrobe Derivation

* **Physicality Standards (Balanced Fit Build):** All main protagonists and featured characters (male and female) must be defaulted to a **balanced, naturally fit, healthy medium-slender build (neither too skinny/bony nor too chubby, graceful feminine curves with toned waist for women, lean-athletic fit build for men)**, strikingly beautiful / handsome, in their mid-20s (ages 23–27) unless explicitly specified otherwise by the user.
* **Autonomous Scene Derivation:** The user must never be required to manually specify clothing, lighting, camera angles, or background aesthetics. The LLM story agent must autonomously deduce and enrich these details directly from narrative and cultural cues.
* **Scene-Matched Outfits:** Outfits and wardrobe must dynamically and authentically match the context of each scene in the story (e.g., festive village jathara -> vibrant traditional festive attire; modern IT office/WFH -> stylish smart-casual; rainy alpine trek -> functional stylish waterproof alpine outdoor wear; romantic evening -> elegant evening wear; casual home -> relaxed stylish loungewear).

---

## 10. Natural Daylight Lighting & Realistic Human Walking Cadence Standards

* **Natural Open-Air Lighting:** Outdoor celebrations, dances, and village scenes must default to crisp, balanced natural daylight (5400K–5600K) with soft ambient sun, realistic authentic skin tones, and neutral contrast. Strictly avoid artificial golden-hour lens flare blowouts or oversaturated yellow/amber washes.
* **Leisurely Human Walking Cadence:** POV walking documentaries (e.g., Swiss Alps, city tours) must maintain a calm, meditative walking speed (~1 m/s / 3 km/h) with subtle steadycam sway, avoiding rapid drone-like fly-throughs or rushed translations.

---

## 11. Broadcast-Grade Video, Audio & Story-Driven Dynamic FPS Standards

* **Directorial Story-Driven FPS Selection:** Frame rates must never be arbitrary or hardcoded; Gemini must autonomously assign `recommended_fps` based on narrative tempo and camera motion:
  * **24 fps (Cinematic Drama):** For narrative storytelling, emotional romance, slow-paced aesthetic dialogue. Provides natural cinematic motion blur and prevents the artificial "soap opera" effect.
  * **30 fps (Music, Dance & Comedy):** For high-tempo folk choreographies, stage comedy, music videos, and dynamic performances. Delivers clean temporal sharpness for footwork, spinning fabrics, and facial expressions while preserving artistic cadence.
  * **60 fps (POV Walking Tours & Fluid Motion):** For first-person POV walking tours (e.g., Swiss Alps, city explorations), tracking landscape glides, and sports action. Eliminates camera judder and creates smooth, realistic physical presence.
* **Broadcast Audio Standards:**
  * **Sample Rate:** Mandatory **48,000 Hz (48 kHz) 24-bit stereo** across all audio stems and final master containers (never 44.1 kHz in video containers).
  * **Codec & Bitrate:** AAC-LC at **256 kbps – 320 kbps**.
  * **Loudness Normalization:** Integrated loudness targeted strictly to **-14.0 LUFS (±1.0 LUFS)** with True Peak < **-1.0 dBFS** (complying with YouTube and EBU R128 standards).
  * **Deterministic Dynamic Ducking:** Dialogue mixed cleanly at -14 LUFS, with background music (BGM) automatically ducked by -18 dB to -22 dB during speech intervals and rising back up during musical interludes.
* **Visually Lossless 4K Video:** Master all final video deliveries in **4K UHD (3840×2160 for 16:9, 2160×3840 for 9:16 Shorts)** at **CRF 18–20** visually lossless quality via single-pass FFmpeg with `yuv420p` pixel format and `+faststart` MP4 metadata flags.

---

## 12. Mandatory Beat-Driven Choreographic Progression & Musical Alignment Standards

* **Gemini Lyrics & Scriptwriting Contract:** In all dance, song, and musical productions, **Gemini MUST create the structured script and rhyming lyrical verse / hook couplets** with metric cadence (*prasa*), rhythmic meter, and cultural authenticity. Never allow Suno or external models to hallucinate arbitrary lyrics without Gemini's structured direction.
* **Suno Music & Beat Composition from Lyrics:** **Suno composes the song, instrumentation, and beats directly based on Gemini's lyrics.** Suno MUST receive Gemini's exact generated lyrics in its `prompt` parameter along with musical tags (`tags: "[genre], [BPM], [instruments], [vocal_gender] vocals"`). Suno then synthesizes the musical arrangement, rhythm, drum transients, and singing performance directly aligned to those lyrics.
* **Strict Vocal Gender & Lead Performer Consistency:** The vocal gender passed to Suno MUST strictly match the gender of the on-screen lead performer (e.g., Male lead dancer -> `male vocals` / deep energetic hero vocals; Female lead dancer -> `female vocals`). Strictly prohibit pairing a male dancer with a female vocal track or vice versa.
* **Mandatory Facial Lip-Sync for Musical Dance (`fal-ai/sync-lipsync`):** On-screen singing/dancing lead characters in medium shots and close-ups MUST be processed through the avatar lip-sync pipeline (`fal-ai/sync-lipsync` or `fal-ai/live-portrait`) driven by the Suno vocal track stem, ensuring the mouth moves in authentic synchronization with the sung lyrics.
* **Strict Ban on Hardcoded or Cached Audio Reuse Across Different Productions:** Never hardcode, recycle, or reuse audio stems across different productions (e.g. reusing legacy test audio like `surrumantadiro_song.mp3`). Every distinct production must use freshly composed Gemini lyrics and Suno music tailored to the episode topic.
* **Song Reusability During Iterative Video Improvements (No Duplicate Songs):** When testing and iterating on the same video/episode for visual, prompt, or editorial improvements, if a Suno song has already been created and exists on disk for that specific video project, NEVER invoke Suno again. Always reuse the existing synthesized song stem to prevent redundant API expenditures and unwanted duplicate song variations.
* **Musical Choreographic Progression (Anti-Monotony Guard):** Every dance production must dynamically evolve its visual choreography in lockstep with the musical shifts across 3 phases:
  * **Phase 1 (Intro Build-Up):** Swagger walk forward, rhythmic shoulder shrugs, subtle hip sway, teasing facial expressions (*abhinaya*).
  * **Phase 2 (Lyrical Verse / Transitions):** Expressive narrative hand gestures matching lyrics, half-turn spins, troupe interactions.
  * **Phase 3 (Beat Drop / Hook):** High-intensity synchronized hook step—vigorous foot-stomping, waist twists, spinning *chakkars*, explosive jumps.
* **Deterministic Beat Alignment:** Use `LocalBeatDetector` to compute BPM/downbeats. Scene transitions must snap directly to musical downbeats (`align_scene_cuts_to_beats`).
* **Zero Spoken Narration in Dance Videos (Musical Lip-Sync Only):** In dance videos, characters must NEVER speak title text, narrator descriptions, or prompt dialogue. Lip-sync synchronization MUST be driven directly by the musical song track and sung lyrics (Suno stem), preserving 100% of the instrumentation and festive singing. Spoken TTS dialogue is strictly prohibited in dance music productions.

---

## 13. Mandatory Multi-Location Progression & Camera-Matched Background Depth

* **Multi-Location Hubs for Long-Form Songs (Anti-Static Set Guard):** In full songs (2–3+ mins), never anchor the entire video to a single static set. Gemini must autonomously derive and rotate across **3 to 4 distinct location hubs** matching the lyrical narrative (e.g., village bazaar street -> lush green paddy fields -> ancient banyan tree platform -> twilight fairgrounds).
* **Camera-Matched Optical Background Depth (Angle Consistency):** Within each location, backgrounds must authentically adapt to shot geometry and focal length:
  * **Wide Shot:** Expansive environmental panorama with deep depth-of-field capturing full background architecture and troupe formations.
  * **Medium Shot:** 50mm cinematic perspective with moderate natural background depth and subtle bokeh.
  * **Close-Up:** 85mm portrait framing with creamy optical bokeh ($f/1.4$) dissolving background elements into soft blur to maximize facial expression and lipsync focus.
  * **Low-Angle:** Ground-level upward perspective capturing ground dust, dancing feet, and towering sky/flags.
* **Autonomous Directorial Derivation:** The user must NEVER have to specify location transitions or focal depth; Gemini dynamically enriches each scene's `location_hub`, `shot_type`, and optical background descriptors directly from lyrics and musical energy.

---

## 14. Mandatory Blue-Chip Nature & Extreme Climate Survival Standards (BBC / NatGeo Style)

* **Cinematic 24.0 fps Film Cadence:** Blue-chip wildlife and mountain blizzard survival productions must strictly default to **24.0 fps** with natural motion blur to convey monumental timelessness and heavy blizzard drifts.
* **Visceral Survival Realism & Contrast:** Contrast sub-zero blizzard gales, drifting powder snow, and stone huts with interior hearth embers and steaming tea kettles. Layer authentic procedural foley (howling wind, snow crunching) with sparse acoustic instruments (rubab, mountain flute, low cello drone).
* **Authoritative Measured Narration (YPP Guard):** Paced deliberately (~110–125 wpm) with ecological, geographical, and cultural survival lore to ensure 100% YouTube Partner Program monetization clearance.
