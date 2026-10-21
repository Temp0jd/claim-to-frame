# Knowledge film

A knowledge film is a short, no-narration explainer: the audience reads one bottom caption line and watches that sentence happen on screen. It is closer to a visual essay than to a lecture.

Use `artifact = knowledge-film` when:

- the idea has a concrete visual mechanism or a strong everyday metaphor;
- the audience can read one line at a time;
- 2-5 minutes is enough;
- narration would compete with the visuals rather than help.

Do not use it for reference tables, exact procedures, or material the viewer will skim.

This method is inspired by **vibe-knowledge-film** (MIT, https://github.com/HeyChengC/vibe-knowledge-film). The wording, presets, and examples below are adapted for this skill; see `NOTICE.md`.

## The eight rules

1. **Find the image before the words.** Every concept gets a concrete thing the audience already knows. If a sentence has no visible noun and verb, rewrite the sentence.
2. **The subject looks like itself.** A protein is a beaded chain, a red blood cell is a disk with a dent, a number line has ticks. A dot with a label is not a subject.
3. **Show the verb.** "Cut in half" actually cuts. "Stick" actually sticks. Numbers are computed, not asserted.
4. **Example before explanation.** The first 10 seconds show something happening or let the viewer try it. The title comes after.
5. **Do not illustrate questions, naming, conclusions, or citations.** About one in five caption lines should have no new visual.
6. **One world, one scale, a few props.** A scene holds at least two caption lines; each line changes one thing; the ending returns to the opening image.
7. **One color, one meaning.** The palette is a grammar, not decoration.
8. **Every fact has a source.** Put years, names, and numbers on screen; mark illustrative values.

## Shot table

Write one row per caption line, not one row per "scene" in the film-school sense.

| Field | Meaning |
| --- | --- |
| `id` | stable row ID |
| `start`, `end` | seconds |
| `caption` | the one line the audience reads |
| `shot` | wide / medium / close / insert / title / no-new-visual |
| `subject` | the recognizable object on screen |
| `action` | the one verb that happens |
| `small_text` | labels, numbers, equations (at most one cluster) |
| `takeaway` | what the viewer should understand after this line |
| `sound` | SFX / silence / music cue |
| `acceptance` | how you will know the frame works |

The machine-readable version is `storyboard.json`. The human version is `storyboard.md`. They must agree.

## World presets

A "world" is a consistent visual grammar: palette, type, layout, recurring props, title card, and sound palette. Pick one and keep it. If unsure, start with `lumen`.

### `lumen` — for abstract concepts and invisible mechanisms

| Token | Value |
| --- | --- |
| background | `#0B1020` |
| text | `#E6EDF3` |
| primary | `#22D3EE` |
| accent | `#FF6B9D` |
| warning | `#FF7B72` |
| font_display | `Noto Sans CJK SC` (or a bold geometric sans) |
| font_body | `Noto Sans CJK SC` |
| font_mono | `DejaVu Sans Mono` |
| safe_margin | 80 px at 1920×1080 |

Use glow, grids, and soft gradients sparingly. Keep the subject brighter than the background. Avoid neon on every element; the accent is for the one thing that changes.

### `fable` — for psychology, behavior, and everyday stories

| Token | Value |
| --- | --- |
| background | `#F4EBDD` |
| text | `#2B2118` |
| primary | `#2F6B5E` |
| accent | `#D97745` |
| warning | `#A33A2B` |
| font_display | `Noto Serif CJK SC` (or a warm serif) |
| font_body | `Noto Sans CJK SC` |
| font_mono | `DejaVu Sans Mono` |
| safe_margin | 80 px at 1920×1080 |

Use paper textures, ink lines, and flat shapes. Keep the frame calm; let the behavior be the drama.

You may define a custom world, but record its tokens in `storyboard.json` and keep them for the whole film.

## The 30-second pilot

Before the full film, build the first 30 seconds:

- one idea only;
- a visible change within 0.3 s of each caption;
- no more than three caption lines per scene;
- a title after the opening example, not before;
- one "oh" moment with a setup and a hold.

Render it, cover the captions, and ask:

1. What is this? (a everyday noun)
2. What is it doing? (one verb)
3. What did I learn? (one sentence)

If any answer is vague, fix the image or the action, not the caption.

## Frame-by-frame QA

- Cover captions and small text; the visual still reads.
- Shrink to phone width; the subject is still recognizable.
- Check the safe area: nothing important within 80 px of the frame edge.
- Check the caption band: no other object intrudes.
- Check motion: one focal action at a time; no two things competing.
- Check color semantics: the same color means the same thing throughout.
- Check returns: props and scale come back at the end.
- Check facts: every number matches `sources.md`; illustrative values are labeled.
- Check sound: every change has a cue, or deliberate silence; no music fighting the captions.

## Anti-patterns

- A generic dot/line/circle while the caption names a concrete thing.
- A visual that would work for any script.
- A title card before the audience has seen anything.
- A caption that describes something not on screen.
- A conclusion illustrated with a new metaphor the audience has never seen.
- Three ideas in one frame.
- A color used for two different meanings.
- A "beautiful" frame that does not explain.

## Attribution

The visual-first process, shot-table discipline, and 30-second pilot idea are adapted from **vibe-knowledge-film** by HeyChengC (MIT). The `lumen` and `fable` presets here are new tokens for this skill, not copies of that project's exact worlds. Do not reuse third-party example footage, music, or fonts without checking their licenses.
