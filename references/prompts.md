# Prompts

Copy-paste prompts for each stage. They are model-agnostic: replace `{{...}}` placeholders; do not assume a model from its name.

## 0. Intake and model plan

```text
Before starting, help me choose the models for this explanation project.

Source: {{SOURCE}}
Mode: {{forward | reverse | hybrid}}
Artifact: {{answer | ste | diagram | html | video | knowledge-film}}
Language: {{LANGUAGE}}
Privacy: {{public | private | local-only}}

Ask me which model to use for each role:
1. analysis — reads sources, images, video frames, transcript, OCR
2. storyboard — narrative, visual metaphor, captions, shot table
3. implementation — writes code and runs the renderer
4. review — checks fidelity, comprehension, and visual quality

I can say "same for all", "auto", or name a model per role.
Record the result in project.json, including capabilities and the reason.
Do not start stage 1 until all four roles are recorded.
```

## 1. Source and claim ledger

```text
Build a claim ledger for {{TOPIC}}.

Audience: {{AUDIENCE}}
Source: {{SOURCE}}
Language: {{LANGUAGE}}

Return:
1. A one-sentence thesis.
2. 3-7 claims (up to 12 for a knowledge film).
3. For each claim: source anchor, type (fact/inference/analogy), confidence.
4. Open questions and claims that cannot be supported.

Rules:
- Every number, name, date, equation, and causal claim needs an anchor.
- Do not invent quotes or benchmarks.
- If the source is insufficient, say so.
```

## 2. Visual metaphor

```text
Find a visual system for {{TOPIC}} before writing captions.

For each core concept, answer:
- Is it a thing, a process, a quantity, a mental model, a rule, or none of these?
- What does it look like in everyday life?
- What does it look like at a different scale?
- What happens when it breaks?
- How can the verb in the sentence actually happen on screen?

Then choose:
- the one subject that carries the film;
- the one scale/coordinate system;
- the props that return;
- the "oh" moment.

Reject any image that would work for a different script. A dot, line, circle, or labeled box is not a subject.
Return a short visual brief, not code.
```

## 3. Storyboard

```text
Turn the visual brief and claim ledger into storyboard.json and storyboard.md.

For each scene/row:
- id, start, end
- purpose (hook/example/mechanism/boundary/recap/transition/title)
- caption (one line the audience reads)
- visual (a recognizable subject, not a generic shape)
- action (one verb that changes)
- on_screen_text (at most one cluster)
- audio (narration/music/SFX/silence)
- renderer (manim/hyperframes/remotion/canvas/static)
- evidence (frame/transcript/source anchors)
- acceptance (1-3 observable checks)

Rules:
- One focal action per scene.
- A scene holds at least two caption lines; each line changes one thing.
- About one in five lines has no new visual (question, name, conclusion, citation).
- Every noun in the caption exists on screen.
- Timings are monotonic and within the target duration.
- Return JSON that validates against schemas/storyboard.schema.json.
```

## 4. Video reverse analysis

```text
You are analyzing a video into evidence-backed shots.

Inputs:
- metadata: {{METADATA}}
- shot list: {{SHOTS}}
- keyframes: {{FRAMES}}
- transcript: {{TRANSCRIPT}}
- OCR: {{OCR}}

For each shot, return:
- id, start, end
- purpose
- visual: the recognizable subject and layout
- action: the one verb that changes
- on_screen_text
- audio
- evidence: frame timestamps, transcript spans, OCR strings
- confidence: high/medium/low

Do not invent timestamps. If the evidence is insufficient, say so.
Return JSON that validates against schemas/analysis.schema.json.
```

## 5. Implementation

```text
Read storyboard.json and build the {{RENDERER}} project.

Do not change:
- start/end times;
- captions;
- on-screen claims;
- renderer.

If a change is technically necessary, record it in a deviation array and ask before applying it.

Requirements:
- match style_tokens (palette, fonts, safe margins);
- one focal action per scene;
- render a pilot before the full build;
- run the renderer's check command;
- produce render_manifest.json with files, duration, resolution, fps, and checks.

Return the files, commands, and check output. Do not claim success without ffprobe evidence.
```

## 6. Review and QA

```text
Review the artifact against the claim ledger, storyboard, and style tokens.

For each check, return pass/fail/warn with evidence:
1. Fidelity: every claim traceable; numbers/names/dates/quotes checked.
2. Visual-first: subject recognizable; verb happens; no generic placeholders.
3. Comprehension: cover captions; can a first-time viewer say what this is, what it is doing, and what they learned?
4. Timing: scene boundaries match the storyboard within 0.2 s.
5. Accessibility: contrast, captions, safe margins, no text overflow.
6. Render: decode, black frames, loudness, missing assets.
7. Model transparency: all four roles recorded; no silent swap.

Do not rewrite the artifact. Report problems and exact timestamps.
```

## 7. Revision

```text
Fix only the failed checks below. Do not change passing scenes.

Failed checks: {{FAILED_CHECKS}}
Evidence: {{EVIDENCE}}
Constraints: keep storyboard timings, captions, and claims unless a change is explicitly approved.

After the fix:
1. Re-render only the changed scenes.
2. Re-run the same checks.
3. Report what changed and what still fails.
```

## 8. Knowledge film

```text
Create a {{DURATION}}-second no-narration knowledge film on {{TOPIC}}.

Audience: {{AUDIENCE}}
Source: {{SOURCE}}
Language: {{LANGUAGE}}
World: {{lumen | fable | custom}}

Work in this order:
1. Claim ledger.
2. Find the concrete image and the one visual system.
3. Write the shot table: caption -> subject -> action -> small text -> takeaway -> sound.
4. Choose the world tokens; one color, one meaning.
5. Build the first 30 seconds only.
6. Review frames: cover captions, shrink to phone width, check the three questions.
7. Build the full film; return to the opening image at the end.

Rules:
- No narration by default.
- Do not illustrate questions, naming, conclusions, or citations.
- The subject must look like itself; the verb must happen.
- One world, one scale, a few props.
- Every fact has a source; mark illustrative values.
```
