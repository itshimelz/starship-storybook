# Workflow: Claude Code + ElevenLabs applied to this project

This guide applies the [research](claude-video-research.md) to **Ship 42 · ঘরে ফেরা** (this repo). The current pipeline is code-drawn Canvas2D in `src/template.html`, with Puppeteer rendering frames and ffmpeg encoding. The same process works with HyperFrames (HTML) or Remotion (React).

## 1. Install skills + MCP

```bash
# renderers / motion taste (pick what you use)
claude plugin marketplace add heygen-com/hyperframes && claude plugin install hyperframes@hyperframes
claude plugin marketplace add remotion-dev/claude-code-plugin && claude plugin install remotion@remotion
npx skills add LottieFiles/motion-design-skill

# voice, music, SFX
npx skills add elevenlabs/skills
claude mcp add --transport http elevenlabs https://api.elevenlabs.io/v1/mcp   # then run /mcp to authenticate
```

The directory ElevenLabs connector is a restricted subset. Add it as a custom connector if you need music, image or video tools.

## 2. CLAUDE.md style rules (put this file at the repo root)

```markdown
# Style: code-drawn storybook
- Everything procedural in src/template.html (Canvas2D). No images, no external libs/fonts.
- Flat bold colours on warm palette; wobbly double ink outlines via paint()/wpath(); crayon texture + paper grain.
- Seeded randomness only (mulberry32/hsh). Never Math.random().
- 12 fps; outlines re-jitter every 2 frames (BOIL = floor(f/2)).
- Every motion is a pure function of time: seg/ease/backOut/bump. ?frame=N must render deterministically.
- Scene starts are fixed: 0 / 25 / 55 / 85 / 110 s (total 120 s, 1920x1080).
- Starship must stay recognisable: steel body, black tile shield, 2 fwd + 2 aft flaps, 3 engines; small tasteful face.
- After any change: render the affected frames and LOOK at them before continuing.
```

## 3. Script table

| # Scene | Time | Text on Scene | Visuals | Narration (bn) |
|---|---|---|---|---|
| 1 | 0:00–0:25 | মহাকাশের নিস্তব্ধতা আর ঘরে ফেরার টান | Orbit, door opens, 26 Starlinks, door closes, turn and burn | `vo/s1.txt` |
| 2 | 0:25–0:55 | আগুনের বুক চিরে ফিরে আসা | Re-entry plasma, glowing tiles, flaps steering, bird flock | `vo/s2.txt` |
| 3 | 0:55–1:25 | মেঘ ফুঁড়ে মাটির কাছাকাছি | Clouds, Texas coast, tower, engine flip upright | `vo/s3.txt` |
| 4 | 1:25–1:50 | শ্বাসরুদ্ধকর সেই আলিঙ্গন | Mechazilla arms open, ship slides in through smoke, catch | `vo/s4.txt` |
| 5 | 1:50–2:00 | নতুন এক ভোরের গল্প | Pull-back, steam, dawn | `vo/s5.txt` |

## 4. Voice: per sentence, with timestamps

- Generate **each sentence separately** with ElevenLabs text-to-speech, using a Bengali-capable model (e.g. `eleven_v3`) and a narrator voice. This follows guetteman's tip.
- Keep the files per scene: `vo/scene1.mp3 … vo/scene5.mp3`. You can concatenate the sentence clips into each one, or extend `build.py` to place sentence clips individually.
- Ask for **timestamps** (character or word alignment) when generating, or run ElevenLabs speech-to-text or Whisper on the result to get them.
- Regenerate only the lines that sound off.

## 5. Timing from real durations

- `src/build.py` measures every clip and trims the silence at each end.
- Each clip starts at scene start + 0.2 s. It is time-stretched (`atempo`) only if it would overflow its window.
- Subtitle boundaries come from real pauses (`silencedetect`). If you have word timestamps, replace this with them.
- Move visual beats to the voice, not the other way round. In this project, for example:
  - The scene 1 turn and burn sit on "ছোট্ট বার্ন … মুখ ঘোরাল".
  - The scene 3 flip sits on "হঠাৎ ইঞ্জিনের গর্জন".
  - The scene 4 catch sits on "ইতিহাসের প্রথম আলিঙ্গন".

## 6. Scene-by-scene iteration (don't one-shot)

1. Work on one scene function (`scene1` … `scene5` / `catchWorld`) at a time.
2. Render 5–10 key frames:
   ```bash
   node src/render.mjs build/render.html /tmp/pv 30,120,240 4
   ```
3. Tile them into a contact sheet with ffmpeg `xstack` and **look at it**. Fix anything broken or ugly, then repeat.
4. Only then tune the transitions (crossfades at 25, 55 and 85 s).

## 7. SFX and music after picture lock

- Edit `sfx/cues.json` (`file`, `start`, `gain_db`). Use cue times read off the locked picture.
- Generate each cue with the ElevenLabs `sound-effects` skill or MCP and save it under the same file name in `sfx/`. Generate music with the `music` skill.
- `build.py` mixes it all: the VO is normalised to −16 LUFS, SFX are side-chain ducked under the VO, and a limiter runs at the end.

## 8. Beat sync with aubio (if you add music)

```bash
pip install aubio      # or apt install aubio-tools
aubio beat music.wav > beats.txt   # beat timestamps in seconds
```
Snap cuts and accents to the nearest beat. Examples: the satellite pops, the flap flicks, the catch sparkle burst.

## 9. Render and self-check

```bash
python3 src/build.py
node src/render.mjs build/render.html frames all 7 jpg
ffmpeg -y -framerate 12 -i frames/f%04d.jpg -i build/mix.m4a -map 0:v -map 1:a \
  -c:v libx264 -preset slow -crf 18 -tune animation -r 24 -pix_fmt yuv420p -c:a copy -movflags +faststart -shortest starship-storybook.mp4
ffprobe -v error -show_entries format=duration -of csv=p=0 starship-storybook.mp4   # ≈ 120.0
```

Then extract frames at each VO cue and look at them:
```bash
ffmpeg -ss 100.4 -i starship-storybook.mp4 -frames:v 1 check-catch.png
```
Confirm the picture matches the line being spoken.
