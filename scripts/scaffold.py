#!/usr/bin/env python3
"""Scaffold an explain-anything project.

Examples:
    python scripts/scaffold.py --mode forward --artifact video --title "Why caches help" --out ./explainers/caches
    python scripts/scaffold.py --mode reverse --artifact video --title "Reference analysis" --out ./explainers/reverse --language zh-CN
    python scripts/scaffold.py --mode forward --artifact knowledge-film --title "The shape of luck" --out ./explainers/luck

The scaffold creates the contract files. It does not choose models: edit project.json
or let the agent ask the user which model to use for each role.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "assets" / "project-template"


def replace(text: str, values: dict[str, str]) -> str:
    for key, value in values.items():
        text = text.replace("{{" + key + "}}", value)
    return text


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=["forward", "reverse", "hybrid"], default="forward")
    parser.add_argument("--artifact", choices=["answer", "ste", "diagram", "html", "video", "knowledge-film"], default="video")
    parser.add_argument("--title", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--language", default="en")
    parser.add_argument("--renderer", choices=["manim", "hyperframes", "remotion", "canvas", "static"], default="hyperframes")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    out = Path(args.out).expanduser().resolve()
    if out.exists() and any(out.iterdir()) and not args.force:
        print(f"error: {out} is not empty; pass --force to overwrite", file=sys.stderr)
        return 1
    out.mkdir(parents=True, exist_ok=True)

    values = {
        "TITLE": args.title,
        "THESIS": "One sentence: what should the viewer understand?",
        "AUDIENCE": "Who is this for, and what do they already know?",
        "OUTCOME_1": "explain the core idea",
        "OUTCOME_2": "predict what happens when a variable changes",
        "OUTCOME_3": "state where the model or analogy breaks",
        "HOW_TO_OPEN": "Describe how to open the artifact, or run the renderer.",
        "ARTIFACT": "Describe the artifact and its files.",
        "SIMPLIFICATIONS": "List what is simplified or illustrative.",
        "DURATION": "90",
        "RENDERER": args.renderer,
        "MODE": args.mode,
        "END": "9.0",
        "CAPTION": "One line the audience reads.",
        "VISUAL": "A recognizable subject, not a generic shape.",
        "ACTION": "One verb that changes.",
        "TEXT": "Labels, numbers, or equations.",
        "AUDIO": "Narration, music, SFX, or silence.",
        "ACCEPTANCE": "What must be true in the frame.",
        "BACKGROUND": "#0B1020",
        "TEXT_COLOR": "#E6EDF3",
        "PRIMARY": "#22D3EE",
        "ACCENT": "#FF6B9D",
        "FONT_DISPLAY": "Noto Sans CJK SC",
        "FONT_BODY": "Noto Sans CJK SC",
        "SAFE_MARGIN": "80",
        "CLAIM_1": "A claim that matters.",
        "ANCHOR_1": "source.md#section",
        "CONFIDENCE_1": "high",
        "CLAIM_2": "A second claim.",
        "ANCHOR_2": "source.md#section",
        "CONFIDENCE_2": "medium",
        "OPEN_QUESTION": "What is still unknown?",
        "VIDEO_ID": "reference-001",
        "SOURCE_PATH": "input.mp4",
        "PROJECT_SLUG": out.name,
    }

    # Copy and fill the Markdown/JSON templates.
    copies = {
        "README.md": "README.md",
        "sources.md": "sources.md",
        "storyboard.md": "storyboard.md",
        "storyboard.json": "storyboard.json",
    }
    for src_name, dst_name in copies.items():
        src = TEMPLATE / src_name
        if src.exists():
            text = replace(src.read_text(encoding="utf-8"), values)
            (out / dst_name).write_text(text, encoding="utf-8")

    project = json.loads((TEMPLATE / "project.json").read_text(encoding="utf-8"))
    project["title"] = args.title
    project["mode"] = args.mode
    project["artifact"] = args.artifact
    project["language"] = args.language
    project["renderer"] = args.renderer
    (out / "project.json").write_text(json.dumps(project, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # Create mode/artifact-specific directories.
    (out / "qa").mkdir(exist_ok=True)
    if args.mode == "reverse":
        (out / "analysis").mkdir(exist_ok=True)
        (out / "analysis" / "frames").mkdir(exist_ok=True)
        analysis = json.loads((TEMPLATE / "analysis.json").read_text(encoding="utf-8"))
        (out / "analysis" / "analysis.json").write_text(json.dumps(analysis, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        (out / "analysis" / "README.md").write_text(
            "# Analysis inputs\n\nPut metadata, shot list, keyframes, transcript, OCR, and palette here.\n",
            encoding="utf-8",
        )

    if args.artifact in {"video", "knowledge-film"}:
        (out / "render").mkdir(exist_ok=True)
        (out / "render" / "README.md").write_text(
            "# Render\n\nPut renderer output here. Keep render_manifest.json next to it.\n",
            encoding="utf-8",
        )

    if args.renderer == "hyperframes" and args.artifact in {"video", "knowledge-film"}:
        hf = out / "render" / "hyperframes"
        hf.mkdir(parents=True, exist_ok=True)
        if (ROOT / "assets" / "hyperframes" / "index.html").exists():
            shutil.copy2(ROOT / "assets" / "hyperframes" / "index.html", hf / "index.html")
            (hf / "compositions").mkdir(exist_ok=True)
            shutil.copy2(ROOT / "assets" / "hyperframes" / "compositions" / "scene.html", hf / "compositions" / "scene.html")

    print(f"Created {out}")
    print("Next:")
    print("  1. Ask which model to use for analysis, storyboard, implementation, and review.")
    print("  2. Edit project.json with the choices.")
    print("  3. Fill sources.md, storyboard.md, and storyboard.json.")
    print("  4. Run: python scripts/validate_project.py <project.json>")
    print("  5. Run: python scripts/validate_storyboard.py <storyboard.json>")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
