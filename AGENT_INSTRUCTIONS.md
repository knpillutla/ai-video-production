# AI Agent Instructions & Engineering Guidelines
# Project: Professional AI Video Producer Studio

> **Scope:** Mandatory guidelines for all AI agents, engineers, and subagents contributing to this codebase.  
> **Core Mandate:** High performance, extreme token efficiency, reusable deterministic scripts over LLMs, modular functional design, performance optimization, and a strict 300-line limit per file.

---

## 1. Golden Rules (Non-Negotiable)

1. **Token Economy First:** Minimize LLM calls and context size. If a task can be calculated, parsed, or formatted with deterministic code, **never call an LLM**.
2. **Deterministic Script Reusability:** Build standalone, reusable scripts and utilities for recurring operations (formatting, compliance scanning, audio ducking, subtitle parsing, thumbnail rendering).
3. **Hard 300-Line File Limit:** **No code file may exceed 300 lines.** If a file approaches 250 lines, refactor immediately into focused sub-modules.
4. **Functional & Modular Design:** Favor pure functions, explicit dependency injection, clear interface contracts, and zero hidden side effects.
5. **High-Performance Architecture:** Enforce asynchronous non-blocking I/O, streaming media transfers (zero RAM bloat), connection pooling, single-pass FFmpeg filter graphs, and vectorized math.
6. **Zero Duplication & Single Source of Truth:** Never create or keep duplicate code, redundant helpers, or overlapping documentation files. Maintain exactly one authoritative source file per domain. Delete superseded drafts immediately.
7. **Fail-Fast & Idempotent:** Every pipeline step must be replayable and idempotent without corrupting data or consuming redundant API credits.
8. **Pre-Flight Cost Transparency & Explicit Confirmation:** UI submissions must NEVER immediately trigger generation. The pipeline must first calculate and display an itemized cost breakdown (LLM tokens, TTS characters, visual assets, cloud compute) and require explicit user confirmation before executing billable jobs.
9. **Model Testing Safety & Cost Guard (Automated Tests Mandate):** When testing models as part of automated tests, **only run one test only with 10 sec duration**; ensure we do not call more than one test, to save on costs. The standard automated test suite (`pytest`) must ALWAYS run 100% locally with offline deterministic mocks/fallbacks even if model keys are present in `.env`.
10. **Terraform-Only IaC:** Always create Terraform scripts only for all cloud platforms (Azure, GCP, AWS, Multi-Cloud). Never use Bicep, ARM, CloudFormation, or platform-specific template languages.
11. **Topic, Metadata & Story Deduplication & User Alerting:** Every time a video is created, save the topic, metadata information (genre, tags, target audience, format), and the final story created from the script into the persistent Topic Memory vault. When the user creates for similar metadata or topic (cosine similarity $\ge 0.80$ or heavy metadata overlap), do not create duplicate content; block generation immediately and alert the user with a descriptive duplicate alert.


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


