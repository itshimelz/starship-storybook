# Ship 42 · ঘরে ফেরা — a code-drawn storybook animation

A 2-minute (120 s, 1920×1080) animated short about Starship Ship 42 coming home: payload deploy → re-entry → flip over the Texas coast → Mechazilla catch → dawn. It has a Bengali voiceover and subtitles.

**Every pixel is drawn by code.** One HTML file uses Canvas2D and plain JavaScript. There are no images, no libraries and no image generator. The style follows Vamsi Batchu's Gemini "code-drawn storybook" post: flat bold colours, wobbly ink outlines, crayon and paper-grain texture, and boiling lines at 12 fps.

| Output | Path |
|---|---|
| Live player, self-contained with audio embedded and a Play button | `index.html` |
| Scene stills | `scene-1.png … scene-5.png` (not in the repo, see below) |
| Final MP4 | `starship-storybook.mp4`, built locally and git-ignored |

---

## 1. Setup

Requirements:
- Node ≥ 18
- Python ≥ 3.10 with `numpy`
- `ffmpeg`
- Google Chrome or Chromium

```bash
npm install                       # puppeteer-core only
pip install numpy edge-tts        # edge-tts is only needed for the free voice option
export CHROME=/usr/bin/google-chrome   # path to your Chrome/Chromium
```

## 2. Timeline (fixed)

| # | Time | Scene | VO file |
|---|---|---|---|
| 1 | 0:00–0:25 | Orbit above Earth: door opens, 26 Starlinks out, door closes, yaw-turn and burn | `vo/scene1.mp3` |
| 2 | 0:25–0:55 | Re-entry: tiles glow orange/purple, plasma tongues, 4 flaps steering, migrating-bird flock | `vo/scene2.mp3` |
| 3 | 0:55–1:25 | Down through clouds, Texas coast and tower appear, blue-gold engine flip upright | `vo/scene3.mp3` |
| 4 | 1:25–1:50 | Mechazilla arms wait open, ship slides in through smoke and fire, arms catch it, engines cut | `vo/scene4.mp3` |
| 5 | 1:50–2:00 | Continuous pull-back, steam from scorched steel, dawn sky | `vo/scene5.mp3` |

Frames run at 12 fps, 1440 in total. Scene starts are `SCENES=[0,25,55,85,110,120]` in `src/template.html`. Scenes 1→2, 2→3 and 3→4 crossfade; 4→5 is one continuous camera move.

## 3. Art in code (`src/template.html`)

- **Seeded randomness:** `mulberry32` plus a hash. Nothing uses `Math.random()`, so every frame is reproducible.
- **Wobbly ink:** `wpath()` densifies each polygon to about 13 px steps. It displaces the points with smooth value-noise (about 2 px on screen) and redraws them as quadratic curves. `paint()` fills the shape, then strokes the outline twice with different seeds, like a pencil going over a line.
- **Crayon texture:** two pattern canvases are generated once from thousands of short semi-transparent strokes, one light and one dark. They are overlaid inside each shape, plus a soft inner edge shade.
- **Paper grain:** a seeded noise canvas blended with `overlay`, plus a vignette.
- **Starship (`ship()`):**
  - Local space, nose up. Ogive nose, steel body with highlight and shade stripes, weld rings.
  - Black tiled heat shield on one side that glows during re-entry.
  - 2 forward and 2 aft flaps, each rotating on a hinge.
  - Three engine bells with a layered flame (`shipFlame`).
  - "Pez" payload door.
  - The face (`shipFace`) is always drawn upright in screen space: blinking eyes, blush, and calm / wide / happy moods.
- **Scenery:**
  - Earth limb with a drifting continents band.
  - Starlink satellites that unfold their arrays.
  - Plasma tongues, wind streaks, clouds made from bump outlines, perspective sea waves.
  - Coast and tower, Mechazilla tower with truss arms, smoke and steam puffs (`blob()`).

## 4. Procedural animation

- `renderFrame(f)` sets `BOIL = floor(f/2)`, so outlines re-jitter every 2 frames.
- It picks the scene and calls `sceneN(localTime)`.
- Every motion is a pure function of time, built from `seg`, `ease`, `backOut` and `bump`. Examples: `door`, `flip`, `burn`, `heat`, `ign`, `fp` and the arm close `cl`.
- Satellites, sparks, smoke and steam are deterministic particles indexed by `i` with a birth time.
- Modes:
  - `index.html?frame=N` renders exactly frame N.
  - `?capture=1` is the capture mode used by the renderer.
  - With no query string you get the live player. The audio clock drives the frame number.

## 5. Voice (per-scene, swappable)

Put five clips at `vo/scene1.mp3 … vo/scene5.mp3`. The scripts are in `vo/s1.txt … vo/s5.txt`.

