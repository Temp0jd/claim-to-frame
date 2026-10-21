# Model selection

The pipeline is fixed. Models are swappable. This document defines the roles, the intake question, the project record, and the rules for switching.

## Roles

| Role | Does | Needs | Does not |
| --- | --- | --- | --- |
| `analysis` | Reads source documents, images, video frames, transcripts, OCR; extracts evidence | text; image/video if the source is visual; long context helps | Invent timestamps or claims; write final copy |
| `storyboard` | Turns evidence into narrative, visual metaphor, captions, shot table | strong writing and visual reasoning; language fluency | Write production code; silently change facts |
| `implementation` | Writes Manim/HyperFrames/Remotion/Canvas code; runs checks; renders | code, tools, shell, file editing; renderer knowledge | Change the story, timings, or on-screen claims without a deviation record |
| `review` | Checks fidelity, comprehension, visual clarity, accessibility, and render quality | can read images/frames and code; can apply a rubric | Rewrite the whole artifact; approve its own unverified claims |

One model may fill several roles. One role may use different models at different stages (for example, a vision model for frame analysis and a text model for claims). Record each role separately.

## Intake question

Ask once, explicitly, before stage 1:

> Which **provider and model** should I use for each role: **analysis**, **storyboard**, **implementation**, and **review**?
>
> You can:
> - say **"same for all"**,
> - say **"auto"** and I will recommend based on capabilities and cost,
> - name a provider and model per role (for example, `command-code` + `deepseek/deepseek-v4.1-flash`),
> - or say **"default"** to use the current session model for all roles.
>
> If the source is private, say **"local only"** and I will avoid hosted APIs.

Do not skip this question because a model name appears in the prompt. Do not infer a provider or model from a brand name. Record the exact provider, the exact model id, and who owns the quota.

## What to ask next

Only ask follow-ups that change the plan:

- Does the analysis model accept **video**, or only images/text? If only images, the pipeline will sample keyframes and pass a transcript.
- Is the source **private** or under NDA? If yes, prefer local models or a user-controlled endpoint.
- Is there a **budget** for paid TTS, image generation, or long renders?
- Does the implementation model have **shell/file tools**, or only chat? If only chat, it can draft code but not run the render.
- Does the review model accept **images**? If not, use deterministic frame checks plus a text rubric.

## Project record

`project.json` is the source of truth:

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
      "capabilities": ["text", "long_context"],
      "selected_by": "user"
    },
    "implementation": {
      "status": "selected",
      "provider": "provider-c",
      "model": "code-model",
      "capabilities": ["code", "shell", "file_edit"],
      "selected_by": "user"
    },
    "review": {
      "status": "selected",
      "provider": "provider-a",
      "model": "vision-model",
      "capabilities": ["text", "image"],
      "selected_by": "user"
    }
  },
  "model_history": []
}
```

Allowed `status`: `unset`, `selected`, `changed`, `unavailable`.

If the user says **auto**:

```json
{
  "status": "selected",
  "provider": "<chosen>",
  "model": "<chosen>",
  "selected_by": "auto",
  "reason": "video input + long context; cheapest model that meets both"
}
```

State the recommendation and its assumptions in the delivery message. Do not pretend the user chose it.

If the user says **default**:

```json
{
  "status": "selected",
  "provider": "current-session",
  "model": "current-session",
  "selected_by": "default",
  "reason": "user did not specify; using the active session model"
}
```

## Preflight

Before stage 5, run:

```bash
python scripts/preflight_model.py project.json --registry model-registry.json
```

The registry is optional but recommended. Copy `assets/model-registry.example.json` to `model-registry.json`, replace it with models you have actually verified, and keep it outside the deliverable if it contains private routing. The script validates structure and declared capabilities; it does **not** test quota, latency, or live availability. Those still need a real call or a user confirmation.

## Switching models

Models can change mid-project. Do this:

1. Append an entry to `model_history`:
   ```json
   {
     "role": "implementation",
     "from": {"provider": "a", "model": "x"},
     "to": {"provider": "b", "model": "y"},
     "reason": "renderer requires shell access",
     "at_stage": 5,
     "timestamp": "2026-01-01T00:00:00Z"
   }
   ```
2. Re-run the affected stage and every downstream gate.
3. Tell the user what changed and what was re-validated.
4. Never swap silently to "make it work".

## Capability checks

Do not trust a model's name. Check:

- **Input modalities:** text, image, video, audio, PDF.
- **Output:** text only, JSON/tool calls, code, images.
- **Tools:** shell, file read/write, browser, code execution.
- **Context window:** long transcripts and many frames.
- **Determinism:** temperature and seed controls, if reproducibility matters.
- **Data handling:** hosted vs local, retention, region.
- **Cost and rate limits.**

If a capability is unknown, mark it `unverified` and design a fallback.

## Privacy

Ask before sending private material to a hosted model. For sensitive sources:

- prefer local models or a user-controlled endpoint;
- send sampled frames/redacted excerpts, not the whole video;
- remove names, faces, credentials, and customer data;
- record the data-handling choice in `project.json`.

## Cost and consent

Ask before:

- paid TTS or image generation;
- long renders (for example, > 5 minutes of video or > 4K);
- uploading a large source corpus;
- installing heavy dependencies (LaTeX, CUDA, Chrome, model weights).

## Example dialogs

**User:** "Make a 90-second video about Transformers."

**Assistant:** "Before I start: which model should I use for analysis, storyboard, implementation, and review? You can say 'same for all', 'auto', or name one per role. If you want local-only processing, say so."

**User:** "Auto. The source is public."

**Assistant:** "I'll use a vision-capable model for analysis and review, a long-context writer for storyboard, and a code/tool-capable model for implementation. I'll record these in project.json and state them in the delivery."

**User:** "Use model X for everything."

**Assistant:** "Recorded: X for analysis, storyboard, implementation, and review. I'll verify it accepts images and has shell access before stage 5; if not, I'll ask before switching."
