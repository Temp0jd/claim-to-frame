#!/usr/bin/env python3
"""Retiming a storyboard from measured TTS durations.

Input timings may be:
  {"scenes": [{"id": "S01", "duration": 22.5}, ...]}
  [{"id": "S01", "audio_duration": 20.8, "lead": 0.4, "tail": 0.9}, ...]
  {"S01": 22.5, "S02": 24.9, ...}

Examples:
    python scripts/retime_storyboard.py storyboard.json --timings audio/timings.json
    python scripts/retime_storyboard.py storyboard.json --timings audio/timings.json --write
    python scripts/retime_storyboard.py storyboard.json --timings audio/timings.json --fit-target 300 --out storyboard.retimed.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def load_timings(path: Path) -> dict[str, float]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict) and isinstance(data.get("scenes"), list):
        items = data["scenes"]
    elif isinstance(data, list):
        items = data
    elif isinstance(data, dict):
        return {str(k): float(v) for k, v in data.items() if isinstance(v, (int, float))}
    else:
        raise SystemExit("timings must be an object or array")

    result: dict[str, float] = {}
    for item in items:
        if not isinstance(item, dict):
            continue
        scene_id = str(item.get("id", ""))
        if not scene_id:
            continue
        duration = item.get("duration")
        if duration is None:
            duration = item.get("end", 0) - item.get("start", 0)
        if duration is None and item.get("audio_duration") is not None:
            duration = float(item["audio_duration"]) + float(item.get("lead", 0)) + float(item.get("tail", 0))
        if duration is None:
            continue
        result[scene_id] = round(float(duration), 3)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("storyboard", type=Path)
    parser.add_argument("--timings", type=Path, required=True)
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--write", action="store_true", help="overwrite the input storyboard")
    parser.add_argument("--fit-target", type=float, default=None, help="scale durations proportionally to this total")
    args = parser.parse_args()

    board = json.loads(args.storyboard.read_text(encoding="utf-8"))
    scenes = board.get("scenes")
    if not isinstance(scenes, list) or not scenes:
        raise SystemExit("storyboard has no scenes")
    timings = load_timings(args.timings)

    missing = [str(scene.get("id")) for scene in scenes if str(scene.get("id")) not in timings]
    if missing:
        raise SystemExit(f"missing measured duration for: {', '.join(missing)}")

    durations = [timings[str(scene.get("id"))] for scene in scenes]
    total = sum(durations)
    if args.fit_target and args.fit_target > 0:
        scale = args.fit_target / total
        durations = [max(0.5, round(value * scale, 3)) for value in durations]
        total = sum(durations)

    cursor = 0.0
    changes = []
    for scene, duration in zip(scenes, durations):
        old_start, old_end = scene.get("start"), scene.get("end")
        scene["start"] = round(cursor, 3)
        scene["end"] = round(cursor + duration, 3)
        cursor = scene["end"]
        changes.append((scene.get("id"), old_start, old_end, scene["start"], scene["end"]))

    board["target_duration"] = round(total, 3)
    destination = args.storyboard if args.write else args.out
    if destination:
        destination.write_text(json.dumps(board, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"{args.storyboard}: {len(scenes)} scenes, total {total:.3f}s")
    for scene_id, old_start, old_end, new_start, new_end in changes:
        print(f"  {scene_id}: {old_start}..{old_end} -> {new_start}..{new_end}")
    if not destination:
        print("dry run; pass --write or --out to save")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
