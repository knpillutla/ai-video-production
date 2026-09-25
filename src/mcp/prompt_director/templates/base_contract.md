### CONTEXT EXTRACTION & CULTURAL GROUNDING MANDATE (Studio Grade)
Before writing scenes, music, wardrobe, or dialogue, first extract and lock the exact context from the user prompt:
- Region / location: village, city, temple, festival ground, hotel ballroom, mountain, forest, beach, etc.
- Culture / ethnic identity: Telugu, Telangana, Hindi, Tamil, Bengali, Western, etc.
- Language / dialect: Telugu, Hindi, English, local dialect, spoken style, accent cues.
- Setting: open-air courtyard, paddy field, temple courtyard, banquet hall, hotel lobby, family home, wedding reception, desert, etc.
- Clothing & wardrobe: traditional folk attire, modern smart casual, festive wedding wear, temple silks, regional costumes, partywear.
- Architecture & props: terracotta homes, temple gopuram, paddy fields, banquet stage, chandeliers, reception decor, market streets.
- Lighting & atmosphere: natural daylight, golden hour, indoor luxury lighting, monsoon haze, evening glow, cinematic night mood.
- Character social context: family gathering, village celebration, dance troupe, wedding reception, workplace event, travel documentary crew.

The extracted context must remain consistent across the entire storyboard. Do not invent a different culture, region, or venue than the prompt specifies. If the prompt says Telangana folk dance in a village, the output must remain Telangana village folk — never convert it into a hotel party, wedding hall, or generic family function scene. If the prompt says Hindi family party dance in a hotel, the output must remain a hotel family celebration — never convert it into a rural folk festival.

### MANDATORY CAST & CHARACTER PHYSICALITY DIRECTIVE (Directive 12)
All main characters (both male and female) MUST have a balanced, naturally fit, healthy medium-slender build (neither too skinny/bony nor too chubby, graceful feminine curves with toned midriff for women, lean-athletic fit build for men), strikingly beautiful / handsome, and in their mid-20s (ages 23–27) unless explicitly instructed otherwise.
Autonomously derive setting aesthetics, background environment, and lighting directly from narrative context. Outfits and wardrobe MUST dynamically and authentically match the context of each scene in the story.

### DIRECTORIAL VOCAL GENDER & DELIVERY MANDATE
Autonomously derive 'vocal_gender' ('female', 'male', 'duet', 'background_chorus', 'instrumental') and 'vocal_delivery_type' ('lead_lip_sync', 'background_song', 'voiceover_narration', 'instrumental_only').
If the main protagonist or lead dancer is female, 'vocal_gender' MUST match as 'female' for on-screen singing/lipsync, unless deliberately specified as an off-screen male background chorus singing about her.

### LIGHTING, TIME-OF-DAY & FACE READABILITY MANDATE (Cinematic Quality Guard)
Before generating any scene, determine the time of day and lighting condition from the prompt. If the prompt does not specify night, default to natural daylight for outdoor village, festival, and folk scenes. Outdoor village and folk performances default to 5400K–5600K natural open-air daylight with clean balanced exposure, visible face contours, and clear costume detail. Hotel, family celebration, and premium event scenes default to well-lit event lighting with soft key + fill illumination, bright polished ambience, and readable faces/costumes. Do not allow dark, under-lit frames, heavy shadow blocking, or low-contrast compositions unless the prompt explicitly asks for a night mood or dramatic dark scene. Every shot must clearly expose faces, hair, jewelry, costume fabrics, and expressions.

### DIRECTORIAL FPS & BROADCAST AUDIO STANDARDS (Directive 14)
Autonomously select the optimal 'recommended_fps' matching the story dynamics:
- 60 fps: First-person POV walking tours, fluid scenic landscape tracking, fluid outdoor action.
- 30 fps: Music videos, mass folk dance, upbeat choreography, stage comedy.
- 24 fps: Cinematic drama, narrative shorts, emotional dialogues, slow romance.
Audio standard is 48000 Hz 24-bit broadcast stereo, normalized to -14.0 LUFS.

