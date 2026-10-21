import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
AUDIO = ROOT / "audio"

def run(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise SystemExit("command failed: " + " ".join(cmd) + "\n" + result.stderr[-2000:])
    return result

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

def fmt_srt(t):
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

def fmt_vtt(t):
    return fmt_srt(t).replace(",", ".")

def split_cue(start, end, body):
    if end - start <= 5.8 and len(body) <= 32:
        return [(start, end, body)]
    marks = list(re.finditer(r"[，；。！？：]", body))
    if not marks:
        return [(start, end, body)]
    mid = len(body) / 2.0
    cut = min(marks, key=lambda m: abs(m.end() - mid))
    left = body[:cut.end()].strip()
    right = body[cut.end():].strip()
    if not left or not right or len(left) < 2 or len(right) < 2:
        return [(start, end, body)]
    frac = len(left) / float(len(left) + len(right))
    t = start + (end - start) * frac
    return split_cue(start, t, left) + split_cue(t, end, right)

def main():
    data = json.loads((AUDIO / "timings.json").read_text(encoding="utf-8"))
    wavs = []
    cues = []
    for scene in data["scenes"]:
        sid = scene["id"]
        target = float(scene["duration"])
        lead = float(scene["lead"])
        audio_dur = float(scene["audio_duration"])
        pad = target - lead - audio_dur
        if pad < 0.05:
            raise SystemExit(f"{sid}: not enough room (pad={pad:.3f})")
        src = AUDIO / f"{sid}.mp3"
        dst = AUDIO / f"{sid}.wav"
        fade_out = max(0.0, target - 0.2)
        af = (
            f"adelay={int(round(lead * 1000))}:all=1,"
            f"apad=pad_dur={pad:.3f},"
            "loudnorm=I=-16:TP=-1.5:LRA=11,"
            "aresample=48000,"
            "afade=t=in:st=0:d=0.06,"
            f"afade=t=out:st={fade_out:.3f}:d=0.2"
        )
        run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(src),
             "-af", af, "-ac", "2", "-ar", "48000", "-t", f"{target:.3f}",
             "-c:a", "pcm_s16le", str(dst)])
        wavs.append(dst)
        scene_start = float(scene["start"])
        for start, end, body in parse_vtt(AUDIO / f"{sid}.vtt"):
            cues.append((scene_start + lead + start, scene_start + lead + end, body))
        print(f"{sid}: {audio_dur:.2f}s + lead {lead:.2f} + pad {pad:.2f} = {target:.2f}s")

    list_path = AUDIO / "wav_list.txt"
    list_path.write_text("".join(f"file '{p}'\n" for p in wavs), encoding="utf-8")
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0",
         "-i", str(list_path), "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2",
         str(AUDIO / "narration.wav")])
    print("narration.wav", duration(AUDIO / "narration.wav"))

    expanded = []
    for cue in cues:
        expanded.extend(split_cue(*cue))
    fixed = []
    prev_end = 0.0
    for start, end, body in expanded:
        start = max(start, prev_end)
        end = max(end, start + 0.55)
        fixed.append((start, end, body))
        prev_end = end

    srt = []
    for i, (start, end, body) in enumerate(fixed, 1):
        srt.append(f"{i}\n{fmt_srt(start)} --> {fmt_srt(end)}\n{body}\n")
    (ROOT / "captions.srt").write_text("\n".join(srt), encoding="utf-8")
    vtt = ["WEBVTT", ""]
    for start, end, body in fixed:
        vtt.append(f"{fmt_vtt(start)} --> {fmt_vtt(end)}\n{body}\n")
    (ROOT / "captions.vtt").write_text("\n".join(vtt), encoding="utf-8")
    print("captions", len(fixed))

if __name__ == "__main__":
    main()
