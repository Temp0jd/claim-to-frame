# Notices and attribution

This repository is a new, model-agnostic skill. It integrates the author's original
`explain-anything` material with ideas and contracts from the projects below.

## vibe-knowledge-film

- Source: https://github.com/HeyChengC/vibe-knowledge-film
- License: MIT
- Used for: the visual-first knowledge-film process, the sentence-to-screen shot
  table, the 30-second pilot, the "do not illustrate questions/definitions"
  rule, and the frame-by-frame review discipline.
- No source code, example footage, music, or signature visual assets from that
  repository are copied into this project. The `lumen` and `fable` presets here
  are new token sets written for this skill.

## HyperFrames

- Source: https://github.com/heygen-com/hyperframes
- License: Apache-2.0
- Used for: the HTML/CSS/GSAP composition contract, CLI workflow, and the
  starter composition in `assets/hyperframes/`.
- The starter HTML was written for this project against the public HyperFrames
  contract; it is not a copy of a HyperFrames example. HyperFrames itself is
  not bundled.

## Manim Community

- Source: https://github.com/ManimCommunity/manim
- License: MIT
- Used for: the Manim renderer option and the earlier local Manim experiment; the current example uses HyperFrames.
- Manim is a dependency, not bundled.

## Remotion

- Source: https://www.remotion.dev
- License: Remotion's own license; check https://www.remotion.dev/license before
  commercial use.
- Remotion is mentioned as a separate renderer option. No Remotion code is
  bundled.

## GSAP

- Source: https://gsap.com
- License: GSAP Standard License (see https://gsap.com/standard-license)
- Used for: the timeline in the Transformer example. The minified file is included
  under its license header in `examples/transformer/assets/gsap.min.js`. Remove it
  and use a CDN instead if you prefer not to redistribute the file.

## Fonts and media

- No font files are bundled. Examples reference system fonts such as
  `Noto Sans CJK SC` and `DejaVu Sans Mono`; check their licenses before
  redistributing them.
- The Transformer video in `examples/transformer/` was generated for this
  project. Its sources are cited in `examples/transformer/sources.md`.
- Do not republish third-party footage, music, or fonts without permission.

## Original explain-anything material

The artifact ladder, STE-lite guidance, diagram/HTML/video references, and
quality-gate structure come from the author's original `explain-anything`
skill. They are included here under the repository's MIT license.
