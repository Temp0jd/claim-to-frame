# Changelog

## 0.2.0 — 2026-10-21

- Added `preflight_model.py` for provider/model/capability checks before rendering.
- Added `qa_video.py` for streams, duration, audio, decode, black frames, loudness, captions, storyboard timing, and optional OCR.
- Added `retime_storyboard.py` to reconcile measured TTS durations with storyboard timings.
- Added `check_release.py` for placeholders, absolute paths, invalid JSON, secrets, and required files.
- Added `assets/model-registry.example.json`; provider is now part of the intake question.
- Extended `qa-report`, `render-manifest`, and `project` schemas to document model/video/QA fields.
- Added tests and CI for preflight, video QA, retiming, and schema coverage.
- Replaced placeholder provider/model records with an honest `single-session` example record.
- Published to npm as `@tempo1221/claim-to-frame` (80 files, 563 KB tarball).

## 0.1.0 — 2026-10-21

- Initial public version.
- Forward, reverse, and hybrid modes.
- Artifact ladder: answer, STE-lite, diagram, HTML, video, knowledge film.
- Model-agnostic roles: analysis, storyboard, implementation, review; explicit intake question; `model_history`.
- JSON contracts: `project.json`, `analysis.json`, `storyboard.json`, `render_manifest.json`, `qa_report.json`.
- Renderer adapters: Manim, HyperFrames, Remotion, Canvas, static.
- Visual-first knowledge-film method adapted from `vibe-knowledge-film`.
- Validators, scaffold, artifact checker, STE lint.
- Example: Transformer visual introduction (HyperFrames, light academic style), with a 9-second GIF preview.
