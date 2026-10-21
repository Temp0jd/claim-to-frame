# Quality gates

Use the smallest checks that cover the artifact. A passing build is not completion.

## Universal

| Check | Pass condition |
| --- | --- |
| Thesis | One sentence, stated in README and artifact |
| Fidelity | Every claim has a source anchor; no invented numbers/quotes |
| Compression | Every section serves the thesis |
| Audience | Prerequisites are stated; jargon is defined once |
| Boundaries | At least one limitation or failure case |
| Exit questions | Recall, transfer, boundary |
| Sources | `sources.md` exists and matches the artifact |
| Model record | Four roles selected; no silent swaps |
| Portability | Opens on a normal machine; dependencies documented |

## Prose / STE

- One idea per sentence; active voice; simple present.
- One term per concept; define it once.
- Procedures use vertical lists; warnings precede the step.
- No contractions, idioms, or vague "etc." in STE-lite.
- Read aloud; if it sounds like a translation, rewrite.
- Run `python scripts/ste_lint.py <file> --max-sentence 20`.

## Diagram

- The title is a claim, not a category.
- 5-9 primary nodes; one reading direction.
- Every edge has a verb/relation label.
- One accent path; color is not the only encoding.
- Caption states the takeaway and the main simplification.
- Source (Mermaid/SVG) and rendered image are both delivered.

## HTML

- One self-contained `.html`; opens offline.
- Thesis and three outcomes above the fold.
- One concrete case before definitions.
- 4-7 step mechanism with one active step.
- One variable the reader can change, with units and a labeled consequence.
- Boundaries section; three exit questions.
- Keyboard access, visible focus, reduced motion, mobile width.
- No external fonts/scripts/API unless the user accepts the dependency.
- Run `python scripts/check_artifact.py --kind html <file> --require-offline`.

## Video

| Check | Pass condition |
| --- | --- |
| Duration | Matches the storyboard within 0.2 s per scene |
| Streams | H.264 + AAC (or documented), correct resolution/fps |
| Audio | Present, not clipped; voice starts after the visual lead-in |
| Captions | Sidecar SRT/VTT or burned-in; matches narration |
| Decode | `ffmpeg -v error -i final.mp4 -f null -` returns no errors |
| Black frames | `ffmpeg -vf blackdetect=d=0.1:pix_th=0.02` reports none |
| Automated QA | `python scripts/qa_video.py ... --require-audio` reports no errors |
| Provider | `python scripts/preflight_model.py ...` reports no errors |
| OCR | Key frames show the intended text, no missing glyphs |
| Frames | 10%, 50%, 90% sampled and reviewed |
| Visual-first | Subject recognizable; verb happens; no generic placeholders |
| Facts | On-screen numbers match `sources.md` |

## Knowledge film

- No narration unless requested; one bottom caption line.
- First 10 seconds show something happening; title after.
- Every caption noun exists on screen; every verb happens.
- About one in five lines has no new visual.
- One world, one scale, props return at the end.
- Color semantics consistent.
- 30-second pilot approved before full build.
- Cover captions: can a first-time viewer answer what/doing/learned?
- Phone-width check: subject still recognizable.
- No third-party footage/music/fonts without permission.

## Reverse mode

- Deterministic ingest: metadata, shots, keyframes, transcript, OCR.
- Every shot cites frame timestamps and/or transcript spans.
- No invented timestamps; low-confidence shots flagged.
- Storyboard timings are monotonic and within the source duration.
- Replication permission/credit recorded; hybrid structure documented.
- Rendered comparison at 10/50/90% of each shot.

## Model transparency

- `project.json` has all four roles.
- `selected_by` is `user`, `auto`, or `default`.
- Any switch is in `model_history`.
- The delivery message repeats the model choices and the checks that were rerun.

## Delivery message

Return:

1. The one-sentence thesis.
2. The chosen artifact and why.
3. File paths.
4. Model choices (or "default session model").
5. What passed, what did not, and what the user should verify.
6. One offered next step, without pressure.
