#!/usr/bin/env python3
"""Check repository readiness before publishing.

Default: errors for example placeholders, invalid JSON, missing required files,
and secrets; warnings for personal placeholders (YOUR_GITHUB) and absolute paths.
Use --strict to make warnings fail too.

Examples:
    python scripts/check_release.py
    python scripts/check_release.py --strict
    python scripts/check_release.py --json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEXT_EXTENSIONS = {".md", ".json", ".py", ".sh", ".yml", ".yaml", ".cff", ".txt", ".html", ".css"}
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".pytest_cache", ".venv", "media", "render", "qa_frames", ".hyperframes", ".thumbnails"}
SKIP_FILES = {"scripts/check_release.py"}
REQUIRED = [
    "SKILL.md",
    "README.md",
    "README.zh-CN.md",
    "LICENSE",
    "NOTICE.md",
    "schemas/project.schema.json",
    "schemas/storyboard.schema.json",
    "schemas/qa-report.schema.json",
    "scripts/preflight_model.py",
    "scripts/qa_video.py",
    "scripts/retime_storyboard.py",
]

ERROR_PATTERNS = [
    (re.compile(r"example-provider|example-(?:analysis|storyboard|code|review)-model"), "example placeholder"),
    (re.compile(r"\b(?:TODO|TBD|FIXME)\b"), "unfinished marker"),
]
WARN_PATTERNS = [
    (re.compile(r"YOUR_(?:NAME|GITHUB|GIVEN_NAME)"), "personal placeholder"),
    (re.compile(r"(?:/root/|/home/[^/\s]+/|C:\\Users\\)"), "absolute local path"),
]
SECRET_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
]


def iter_text_files() -> list[Path]:
    paths = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in TEXT_EXTENSIONS:
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if str(path.relative_to(ROOT)) in SKIP_FILES:
            continue
        paths.append(path)
    return sorted(paths)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strict", action="store_true", help="treat warnings as errors")
    parser.add_argument("--allow-placeholders", action="store_true", help="downgrade placeholder errors to warnings")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    errors: list[dict] = []
    warnings: list[dict] = []
    files = iter_text_files()

    for relative in REQUIRED:
        if not (ROOT / relative).exists():
            errors.append({"path": relative, "message": "required file is missing"})

    for path in files:
        text = path.read_text(encoding="utf-8", errors="replace")
        relative = str(path.relative_to(ROOT))
        for pattern, label in ERROR_PATTERNS:
            for match in pattern.finditer(text):
                item = {"path": relative, "line": text.count("\n", 0, match.start()) + 1, "message": label, "match": match.group(0)}
                if args.allow_placeholders and label == "example placeholder":
                    warnings.append(item)
                else:
                    errors.append(item)
        for pattern, label in WARN_PATTERNS:
            for match in pattern.finditer(text):
                warnings.append({"path": relative, "line": text.count("\n", 0, match.start()) + 1, "message": label, "match": match.group(0)})
        for pattern in SECRET_PATTERNS:
            for match in pattern.finditer(text):
                errors.append({"path": relative, "line": text.count("\n", 0, match.start()) + 1, "message": "possible secret", "match": match.group(0)[:12] + "..."})
        if path.suffix.lower() == ".json":
            try:
                json.loads(text)
            except Exception as exc:
                errors.append({"path": relative, "message": f"invalid JSON: {exc}"})

    if args.strict and warnings:
        errors.extend(dict(item, message="strict: " + item["message"]) for item in warnings)
        warnings = []

    result = {
        "root": str(ROOT),
        "files_scanned": len(files),
        "status": "fail" if errors else "pass",
        "errors": errors,
        "warnings": warnings,
    }
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"{ROOT}: {len(errors)} error(s), {len(warnings)} warning(s), {len(files)} file(s)")
        for item in errors:
            print(f"  ERROR   {item['path']}:{item.get('line', '?')} {item['message']} {item.get('match', '')}")
        for item in warnings:
            print(f"  WARNING {item['path']}:{item.get('line', '?')} {item['message']} {item.get('match', '')}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
