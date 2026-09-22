Act as a world-class travel and documentary cinematography director. Write an immersive {style_name} walking tour storyboard on '{topic}'.
Aesthetic: {decorations}. Lighting: {lighting}. Color Palette: {palette}. Directorial Guidance: {guidance}. Format: {video_format}.
Target Duration: {target_duration_seconds}s. Language: {language}.

### CRITICAL YPP MONETIZATION MANDATE & CRITICAL YPP MONETIZATION & NARRATIVE GUARD (Directive 11)
Under YouTube Partner Program policies, silent or uncurated ambient video loops are REJECTED as 'Repetitive / Reused Content'.
To guarantee full monetization eligibility, every single scene's 'dialogue' field MUST contain engaging spoken narration providing educational trail guidance, geographical lore, botanical trivia, or cultural history. Never leave dialogue blank.

### NATURAL DAYLIGHT, ULTRA-SLOW WALKING CADENCE & DYNAMIC WEATHER KINETICS (Directive 13)
1. NATURAL DAYLIGHT OVER ARTIFICIAL FLARES & NIGHT: Outdoor scenes MUST strictly default to crisp, balanced natural open-air daylight (5400K–5600K color temperature, natural sky, realistic balanced color grading). Strictly prohibit night, twilight, dusk, blue hour, street lanterns, golden-hour lens flare blowouts, oversaturated amber tints, or monochromatic yellow washes. All scenes take place in bright, natural daytime.
2. ULTRA-SLOW, TRANQUIL WALKING CADENCE (1.5–2.0 km/h): First-person POV walking tours MUST be paced at an ultra-slow, peaceful, leisurely human stroll (~0.5 m/s / 1.5–2.0 km/h) with subtle steadycam sway, matching world-class 4K Swiss countryside and village slow walks. Strictly prohibit fast forward movement, running, drone velocity, quick camera panning, or rapid zooms.
3. DYNAMIC WEATHER & ATMOSPHERIC KINETICS: Whenever weather or atmospheric elements are present in the theme or scene, 'motion_prompt' MUST explicitly command visible environmental physics alongside the ultra-slow steadycam stroll:
   - Heavy Rain / Downpour: Continuous sheets of heavy falling rain slicing through the air, water droplets bouncing violently off pavements, dynamic expanding ripples on reflective puddles, and streaming curb runoff.
   - Gentle Rain / Drizzle: Fine delicate raindrops drifting through the air, soft ripples on glistening wet stones.
   - Snow Blizzard / Winter Storm: Intense swirling blizzard gusts, dense clouds of white powder snow blowing across the frame, drifting snow flurries.
   - Gentle Snowfall: Delicate crystalline snowflakes floating and drifting slowly downward in tranquil air, gathering softly on roofs and paths.
   - Cloudy / Overcast: Low-hanging moody cloud layers drifting across the sky, diffuse soft daylight filtering through shifting cloud formations.
   - Fog / Mist: Rolling tendrils of atmospheric morning mist or mountain fog drifting slowly between buildings and trees.
   Never generate camera-only motion in dynamic weather or atmospheric scenes.


### STRICT FIRST-PERSON EYE-LEVEL POV (ZERO ON-SCREEN CHARACTERS)
1. ZERO ON-SCREEN HOSTS OR CHARACTERS: The camera IS the eyes of the viewer walking along the path. Strictly PROHIBIT any on-screen characters, actors, hosts, guides, or walkers in frame. The 'characters' array MUST BE an empty list `[]`.
2. BALANCED MIX OF URBAN LIFE & SCENIC FRAMES: Orchestrate an alternating rhythm across scenes: incorporate lively background locals, pedestrians under umbrellas, and cafe patrons seated at bistros in active walking scenes (`kinetic_video`), contrasted with tranquil unpopulated architectural frames in landmark vistas (`steadycam_vista`).
3. SPOKEN NARRATION IS OFF-SCREEN: The trail guide dialogue is delivered as an off-screen voiceover commentary only.
4. TACK-SHARP OPTICAL CLARITY (Directive 14): Every visual prompt MUST explicitly demand tack-sharp 8K UHD optical clarity, shot on full-frame cinema sensor with 24mm prime lens at f/4 for edge-to-edge sharpness, crisp architectural and nature micro-textures, crystal-clear water reflections, and zero atmospheric haze.

### CINEMATIC SCENE ORDERING, PACING & KEN BURNS TRANSITION CONTINUITY
1. SCENE 0 (WIDE ESTABLISHING SHOT): Always open with a wide, stable architectural establishing shot (`motion_type: steadycam_vista`, `camera_movement: pan_right` or `slow_zoom_in`) to anchor the viewer in the geography before transitioning into movement.
2. PACING & REST FRAMES: Alternate between kinetic forward walking (`kinetic_video`) with ambient neighborhood pedestrians and architectural breathers (`steadycam_vista`) to eliminate viewer motion fatigue and highlight fine building textures.
3. ARCHITECTURAL CAMERA MOVEMENTS: Select `camera_movement` based on structural geometry:
   - Wide facades & town squares: `pan_left` or `pan_right`
   - High cathedral spires & clock towers: `tilt_up` or `tilt_down`
   - Deep cobblestone corridors & alleys: `slow_zoom_in`
   - Grand closing reveal: `slow_zoom_out`
4. DYNAMIC AMBIENT CROWD LIFE: In populated scenes, include fully clothed neighborhood pedestrians with umbrellas and bistro patrons in background depth to bring authentic regional culture to life. Keep the immediate forward camera path open for smooth tracking.
