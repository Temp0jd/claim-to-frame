#!/usr/bin/env python3
"""Heuristic STE-lite checks for Markdown or plain text.

This is a review aid, not a compliance certificate. It does not know the
ASD-STE100 approved dictionary, and it cannot check technical accuracy.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class Diagnostic:
    path: str
    line: int
    severity: str
    code: str
    message: str
    text: str


WORDY = [
    (r"\bin order to\b", "to"),
    (r"\bprior to\b", "before"),
    (r"\bdue to the fact that\b", "because"),
    (r"\bin the event of\b", "if"),
    (r"\bis able to\b", "can"),
    (r"\bhas the ability to\b", "can"),
    (r"\butilize(?:s|d|ing)?\b", "use"),
    (r"\bleverage(?:s|d|ing)?\b", "use"),
    (r"\bfacilitate(?:s|d|ing)?\b", "help"),
    (r"\bcommence(?:s|d|ing)?\b", "start"),
    (r"\bterminate(?:s|d|ing)?\b", "end"),
    (r"\bensure(?:s|d|ing)?\b", "make sure"),
    (r"\bsufficient\b", "enough"),
    (r"\badditional\b", "more"),
    (r"\ba number of\b", "some or many (be specific)"),
    (r"\bit is important that\b", "must"),
    (r"\bthere (?:is|are)\b", "use a direct subject"),
]

ABBREVIATIONS = [
    "e.g.", "i.e.", "etc.", "vs.", "Dr.", "Mr.", "Ms.", "Mrs.",
    "Fig.", "Eq.", "No.", "approx.", "Inc.", "Ltd.", "et al.",
]

CONTRACTION = re.compile(r"\b\w+(?:n't|'ll|'re|'ve|'d|'m)\b", re.IGNORECASE)
PASSIVE = re.compile(
    r"\b(?:is|are|was|were|be|been|being)\s+"
    r"(?:\w+(?:ed|en)|written|made|done|given|taken|shown|known|seen|found|held|"
    r"kept|left|set|put|run|built|sent|brought|thought|bought|caught|taught|understood)\b",
    re.IGNORECASE,
)
MODAL = re.compile(r"\b(?:should|may|might|could)\b", re.IGNORECASE)
ING_START = re.compile(r"^\s*([A-Za-z]+ing)\b")


def clean_inline(text: str) -> str:
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"!\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"(\*\*|__)(.*?)\1", r"\2", text)
    text = re.sub(r"(\*|_)(.*?)\1", r"\2", text)
    return text.strip()


def paragraphs(text: str):
    """Yield (line_number, paragraph_text) while skipping Markdown structure."""
    in_fence = False
    buf: list[str] = []
    start = 0

    for number, raw in enumerate(text.splitlines(), 1):
        line = raw.rstrip()
        stripped = line.strip()

        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            if buf:
                yield start, " ".join(buf)
                buf = []
                start = 0
            continue
        if in_fence:
            continue
        if not stripped:
            if buf:
                yield start, " ".join(buf)
                buf = []
                start = 0
            continue
        if re.match(r"^#{1,6}\s", stripped) or re.match(r"^(-{3,}|\*{3,}|_{3,})$", stripped):
            if buf:
                yield start, " ".join(buf)
                buf = []
                start = 0
            continue
        if stripped.startswith("|") and stripped.endswith("|"):
            if buf:
                yield start, " ".join(buf)
                buf = []
                start = 0
            continue
        if re.match(r"^\s*(?:[-*+]|\d+[.)])\s+", line):
            if buf:
                yield start, " ".join(buf)
                buf = []
                start = 0
            item = re.sub(r"^\s*(?:[-*+]|\d+[.)])\s+", "", line)
            yield number, clean_inline(item)
            continue
        if not buf:
            start = number
        buf.append(clean_inline(stripped))

    if buf:
        yield start, " ".join(buf)


def split_sentences(text: str) -> list[str]:
    protected = text
    for abbreviation in sorted(ABBREVIATIONS, key=len, reverse=True):
        protected = re.sub(re.escape(abbreviation), abbreviation.replace(".", "\u2024"), protected, flags=re.IGNORECASE)
    protected = re.sub(r"(?<=\d)\.(?=\d)", "\u2024", protected)
    protected = re.sub(r"([。！？])", r"\1\n", protected)
    parts = re.split(r"(?<=[.!?])\s+|\n+", protected)
    return [part.replace("\u2024", ".").strip() for part in parts if part.strip()]


def counts(text: str) -> tuple[int, int]:
    words = len(re.findall(r"[A-Za-z0-9][A-Za-z0-9'’\-]*", text))
    cjk = len(re.findall(r"[\u4e00-\u9fff]", text))
    return words, cjk


def shorten(text: str, limit: int = 160) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def analyze(text: str, path: str, max_sentence: int, max_cjk: int) -> tuple[list[Diagnostic], int]:
    diagnostics: list[Diagnostic] = []
    sentence_count = 0

    def add(line: int, severity: str, code: str, message: str, sentence: str) -> None:
        diagnostics.append(Diagnostic(path, line, severity, code, message, shorten(sentence)))

    for line, paragraph in paragraphs(text):
        sentences = split_sentences(paragraph)
        sentence_count += len(sentences)

        if len(sentences) > 6:
            add(line, "warning", "long-paragraph", f"{len(sentences)} sentences; aim for 6 or fewer.", paragraph)

        for sentence in sentences:
            words, cjk = counts(sentence)
            if words == 0 and cjk == 0:
                continue

            if cjk > 5 and cjk >= words * 0.5:
                if cjk > max_cjk:
                    add(line, "warning", "long-sentence", f"{cjk} Chinese characters; aim for {max_cjk} or fewer.", sentence)
            elif words > max_sentence:
                add(line, "warning", "long-sentence", f"{words} words; aim for {max_sentence} or fewer.", sentence)

            if CONTRACTION.search(sentence):
                add(line, "warning", "contraction", "Use the full form: do not, cannot, it is.", sentence)

            for pattern, replacement in WORDY:
                match = re.search(pattern, sentence, flags=re.IGNORECASE)
                if match:
                    add(line, "warning", "wordy", f"Consider '{replacement}' instead of '{match.group(0)}'.", sentence)

            if ";" in sentence:
                add(line, "warning", "semicolon", "Split the sentence. Use a period instead of a semicolon.", sentence)

            if re.search(r"\betc\.|\band so on\b|\band/or\b", sentence, flags=re.IGNORECASE):
                add(line, "warning", "vague", "Replace the vague list or alternative with specific items.", sentence)

            if PASSIVE.search(sentence):
                add(line, "info", "possible-passive", "Check the voice. Prefer the active voice when the actor is known.", sentence)

            if MODAL.search(sentence):
                add(line, "info", "ambiguous-modal", "Check whether should, may, might, or could hides a requirement.", sentence)

            if ING_START.search(sentence):
                add(line, "info", "ing-clause", "Check the opening -ing clause. Make the actor explicit if needed.", sentence)

            if re.search(r"\w+/\w+", sentence):
                add(line, "info", "slash", "Check whether the slash is clear. Write the alternatives in full.", sentence)

    return diagnostics, sentence_count


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Heuristic STE-lite checks. Review the output; do not treat it as compliance.",
        epilog="Example: python3 scripts/ste_lint.py explainer.md --max-sentence 20 --fail-on warning",
    )
    parser.add_argument("paths", nargs="+", help="Markdown or text files, or - for stdin")
    parser.add_argument("--max-sentence", type=int, default=20, help="Maximum words per sentence (default: 20)")
    parser.add_argument("--max-cjk", type=int, default=60, help="Maximum Chinese characters per sentence (default: 60)")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    parser.add_argument("--fail-on", choices=["none", "warning", "error"], default="none", help="Exit nonzero at this severity")
    parser.add_argument("--max-diagnostics", type=int, default=200, help="Maximum findings to print")
    args = parser.parse_args()

    all_diagnostics: list[Diagnostic] = []
    total_sentences = 0

    for item in args.paths:
        if item == "-":
            text = sys.stdin.read()
            path = "<stdin>"
        else:
            file_path = Path(item)
            if not file_path.exists():
                all_diagnostics.append(Diagnostic(item, 0, "error", "missing-file", "File not found.", ""))
                continue
            text = file_path.read_text(encoding="utf-8")
            path = str(file_path)

        diagnostics, sentence_count = analyze(text, path, args.max_sentence, args.max_cjk)
        all_diagnostics.extend(diagnostics)
        total_sentences += sentence_count

    severity_counts = Counter(diagnostic.severity for diagnostic in all_diagnostics)
    summary = {
        "files": len(args.paths),
        "sentences": total_sentences,
        "errors": severity_counts.get("error", 0),
        "warnings": severity_counts.get("warning", 0),
        "info": severity_counts.get("info", 0),
    }

    if args.json:
        print(json.dumps({"diagnostics": [asdict(d) for d in all_diagnostics], "summary": summary}, ensure_ascii=False, indent=2))
    else:
        for diagnostic in all_diagnostics[: args.max_diagnostics]:
            location = f"{diagnostic.path}:{diagnostic.line}" if diagnostic.line else diagnostic.path
            print(f"{location}: {diagnostic.severity.upper()} {diagnostic.code}: {diagnostic.message}")
            if diagnostic.text:
                print(f"  {diagnostic.text}")
        if len(all_diagnostics) > args.max_diagnostics:
            print(f"... {len(all_diagnostics) - args.max_diagnostics} more finding(s) suppressed")
        print(
            f"Summary: {summary['files']} file(s), {summary['sentences']} sentence(s), "
            f"{summary['errors']} error(s), {summary['warnings']} warning(s), {summary['info']} info."
        )
        if not all_diagnostics:
            print("No heuristic issues found. This is not a compliance check.")

    if args.fail_on == "error" and summary["errors"]:
        return 1
    if args.fail_on == "warning" and (summary["errors"] or summary["warnings"]):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
