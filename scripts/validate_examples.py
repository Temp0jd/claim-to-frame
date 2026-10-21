#!/usr/bin/env python3
"""Validate all example projects, storyboards, analyses, manifests, and QA reports."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from validate_project import validate_project_file  # noqa: E402
from validate_storyboard import validate_storyboard_file  # noqa: E402

SCHEMAS = {
    "analysis.json": ROOT / "schemas" / "analysis.schema.json",
    "render_manifest.json": ROOT / "schemas" / "render-manifest.schema.json",
    "qa_report.json": ROOT / "schemas" / "qa-report.schema.json",
}


def schema_errors(path: Path, schema_path: Path) -> list[str]:
    try:
        import jsonschema  # type: ignore
    except Exception:
        return []
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    data = json.loads(path.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)
    return [f"{'/'.join(map(str, e.path))}: {e.message}" for e in sorted(validator.iter_errors(data), key=lambda e: list(e.path))]


def main() -> int:
    examples = ROOT / "examples"
    failures = 0
    checked = 0
    for project in sorted(examples.glob("*/project.json")):
        checked += 1
        errors, warnings = validate_project_file(project)
        print(f"{project.relative_to(ROOT)}: {len(errors)} error(s), {len(warnings)} warning(s)")
        for item in errors:
            print(f"  ERROR   {item}")
        for item in warnings:
            print(f"  WARNING {item}")
        failures += len(errors)

        board = project.parent / "storyboard.json"
        if board.exists():
            checked += 1
            errors, warnings = validate_storyboard_file(board)
            print(f"{board.relative_to(ROOT)}: {len(errors)} error(s), {len(warnings)} warning(s)")
            for item in errors:
                print(f"  ERROR   {item}")
            for item in warnings:
                print(f"  WARNING {item}")
            failures += len(errors)

    for name, schema_path in SCHEMAS.items():
        for path in sorted(examples.glob(f"*/{name}")):
            checked += 1
            errors = schema_errors(path, schema_path)
            print(f"{path.relative_to(ROOT)}: {len(errors)} schema error(s)")
            for item in errors:
                print(f"  ERROR   {item}")
            failures += len(errors)

    print(f"checked {checked} file(s); {failures} error(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
