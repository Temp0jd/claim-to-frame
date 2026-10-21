#!/usr/bin/env python3
"""QA a rendered video and write a structured qa_report.json.

Checks: streams/spec, duration, audio, decode, black frames, loudness,
caption overlap, storyboard timing, and optional per-scene OCR.

Examples:
    python scripts/qa_video.py final.mp4 --project my-video \
      --storyboard storyboard.json --captions captions.srt --ocr
    python scripts/qa_video.py final.mp4 --model-provider command-code \
      --model deepseek/deepseek-v4.1-flash --require-audio
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path


def run(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True)


def ffprobe(path: Path) -> dict:
    proc = run(["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", str(path)])
    if proc.returncode != 0:
        raise SystemExit(f"ffprobe failed: {proc.stderr[-1000:]}")
    return json.loads(proc.stdout)


def parse_rate(value: str | None) -> float:
    if not value:
        return 0.0
    if "/" in value:
        a, b = value.split("/", 1)
        try:
            return float(a) / float(b) if float(b) else 0.0
        except ValueError:
            return 0.0
    try:
        return float(value)
    except ValueError:
        return 0.0


def parse_srt(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8", errors="replace").replace("\ufeff", "")
    pattern = re.compile(
        r"(\d{2}):(\d{2}):(\d{2})[,.](\d{3})\s*-->\s*"
        r"(\d{2}):(\d{2}):(\d{2})[,.](\d{3})\s*\n(.*?)(?=\n\s*\n|\Z)",
        re.S,
    )
    cues = []
    for index, match in enumerate(pattern.finditer(text), 1):
        h1, m1, s1, ms1, h2, m2, s2, ms2, body = match.groups()
        start = int(h1) * 3600 + int(m1) * 60 + int(s1) + int(ms1) / 1000
        end = int(h2) * 3600 + int(m2) * 60 + int(s2) + int(ms2) / 1000
        body = re.sub(r"<[^>]+>", "", body).strip()
        cues.append({"index": index, "start": start, "end": end, "text": body})
    return cues


def loudness(path: Path) -> dict:
    proc = run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-af", "loudnorm=print_format=json", "-f", "null", "-"])
    text = proc.stderr
    start = text.rfind("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return {}
    try:
        return json.loads(text[start:end + 1])
    except json.JSONDecodeError:
        return {}


def black_segments(path: Path) -> list[float]:
    proc = run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-vf", "blackdetect=d=0.3:pix_th=0.10", "-an", "-f", "null", "-"])
    return [float(x) for x in re.findall(r"black_start:(\d+(?:\.\d+)?)", proc.stderr)]


def md5(path: Path) -> str:
    digest = hashlib.md5()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalize(text: str) -> str:
    return re.sub(r"[\s\W_]+", "", text, flags=re.UNICODE).upper()


def ocr_scenes(video: Path, storyboard: dict, workdir: Path) -> dict:
    if not shutil.which("tesseract"):
        return {"status": "skip", "reason": "tesseract not found"}
    langs = run(["tesseract", "--list-langs"]).stdout
    language = "chi_sim+eng" if "chi_sim" in langs else "eng"
    scenes = []
    total_hits = 0
    total_expected = 0
    for scene in storyboard.get("scenes", []):
        start = float(scene.get("start", 0))
        end = float(scene.get("end", start))
        midpoint = (start + end) / 2 if end > start else start
        frame = workdir / f"{scene.get('id', 'scene')}.png"
        proc = run(["ffmpeg", "-loglevel", "error", "-y", "-ss", f"{midpoint:.3f}", "-i", str(video), "-frames:v", "1", str(frame)])
        if proc.returncode != 0 or not frame.exists():
            continue
        text = run(["tesseract", str(frame), "stdout", "-l", language, "--psm", "6"]).stdout
        normalized = normalize(text)
        expected = [str(item) for item in scene.get("on_screen_text", []) if str(item).strip()]
        matched = [item for item in expected if len(normalize(item)) >= 2 and normalize(item) in normalized]
        total_hits += len(matched)
        total_expected += len(expected)
        scenes.append({
            "id": scene.get("id"),
            "time": round(midpoint, 3),
            "expected": expected,
            "matched": matched,
            "hits": len(matched),
            "of": len(expected),
        })
    rate = (total_hits / total_expected) if total_expected else 0.0
    return {"status": "ok", "language": language, "match_rate": round(rate, 3), "scenes": scenes}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("video", type=Path)
    parser.add_argument("--project", default=None)
    parser.add_argument("--storyboard", type=Path, default=None)
    parser.add_argument("--captions", type=Path, default=None)
    parser.add_argument("--out", type=Path, default=Path("qa_report.json"))
    parser.add_argument("--model-provider", default=None)
    parser.add_argument("--model", default=None)
    parser.add_argument("--silent-source", default=None)
    parser.add_argument("--promoted-from", default=None)
    parser.add_argument("--require-audio", action="store_true")
    parser.add_argument("--ocr", action="store_true")
    parser.add_argument("--strict", action="store_true", help="exit 1 on warnings too")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    for tool in ("ffprobe", "ffmpeg"):
        if not shutil.which(tool):
            raise SystemExit(f"{tool} not found; install FFmpeg before running video QA")

    video = args.video.expanduser().resolve()
    if not video.exists():
        raise SystemExit(f"video not found: {video}")

    data = ffprobe(video)
    streams = data.get("streams", [])
    video_stream = next((s for s in streams if s.get("codec_type") == "video"), None)
    audio_stream = next((s for s in streams if s.get("codec_type") == "audio"), None)
    subtitle_streams = [s for s in streams if s.get("codec_type") == "subtitle"]
    fmt = data.get("format", {})
    duration = float(fmt.get("duration") or (video_stream or {}).get("duration") or 0)
    width = int((video_stream or {}).get("width") or 0)
    height = int((video_stream or {}).get("height") or 0)
    fps = parse_rate((video_stream or {}).get("avg_frame_rate"))
    frames = int(fmt.get("nb_frames") or round(duration * fps))

    errors: list[str] = []
    warnings: list[str] = []
    checks: list[dict] = []

    def add(check_id: str, severity: str, status: str, message: str, evidence: str = "") -> None:
        checks.append({"id": check_id, "severity": severity, "status": status, "message": message, "evidence": evidence})
        if status == "fail" and severity == "error":
            errors.append(f"{check_id}: {message}")
        if status in {"warn", "fail"} and severity != "error":
            warnings.append(f"{check_id}: {message}")

    if video_stream:
        add("spec", "error", "pass", f"{width}x{height}, {fps:g} fps, {duration:.3f}s", f"{len(streams)} stream(s), {len(subtitle_streams)} subtitle stream(s)")
        if (width, height) != (1920, 1080):
            add("resolution", "warn", "warn", f"expected 1920x1080, found {width}x{height}")
        if abs(fps - 30) > 0.01:
            add("fps", "warn", "warn", f"expected 30 fps, found {fps:g}")
    else:
        add("spec", "error", "fail", "no video stream")

    if duration <= 0:
        add("duration", "error", "fail", "duration is zero or missing")
    elif args.storyboard and args.storyboard.exists():
        storyboard = json.loads(args.storyboard.read_text(encoding="utf-8"))
        target = storyboard.get("target_duration")
        if isinstance(target, (int, float)) and target > 0:
            delta = abs(duration - float(target))
            if delta > max(1.0, float(target) * 0.02):
                add("duration", "warn", "warn", f"video is {duration:.1f}s; storyboard target is {float(target):.1f}s", f"delta {delta:.2f}s")
            else:
                add("duration", "error", "pass", f"video {duration:.3f}s matches storyboard {float(target):.3f}s")
    if not any(c["id"] == "duration" for c in checks):
        add("duration", "error", "pass", f"duration {duration:.3f}s")

    if not audio_stream:
        severity = "error" if args.require_audio else "warn"
        add("audio", severity, "fail" if args.require_audio else "warn", "no audio stream")
    else:
        add("audio", "error", "pass", f"{audio_stream.get('codec_name')} {audio_stream.get('sample_rate')} Hz, {audio_stream.get('channels')} ch")
        level = loudness(video)
        if level:
            integrated = float(level.get("input_i", "nan"))
            peak = float(level.get("input_tp", "nan"))
            status = "pass"
            if integrated == integrated and not (-20.0 <= integrated <= -12.0):
                status = "warn"
                warnings.append(f"loudness: integrated {integrated:.2f} LUFS is outside -20..-12")
            if peak == peak and peak > -1.0:
                status = "warn"
                warnings.append(f"loudness: true peak {peak:.2f} dBTP is above -1.0")
            add("loudness", "warn", status, f"I={level.get('input_i')} LUFS, TP={level.get('input_tp')} dBTP", f"LRA={level.get('input_lra')}")

    decode = run(["ffmpeg", "-v", "error", "-i", str(video), "-f", "null", "-"])
    if decode.returncode != 0 or decode.stderr.strip():
        add("decode", "error", "fail", "decode errors", decode.stderr.strip()[:600])
    else:
        add("decode", "error", "pass", "full decode without errors")

    black = black_segments(video)
    if black:
        add("black-frames", "error", "fail", f"{len(black)} black segment(s) >= 0.3s", ", ".join(f"{x:.2f}s" for x in black[:8]))
    else:
        add("black-frames", "error", "pass", "no black segments >= 0.3s")

    if args.captions:
        if not args.captions.exists():
            add("captions", "error", "fail", f"caption file not found: {args.captions}")
        else:
            cues = parse_srt(args.captions)
            overlaps = [(a, b) for a, b in zip(cues, cues[1:]) if b["start"] < a["end"] - 0.01]
            if not cues:
                add("captions", "warn", "warn", "no cues parsed")
            elif overlaps:
                add("captions", "error", "fail", f"{len(overlaps)} overlapping cue pair(s)", f"first at {overlaps[0][0]['start']:.2f}s")
            elif cues[-1]["end"] > duration + 0.25:
                add("captions", "error", "fail", f"last cue ends at {cues[-1]['end']:.2f}s, after video {duration:.2f}s")
            else:
                add("captions", "error", "pass", f"{len(cues)} cues; {cues[0]['start']:.2f}s to {cues[-1]['end']:.2f}s; no overlaps")

    storyboard = None
    if args.storyboard:
        if not args.storyboard.exists():
            add("storyboard", "error", "fail", f"storyboard not found: {args.storyboard}")
        else:
            storyboard = json.loads(args.storyboard.read_text(encoding="utf-8"))
            scenes = storyboard.get("scenes", [])
            problems = []
            prev_end = 0.0
            for scene in scenes:
                start = float(scene.get("start", 0))
                end = float(scene.get("end", 0))
                if end <= start:
                    problems.append(f"{scene.get('id')}: end <= start")
                if start < prev_end - 0.01:
                    problems.append(f"{scene.get('id')}: overlaps previous")
                prev_end = max(prev_end, end)
            if problems:
                add("storyboard", "error", "fail", f"{len(problems)} scene timing problem(s)", "; ".join(problems[:5]))
            elif prev_end > duration + 0.3:
                add("storyboard", "warn", "warn", f"last scene ends at {prev_end:.2f}s, after video {duration:.2f}s")
            else:
                add("storyboard", "error", "pass", f"{len(scenes)} scenes, timing within video")

    ocr = None
    if args.ocr and storyboard:
        with tempfile.TemporaryDirectory(prefix="qa-video-") as tmp:
            ocr = ocr_scenes(video, storyboard, Path(tmp))
        if ocr.get("status") == "skip":
            add("ocr", "warn", "warn", ocr.get("reason", "OCR unavailable"))
        elif ocr.get("match_rate", 0) < 0.5:
            add("ocr", "warn", "warn", f"OCR match rate {ocr.get('match_rate'):.0%}", "review scene midpoints")
        else:
            add("ocr", "warn", "pass", f"OCR match rate {ocr.get('match_rate'):.0%} across {len(ocr.get('scenes', []))} scenes")

    status = "fail" if errors else "pass"
    report = {
        "schema_version": "1.0",
        "project": args.project or video.stem,
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "status": status,
        "video": {
            "path": str(video),
            "duration": round(duration, 6),
            "width": width,
            "height": height,
            "fps": round(fps, 3),
            "frames": frames,
            "size_bytes": video.stat().st_size,
            "md5": md5(video),
            "streams": [s.get("codec_name") for s in streams],
            "silent_source": args.silent_source,
            "promoted_from": args.promoted_from,
        },
        "checks": checks,
    }
    if args.model_provider or args.model:
        report["model"] = {"role": "implementation", "provider": args.model_provider, "model": args.model}
    if ocr:
        report["ocr"] = ocr

    args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"{args.out}: {status} ({len(errors)} error(s), {len(warnings)} warning(s))")
        for check in checks:
            print(f"  {check['status'].upper():4} {check['id']}: {check['message']}")
    return 1 if errors or (args.strict and warnings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
