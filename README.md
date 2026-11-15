# Ship 42 · ঘরে ফেরা — storybook animation (120 s, 1920x1080)
- starship-storybook.mp4        final (H.264 crf18, 24fps container of 12fps animation, AAC 192k), ~87 MB
- starship-storybook-small.mp4  same, crf25, ~33 MB (for sharing)
- index.html                    self-contained live version (embedded audio, Play button). ?frame=N renders one frame (0..1439)
- scene-1..5.png                one still per scene
## Audio is swappable
- VO clips: vo/scene1.mp3 .. vo/scene5.mp3 (placeholder = edge-tts bn-BD-PradeepNeural). Scene starts fixed at 0/25/55/85/110 s (+0.2 s lead); clips auto-trimmed and sped up (atempo) only if they overflow the window.
- SFX: sfx/*.wav + sfx/cues.json (file, start s, gain dB). Placeholders are procedural (src/make_sfx.py). Replace any file with an ElevenLabs SFX of the same name (or edit cues.json); SFX are side-chain ducked under the VO.
## Rebuild
python3 src/build.py                                   # mix + subtitles + index.html
node src/render.mjs build/render.html /tmp/frames all 7 jpg
ffmpeg -y -framerate 12 -i /tmp/frames/f%04d.jpg -i build/mix.m4a -map 0:v -map 1:a -c:v libx264 -preset slow -crf 18 -tune animation -r 24 -pix_fmt yuv420p -c:a copy -movflags +faststart -shortest starship-storybook.mp4
(Only the audio changed? Skip the render and just re-run the ffmpeg mux step, since the frames don't depend on audio. Subtitle timing does, so re-render if VO changes.)

## Going further

- [docs/claude-video-research.md](docs/claude-video-research.md): research on agent-driven video. It covers notable X posts, skills and repos with install commands (Remotion, HyperFrames, Video Use, LottieFiles motion-design, ElevenLabs skills and MCP), a recommended process and example prompts.
- [docs/workflow-claude-elevenlabs.md](docs/workflow-claude-elevenlabs.md): that research applied to this project. It covers skills and MCP setup, CLAUDE.md style rules, the script table, per-sentence voice with timestamps, timing from real durations, scene-by-scene iteration, SFX and music after picture lock, aubio beat sync, and render plus frame self-check.
