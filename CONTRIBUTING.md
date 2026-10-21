# Contributing

Thanks for improving `claim-to-frame`. Keep changes small, testable, and model-agnostic.

## Before you start

- Read `SKILL.md` and `docs/pipeline.md`.
- Do not hardcode a model name to a content type. Models are chosen at intake and recorded in `project.json`.
- Do not add a new renderer without an adapter contract and a minimal example.

## Development

```bash
python -m pip install -r requirements-dev.txt
python -m pytest
python scripts/validate_examples.py
```

## Adding a renderer

1. Add a section to `references/renderers.md`.
2. Add an adapter note or script under `scripts/` or `assets/`.
3. Add a minimal example under `examples/<renderer>-<name>/`.
4. Include `project.json`, `storyboard.json`, and `render_manifest.json`.
5. Run `python scripts/validate_examples.py`.
6. State the renderer's license and platform requirements in `NOTICE.md`.

## Changing a schema

1. Update the JSON Schema in `schemas/`.
2. Update `docs/contracts.md`.
3. Update the scaffold template in `assets/project-template/`.
4. Update the validators and tests.
5. Bump `CHANGELOG.md`.

## Pull request checklist

- [ ] `python -m pytest` passes.
- [ ] `python scripts/validate_examples.py` passes.
- [ ] No secrets, private footage, or personal data.
- [ ] Third-party assets credited and licensed.
- [ ] README/Chinese README updated if the public interface changed.
- [ ] Model-agnostic rule preserved: no hardcoded model-to-content mapping.
