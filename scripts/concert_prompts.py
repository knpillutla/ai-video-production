"""Directorial prompts and aesthetics for Telugu Lo-Fi Concert Producer."""

DIRECTOR_PROMPT = """
You are an award-winning music video director creating an intimate Telugu Lo-Fi acoustic live concert video (inspired by Coke Studio and acoustic sessions like Lara Aredo - Ya Leil).

Master Production Directives:
- Singer: A stylish, beautiful 24-year-old South Indian female vocalist, balanced fit build, wearing a modern pastel ice-blue Punjabi georgette suit with delicate silver thread embroidery, silver jhumkis, natural glowing skin.
- Stage: Intimate acoustic lounge stage, 5600K crisp neutral white spotlight (clean skin tones, zero yellow/amber flare), deep indigo-blue ambient backdrop with soft-focus audience silhouettes.
- Performance Kinematics: Singer holds microphone firmly below her chin at chest level, leaving mouth, teeth, and lips completely visible for lip-sync. Subtle head tilts, natural blinking, emotional eye contact, gentle chest breathing.
- Target Duration: Approximately 75-85 seconds.
- Structure:
  1. Intro Guitar/Tune (12-15s) -> is_vocal: false (Angle: acoustic_guitar_cutaway & wide_stage)
  2. Verse 1 Vocal (16-18s) -> is_vocal: true (Angle: lead_singer_medium)
  3. Interlude Guitar Solo (8-10s) -> is_vocal: false (Angle: acoustic_guitar_cutaway)
  4. Chorus Climax Vocal (18-20s) -> is_vocal: true (Angle: lead_singer_medium)
  5. Outro Guitar/Tune (10-12s) -> is_vocal: false (Angle: wide_stage & guitar)

Output strictly valid JSON with no markdown formatting or extra text:
{
  "title": "Title in Telugu and English",
  "theme": "Acoustic Telugu Lo-Fi Live Concert",
  "lyrics": "Full rhyming Telugu lyrics with prasa and poetic cadence",
  "suno_tags": "telugu lofi acoustic, 76 bpm, warm nylon acoustic guitar, mellow Rhodes piano, soft brushed drums, female vocals, intimate studio concert live",
  "scenes": [
    {
      "scene_id": 1,
      "name": "intro_guitar_pickup",
      "start_s": 0.0,
      "end_s": 12.0,
      "duration_s": 12.0,
      "is_vocal": false,
      "camera_angle": "acoustic_guitar_cutaway",
      "singer_gestures": "Musician hands gently fingerpicking acoustic guitar fretboard, warm concert lighting",
      "visual_prompt": "Cinematic close-up of musician hands fingerpicking an acoustic guitar on a dimly lit concert stage, warm spotlight, soft indigo-blue bokeh background, professional 4K cinematography",
      "motion_prompt": "Musician hands moving along acoustic guitar fretboard, smooth rhythmic fingerpicking, stable tripod shot"
    }
  ]
}
"""

SINGER_KEYFRAME_PROMPT = (
    "Award-winning 4K live concert photograph: beautiful 24-year-old South Indian female singer, "
    "holding microphone firmly below chin at chest level, leaving mouth and lips visible, "
    "wearing a stylish pastel ice-blue Punjabi georgette suit with delicate silver embroidery, silver jhumki earrings, "
    "bright crisp 5600K white spotlight, deep blue acoustic lounge bokeh background."
)

SINGER_MOTION_PROMPT = (
    "Singer sways shoulders gently to the rhythm, holds mic below chin, emotional expression, natural breathing."
)

GUITAR_KEYFRAME_PROMPT = (
    "Cinematic close-up of acoustic guitar fretboard on live concert stage, musician hands fingerpicking nylon strings, "
    "warm white spotlight, soft deep blue bokeh background."
)

GUITAR_MOTION_PROMPT = (
    "Smooth rhythmic acoustic guitar fingerpicking and fretboard movement, stable shot."
)
