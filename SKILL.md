---
name: explain-anything
description: |
  Turn complex material into understanding-optimized artifacts instead of plain prose: calibrated answers, STE-lite documents, diagrams, offline HTML explainers, Manim/HyperFrames videos, and 2-5 minute knowledge films. Also supports reverse mode: analyze an existing video into evidence-backed shots, then rebuild or remix its structure.

  Model-agnostic by design. At intake, explicitly ask which provider and model to use for analysis, storyboard, implementation, and review; record the choices in project.json. Never assume a provider or model from its name.

  Use when the user asks to explain, teach, simplify, visualize, or help them understand a concept, paper, system, algorithm, policy, or decision; mentions ASD-STE100, diagrams, interactive HTML, 3Blue1Brown-style videos, HyperFrames, Manim, or "vibe knowledge film"; or wants to reverse-engineer a video into a storyboard. Handles English and Chinese requests such as 解释一下、帮我理解、讲清楚、可视化解释、交互式网页解释、科普视频、知识短片、视频拆解、分镜脚本.
---

# Explain Anything

Most explanations fail because they optimize for text, not understanding. Choose the representation that makes the idea easiest to predict, debug, or decide with. Then prove that the representation is faithful.

**Core rule:** climb the artifact ladder only as high as the idea needs. A polished artifact that distorts the idea is worse than a plain paragraph that is correct.

## Two axes

Every project chooses one **mode** and one **artifact**.

| Mode | Input | Output |
| --- | --- | --- |
| `forward` | concept, paper, system, policy, notes | explanation artifact from scratch |
| `reverse` | existing video / talk / animation | `analysis.json` + `storyboard.json`, then an optional rebuild |
| `hybrid` | reference video + new topic | reuse the reference's structure, not its claims or assets |

| Artifact | Rung | Best when |
| --- | --- | --- |
| `answer` | 0 | small, familiar, factual |
| `ste` | 1 | terminology, procedure, compliance, audit |
| `diagram` | 2 | structure, hierarchy, flow, state, dependency |
| `html` | 3 | a mechanism with variables, counterfactuals, layers |
| `video` | 4 | change over time, derivation, intuition, narrative |
| `knowledge-film` | 4 | 2-5 min, 16:9, no narration, bottom captions, visual-first |

If two artifacts fit, choose the cheaper one that still supports the reader's task. Offer the next rung as an option.

## Model-agnostic contract

The process is fixed. Models are swappable.

At **intake**, ask the user explicitly:

> Which **provider and model** should I use for each role: **analysis**, **storyboard**, **implementation**, and **review**? Name the provider as well as the model (for example, `command-code` + `deepseek/deepseek-v4.1-flash`, not just "DeepSeek"). You can say "same for all", "auto", or specify per role. If you want local-only processing, say so now.

Record the answer in `project.json`:

```json
{
  "models": {
    "analysis": {
      "status": "selected",
      "provider": "<provider>",
      "model": "<model>",
      "capabilities": ["text", "image", "video"],
      "selected_by": "user",
      "reason": "video + OCR + transcript analysis"
    },
    "storyboard": { "status": "selected", "provider": "<provider>", "model": "<model>", "selected_by": "user" },
    "implementation": { "status": "selected", "provider": "<provider>", "model": "<model>", "selected_by": "user" },
    "review": { "status": "selected", "provider": "<provider>", "model": "<model>", "selected_by": "user" }
  }
}
```

Rules:

1. **Do not infer a provider or model from a brand name.** Record the exact provider and model id; a model family is not a provider. Check capabilities at runtime.
2. If the user says **auto**, recommend models by capability and cost, state the assumptions, and record `selected_by: "auto"`.
3. If the user does not choose, use the current session model for all roles and record `selected_by: "default"`. Do not silently switch later.
4. If a model changes mid-project, append to `model_history` and re-run the affected stage. Never switch silently.
5. Ask before uploading private source material to a hosted model. Offer a local-only path when needed.
6. Ask before paid TTS, long renders, or heavy installs.

See `docs/model-selection.md` for the role/capability matrix and examples.

## Pipeline

Every stage has a gate. Do not move on until the gate passes. If the user says "just do it", you may skip the *confirmation* at stages 2-4, but you must still produce the artifacts.

### 0. Intake and model plan

Identify: authoritative source, audience's prior knowledge, task the reader must perform, output language, budget, mode, artifact, privacy constraints.

Ask the model question above. Create `project.json`.

**Gate:** mode, artifact, language, and four model roles are recorded.

