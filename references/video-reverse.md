# Video reverse

Reverse mode turns an existing video into an evidence-backed shot list and storyboard. It is useful for studying structure, rebuilding a style, or creating a new film from a reference.

**Do not ask a model to guess timestamps from raw video.** Run deterministic tools first; the model reads their output.

## 1. Ingest

```bash
mkdir -p analysis/frames
ffprobe -v error -show_entries format=duration,size -show_entries stream=width,height,r_frame_rate,codec_name \
  -of json input.mp4 > analysis/metadata.json

# Shot boundaries (optional but recommended)
scenedetect -i input.mp4 detect-adaptive list-scenes -o analysis/

# Keyframes: 3 per shot, or every N seconds
ffmpeg -i input.mp4 -vf "fps=1/3,scale=960:-1" analysis/frames/f_%04d.jpg

# Transcript with word timestamps
whisper input.mp4 --model medium --output_format json --output_dir analysis/

# OCR on sampled frames (tesseract example)
for f in analysis/frames/*.jpg; do
  base=$(basename "$f" .jpg)
  tesseract "$f" "analysis/frames/$base" -l chi_sim+eng --psm 11 2>/dev/null
done

# Palette (optional)
ffmpeg -i input.mp4 -vf "fps=1/10,scale=320:-1" -frames:v 12 analysis/frames/palette_%02d.png
```

If the source is private, do not upload the whole file. Send sampled frames and redacted transcript spans, or use a local model.

## 2. Analysis

The analysis model receives:

- `metadata.json`
- shot boundaries
- keyframe images (or their paths)
- transcript JSON
- OCR text per frame
- optional palette

It returns `analysis.json` (schema: `schemas/analysis.schema.json`). Each shot must cite:

- frame timestamps;
- transcript span(s);
- OCR text;
- source file.

Do not allow a shot with no evidence. If the model is unsure, set `confidence: "low"` and put the question in `open_questions`.

## 3. Storyboard

The storyboard model converts `analysis.json` into `storyboard.json`:

- Preserve the reference's **structure** (hook, example, mechanism, boundary, recap).
- Preserve **timing** unless the new project explicitly changes it.
- Rewrite captions for the new topic; do not copy the reference's claims.
- Mark reused structure in `sources.md`.
- Keep evidence anchors for every scene.

If the goal is a shot-for-shot rebuild, this is a **replication**; get permission and credit the original. If the goal is a new topic with a similar rhythm, this is a **hybrid**; change the visuals and claims.

## 4. Rebuild

Choose the renderer from the storyboard's `renderer` field. The implementation model must:

- read `storyboard.json`, not the raw video;
- produce a `render_manifest.json`;
- not change timings or captions without a `deviation` record;
- render a pilot before the full build.

## 5. QA against the reference

For a replication, compare:

- shot boundaries within ±0.2 s;
- frame composition at 10%, 50%, 90% of each shot;
- on-screen text (OCR);
- caption timing;
- audio events.

For a hybrid, compare structure only: hook, example, mechanism, boundary, recap. Do not compare visual identity.

## Model-agnostic prompts

### Analysis prompt

```text
You are analyzing a video into evidence-backed shots.

Inputs:
- metadata: {{METADATA}}
- shots: {{SHOTS}}
- keyframes: {{FRAMES}}
- transcript: {{TRANSCRIPT}}
- OCR: {{OCR}}

For each shot, return:
- id, start, end
- purpose (hook/example/mechanism/boundary/recap/transition)
- visual: the recognizable subject and its layout
- action: the one verb that changes
- on_screen_text
- audio
- evidence: frame timestamps, transcript spans, OCR strings
- confidence: high/medium/low

Do not invent timestamps. If the evidence is insufficient, say so.
Return JSON that validates against schemas/analysis.schema.json.
```

### Storyboard prompt

```text
Convert analysis.json into storyboard.json for {{TARGET_TOPIC}}.

Keep:
- the reference's structural rhythm;
- the evidence anchors;
- monotonic timings.

Change:
- captions and claims to the new topic;
- visuals that were specific to the reference's content.

Do not copy third-party footage, music, or signature assets.
Mark every claim with a source anchor from sources.md.
Return JSON that validates against schemas/storyboard.schema.json.
```

### Implementation prompt

```text
Read storyboard.json and build the {{RENDERER}} project.

Do not change:
- start/end times;
- captions;
- on-screen claims;
- renderer.

If a change is technically necessary, record it in a deviation array and ask before applying it.

Run the renderer's check command, render the pilot, and produce render_manifest.json.
```

## Copyright and privacy

- Ask before analyzing a third-party video.
- Do not republish the original footage, music, or fonts.
- A shot-for-shot replication is a derivative work; credit and permission matter.
- Remove faces, names, and customer data when sharing frames with a hosted model.
- Keep an `analysis/README.md` with source URL, date, and license/usage note.
