# Pipeline

This is the fixed process. Models are chosen separately in `docs/model-selection.md`.

## Stage map

```text
0. Intake + model plan
1. Source + claim ledger
2. Explanation strategy + visual metaphor
3. Script + storyboard
4. Visual system
5. Renderer plan + scaffold
6. Pilot
7. Full build
8. QA + delivery
```

Each stage writes a file and has a gate. Do not advance on a failed gate.

## Stage 0 — Intake + model plan

**Input:** user request, source material, constraints.

**Do:**

- Identify mode: `forward`, `reverse`, or `hybrid`.
- Identify artifact: `answer`, `ste`, `diagram`, `html`, `video`, `knowledge-film`.
- Identify audience, prior knowledge, task, language, budget, privacy.
- Ask the model question (analysis, storyboard, implementation, review).
- Create `project.json`.

**Output:** `project.json`.

**Gate:** all four model roles have `status: selected` (or an explicit `default`/unavailable fallback); mode and artifact are set.

## Stage 1 — Source + claim ledger

**Input:** source documents, links, data, transcripts.

**Do:**

- Write 3-7 claims (up to 12 for a knowledge film).
- For each claim, record a source anchor and label: `fact`, `inference`, or `analogy`.
- Mark confidence and open questions.
- Remove or qualify unsupported claims.

**Output:** `sources.md`.

**Gate:** every number, name, date, equation, and causal claim has an anchor; no invented quotes or benchmarks.

## Stage 2 — Explanation strategy + visual metaphor

**Input:** claim ledger, audience, artifact.

**Do:**

- Choose the rung. Do not climb higher than needed.
- Write the thesis in one sentence.
- Write "After this, the reader can …" with three verbs.
- For video/knowledge-film: find a concrete visual image before writing captions.
- Test the image: does it have a everyday name, does it look like itself, can the verb happen on it, would it work for a different script? If yes to the last question, it is a placeholder, not a metaphor.

**Output:** a short strategy note in `README.md` or `storyboard.md`.

**Gate:** thesis fits in one sentence; the visual metaphor is specific and non-transferable; the planned omission list is explicit.

## Stage 3 — Script + storyboard

**Input:** strategy, claims, visual metaphor.

**Do:**

- For prose/STE/HTML/diagram: write the artifact.
- For video: write `storyboard.md` and `storyboard.json` together.
- Each scene has one focal action. A scene should hold at least two caption lines; each line changes one thing.
- About one in five lines should be "no new visual" (question, name, conclusion, citation).
- Include acceptance checks per scene.

**Output:** artifact draft, `storyboard.md`, `storyboard.json`.

**Gate:** hide the caption column and read only visual/action; the story is still understandable. Every noun in the caption exists on screen. Timings are monotonic and within the target duration.

## Stage 4 — Visual system

**Input:** storyboard.

**Do:**

- Define `style_tokens`: background, text, primary, accent, warning, fonts, safe margin.
- Assign one meaning per color for the whole piece.
- Choose a world preset for knowledge films, or define a custom world.
- Match type scale and margins across renderers.

**Output:** `style_tokens` in `storyboard.json`; optional `design.md`.

**Gate:** every color has a meaning; fonts support the language; safe margins are explicit.

## Stage 5 — Renderer plan + scaffold

**Input:** storyboard, artifact, models.

**Do:**

- Choose renderer: `manim`, `hyperframes`, `remotion`, `canvas`, `static`.
- Verify capabilities: Node/FFmpeg/Chrome for HyperFrames; Python/Manim/LaTeX for Manim; React toolchain for Remotion.
- Scaffold the project with `scripts/scaffold.py`.
- Run `python scripts/preflight_model.py project.json --registry model-registry.json` and fix every error.
- Confirm the implementation model can actually run the renderer (shell/file tools). If not, ask before switching.

**Output:** renderer project, `project.json` stage status.

**Gate:** the renderer can read `storyboard.json`; the implementation model has the required tools; no silent model switch.

## Stage 6 — Pilot

**Input:** renderer project, first scene or first 30 seconds.

**Do:**

- Render one scene (or the first 30 seconds for a knowledge film).
- Review frames, not code.
- Cover captions and small text: what is this / what is it doing / what did I learn?
- Shrink to phone width; check recognizability.
- Check safe margins, overflow, contrast, one focal action.

**Output:** pilot video/stills, `qa_report.json` draft.

**Gate:** pilot passes the three questions and the scene acceptance checks. Fix the metaphor before scaling.

## Stage 7 — Full build

**Input:** approved pilot, full storyboard.

**Do:**

- Build scene by scene.
- Reuse shared components and style tokens.
- Render segments; keep a `render_manifest.json`.
- Re-render only changed scenes when possible.

**Output:** full render, `render_manifest.json`, scene files.

**Gate:** every scene renders; duration within 0.2 s per scene of the storyboard; no missing assets.

## Stage 8 — QA + delivery

**Input:** full render, storyboard, claim ledger.

**Do:**

- Run validators and artifact checks.
- Run `python scripts/qa_video.py final.mp4 --project <slug> --storyboard storyboard.json --captions captions.srt --require-audio --ocr`.
- If measured TTS changed the timeline, run `python scripts/retime_storyboard.py storyboard.json --timings audio/timings.json --write` before rendering.
- Check streams, duration, decode, black frames, loudness, OCR, captions.
- Compare five sampled scenes against the storyboard.
- Write `qa_report.json`.
- State simplifications, open questions, and what was not verified.

**Output:** final artifact, `qa_report.json`, `README.md`.

**Gate:** all required checks pass; the delivery message names the model choices and the files.

## Reverse mode

```text
video
  → deterministic ingest (ffprobe, shots, keyframes, ASR, OCR, palette)
  → analysis.json
  → storyboard.json
  → optional rebuild/remix
  → QA against the reference
```

Rules:

- The analysis model reads frames + transcript + OCR, not raw timestamps guessed from memory.
- Every scene cites frame timestamps or transcript spans.
- The storyboard model may propose structure, but cannot invent facts.
- Rebuilding must not copy third-party footage, music, or claims without permission.

## Hybrid mode

Use a reference video's **structure** (hook, example, mechanism, boundary, recap) for a new topic. Do not reuse its specific claims, assets, or signature visual identity. Record what was reused in `sources.md`.

## Stage status

`project.json` records:

```json
{
  "stages": {
    "0_intake": "done",
    "1_sources": "done",
    "2_strategy": "done",
    "3_storyboard": "done",
    "4_visual_system": "done",
    "5_renderer": "in_progress",
    "6_pilot": "pending",
    "7_build": "pending",
    "8_qa": "pending"
  }
}
```

Allowed values: `pending`, `in_progress`, `done`, `blocked`, `skipped`.