### 1. Source and claim ledger

Write `sources.md`: 3-7 claims (up to 12 for a knowledge film), each with a source anchor and a label: `fact`, `inference`, or `analogy`. Every number, name, date, equation, and causal claim needs a traceable source.

**Gate:** every claim has an anchor; unsupported claims are removed or marked as open questions.

### 2. Explanation strategy

Choose the artifact rung. Write one sentence: "After this, the reader can …". Decide what to omit.

For a knowledge film or video, do **visual-first planning** before writing the script:

- Find a concrete image the audience already knows.
- The on-screen subject must look like itself, not a dot, line, circle, or labeled box.
- The verb in the sentence must actually happen on screen.
- Examples before names, formulas, or conclusions.
- Do not illustrate questions, definitions, or conclusions just to fill the frame.
- One world, one scale, a few props, reused throughout.

**Gate:** the thesis fits in one sentence; the visual metaphor is specific to this idea and cannot be swapped into another video.

### 3. Script and storyboard

For prose/HTML/diagram, write the artifact directly.

For video, write `storyboard.md` and `storyboard.json` together. Each row/scene contains:

| Field | Meaning |
| --- | --- |
| `id` | stable scene ID |
| `start`, `end` | seconds, monotonic |
| `purpose` | hook / example / mechanism / boundary / recap |
| `caption` | the one line the audience reads |
| `visual` | what is on screen, described as a recognizable object |
| `action` | what changes; one focal action per scene |
| `on_screen_text` | labels, numbers, equations |
| `audio` | narration, music, SFX, or silence |
| `renderer` | `manim`, `hyperframes`, `remotion`, `canvas`, `static` |
| `evidence` | frame/transcript/source anchors |
| `acceptance` | 1-3 observable checks |

**Gate:** hide the caption column and read only `visual` + `action`; the story must still be understandable. Every noun in the caption must exist on screen. At least ~20% of scenes should be "no new visual" (questions, definitions, conclusions).

### 4. Visual system

Define `style_tokens` in `storyboard.json`:

```json
{
  "background": "#0B1020",
  "text": "#E6EDF3",
  "primary": "#22D3EE",
  "accent": "#FF6B9D",
  "warning": "#FF7B72",
  "font_display": "Noto Sans CJK SC",
  "font_body": "Noto Sans CJK SC",
  "font_mono": "DejaVu Sans Mono",
  "safe_margin_px": 80
}
```

One color has one meaning for the whole film. Match type scale and margins across renderers. For a knowledge film, choose a world preset (see `references/knowledge-film.md`) or define a custom world; do not mix worlds.

**Gate:** palette and type are recorded; every color has a stated meaning.

### 5. Renderer plan and scaffold

Choose the renderer from the shape of the visuals, not from habit:

| Need | Renderer |
| --- | --- |
| Equations, axes, geometry, LaTeX, 3D math | `manim` |
| HTML/CSS/GSAP, typography, UI, charts, code, kinetic type | `hyperframes` |
| Existing React/Remotion composition | `remotion` |
| Custom Canvas/JS frame-by-frame knowledge film | `canvas` |
| Static diagram or poster | `static` |

Scaffold with `scripts/scaffold.py`, then write the renderer-specific project. Each renderer must consume `storyboard.json` and produce `render_manifest.json`.

Before the pilot, run the model preflight:

```bash
python scripts/preflight_model.py project.json --registry model-registry.json
```

The registry is optional but recommended: copy `assets/model-registry.example.json`, replace it with models you have actually verified, and keep it outside the deliverable if it contains private routing.

**Gate:** a scaffold exists; the renderer can read the storyboard without guessing; model roles are selected.

### 6. Pilot

Render **one scene** or the **first 30 seconds**. For a knowledge film, the first 30 seconds must stand alone.

Review the pilot as an image, not as code:

- Cover the caption and small text. Ask: what is this / what is it doing / what did I learn?
- Shrink to phone width. Is the subject still recognizable?
- Check safe margins, text overflow, contrast, and one-focal-action-per-scene.
- Compare against the storyboard's acceptance checks.

**Gate:** the pilot passes the three questions and the acceptance checks. Fix the visual metaphor before scaling up.

### 7. Full build

Build scene by scene. Reuse shared components and style tokens. Render in segments. Keep a `render_manifest.json` with command, renderer version, duration, resolution, files, and checks.

**Gate:** every scene renders; no missing assets; duration matches the storyboard within 0.2 s per scene.

### 8. QA and delivery