- **Free option, edge-tts (Bengali, Bangladesh):**
  ```bash
  for i in 1 2 3 4 5; do edge-tts --voice bn-BD-PradeepNeural --rate=-5% -f vo/s$i.txt --write-media vo/scene$i.mp3; done
  # scene 5 has only a 10 s window: use --rate=+15% for it
  # alternative voice: bn-BD-NabanitaNeural. The service is flaky, so retry on "No audio received".
  ```
- **ElevenLabs:** generate each script with a Bengali-capable model (`eleven_v3`) and a narrator voice, then save the files as `vo/sceneN.mp3`. Bengali narrator voices found in the library: "Rahat" and "Hamim – Deep, Mature, Calm".

`src/build.py` trims leading and trailing silence from each clip and starts it at the scene start + 0.2 s. It applies `atempo` only if a clip would overflow its window.

## 6. Sound effects

`sfx/cues.json` lists every cue as `{file, start (s), gain_db}`.

```bash
python3 src/make_sfx.py      # writes procedural placeholder WAVs plus cues.json
```

The cues are:
- **Scene 1:** space hum, door open and close (servo plus clunk), 26 satellite puffs, ignition burn
- **Scene 2:** re-entry roar, flap servos
- **Scene 3:** cloud wind, ocean waves, engine roar at the flip
- **Scene 4:** engines through smoke, tower arms, catch clank, engine cutoff
- **Scene 5:** steam hiss, breeze, triumphant swell

To use real recordings (for example ElevenLabs sound effects), replace any WAV under the same name, or edit `cues.json`. Starts are synced to on-screen events.

## 7. Subtitles

`build.py` splits each script at `।`. It finds pauses in the voice clip with ffmpeg `silencedetect` and places sentence boundaries at the pause nearest each sentence's share of the characters. The result goes to `build/subs.json`, which is injected into the HTML as `SUBS`.

## 8. Audio mix and HTML build

```bash
python3 src/build.py
```

What it does:
- Positions the voice clips with `adelay`, mixes them and normalises to −16 LUFS (`loudnorm`).
- Positions the sound effects and ducks them under the voice with `sidechaincompress`.
- Runs a limiter and writes `build/mix.wav`, `build/mix.m4a` and `build/mix.mp3`.
- Writes `index.html`, a self-contained live version with the mix embedded as base64.
- Writes `build/render.html`, the silent capture copy.

## 9. Render frames with Puppeteer

```bash
node src/render.mjs build/render.html frames all 7 jpg     # 1440 frames, 7 parallel pages (~20 s on 8 cores)
node src/render.mjs build/render.html stills 110,400,760,1220,1400 1 png   # scene stills
```

Each page calls `renderFrame(f)` and saves `canvas.toDataURL()`.

## 10. Encode

```bash
ffmpeg -y -framerate 12 -i frames/f%04d.jpg -i build/mix.m4a -map 0:v -map 1:a \
  -c:v libx264 -preset slow -crf 18 -tune animation -r 24 -pix_fmt yuv420p \
  -c:a copy -movflags +faststart -shortest starship-storybook.mp4
# smaller share copy
ffmpeg -y -i starship-storybook.mp4 -c:v libx264 -preset slow -crf 25 -tune animation -pix_fmt yuv420p -c:a aac -b:a 160k -movflags +faststart starship-storybook-small.mp4
```

Check the duration: `ffprobe -v error -show_entries format=duration -of csv=p=0 starship-storybook.mp4` should print about 120.0.

## Files

```
src/template.html   the whole animation (art + timeline + player), with __AUDIO__/__SUBS__ placeholders
src/build.py        VO fitting, subtitles, audio mix, builds index.html + build/render.html
src/make_sfx.py     procedural placeholder SFX + sfx/cues.json
src/render.mjs      Puppeteer frame renderer
vo/s1..s5.txt       Bengali VO scripts
sfx/cues.json       SFX cue sheet
index.html          built live version (audio embedded)
```

**Binary assets are not in this repo.** These are the `vo/*.mp3` clips, `sfx/*.wav`, the scene PNGs and the MP4s. They were made on a box whose only GitHub access is a text-only API connector. Regenerate them with the steps above, or add them with a normal `git push`.

## Going further

- [docs/claude-video-research.md](docs/claude-video-research.md): research on agent-driven video. It covers notable X posts, skills and repos with install commands (Remotion, HyperFrames, Video Use, LottieFiles motion-design, ElevenLabs skills and MCP), a recommended process and example prompts.
- [docs/workflow-claude-elevenlabs.md](docs/workflow-claude-elevenlabs.md): that research applied to this project. It covers skills and MCP setup, CLAUDE.md style rules, the script table, per-sentence voice with timestamps, timing from real durations, scene-by-scene iteration, SFX and music after picture lock, aubio beat sync, and render plus frame self-check.
