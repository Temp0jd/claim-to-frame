#!/usr/bin/env python3
"""Validate storyboard.json against the schema and timing gates."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCHEMA = ROOT / "schemas" / "storyboard.schema.json"
RENDERERS = {"manim", "hyperframes", "remotion", "canvas", "static"}


def schema_errors(data: dict) -> list[str]:
    try:
        import jsonschema  # type: ignore
    except Exception:
        return []
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)
    return [f"{'/'.join(map(str, e.path))}: {e.message}" for e in sorted(validator.iter_errors(data), key=lambda e: list(e.path))]


def validate_storyboard_file(path: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return [f"cannot read JSON: {exc}"], warnings
    if not isinstance(data, dict):
        return ["storyboard.json must be an object"], warnings

    errors.extend(schema_errors(data))

    scenes = data.get("scenes")
    if not isinstance(scenes, list) or not scenes:
        return errors + ["scenes must be a non-empty array"], warnings

    ids: set[str] = set()
    prev_end = 0.0
    for index, scene in enumerate(scenes):
        label = f"scenes[{index}]"
        if not isinstance(scene, dict):
            errors.append(f"{label} must be an object")
            continue
        sid = scene.get("id")
        if not isinstance(sid, str) or not sid:
            errors.append(f"{label}.id is missing")
        elif sid in ids:
            errors.append(f"duplicate scene id: {sid}")
        else:
            ids.add(sid)

        try:
            start = float(scene["start"])
            end = float(scene["end"])
        except Exception:
            errors.append(f"{label} needs numeric start/end")
            continue
        if start < 0:
            errors.append(f"{label}.start must be >= 0")
        if end <= start:
            errors.append(f"{label}.end must be > start")
        if start < prev_end - 1e-6:
            errors.append(f"{label} overlaps the previous scene ({start:.3f} < {prev_end:.3f})")
        prev_end = max(prev_end, end)

        for key in ["caption", "visual", "action"]:
            if not isinstance(scene.get(key), str) or not scene[key].strip():
                errors.append(f"{label}.{key} must be a non-empty string")
        if scene.get("renderer") not in RENDERERS:
            errors.append(f"{label}.renderer is invalid: {scene.get('renderer')!r}")
        if not isinstance(scene.get("acceptance"), list) or not scene["acceptance"]:
            errors.append(f"{label}.acceptance must be a non-empty array")
        if not isinstance(scene.get("on_screen_text"), list):
            errors.append(f"{label}.on_screen_text must be an array")

    tokens = data.get("style_tokens")
    if not isinstance(tokens, dict):
        errors.append("style_tokens must be an object")
    else:
        for key in ["background", "text", "primary", "accent", "font_display", "font_body", "safe_margin_px"]:
            if key not in tokens:
                errors.append(f"style_tokens.{key} is missing")

    target = data.get("target_duration")
    if isinstance(target, (int, float)) and target > 0:
        if abs(prev_end - target) > max(1.0, target * 0.02):
            warnings.append(f"last scene ends at {prev_end:.2f}s; target is {target:.2f}s")
    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("storyboard", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    errors, warnings = validate_storyboard_file(args.storyboard)
    if args.json:
        print(json.dumps({"file": str(args.storyboard), "errors": errors, "warnings": warnings}, ensure_ascii=False, indent=2))
    else:
        print(f"{args.storyboard}: {len(errors)} error(s), {len(warnings)} warning(s)")
        for item in errors:
            print(f"  ERROR   {item}")
        for item in warnings:
            print(f"  WARNING {item}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