Run:

- `python scripts/validate_project.py <project.json>`
- `python scripts/validate_storyboard.py <storyboard.json>`
- `python scripts/check_artifact.py --kind dir <project>`
- Renderer-specific checks: `hyperframes check`, Manim render success, etc.
- `python scripts/qa_video.py final.mp4 --project <slug> --storyboard storyboard.json --captions captions.srt --require-audio --ocr`
- `python scripts/retime_storyboard.py storyboard.json --timings audio/timings.json --write` when measured TTS differs from the estimate.
- `python scripts/check_release.py` before publishing; use `--strict` for the final release gate.
- Three exit questions: recall, transfer, boundary.

**Gate:** all required checks pass; simplifications and open questions are stated in the README; the user gets a compact delivery message with paths and what to verify.

## Knowledge-film rules

Use these when `artifact = knowledge-film`, or when a video should feel like a "vibe knowledge film" rather than a narrated lesson.

1. **No narration by default.** The audience reads one bottom caption line and watches the sentence happen.
2. **Find the image before the words.** If a sentence has no visible noun and verb, rewrite it.
3. **The subject looks like itself.** A protein is a beaded chain, a red blood cell is a disk with a dent, a number line has ticks. A dot with a label is not a subject.
4. **Show the verb.** "Cut in half" actually cuts; "stick" actually sticks; numbers are computed, not asserted.
5. **Example before explanation.** The first 10 seconds show something happening or let the viewer try it; the title comes after.
6. **Do not illustrate questions, naming, conclusions, or citations.** Roughly one in five caption lines should have no new visual.
7. **One world, one scale, a few props.** A scene holds at least two caption lines; each line changes one thing; the ending returns to the opening image.
8. **Every fact has a source.** Put years, names, and numbers on screen; mark illustrative values.

See `references/knowledge-film.md` for the shot table, world presets, 30-second pilot, and frame-by-frame QA. The original `vibe-knowledge-film` project is credited in `NOTICE.md`; its engine is an optional `canvas` renderer, not a required dependency.

## Video reverse mode

When the input is an existing video:

1. **Ingest deterministically:** `ffprobe`, shot detection, keyframes, Whisper transcript, OCR, palette. Do not ask a model to guess timestamps.
2. **Analyze:** the analysis model reads frames + transcript + OCR and writes `analysis.json` with evidence anchors and confidence.
3. **Storyboard:** the storyboard model converts the analysis into `storyboard.json`. Every scene cites frame timestamps or transcript spans.
4. **Rebuild or remix:** only after the storyboard is approved. Never copy third-party footage, music, or claims without permission.
5. **QA:** compare rendered frames with the reference at matching times; report drift.

See `references/video-reverse.md` for the schema, tools, and model-agnostic prompts.

## Renderer contracts

### HyperFrames

- HTML + CSS + GSAP, Node >= 22, FFmpeg, Chrome.
- Root `data-composition-id`, `data-duration`, `data-width`, `data-height`.
- Timed elements: `class="clip"`, `data-start`, `data-duration`.
- One paused GSAP root timeline per composition on `window.__timelines`.
- `npx hyperframes@0.8.181 check`, then `render --fps 30 --quality high --workers 4`.
- Use `assets/hyperframes/` as a lint-clean starter.

### Manim

- Python + Manim Community; LaTeX for equations.
- One scene class per storyboard scene; use `Text`/MarkupText for CJK, not `Tex`.
- Render each scene silently, then mux narration/captions.
- Check geometry with a dry-run text-bounds script; OCR key frames.

### Remotion

- React + `useCurrentFrame()`; separate toolchain and license. Check the current Remotion license before commercial use.
- Do not describe Remotion as a HyperFrames feature.

### Canvas / custom

- Use when the visual system needs per-frame drawing that HTML/GSAP cannot express.
- The renderer must be deterministic: `seek(t)`, no `Date.now()`, no unseeded randomness.
- `vibe-knowledge-film` is a reference implementation; credit it and do not copy its examples as your own.

## Deliverable contract

Save under `./explainers/<slug>/` unless the user names a path:

```text
<slug>/
  README.md                 # thesis, audience, how to open, simplifications, exit questions
  project.json              # mode, artifact, models, renderer, stage status
  sources.md                # claim ledger with anchors
  storyboard.md             # human-readable storyboard
  storyboard.json           # machine-readable contract
  analysis.json             # reverse mode only
  render_manifest.json      # renderer output + checks
  qa_report.json            # validation results
  <artifact>                # .md, .svg, .html, .mp4, or renderer project
```

