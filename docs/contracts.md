# Contracts

The pipeline exchanges JSON, not free-form prose. Markdown is for humans; JSON is for tools and models.

## Files

| File | Written by | Read by |
| --- | --- | --- |
| `project.json` | orchestrator | all stages |
| `analysis.json` | analysis model + deterministic ingest | storyboard model |
| `storyboard.json` | storyboard model | implementation model, validators |
| `render_manifest.json` | implementation model | review model, QA |
| `qa_report.json` | review model + validators | delivery |

Schemas live in `schemas/`. Validate with:

```bash
python scripts/validate_project.py path/to/project.json
python scripts/validate_storyboard.py path/to/storyboard.json
```

## `project.json`

```json
{
  "schema_version": "1.0",
  "title": "Why caches help",
  "mode": "forward",
  "artifact": "video",
  "language": "en",
  "renderer": "hyperframes",
  "models": {
    "analysis": {
      "status": "selected",
      "provider": "provider-a",
      "model": "vision-model",
      "capabilities": ["text", "image", "video"],
      "selected_by": "user",
      "reason": "reads keyframes and transcript"
    },
    "storyboard": {
      "status": "selected",
      "provider": "provider-b",
      "model": "writer-model",
      "selected_by": "user"
    },
    "implementation": {
      "status": "selected",
      "provider": "provider-c",
      "model": "code-model",
      "selected_by": "user"
    },
    "review": {
      "status": "selected",
      "provider": "provider-a",
      "model": "vision-model",
      "selected_by": "user"
    }
  },
  "stages": {
    "0_intake": "done",
    "1_sources": "done",
    "2_strategy": "done",
    "3_storyboard": "in_progress",
    "4_visual_system": "pending",
    "5_renderer": "pending",
    "6_pilot": "pending",
    "7_build": "pending",
    "8_qa": "pending"
  },
  "model_history": []
}
```

## `analysis.json`

Reverse mode only. Produced from deterministic ingest + analysis model.

```json
{
  "schema_version": "1.0",
  "video_id": "reference-001",
  "source": "input.mp4",
  "duration": 91.2,
  "fps": 30,
  "resolution": [1920, 1080],
  "style_tokens": {
    "background": "#0B1020",
    "text": "#E6EDF3",
    "primary": "#22D3EE",
    "accent": "#FF6B9D",
    "font_display": "Noto Sans CJK SC",
    "font_body": "Noto Sans CJK SC",
    "safe_margin_px": 80
  },
  "shots": [
    {
      "id": "S01",
      "start": 0.0,
      "end": 9.5,
      "purpose": "hook",
      "visual": "a dark grid; a pixel image resolves from noise",
      "action": "noise resolves into a recognizable cat face",
      "on_screen_text": ["Transformer"],
      "audio": { "narration": "...", "music": "low pulse" },
      "evidence": {
        "frames": [0.5, 4.2, 8.8],
        "transcript": ["0.8-4.2: ...", "4.5-9.0: ..."],
        "ocr": ["0.5: Transformer"],
        "source": "input.mp4"
      },
      "confidence": "high"
    }
  ],
  "open_questions": []
}
```

## `storyboard.json`

The single timing source. `storyboard.md` is generated from it or hand-written alongside it; they must agree.

```json
{
  "schema_version": "1.0",
  "project": "why-caches-help",
  "mode": "forward",
  "target_duration": 90,
  "style_tokens": {
    "background": "#0B1020",
    "text": "#E6EDF3",
    "primary": "#22D3EE",
    "accent": "#FF6B9D",
    "warning": "#FF7B72",
    "font_display": "Noto Sans CJK SC",
    "font_body": "Noto Sans CJK SC",
    "font_mono": "DejaVu Sans Mono",
    "safe_margin_px": 80
  },
  "scenes": [
    {
      "id": "S01",
      "start": 0.0,
      "end": 9.5,
      "purpose": "hook",
      "caption": "A cache is a small, fast copy.",
      "visual": "a desk with a notebook and a sticky note",
      "action": "a hand copies one line from the notebook to the note",
      "on_screen_text": ["cache = fast copy"],
      "audio": { "narration": "...", "music": "none" },
      "renderer": "hyperframes",
      "evidence": {
        "frames": [],
        "transcript": [],
        "ocr": [],
        "source": "sources.md#claim-1"
      },
      "acceptance": [
        "the notebook and note are both visible",
        "the copied line is legible at 720p"
      ]
    }
  ]
}
```

## `render_manifest.json`

```json
{
  "schema_version": "1.0",
  "project": "why-caches-help",
  "renderer": "hyperframes",
  "renderer_version": "0.8.181",
  "output": "render/final.mp4",
  "duration": 90.0,
  "width": 1920,
  "height": 1080,
  "fps": 30,
  "files": ["render/final.mp4", "render/scene-01.mp4"],
  "checks": [
    { "name": "hyperframes-check", "status": "pass", "evidence": "0 errors, 0 warnings" },
    { "name": "ffprobe", "status": "pass", "evidence": "h264/aac, 90.0s" }
  ]
}
```

## `qa_report.json`

```json
{
  "schema_version": "1.0",
  "project": "why-caches-help",
  "generated_at": "2026-01-01T00:00:00Z",
  "status": "pass",
  "checks": [
    {
      "id": "fidelity",
      "severity": "error",
      "status": "pass",
      "message": "All claims trace to sources.md",
      "evidence": "source anchors checked"
    },
    {
      "id": "visual-first",
      "severity": "error",
      "status": "pass",
      "message": "Subject recognizable; verb happens",
      "evidence": "frames at 2.0s, 6.0s, 8.5s"
    }
  ]
}
```

`qa_video.py` adds `video`, `model`, `ocr`, and optional `content_coverage` fields. The `video` object records path, duration, width, height, fps, frames, size, md5, streams, silent source, and promoted source. The `model` object records the implementation provider/model actually used.

## Rules

- JSON must be valid; comments are not allowed in the files.
- Times are seconds, floating point, monotonic.
- IDs are stable and unique within a project.
- `storyboard.json` is the timing source; do not let the renderer invent timings.
- If a model changes a contract field, record it in `model_history` or a `deviation` array; do not silently mutate.
- Keep evidence anchors small but sufficient: frame timestamps, transcript spans, source IDs.
