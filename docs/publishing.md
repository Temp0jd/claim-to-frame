# Publishing to GitHub

This repository is a standalone skill. You can upload it as your own project.

## 1. Replace the placeholders

- `LICENSE`: the copyright holder is currently `Tempo`; change it if needed.
- `README.md` / `README.zh-CN.md`: repository URLs point to `Temp0jd/claim-to-frame`.
- `CITATION.cff` (if present): update author and title.
- `NOTICE.md`: keep the attribution to vibe-knowledge-film, HyperFrames, and Manim.

## 2. Create the repository

```bash
cd /path/to/claim-to-frame
git init -b main
git add .
git commit -m "Initial commit: claim-to-frame skill"

# GitHub CLI
gh repo create Temp0jd/claim-to-frame --public --source=. --remote=origin --push

# Or create an empty repo on github.com, then:
git remote add origin git@github.com:Temp0jd/claim-to-frame.git
git push -u origin main
```

## 3. Verify the package

```bash
python -m pytest -q
python scripts/validate_project.py examples/transformer/project.json
python scripts/validate_storyboard.py examples/transformer/storyboard.json
python scripts/preflight_model.py examples/transformer/project.json --registry assets/model-registry.example.json
python scripts/qa_video.py examples/transformer/render/final.mp4 --project transformer-example \
  --storyboard examples/transformer/storyboard.json --captions examples/transformer/captions.srt --require-audio
python scripts/check_artifact.py --kind dir examples/transformer
python scripts/check_release.py --strict
```

The GitHub Actions workflow in `.github/workflows/validate.yml` runs tests, examples, preflight, video QA, and a non-strict release scan. Run `check_release.py --strict` locally after replacing placeholders.

## 4. Install as an agent skill

For Claude Code / Codex / Cursor-style skill directories:

```bash
mkdir -p ~/.claude/skills
cp -r ./claim-to-frame ~/.claude/skills/claim-to-frame
```

For skills.sh-style installation:

```bash
npx skills add Temp0jd/claim-to-frame
```

Keep the folder name `claim-to-frame` and the root `SKILL.md`.

## 5. Suggested repository settings

- Description: "Model-agnostic skill for source-grounded explanations, diagrams, HTML explainers, Manim/HyperFrames videos, and knowledge films."
- Topics: `agent-skill`, `explain`, `manim`, `hyperframes`, `storyboard`, `video`.
- Enable Issues and Discussions.
- Add a `good first issue` label for template/renderer contributions.
- Keep large media in `examples/` small; use Git LFS only if necessary.

## 6. Release checklist

- [ ] README and Chinese README agree.
- [ ] LICENSE and NOTICE are present.
- [ ] All placeholders replaced.
- [ ] `pytest` passes.
- [ ] Preflight, video QA, and `check_release.py --strict` pass.
- [ ] Example project/storyboard validate.
- [ ] No secrets, API keys, private footage, or personal data.
- [ ] Third-party assets credited and licensed.
- [ ] Version and CHANGELOG updated.
