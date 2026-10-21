#!/usr/bin/env python3
"""Validate project.json against the schema and semantic gates."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCHEMA = ROOT / "schemas" / "project.schema.json"
ROLES = ["analysis", "storyboard", "implementation", "review"]
STAGES = ["0_intake", "1_sources", "2_strategy", "3_storyboard", "4_visual_system", "5_renderer", "6_pilot", "7_build", "8_qa"]


def schema_errors(data: dict) -> list[str]:
    try:
        import jsonschema  # type: ignore
    except Exception:
        return []
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)
    return [f"{'/'.join(map(str, e.path))}: {e.message}" for e in sorted(validator.iter_errors(data), key=lambda e: list(e.path))]


def validate_project_file(path: Path, allow_unset_models: bool = False) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return [f"cannot read JSON: {exc}"], warnings
    if not isinstance(data, dict):
        return ["project.json must be an object"], warnings

    errors.extend(schema_errors(data))

    for key in ["schema_version", "title", "mode", "artifact", "language", "renderer", "models", "stages"]:
        if key not in data:
            errors.append(f"missing required key: {key}")

    models = data.get("models")
    if not isinstance(models, dict):
        errors.append("models must be an object")
    else:
        for role in ROLES:
            entry = models.get(role)
            if not isinstance(entry, dict):
                errors.append(f"models.{role} is missing")
                continue
            status = entry.get("status")
            if status not in {"unset", "selected", "changed", "unavailable"}:
                errors.append(f"models.{role}.status is invalid: {status!r}")
            if status == "selected":
                if not entry.get("provider") or not entry.get("model"):
                    errors.append(f"models.{role} is selected but provider/model is empty")
            elif status == "unset" and not allow_unset_models:
                errors.append(f"models.{role} is unset; ask the user before stage 5 (or pass --allow-unset-models)")

    stages = data.get("stages")
    if not isinstance(stages, dict):
        errors.append("stages must be an object")
    else:
        for stage in STAGES:
            if stage not in stages:
                errors.append(f"stages.{stage} is missing")
            elif stages[stage] not in {"pending", "in_progress", "done", "blocked", "skipped"}:
                errors.append(f"stages.{stage} has invalid status: {stages[stage]!r}")

    artifact = data.get("artifact")
    renderer = data.get("renderer")
    if artifact in {"video", "knowledge-film"} and renderer == "static":
        warnings.append("video artifact with static renderer; is this intentional?")
    if artifact == "knowledge-film" and renderer not in {"hyperframes", "canvas", "manim"}:
        warnings.append("knowledge-film usually uses hyperframes, canvas, or manim")

    history = data.get("model_history", [])
    if not isinstance(history, list):
        errors.append("model_history must be an array")

    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path)
    parser.add_argument("--allow-unset-models", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    errors, warnings = validate_project_file(args.project, args.allow_unset_models)
    if args.json:
        print(json.dumps({"file": str(args.project), "errors": errors, "warnings": warnings}, ensure_ascii=False, indent=2))
    else:
        print(f"{args.project}: {len(errors)} error(s), {len(warnings)} warning(s)")
        for item in errors:
            print(f"  ERROR   {item}")
        for item in warnings:
            print(f"  WARNING {item}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