For video, add `narration.md`, `captions.srt`, `captions.vtt`, and `thumbnail.png`. For a knowledge film, add the visual world spec and the storyboard's "no new visual" markers.

## Quality gates

| Gate | Pass condition |
| --- | --- |
| Fidelity | Every claim traceable; numbers, names, dates, quotes checked |
| Compression | Every section serves the thesis; no impressive but irrelevant detail |
| Modality fit | The artifact matches the shape of the idea |
| Visual-first | The subject is recognizable; the verb happens; no generic placeholder shapes |
| Progressive disclosure | The reader can start simple and add detail without losing the thread |
| Interaction purpose | Every control reveals a consequence or trade-off |
| Accessibility | Keyboard access, contrast, alt text, captions, reduced motion |
| Portability | Offline or documented dependencies; opens on a normal machine |
| Reproducibility | Source, assumptions, model choices, and build steps included |
| Model transparency | All four model roles recorded; changes logged; no silent swaps |

## Anti-patterns

- A wall of headings that is still a wall of text.
- A diagram with every component and no argument.
- A video that reads slides.
- A knowledge film where the screen is a generic dot/line/circle while the caption names a concrete thing.
- A visual that would work for any script.
- An interactive page with sliders that do not change the explanation.
- A simplification that changes the claim.
- Full STE applied so strictly that it becomes harder to read.
- A model chosen by brand name without checking capabilities.
- A model swapped mid-project without recording it.
- "Beautiful" used as a substitute for correct.

## Quick starts

- **Answer:** "Explain <concept> in one calibrated answer. State the thesis, one example, one boundary, and what you simplified."
- **STE-lite:** "Rewrite this in 80% ASD-STE100 style. Keep every fact and number. Use short active sentences, one term per concept, and a procedure list."
- **Diagram:** "Draw a Mermaid diagram that argues <thesis>. At most seven primary nodes; label every edge with a verb."
- **HTML:** "Build a single-file offline HTML explainer for <concept>. Start with one concrete case, then a step-through mechanism, one variable, boundaries, and three exit questions."
- **Video:** "Create a 90-second explainer. First ask which provider and model to use for analysis, storyboard, implementation, and review. Then write the claim ledger, narration, storyboard, pilot, and render."
- **Knowledge film:** "Create a 30-second no-narration knowledge film on <concept>. Find a concrete image first, write sentence-to-screen storyboard rows, and do not illustrate questions or conclusions."
- **Reverse:** "Analyze this video into shots with frame/transcript evidence, then write a storyboard.json. Do not guess timestamps."

## Files

| Path | Purpose |
| --- | --- |
| `docs/pipeline.md` | stage-by-stage gates and handoffs |
| `docs/model-selection.md` | role matrix, explicit ask protocol, switching |
| `docs/contracts.md` | project, analysis, storyboard, render, QA schemas |
| `docs/quality-gates.md` | detailed QA checklists |
| `docs/publishing.md` | GitHub upload and skill installation |
| `references/video-explainer.md` | full video pipeline, Manim/HyperFrames, ffmpeg, TTS |
| `references/knowledge-film.md` | visual-first knowledge-film method |
| `references/video-reverse.md` | video ingestion, analysis, storyboard reconstruction |
| `references/renderers.md` | renderer selection and adapter contracts |
| `references/prompts.md` | model-agnostic prompts for each stage |
| `references/ste100.md` | controlled-language rules |
| `references/diagrams.md` | diagram selection, layout, Mermaid |
| `references/html-explainer.md` | page architecture, interactions, accessibility |
| `assets/` | HTML, STE, storyboard, HyperFrames, and model-registry templates |
| `schemas/` | JSON Schemas for contracts |
| `scripts/` | scaffold, validators, model preflight, video QA, retiming, release check, artifact checker, STE lint |
| `examples/` | worked example with contracts and a rendered video |

## Attribution

This skill integrates the author's original `explain-anything` material with ideas from:

- **vibe-knowledge-film** (MIT): visual-first knowledge-film process, shot table, world presets, frame-by-frame review. https://github.com/HeyChengC/vibe-knowledge-film
- **HyperFrames** (Apache-2.0): HTML/CSS/GSAP composition contract and CLI. https://github.com/heygen-com/hyperframes
- **Manim Community** (MIT): mathematical animation. https://www.manim.community/

See `NOTICE.md` for details. Do not republish third-party example footage, music, or fonts without checking their licenses.
