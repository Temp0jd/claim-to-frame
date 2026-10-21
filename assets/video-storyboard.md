# {{TITLE}} - Explainer video

## Brief

- **Thesis:** {{THESIS}}
- **Audience:** {{AUDIENCE}}
- **After watching, the viewer can:**
  1. {{OUTCOME_1}}
  2. {{OUTCOME_2}}
  3. {{OUTCOME_3}}
- **Duration:** 90 seconds
- **Language:** {{LANG}}
- **Source:** {{SOURCE}}
- **Tone:** Calm, precise, curious
- **Constraints:** No jargon without a definition. No stock footage. One idea per scene.

## Claim ledger

| Claim | Source anchor | Fact / inference / analogy | Confidence |
| --- | --- | --- | --- |
| {{CLAIM_1}} | {{ANCHOR_1}} | {{TYPE_1}} | {{CONFIDENCE_1}} |
| {{CLAIM_2}} | {{ANCHOR_2}} | {{TYPE_2}} | {{CONFIDENCE_2}} |
| {{CLAIM_3}} | {{ANCHOR_3}} | {{TYPE_3}} | {{CONFIDENCE_3}} |

## Narration

Target 210-240 words for 90 seconds, leaving 10-15% of the time for pauses.

```text
[Scene 1]
{{NARRATION_1}}

[Scene 2]
{{NARRATION_2}}

[Scene 3]
{{NARRATION_3}}

[Scene 4]
{{NARRATION_4}}
```

## Storyboard

| Scene | Time | Narration | Visual | Equation or label | Transition |
| --- | --- | --- | --- | --- | --- |
| 1 | 0:00-0:12 | {{NARRATION_1}} | {{VISUAL_1}} | {{LABEL_1}} | Cut |
| 2 | 0:12-0:32 | {{NARRATION_2}} | {{VISUAL_2}} | {{LABEL_2}} | Morph |
| 3 | 0:32-0:58 | {{NARRATION_3}} | {{VISUAL_3}} | {{LABEL_3}} | Transform |
| 4 | 0:58-1:18 | {{NARRATION_4}} | {{VISUAL_4}} | {{LABEL_4}} | Highlight |
| 5 | 1:18-1:30 | {{RECAP}} | {{VISUAL_5}} | {{LABEL_5}} | Hold |

## Visual system

- One focal object per scene.
- One accent color for the focal path, one for the transform, one for the result.
- Body text at 28 px or larger at 1080p. Titles at 40 px or larger.
- Build equations incrementally. Introduce each symbol before using it.
- Keep the safe area clear. Do not put text near the frame edge.

## Audio

- TTS option: {{TTS_OPTION}}
- One audio file per scene, zero-padded names.
- Normalize loudness before muxing. Do not clip.
- Keep `narration.md` as the transcript.

## Captions and transcript

- Produce `captions.srt` from the scene boundaries.
- Check that captions do not cover the focal object.
- Include the transcript in the package.

## QA

- [ ] Thesis is clear in the first 15 seconds.
- [ ] Duration is 90 seconds or the requested length.
- [ ] Every scene has one focal object and one change.
- [ ] Narration matches the visuals.
- [ ] Audio is present, normalized, and not clipped.
- [ ] Captions and transcript are present.
- [ ] Sample frames at 10%, 50%, and 90% are legible.
- [ ] The final card states the sources and simplifications.
- [ ] A static recap exists if the video cannot be played.

## Sources and simplifications

- Source: {{SOURCE}}
- Omitted: {{SIMPLIFICATION}}
- Open question: {{OPEN_QUESTION}}