### UNIVERSAL DYNAMIC WEATHER, CLIMATIC & ATMOSPHERIC KINETICS (Directive 13)
In ALL genres, formats, and themes (grandeur cinema, dance songs, music videos, walking tours, nature documentaries, travel vlogs, drama):
- Heavy Rain / Thunderstorm / Deluge: 'visual_prompt' MUST describe heavy torrential downpour, dense diagonal rain streaks, stormy sky, flooded streets with deep reflective puddles, and water streaming off surfaces. 'motion_prompt' MUST command forceful sheets of falling rain pouring down, dynamic splashing puddle ripples, raindrops bouncing off pavements, and water runoff. 'ambient_sfx' specifies heavy rain roar, rolling thunder, and splashing footsteps.
- Light Rain / Gentle Drizzle / Soft Shower: 'visual_prompt' MUST describe fine delicate drizzle, soft misty daylight, glistening damp pavement with subtle sheen (NO deep flooded puddles), and raindrops beaded on foliage. 'motion_prompt' MUST command gentle micro-raindrops drifting peacefully down, soft subtle shimmering on wet surfaces, and calm breeze. 'ambient_sfx' specifies gentle drizzle patter, soft droplet pings, and soothing calm ambience (NO thunder).
- Snow, Blizzards & Ice: 'motion_prompt' MUST explicitly command dynamic snow physics—swirling blizzard wind gusts whipping powder snow, or delicate crystalline snowflakes gently drifting down, with footwork or dancing kicking up fresh snow powder and visible frosty breath vapor.
- Fiery Hot Sun & Desert Heat: 'motion_prompt' MUST explicitly command thermal kinetics—shimmering heat haze waves rising from hot ground, intense radiant sunbeams, and dynamic dust plumes kicked up into golden light by energetic choreography or movement.
- Cloudy Evening, Sunset & Overcast: 'motion_prompt' MUST command atmospheric sky kinetics—dramatic low-hanging or twilight clouds drifting across the sky, evening breezes fluttering colorful costume fabrics and scarves, and rich shifting ambient glow.
- Fog & Mountain Mist: 'motion_prompt' MUST describe rolling tendrils of atmospheric mist drifting across the scene and between trees or architecture.
- Wind, Autumn Leaves & Festival Dust: 'motion_prompt' MUST describe swirling golden leaves, flying flags/scarves, or vibrant bursts of colored powder/dust skimming across the ground.
Video motion synthesis models animate ONLY what is explicitly commanded in 'motion_prompt'. Never generate static camera-only motion when dynamic weather, climate, or atmospheric conditions are present.

### CINEMA LENS, OPTICAL SENSOR & CAMERA GRAMMAR (Directives 19 & 20)
1. OPTICAL LENS SPECIFICATION (Directive 19):
   - Wide Shots & Establishing: Full-frame 24mm / 28mm prime lens at f/4.0 for tack-sharp architectural and landscape edge-to-edge clarity.
   - Medium Shots: 50mm cinema prime at f/2.8 for natural human eye perspective with gentle background separation.
   - Character Close-ups: 85mm portrait prime at f/1.4 for creamy optical bokeh and facial expression clarity.
   - Blockbuster Epic Cinema: Cooke Anamorphic 40mm with subtle oval bokeh and horizontal flare accents.
2. DIRECTORIAL CAMERA MOVEMENT GRAMMAR (Directive 20):
   - Every motion prompt must command precise cinematic camera movement matching the dramatic beat: slow crane-jib descent, 180° orbiting arc, steadycam forward tracking, or creeping slow push-in. Avoid static unmotivated framing.

### MANDATORY 3-TIER WATER DYNAMICS & MOTION DOMAIN TAXONOMY (Directive 20)
Every scene object in 'scenes' MUST include 'motion_domain' chosen precisely based on fluid physics:
1. 'water_impact_collision' (Kling v3 Pro Route): Use for all heavy cascading waterfalls, rock plunges, violent white-water river rapids churning over boulders, coastal breakers/surf slamming cliff walls, and subjects or wildlife splashing in water.
   - Visual Prompt Mandate: Rich liquid volume, turbulent foam froth at the impact base, atmospheric mist plume.
   - Motion Prompt Mandate: "Powerful volumetric liquid momentum, heavy water crashing down over rock ledge, explosive splash plume and expanding impact ripples at base, billowing fine water vapor. Negative: zero static vertical streaks, zero falling wire artifacts."
2. 'water_fluid' (Alibaba Wan 2.1 Route): Use for continuous smooth laminar rivers, meandering streams, gentle ocean swells, rain, creek currents, and canal flows.
   - Visual Prompt Mandate: Continuous glassy flowing surface, natural wave ripples, specular sunlight glints.
   - Motion Prompt Mandate: "Smooth continuous laminar fluid displacement, natural rolling surface wave crests, dynamic water specular highlights. Negative: gelatinous water, melting foam, static frozen water."
3. 'landscape_solid' (Tencent Hunyuan 1080p Route): Use for calm mirror glacial lakes, still reflection pools, glassy fjords, majestic mountain peaks, and architectural facades.
   - Visual & Motion Prompt Mandate: "Needle-sharp mirror lake reflection, crystal atmospheric stillness, perfectly stable architectural lines."
4. Other Domains: 'wildlife_animal' (Kling), 'human_action' (Kling), 'aerial_fpv' (Kling), 'atmospheric_weather' (Wan 2.1), 'macro_botanical' (Wan 2.1), 'celestial_nightscape' (Hunyuan 1080p).

### MANDATORY AUDIO-VISUAL DURATION SYNCHRONIZATION (Strict Word Budget)
Every scene's spoken dialogue duration MUST match the visual `duration_seconds` of that scene:
- Standard articulate speaking cadence is ~1.8–2.0 words per second (~115–125 words per minute).
- For a 10.0-second scene: write EXACTLY 12–16 spoken words (spoken duration ~6.5–7.5s), leaving 2.5–3.5s of atmospheric visual and ambient sound breathing room before the transition.
- For a 5.0-second scene: write EXACTLY 6–8 spoken words (spoken duration ~3.0–3.5s).
- For a 15.0-second scene: write EXACTLY 18–24 spoken words.
- In spoken narration scenes, NEVER write lengthy or crowded paragraphs exceeding `(duration_seconds * 1.8)` words. Audio delivery and visual display MUST remain in seamless cinematic synchronization.




