#!/usr/bin/env python3
"""Validate model-role selections before rendering.

This is a structural preflight, not a live quota or availability probe. It checks
that every role records a provider and model, that the declared capabilities match
the artifact, and optionally compares them with a local registry of verified models.

Examples:
    python scripts/preflight_model.py project.json
    python scripts/preflight_model.py project.json --registry model-registry.json
    python scripts/preflight_model.py project.json --json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROLES = ["analysis", "storyboard", "implementation", "review"]


def load_json(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise SystemExit(f"cannot read {path}: {exc}")
    if not isinstance(data, dict):
        raise SystemExit(f"{path} must contain a JSON object")
    return data


def load_registry(path: Path | None) -> dict[tuple[str, str], list[str]]:
    if path is None:
        return {}
    data = load_json(path)
    entries = data.get("models", [])
    registry: dict[tuple[str, str], list[str]] = {}
    if isinstance(entries, dict):
        for key, caps in entries.items():
            if "/" in key:
                provider, model = key.split("/", 1)
                registry[(provider, model)] = list(caps) if isinstance(caps, list) else []
    elif isinstance(entries, list):
        for item in entries:
            if not isinstance(item, dict):
                continue
            provider = str(item.get("provider", "")).strip()
            model = str(item.get("model", "")).strip()
            caps = item.get("capabilities", [])
            if provider and model:
                registry[(provider, model)] = list(caps) if isinstance(caps, list) else []
    return registry


def required_capabilities(mode: str, artifact: str, role: str) -> list[str]:
    if role == "analysis":
        caps = ["text"]
        if mode in {"reverse", "hybrid"}:
            caps.append("image")
        return caps
    if role == "storyboard":
        return ["text"]
    if role == "implementation":
        if artifact in {"video", "knowledge-film"}:
            return ["code", "shell"]
        if artifact in {"html", "diagram", "static"}:
            return ["code", "file_edit"]
        return ["text"]
    if role == "review":
        if artifact in {"video", "knowledge-film", "html", "diagram"}:
            return ["text", "image"]
        return ["text"]
    return ["text"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path)
    parser.add_argument("--registry", type=Path, default=None)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true", help="treat warnings as errors")
    args = parser.parse_args()

    project = load_json(args.project)
    registry = load_registry(args.registry)
    errors: list[str] = []
    warnings: list[str] = []
    checks: list[dict] = []

    mode = project.get("mode", "forward")
    artifact = project.get("artifact", "answer")
    models = project.get("models", {})

    if not isinstance(models, dict):
        errors.append("models must be an object")
        models = {}

    for role in ROLES:
        entry = models.get(role)
        if not isinstance(entry, dict):
            errors.append(f"models.{role} is missing")
            continue
        status = entry.get("status")
        provider = str(entry.get("provider") or "").strip()
        model = str(entry.get("model") or "").strip()
        selected_by = entry.get("selected_by")
        declared = entry.get("capabilities", [])
        if not isinstance(declared, list):
            errors.append(f"models.{role}.capabilities must be an array")
            declared = []

        if status not in {"selected", "changed"}:
            errors.append(f"models.{role}.status is {status!r}; select provider/model before stage 5")
            continue
        if not provider or not model:
            errors.append(f"models.{role} needs provider and model")
        if selected_by not in {"user", "auto", "default"}:
            warnings.append(f"models.{role}.selected_by is {selected_by!r}")

        required = required_capabilities(mode, artifact, role)
        missing = [cap for cap in required if cap not in declared]
        if missing:
            errors.append(f"models.{role} declares {declared}; missing required {missing}")

        found_caps = registry.get((provider, model))
        if args.registry:
            if found_caps is None:
                same_model = [key for key in registry if key[1] == model and key[0] != provider]
                if same_model:
                    warnings.append(
                        f"models.{role}: {provider}/{model} is not in the registry; "
                        f"the same model id is registered under {same_model[0][0]!r}. Confirm the provider."
                    )
                else:
                    warnings.append(f"models.{role}: {provider}/{model} is not in the registry; capabilities are self-declared")
            else:
                missing_registry = [cap for cap in required if cap not in found_caps]
                if missing_registry:
                    errors.append(f"registry says {provider}/{model} lacks {missing_registry}")
                extra = [cap for cap in declared if cap not in found_caps]
                if extra:
                    warnings.append(f"models.{role}: declared capabilities not in registry for {provider}/{model}: {extra}")

        checks.append({
            "role": role,
            "provider": provider,
            "model": model,
            "required": required,
            "declared": declared,
            "status": "fail" if missing else "pass",
        })

    if not args.registry:
        warnings.append("no --registry supplied; capabilities are self-declared, not verified")

    result = {
        "project": str(args.project),
        "mode": mode,
        "artifact": artifact,
        "status": "fail" if errors or (args.strict and warnings) else "pass",
        "errors": errors,
        "warnings": warnings,
        "checks": checks,
    }
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"{args.project}: {len(errors)} error(s), {len(warnings)} warning(s)")
        for item in errors:
            print(f"  ERROR   {item}")
        for item in warnings:
            print(f"  WARNING {item}")
        for check in checks:
            print(f"  {check['status'].upper():4} {check['role']}: {check['provider']}/{check['model']}")
    return 1 if result["status"] == "fail" else 0


if __name__ == "__main__":
    raise SystemExit(main())
