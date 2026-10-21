# Renderers

A renderer consumes `storyboard.json` and produces `render_manifest.json` plus media. The process does not change when the renderer changes.

## Matrix

| Renderer | Best for | Stack | Strengths | Limits |
| --- | --- | --- | --- | --- |
| `hyperframes` | typography, UI, charts, code, kinetic type, title cards, captions | HTML/CSS/GSAP, Node >= 22, Chrome, FFmpeg | deterministic, easy for agents, web layout | not a math/LaTeX engine; needs Node/Chrome |
| `manim` | equations, axes, geometry, 3D math, derivations | Python, Manim Community, LaTeX | mathematical objects, 3b1b style | slower; not ideal for UI/typography-heavy layouts |
| `remotion` | existing React compositions, component ecosystems | React, bundler, Remotion | React reuse | separate license and toolchain |
| `canvas` | custom per-frame 2D knowledge films | Canvas/JS, browser, FFmpeg | full control over every frame | you own the engine and determinism |
| `static` | diagrams, posters, single-frame explainers | SVG/HTML/PNG | cheap, portable | no motion |

## Selection rules

- If the core is an equation or a geometric object, use `manim`.
- If the core is a layout, a chart, a code diff, a UI, or a typographic sequence, use `hyperframes`.
- If the user already has a Remotion project, keep it; do not port without a reason.
- If the visual system needs frame-by-frame drawing that HTML cannot express, use `canvas`.
- A hybrid is allowed: Manim for the math core, HyperFrames for title/chapter/end cards. Match `style_tokens` across both.

## Adapter contract

Every renderer must:

1. Read `storyboard.json`; do not invent timings.
2. Use the `renderer` field and the project's `style_tokens`.
3. Render a pilot before the full build.
4. Produce `render_manifest.json`:
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
     "files": ["render/final.mp4"],
     "checks": [
       {"name": "check", "status": "pass", "evidence": "0 errors, 0 warnings"},
       {"name": "ffprobe", "status": "pass", "evidence": "h264/aac, 90.0s"}
     ]
   }
   ```
5. Never silently change captions, claims, or timings. Record a `deviation` and ask.

## HyperFrames

```bash
# scaffold (pin the version)
HYPERFRAMES_SKIP_SKILLS=1 npx hyperframes@0.8.181 init my-video \
  --non-interactive --resolution=landscape

# copy the starter
cp assets/hyperframes/index.html my-video/index.html
mkdir -p my-video/compositions
cp assets/hyperframes/compositions/scene.html my-video/compositions/scene.html

cd my-video
npx hyperframes@0.8.181 check
npx hyperframes@0.8.181 render --fps 30 --quality high --workers 4 -o render/final.mp4
```

Contract:

- root `data-composition-id`, `data-duration`, `data-width`, `data-height`;
- timed elements `class="clip"`, `data-start`, `data-duration`;
- one paused GSAP root timeline per composition on `window.__timelines`;
- media as a direct child of the host root if it must be seeked;
- no `Math.random()`, `Date.now()`, or network fetches;
- `@font-face` for every custom/CJK family.

Tested: 10 s 1080p30 high-quality with 4 workers rendered in ~10-14 s in this environment. Audio mux works with `<audio data-start=... data-duration=...>` as a direct child of the host root.

## Manim

```bash
manim -qh --fps 30 scene.py Scene01
manim -qh --fps 30 -a scene.py
```

Contract:

- one scene class per storyboard scene;
- `Text`/`MarkupText` for CJK, `MathTex` for equations;
- render silently; mux narration/captions with FFmpeg;
- check text bounds with a dry-run script; OCR key frames;
- keep a geometry QA pass (no text outside frame or panel).

## Remotion

- React components; `useCurrentFrame()`, `interpolate()`, `spring()`.
- Check the current Remotion license before commercial use.
- Do not describe Remotion as a HyperFrames feature, and do not call the combination "Remotion HyperFrame".

## Canvas / custom

- Use a deterministic `seek(t)` renderer: every frame is a pure function of time.
- No `Date.now()`, no unseeded randomness, no network at render time.
- The `vibe-knowledge-film` project is a reference implementation. If you use it, credit it and follow its license; do not copy its example footage or signature assets.

## Static

Use SVG for diagrams and a single HTML page for interactive explainers. Export a PNG/PDF for delivery. Static artifacts do not need a `render_manifest.json`, but they do need `README.md`, `sources.md`, and the three exit questions.
