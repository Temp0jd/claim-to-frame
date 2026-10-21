#!/usr/bin/env python3
"""Check an explainer artifact for offline portability, accessibility, and media sanity.

Examples:
    python3 scripts/check_artifact.py --kind html explainer.html --require-offline
    python3 scripts/check_artifact.py --kind video output/final.mp4
    python3 scripts/check_artifact.py --kind dir ./explainers/feedback
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from collections import Counter
from dataclasses import asdict, dataclass
from html.parser import HTMLParser
from pathlib import Path


@dataclass
class Finding:
    path: str
    severity: str
    code: str
    message: str
    line: int | None = None


RESOURCE_TAGS = {
    "script": ["src"],
    "img": ["src", "srcset"],
    "source": ["src", "srcset"],
    "video": ["src", "poster"],
    "audio": ["src"],
    "iframe": ["src"],
    "embed": ["src"],
    "object": ["data"],
    "input": ["src"],
    "use": ["href", "xlink:href"],
    "image": ["href", "xlink:href"],
}


def is_external(value: str) -> bool:
    return value.strip().startswith(("http://", "https://", "//"))


class HTMLAudit(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.counts: Counter[str] = Counter()
        self.resource_refs: list[tuple[str, str, str, str]] = []
        self.external_links: list[str] = []
        self.img_missing_alt: list[str] = []
        self.svg_unlabeled = 0
        self.lang: str | None = None
        self.has_viewport = False
        self.title_text: list[str] = []
        self.in_title = False
        self.script_text: list[str] = []
        self.in_script = False
        self.style_text: list[str] = []
        self.in_style = False
        self.h1 = 0
        self.main = 0
        self.nav = 0

    def _record_resource(self, tag: str, attr: str, value: str) -> None:
        for part in value.split(",") if attr == "srcset" else [value]:
            candidate = part.strip().split()[0] if part.strip() else ""
            if not candidate:
                continue
            if candidate.startswith(("data:", "#", "mailto:", "tel:", "javascript:")):
                continue
            kind = "external" if is_external(candidate) or candidate.startswith("//") else "relative"
            self.resource_refs.append((tag, attr, candidate, kind))

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key: (value or "") for key, value in attrs}
        self.counts[tag] += 1

        if tag == "html":
            self.lang = values.get("lang") or None
        if tag == "meta" and values.get("name", "").lower() == "viewport":
            self.has_viewport = True
        if tag == "title":
            self.in_title = True
        if tag == "h1":
            self.h1 += 1
        if tag == "main":
            self.main += 1
        if tag == "nav":
            self.nav += 1
        if tag == "script" and not values.get("src"):
            self.in_script = True
        if tag == "style":
            self.in_style = True
        if tag == "img" and "alt" not in values:
            self.img_missing_alt.append(values.get("src", "(inline)"))
        if tag == "svg" and values.get("role") == "img":
            if not (values.get("aria-label") or values.get("aria-labelledby")):
                self.svg_unlabeled += 1
        if tag == "link":
            rel = values.get("rel", "").lower().split()
            if any(item in rel for item in ("stylesheet", "icon", "preload", "modulepreload", "manifest")):
                if values.get("href"):
                    self._record_resource(tag, "href", values["href"])
        for attr in RESOURCE_TAGS.get(tag, []):
            if values.get(attr):
                self._record_resource(tag, attr, values[attr])
        if tag in ("a", "area") and values.get("href") and is_external(values["href"]):
            self.external_links.append(values["href"])

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self.in_title = False
        if tag == "script":
            self.in_script = False
        if tag == "style":
            self.in_style = False

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title_text.append(data)
        if self.in_script:
            self.script_text.append(data)
        if self.in_style:
            self.style_text.append(data)


def add(findings: list[Finding], path: Path, severity: str, code: str, message: str, line: int | None = None) -> None:
    findings.append(Finding(str(path), severity, code, message, line))


def check_html(path: Path, require_offline: bool, allow_placeholders: bool) -> list[Finding]:
    findings: list[Finding] = []
    text = path.read_text(encoding="utf-8")
    size = path.stat().st_size
    lowered = text.lower()

    if not re.search(r"<!doctype\s+html", lowered):
        add(findings, path, "error", "doctype", "Missing <!doctype html>.")
    if size > 2_000_000:
        add(findings, path, "warning", "large-html", f"File is {size / 1_000_000:.1f} MB; consider compressing images.")

    audit = HTMLAudit()
    try:
        audit.feed(text)
    except Exception as exc:  # noqa: BLE001 - report malformed HTML instead of crashing
        add(findings, path, "error", "html-parse", f"HTML parser failed: {exc}")
        return findings

    if not audit.lang:
        add(findings, path, "warning", "lang", "Add a lang attribute to <html>.")
    if not audit.has_viewport:
        add(findings, path, "warning", "viewport", "Add <meta name=\"viewport\"> for mobile widths.")
    if not "".join(audit.title_text).strip():
        add(findings, path, "error", "title", "Add a non-empty <title>.")
    if audit.h1 != 1:
        add(findings, path, "warning", "h1-count", f"Expected one <h1>, found {audit.h1}.")
    if audit.main == 0:
        add(findings, path, "warning", "main", "Add a <main> landmark.")
    if audit.nav == 0:
        add(findings, path, "info", "nav", "No <nav> landmark found. Add one if the page has sections.")

    if audit.img_missing_alt:
        add(findings, path, "error", "img-alt", f"{len(audit.img_missing_alt)} image(s) missing alt text: {', '.join(audit.img_missing_alt[:5])}")
    if audit.svg_unlabeled:
        add(findings, path, "warning", "svg-label", f"{audit.svg_unlabeled} SVG(s) with role=img lack aria-label or aria-labelledby.")

    if "prefers-reduced-motion" not in lowered:
        add(findings, path, "warning", "reduced-motion", "No prefers-reduced-motion rule found.")

    placeholders = sorted(set(re.findall(r"\{\{[A-Z0-9_]+\}\}", text)))
    if placeholders and not allow_placeholders:
        add(findings, path, "error", "placeholders", f"Unreplaced template placeholders: {', '.join(placeholders[:8])}")

    if audit.resource_refs:
        details = "; ".join(f"<{tag} {attr}={value}> ({kind})" for tag, attr, value, kind in audit.resource_refs[:8])
        severity = "error" if require_offline else "warning"
        add(findings, path, severity, "resource-ref", f"External or separate resource reference(s): {details}")

    script = "\n".join(audit.script_text)
    if re.search(r"\b(fetch|XMLHttpRequest|WebSocket|EventSource|sendBeacon)\b", script):
        add(findings, path, "warning", "network-api", "Inline script contains a network API. Confirm that the page works offline.")

    style = "\n".join(audit.style_text)
    if re.search(r"@import\b", style) or re.search(r"url\(\s*['\"]?(?:https?:)?//", style):
        add(findings, path, "error" if require_offline else "warning", "css-external", "CSS contains an external @import or url().")

    if audit.external_links:
        add(findings, path, "info", "external-links", f"{len(audit.external_links)} external hyperlink(s). Links do not block offline use.")

    if not findings:
        add(findings, path, "info", "pass", f"HTML passed basic checks ({size / 1024:.0f} KB).")
    return findings


def check_markdown(path: Path, allow_placeholders: bool) -> list[Finding]:
    findings: list[Finding] = []
    text = path.read_text(encoding="utf-8")
    lines = [line for line in text.splitlines() if line.strip()]

    if not lines:
        add(findings, path, "error", "empty", "File is empty.")
        return findings
    if not lines[0].startswith("# "):
        add(findings, path, "warning", "title", "Start the document with a single # title.")
    if len(text.split()) < 20:
        add(findings, path, "warning", "short", "Document is very short. Confirm that it is complete.")

    placeholders = sorted(set(re.findall(r"\{\{[A-Z0-9_]+\}\}", text)))
    if placeholders and not allow_placeholders:
        add(findings, path, "error", "placeholders", f"Unreplaced template placeholders: {', '.join(placeholders[:8])}")

    sources = re.search(r"(?mi)^#{1,6}\s*(?:sources?|references?|来源|参考)\s*$", text)
    if not sources:
        add(findings, path, "warning", "sources", "Add a Sources or References section.")
    else:
        tail = text[sources.end():].strip()
        if len(tail) < 3:
            add(findings, path, "warning", "sources-empty", "The Sources section is empty.")

    if not findings:
        add(findings, path, "info", "pass", "Markdown passed basic checks.")
    return findings


def check_video(path: Path) -> list[Finding]:
    findings: list[Finding] = []
    if not path.exists():
        add(findings, path, "error", "missing", "Video file not found.")
        return findings
    if path.stat().st_size == 0:
        add(findings, path, "error", "empty", "Video file is empty.")
        return findings

    ffprobe = shutil.which("ffprobe")
    if not ffprobe:
        add(findings, path, "warning", "ffprobe-missing", "ffprobe is not installed; stream checks were skipped.")
        return findings

    command = [ffprobe, "-v", "error", "-print_format", "json", "-show_format", "-show_streams", str(path)]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        add(findings, path, "error", "ffprobe", f"ffprobe failed: {result.stderr.strip()[:200]}")
        return findings

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        add(findings, path, "error", "ffprobe-json", f"Could not parse ffprobe output: {exc}")
        return findings

    streams = data.get("streams", [])
    video = next((stream for stream in streams if stream.get("codec_type") == "video"), None)
    audio = next((stream for stream in streams if stream.get("codec_type") == "audio"), None)
    duration = float(data.get("format", {}).get("duration", 0) or 0)

    if not video:
        add(findings, path, "error", "no-video", "No video stream found.")
    else:
        width = int(video.get("width", 0) or 0)
        height = int(video.get("height", 0) or 0)
        if width < 640 or height < 360:
            add(findings, path, "warning", "resolution", f"Low resolution: {width}x{height}.")
        if duration < 1:
            add(findings, path, "error", "duration", "Video duration is under one second.")
    if not audio:
        add(findings, path, "warning", "no-audio", "No audio stream found. Confirm that the video is intentionally silent.")
    if duration > 0:
        add(findings, path, "info", "duration", f"Duration: {duration:.1f} seconds.")

    sidecars = [
        path.with_suffix(".srt"),
        path.with_suffix(".vtt"),
        path.parent / "captions.srt",
        path.parent / "captions.vtt",
        path.parent / "narration.md",
        path.parent / "transcript.md",
        path.parent.parent / "captions.srt",
        path.parent.parent / "captions.vtt",
        path.parent.parent / "narration.md",
        path.parent.parent / "transcript.md",
    ]
    if not any(candidate.exists() for candidate in sidecars):
        add(findings, path, "warning", "captions", "No captions or transcript sidecar found.")

    if not findings:
        add(findings, path, "info", "pass", "Video passed basic stream checks.")
    return findings


def check_dir(path: Path, require_offline: bool, allow_placeholders: bool) -> list[Finding]:
    findings: list[Finding] = []
    found = False

    html_files = sorted(path.glob("*.html"))
    for html_file in html_files:
        found = True
        findings.extend(check_html(html_file, require_offline, allow_placeholders))

    video_files = sorted(path.glob("*.mp4")) + sorted(path.glob("output/*.mp4"))
    for video_file in video_files:
        found = True
        findings.extend(check_video(video_file))

    markdown_files = [candidate for candidate in (path / "explainer.md", path / "README.md") if candidate.exists()]
    for markdown_file in markdown_files:
        found = True
        findings.extend(check_markdown(markdown_file, allow_placeholders))

    if not found:
        add(findings, path, "error", "no-artifact", "No .html, .mp4, explainer.md, or README.md found in the directory.")
    if not (path / "sources.md").exists():
        add(findings, path, "warning", "sources-file", "Add sources.md with the claim ledger.")
    return findings


def infer_kind(path: Path) -> str:
    if path.is_dir():
        return "dir"
    suffix = path.suffix.lower()
    if suffix in (".html", ".htm"):
        return "html"
    if suffix in (".mp4", ".mov", ".webm", ".mkv"):
        return "video"
    if suffix in (".md", ".markdown", ".txt"):
        return "markdown"
    return "unknown"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("path", help="Artifact file or package directory")
    parser.add_argument("--kind", choices=["auto", "html", "video", "markdown", "dir"], default="auto")
    parser.add_argument("--require-offline", action="store_true", help="Fail on external or separate resources in HTML")
    parser.add_argument("--allow-placeholders", action="store_true", help="Do not fail on {{PLACEHOLDER}} text")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as failures")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    args = parser.parse_args()

    path = Path(args.path)
    if not path.exists():
        print(f"{path}: ERROR missing: Path does not exist.", file=sys.stderr)
        return 1

    kind = args.kind if args.kind != "auto" else infer_kind(path)
    if kind == "unknown":
        print(f"{path}: ERROR kind: Cannot infer artifact type. Use --kind.", file=sys.stderr)
        return 1

    if kind == "html":
        findings = check_html(path, args.require_offline, args.allow_placeholders)
    elif kind == "video":
        findings = check_video(path)
    elif kind == "markdown":
        findings = check_markdown(path, args.allow_placeholders)
    else:
        findings = check_dir(path, args.require_offline, args.allow_placeholders)

    counts = Counter(finding.severity for finding in findings)
    if args.json:
        print(json.dumps({"path": str(path), "kind": kind, "findings": [asdict(f) for f in findings], "summary": dict(counts)}, ensure_ascii=False, indent=2))
    else:
        for finding in findings:
            location = f"{finding.path}:{finding.line}" if finding.line else finding.path
            print(f"{location}: {finding.severity.upper()} {finding.code}: {finding.message}")
        print(f"\nSummary: {counts.get('error', 0)} error(s), {counts.get('warning', 0)} warning(s), {counts.get('info', 0)} info.")

    if counts.get("error", 0):
        return 1
    if args.strict and counts.get("warning", 0):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
