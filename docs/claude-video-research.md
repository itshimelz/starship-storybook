# Research: making videos with Claude (Code) + skills — what people on X are doing

This is a collection of notable X posts, skills, tools and repos, plus a recommended process and example prompts for agent-driven video (motion graphics, explainers, promos, storybook animation). It was gathered while building this repo.

> Note: the links are the original sources. Some prompts below are paraphrased; those are labelled.

---

## 1. Notable posts

| Who | What | Link |
|---|---|---|
| @Remotion | Remotion **Agent Skills** launch (`npx skills add remotion-dev/skills`) | https://x.com/Remotion/status/2013626968386765291 |
| @Remotion | Headline / quickstart prompt example | https://x.com/Remotion/status/2017915342022979923 |
| @JNYBGR (Jonny Burger, Remotion) | Skills launch thread | https://x.com/JNYBGR/status/2013650328919405054 |
| @JNYBGR | Step-by-step tip: *"Go step-by-step instead of trying to one-shot it."* | https://x.com/JNYBGR/status/2013689919504359509 |
| @JNYBGR | "Vibe-editing" video with an agent | https://x.com/JNYBGR/status/2013313893683085703 |
| @JNYBGR | Vibe-editing follow-up | https://x.com/JNYBGR/status/2013316427575374285 |
| @SelmanKahyaX | Claude Code + ElevenLabs video playbook | https://x.com/SelmanKahyaX/status/2029551056728777183 |
| @SelmanKahyaX | Playbook follow-up | https://x.com/SelmanKahyaX/status/2029551059509665935 |
| @gregpr07 | **Video Use** (browser-use) | https://x.com/gregpr07/status/2044554557221675380 |
| @HilaShmuel | Promo-video process: script table → voice → music → SFX | https://x.com/HilaShmuel/status/2041911718696137157 |
| @HilaShmuel | Resulting promo | https://x.com/HilaShmuel/status/2041579428044480777 |
| @charliejhills | "28 things to install into Claude" | https://x.com/charliejhills/status/2108971814005424566 |
| @thegreatest_sv | Agent-driven video studio | https://x.com/thegreatest_sv/status/2112609040962359354 |
| @guetteman | Voiceover sentence-by-sentence tip | https://x.com/guetteman/status/2028449242126172414 |
| @guetteman | Follow-up | https://x.com/guetteman/status/2028449247025135921 |
| @DozaVisuals | Motion-graphics with agents | https://x.com/DozaVisuals/status/2115418037700469005 |
| @ardaaltinors | **aubio** beat-sync tip (cut and animate on detected beats) | https://x.com/ardaaltinors/status/2029609414492069906 |

Further reading from @charliejhills:
- https://charliehills.substack.com/p/28-things-to-install-into-claude
- https://charliehills.ai/guides/claude-code-motion-graphics-the-6-free-repos-and-the-starter-bri

---

## 2. Skills, tools and repos (with install commands)

### Remotion (React → video)
- Skills: https://github.com/remotion-dev/skills
  ```bash
  npx skills add remotion-dev/skills
  ```
- Docs: https://www.remotion.dev/docs/ai/coding-agents
- Claude Code plugin: https://www.remotion.dev/docs/ai/claude-code-plugin
  ```bash
  claude plugin marketplace add remotion-dev/claude-code-plugin
  claude plugin install remotion@remotion
  ```

### HyperFrames (HeyGen) — HTML → video
- Repo: https://github.com/heygen-com/hyperframes
- Docs: https://hyperframes.heygen.com/guides/with-claude-code
  ```bash
  claude plugin marketplace add heygen-com/hyperframes
  claude plugin install hyperframes@hyperframes
  # or
  npx skills add heygen-com/hyperframes
  ```

### Video Use (browser-use)
- https://github.com/browser-use/video-use

### LottieFiles motion-design skill
- https://github.com/LottieFiles/motion-design-skill
  ```bash
  npx skills add LottieFiles/motion-design-skill
  ```

### ElevenLabs
- Skills: https://github.com/elevenlabs/skills. It includes `setup-api-key`, `agents`, `speech-to-text`, `text-to-speech`, `music` and `sound-effects`.
  ```bash
  npx skills add elevenlabs/skills
  ```
- MCP server: https://elevenlabs.io/docs/eleven-api/resources/mcp-server
  ```bash
  claude mcp add --transport http elevenlabs https://api.elevenlabs.io/v1/mcp
  # then inside Claude Code:
  /mcp
  ```
  The directory connector is a **restricted subset**. You need a **custom connector** for images, video and music.

### More repos
- https://github.com/jonnyburger/vibe-coded-video
- https://github.com/tuzhechen2005/opus-video-skills
- https://github.com/hculap/skill-motion-graphic
- https://github.com/bangtutorial/bang-motion
- derek-zhuolin/motion-skill
- bowtiedswan/animejs-skills

### Renderers / libraries also named
Manim, Motion Canvas, Revideo, FFmpeg, GSAP, anime.js, three.js, Whisper (for transcription and word timestamps).

---

## 3. Recommended process

These are the common threads across the posts above:

1. **Install the skills first.** Use Remotion or HyperFrames for rendering, LottieFiles motion-design for motion taste, and ElevenLabs skills and MCP for voice, music and SFX.
2. **Script as a table** (Hila): `# Scene | Text on Scene | Visuals | Narration text`.
3. **Voice per sentence, with timestamps** (guetteman, Selman). Export the voiceover sentence by sentence, not as one continuous take, so each line can be timed, swapped or regenerated on its own.
4. **Drive timing from the real audio durations.** Match every word or sentence to a scene (Selman).
5. **Go step-by-step, not one-shot** (Jonny Burger). Build and review one scene at a time, then add transitions.
6. **Music and SFX after picture lock.** Fade the music under the VO (Selman mentions Pixabay music; Hila uses Suno for music and generated SFX).
7. **Beat sync** with aubio: detect beats or onsets and cut or animate on them (ardaaltinors).
8. **Render, look at the frames, iterate.**

---

## 4. Example prompts

**Remotion quickstart**
```bash
npx create-video --yes --blank my-video
cd my-video
npx remotion skills add
npm run dev
claude
```
```
/remotion-create Make a promo video for a record store
```

**HyperFrames**
```
Using /hyperframes:hyperframes, make a 10-second product intro for https://example.com.
```

**Hila Shmuel: script table**
```
create a script in a table for a promo 30-40 seconds video about cabinet. Have columns for: # Scene, Text on Scene, Visuals, Narration text.
```
She follows it with prompts to generate the voice, regenerate weak lines, make music with Suno, and add SFX. See her post for those.

**Selman Kahya: brief** *(paraphrased)*. Study the codebase, write the transcript, generate a timestamped voiceover with ElevenLabs, match every word to a scene, add transitions, add Pixabay music with a fade, render, then iterate.

**guetteman: voiceover**
```
Export voiceover sentence by sentence. Not as one continuous take...
```

**LottieFiles motion brief.** Give the motion-design skill a short brief covering purpose, mood, easing and timing so the motion has intent. See the skill's README.

**aubio beat sync** (ardaaltinors). Run aubio on the music track to get beat timestamps, then align cuts and accents to them.

**Jonny Burger**
```
Go step-by-step instead of trying to one-shot it.
```
