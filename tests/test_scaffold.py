import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "scaffold.py"


def run_scaffold(tmp_path, *args):
    out = tmp_path / "project"
    cmd = [sys.executable, str(SCRIPT), "--title", "Test Project", "--out", str(out), *args]
    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    return out


def test_forward_video_scaffold(tmp_path):
    out = run_scaffold(tmp_path, "--mode", "forward", "--artifact", "video", "--renderer", "hyperframes", "--language", "zh-CN")
    for name in ["README.md", "project.json", "sources.md", "storyboard.md", "storyboard.json", "render", "qa"]:
        assert (out / name).exists(), name
    project = json.loads((out / "project.json").read_text(encoding="utf-8"))
    assert project["mode"] == "forward"
    assert project["artifact"] == "video"
    assert project["renderer"] == "hyperframes"
    assert (out / "render" / "hyperframes" / "index.html").exists()


def test_reverse_scaffold_creates_analysis(tmp_path):
    out = run_scaffold(tmp_path, "--mode", "reverse", "--artifact", "video", "--renderer", "manim")
    assert (out / "analysis" / "analysis.json").exists()
    assert (out / "analysis" / "frames").is_dir()


def test_force_required_for_non_empty(tmp_path):
    out = tmp_path / "project"
    out.mkdir()
    (out / "keep.txt").write_text("x", encoding="utf-8")
    cmd = [sys.executable, str(SCRIPT), "--title", "Test", "--out", str(out)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode != 0
    assert "not empty" in result.stderr
