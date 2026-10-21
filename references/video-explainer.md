# Explainer videos

Video is for change over time, derivation, and intuition. It is a poor format for exact procedures, reference tables, or material the reader will skim. Use it when the idea has a before/after, a build-up, or a visual rhythm that prose cannot carry.

## Preconditions

Check the toolchain before promising a video:

```bash
command -v ffmpeg
command -v ffprobe
command -v python3
command -v node
command -v npx
# Manim route only:
command -v manim
```

If the chosen renderer is missing, do not install it silently. Offer a lightweight fallback: an HTML/CSS animation, a narrated storyboard, or a static explainer. If the user approves an install, use a virtual environment or a local project directory inside the artifact directory.

## Pipeline

```text
1. Brief and claim ledger
2. Narration script
3. Storyboard with timings
4. Text-to-speech per scene
5. Measure audio durations
6. Build scenes with the chosen renderer to match durations
7. Render scenes silently
8. Concatenate video and audio
9. Add captions and transcript
10. QA and preview
```

Do not render the full video before previewing one scene. Do not pay for a long TTS job before the script is approved.

## Renderer choice

| Shape of the idea | Renderer | Load |
| --- | --- | --- |
| Equations, axes, geometry, LaTeX, 3D math | Manim Community | `manimce-best-practices` |
| HTML/CSS layouts, typography, UI, charts, code, kinetic type, captions | HyperFrames | `hyperframes-video` |
| Existing React/Remotion composition | Remotion | separate React toolchain |

HyperFrames and Remotion are alternatives, not one product. HyperFrames renders a plain HTML document with a paused GSAP timeline; Remotion renders a React component. "Remotion Hyperframe" is not a package. If the user says "Remotion", ask whether they mean Remotion (React) or HyperFrames (HTML).

A hybrid package is valid: Manim for the mathematical core, HyperFrames for title/chapter/end cards. Match palette, type scale, and safe margins across both.

## HyperFrames path

Use this when the visuals are better expressed as a web page than as Manim objects.

```bash
# 1. scaffold (pin the CLI version)
HYPERFRAMES_SKIP_SKILLS=1 npx hyperframes@0.8.181 init my-video \
  --non-interactive --resolution=landscape

# 2. author index.html + compositions/scene.html, then validate
cd my-video
npx hyperframes@0.8.181 check

# 3. preview without blocking the agent
npx hyperframes@0.8.181 preview --background
npx hyperframes@0.8.181 preview --status

# 4. render
npx hyperframes@0.8.181 render --fps 30 --quality high --workers 4 -o out.mp4
```

Composition rules:

- Root `data-composition-id`, `data-duration`, `data-width`, `data-height`.
- Timed elements: `class="clip"`, `data-start`, `data-duration`. `data-track-index` is a Studio hint only.
- One paused GSAP root timeline per composition, registered on `window.__timelines["<composition-id>"]`.
- Media stays a direct child of the host root if it must be seeked/decoded.
- No `Math.random()`, `Date.now()`, or network fetches. Vendor GSAP or pin its version.
- Add `@font-face` for every custom/CJK family; lint rejects undeclared families.
- If lint reports `nested_structure_needs_subcomposition`, move the scene into a sub-composition mounted with `data-composition-src`.

Read `hyperframes-video` for the full contract, template, audio/caption patterns, pitfalls, and QA checklist. A 10 s 1080p30 high-quality render typically takes ~14 s with 4 workers in this environment.

## Brief

```text
Thesis: <one sentence>
Audience: <prior knowledge>
After watching, the viewer can: <three verbs>
Duration: <60-120 seconds>
Language: <language>
Source: <authoritative source>
Tone: <calm, precise, curious>
Constraints: <no jargon, no equations, etc.>
```

## Narration

- Write for the ear: short sentences, concrete nouns, active verbs.
- One idea per scene. Do not narrate what the viewer can already see.
- Use silences. A two-second pause after an insight is part of the explanation.
- Introduce a symbol before you use it. Say the name, show the symbol, then use it.
- Do not read equations aloud symbol by symbol unless the symbols are the point.
- Avoid "as you can see", "obviously", and "simply".
- End with a one-sentence recap and one boundary case.

Speaking-rate budget (approximate):

| Duration | Words at 140-160 wpm |
| --- | --- |
| 60 s | 140-160 |
| 90 s | 210-240 |
| 120 s | 280-320 |

Leave 10-15% of the duration for pauses and visual beats.

## Storyboard

Use a table with one row per scene:

