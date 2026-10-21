import json
import os
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
AUDIO = ROOT / "audio"
EDGE = os.environ.get("EDGE_TTS") or shutil.which("edge-tts") or "edge-tts"
VOICE = "zh-CN-XiaoxiaoNeural"
RATE = "+0%"

SCENES = [
    ("S01", "hook", 0.35, 0.9),
    ("S02", "problem", 0.40, 0.9),
    ("S03", "attention", 0.40, 1.0),
    ("S04", "heads", 0.40, 0.9),
    ("S05", "position", 0.40, 0.9),
    ("S06", "block", 0.40, 1.0),
    ("S07", "recap", 0.45, 1.2),
]

def duration(path):
    out = subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=nw=1:nk=1", str(path)
    ], text=True).strip()
    return float(out)

def parse_vtt(path):
    text = path.read_text(encoding="utf-8").replace("\ufeff", "")
    pattern = re.compile(
        r"(\d{2}):(\d{2}):(\d{2})[,.](\d{3})\s*-->\s*"
        r"(\d{2}):(\d{2}):(\d{2})[,.](\d{3})\s*\n(.*?)(?=\n\s*\n|\Z)", re.S)
    cues = []
    for m in pattern.finditer(text):
        h1, m1, s1, ms1, h2, m2, s2, ms2, body = m.groups()
        start = int(h1)*3600 + int(m1)*60 + int(s1) + int(ms1)/1000
        end = int(h2)*3600 + int(m2)*60 + int(s2) + int(ms2)/1000
        body = re.sub(r"\s+", " ", body).strip()
        if body:
            cues.append((start, end, body))
    return cues

def main():
    AUDIO.mkdir(exist_ok=True)
    text = (ROOT / "narration.md").read_text(encoding="utf-8")
    sections = re.split(r"^## Scene (\d+) · ([a-z-]+)\s*$", text, flags=re.M)
    texts = []
    for i in range(1, len(sections), 3):
        texts.append(sections[i+2].strip())
    if len(texts) != len(SCENES):
        raise SystemExit(f"expected {len(SCENES)} scenes, found {len(texts)}")

    rows = []
    for (sid, slug, lead, tail), body in zip(SCENES, texts):
        mp3 = AUDIO / f"{sid}.mp3"
        vtt = AUDIO / f"{sid}.vtt"
        cmd = [EDGE, "--voice", VOICE, "--rate=" + RATE, "--pitch=+0Hz",
               "--text", body, "--write-media", str(mp3), "--write-subtitles", str(vtt)]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise SystemExit(f"{sid} TTS failed:\n{result.stderr[-2000:]}")
        d = duration(mp3)
        scene_duration = round(lead + d + tail, 3)
        rows.append({
            "id": sid, "slug": slug, "text": body,
            "audio_duration": round(d, 3),
            "lead": lead, "tail": tail,
            "duration": scene_duration,
        })
        print(sid, slug, f"audio={d:.3f}s", f"scene={scene_duration:.3f}s")

    start = 0.0
    for row in rows:
        row["start"] = round(start, 3)
        start += row["duration"]
        row["end"] = round(start, 3)
    total = round(start, 3)

    (AUDIO / "timings.json").write_text(json.dumps({"total": total, "scenes": rows}, ensure_ascii=False, indent=2), encoding="utf-8")
    print("total", total)
    print("wrote audio/timings.json")

if __name__ == "__main__":
    main()
