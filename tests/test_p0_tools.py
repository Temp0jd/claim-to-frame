import json
import shutil
import subprocess
import sys
from pathlib import Path

import jsonschema
import pytest

ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable


def run(*args, cwd=ROOT):
    return subprocess.run([PY, *map(str, args)], cwd=cwd, capture_output=True, text=True)


def test_preflight_example_is_clean():
    result = run(
        "scripts/preflight_model.py",
        "examples/transformer/project.json",
        "--registry",
        "assets/model-registry.example.json",
        "--json",
    )
    assert result.returncode == 0, result.stderr
    data = json.loads(result.stdout)
    assert data["status"] == "pass"
    assert data["errors"] == []


def test_preflight_rejects_missing_capability(tmp_path):
    project = json.loads((ROOT / "examples/transformer/project.json").read_text(encoding="utf-8"))
    project["models"]["implementation"]["capabilities"] = ["code"]
    path = tmp_path / "project.json"
    path.write_text(json.dumps(project), encoding="utf-8")
    result = run(
        "scripts/preflight_model.py",
        path,
        "--registry",
        "assets/model-registry.example.json",
        "--json",
    )
    assert result.returncode == 1
    data = json.loads(result.stdout)
    assert any("missing required" in item for item in data["errors"])


def test_preflight_warns_when_provider_is_suspicious(tmp_path):
    project = json.loads((ROOT / "examples/transformer/project.json").read_text(encoding="utf-8"))
    project["models"]["implementation"]["provider"] = "deepseek"
    project["models"]["implementation"]["model"] = "deepseek/deepseek-v4.1-flash"
    path = tmp_path / "project.json"
    path.write_text(json.dumps(project), encoding="utf-8")
    result = run(
        "scripts/preflight_model.py",
        path,
        "--registry",
        "assets/model-registry.example.json",
        "--json",
    )
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert any("same model id is registered" in item for item in data["warnings"])


def test_retime_rewrites_timings_and_validates(tmp_path):
    board = json.loads((ROOT / "examples/transformer/storyboard.json").read_text(encoding="utf-8"))
    timings = {
        "scenes": [
            {"id": scene["id"], "duration": round(float(scene["end"]) - float(scene["start"]) + 1.0, 3)}
            for scene in board["scenes"]
        ]
    }
    timings_path = tmp_path / "timings.json"
    out_path = tmp_path / "storyboard.json"
    timings_path.write_text(json.dumps(timings), encoding="utf-8")
    result = run(
        "scripts/retime_storyboard.py",
        "examples/transformer/storyboard.json",
        "--timings",
        timings_path,
        "--out",
        out_path,
    )
    assert result.returncode == 0, result.stderr
    retimed = json.loads(out_path.read_text(encoding="utf-8"))
    assert retimed["target_duration"] == pytest.approx(sum(item["duration"] for item in timings["scenes"]), abs=0.01)
    assert retimed["scenes"][0]["start"] == 0
    assert retimed["scenes"][-1]["end"] == retimed["target_duration"]
    validate = run("scripts/validate_storyboard.py", out_path)
    assert validate.returncode == 0, validate.stdout + validate.stderr


def test_qa_video_report_matches_schema(tmp_path):
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        pytest.skip("ffmpeg/ffprobe not available")
    video = ROOT / "examples/transformer/render/final.mp4"
    if not video.exists():
        pytest.skip("example video not available")
    out = tmp_path / "qa.json"
    result = run(
        "scripts/qa_video.py",
        video,
        "--project",
        "transformer-example",
        "--storyboard",
        "examples/transformer/storyboard.json",
        "--captions",
        "examples/transformer/captions.srt",
        "--require-audio",
        "--out",
        out,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    report = json.loads(out.read_text(encoding="utf-8"))
    schema = json.loads((ROOT / "schemas/qa-report.schema.json").read_text(encoding="utf-8"))
    jsonschema.validate(report, schema)
    assert report["status"] == "pass"
    assert report["video"]["duration"] > 0


def test_qa_schema_accepts_model_and_ocr():
    report = {
        "schema_version": "1.0",
        "project": "demo",
        "generated_at": "2026-01-01T00:00:00Z",
        "status": "pass",
        "video": {"path": "final.mp4", "duration": 1.0, "width": 1920, "height": 1080, "fps": 30},
        "model": {"role": "implementation", "provider": "command-code", "model": "deepseek/deepseek-v4.1-flash"},
        "ocr": {"status": "ok", "match_rate": 1.0, "scenes": []},
        "checks": [
            {"id": "spec", "severity": "error", "status": "pass", "message": "ok"}
        ],
    }
    schema = json.loads((ROOT / "schemas/qa-report.schema.json").read_text(encoding="utf-8"))
    jsonschema.validate(report, schema)