| Scene | Time | Narration | Visual | Equation or label | Transition |
| --- | --- | --- | --- | --- | --- |
| 1 | 0:00-0:12 | ... | ... | ... | Cut |
| 2 | 0:12-0:30 | ... | ... | ... | Morph |

Each scene needs one focal object and one change. If a scene has two messages, split it.

## Text-to-speech

Choose an option the user can legally use and pay for:

| Option | Notes |
| --- | --- |
| ElevenLabs | High quality; requires an API key and may cost money. Ask before use. |
| Kokoro | Local, open-weight option; check the current installation and license. |
| Piper | Local and lightweight; voice quality varies by model. |
| edge-tts | Network service; check availability and terms. |
| Recorded human | Best for nuance; requires a speaker and editing. |

Rules:

- Read the key from an environment variable. Never print it, commit it, or put it in a command that appears in logs.
- Generate one audio file per scene. Name files with zero-padded scene numbers.
- Normalize loudness before muxing. Aim for a consistent integrated loudness; do not clip.
- Keep the narration script as the source of truth for captions.

## Manim patterns

Use Manim Community. Keep each scene in its own file or class.

```python
from manim import *

class Scene01(Scene):
    def construct(self):
        title = Text("Why attention mixes tokens", font_size=44)
        self.play(Write(title), run_time=1.2)
        self.wait(1.5)
```

Useful ideas:

- `Text` for prose, `MathTex` for equations, `Create` for lines and arrows.
- `TransformMatchingTex` to build an equation across steps without jump cuts.
- `ValueTracker` and `always_redraw` for a parameter that changes continuously.
- `VGroup` to keep a label attached to its object.
- `self.wait(duration)` to match a narration beat.
- Use a consistent color grammar: one color for the focal object, one for the transform, one for the result.

Keep the frame uncluttered. Use the safe area; do not put text near the edges. At 1080p, keep body text at 28 px or larger, titles at 40 px or larger.

## Sync and mux

The robust approach: generate audio first, measure durations, then render each scene to match its audio.

```bash
ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 audio/scene_01.mp3
```

In the scene, use the measured duration to set the final `self.wait()`. Render silently:

```bash
manim -qm --format=mp4 scenes/scene_01.py Scene01
```

Concatenate scenes in order:

```bash
printf "file '%s'\n" scenes/rendered/scene_01.mp4 scenes/rendered/scene_02.mp4 > scenes.txt
ffmpeg -f concat -safe 0 -i scenes.txt -c copy output/video_silent.mp4
```

Concatenate narration in the same order, then mux:

```bash
printf "file '%s'\n" audio/scene_01.mp3 audio/scene_02.mp3 > audio.txt
ffmpeg -f concat -safe 0 -i audio.txt -c copy output/narration.mp3
ffmpeg -i output/video_silent.mp4 -i output/narration.mp3 -c:v copy -c:a aac -b:a 192k -shortest output/final.mp4
```

If the durations drift, adjust the final hold in each scene, not the audio tempo. Re-render only the scene that drifted.

## Captions and transcript

- Keep `narration.md` as the transcript.
- Create `captions.srt` from the scene boundaries. If exact word timing matters, align the narration with a speech-to-text tool and review the output.
- Burn in captions only if the user asks. Prefer a sidecar `.srt` so the video remains editable.
- Check that captions do not cover the focal object.

## QA checklist

- [ ] The thesis is clear in the first 15 seconds.
- [ ] The video is 60-120 seconds unless the user asked for another length.
- [ ] Each scene has one focal object and one change.
- [ ] Narration matches the visuals; no sentence describes something not on screen.
- [ ] Equations are introduced before use.
- [ ] Audio is present, normalized, and not clipped.
- [ ] The final frame holds long enough to read.
- [ ] Captions and transcript are present.
- [ ] The video plays from start to finish with no black frames or frozen audio.
- [ ] The file is 1080p or the requested resolution.
- [ ] Sources and simplifications are in the description or final card.
- [ ] A static fallback (recap + transcript) exists.

Use `python3 scripts/check_artifact.py --kind video output/final.mp4` for stream and sidecar checks. Sample frames at 10%, 50%, and 90% of the duration.

## Cost and consent

- Ask before using a paid TTS service, a paid API, or a long render.
- Preview one scene at low resolution before rendering the full video.
- Cap the duration and resolution unless the user asks for more.
- Do not upload private source material to a third-party service without permission.

## Fallbacks

If video tooling is unavailable, deliver in this order:

1. An HTML/CSS animation with the same storyboard and narration text.
2. A narrated storyboard with one image per scene.
3. A static explainer with a transcript and a clear statement that no video was rendered.

Never claim a video exists when only a storyboard was produced.
