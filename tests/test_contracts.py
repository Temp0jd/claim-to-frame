import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_project import validate_project_file  # noqa: E402
from validate_storyboard import validate_storyboard_file  # noqa: E402


def test_example_projects_validate():
    for project in sorted((ROOT / "examples").glob("*/project.json")):
        errors, warnings = validate_project_file(project)
        assert not errors, (project, errors, warnings)
        board = project.parent / "storyboard.json"
        if board.exists():
            errors, warnings = validate_storyboard_file(board)
            assert not errors, (board, errors, warnings)


def test_storyboard_rejects_overlap(tmp_path):
    board = json.loads((ROOT / "examples" / "transformer" / "storyboard.json").read_text(encoding="utf-8"))
    board["scenes"].append(
        {
            "id": "S02",
            "start": 9.0,
            "end": 11.0,
            "purpose": "recap",
            "caption": "A second scene.",
            "visual": "a card",
            "action": "the card moves",
            "on_screen_text": [],
            "audio": {},
            "renderer": "hyperframes",
            "acceptance": ["card visible"],
        }
    )
    path = tmp_path / "storyboard.json"
    path.write_text(json.dumps(board), encoding="utf-8")
    errors, _ = validate_storyboard_file(path)
    assert any("overlaps" in e for e in errors)


def test_storyboard_rejects_duplicate_ids(tmp_path):
    board = json.loads((ROOT / "examples" / "transformer" / "storyboard.json").read_text(encoding="utf-8"))
    board["scenes"].append(dict(board["scenes"][0], start=10.0, end=11.0))
    path = tmp_path / "storyboard.json"
    path.write_text(json.dumps(board), encoding="utf-8")
    errors, _ = validate_storyboard_file(path)
    assert any("duplicate scene id" in e for e in errors)


def test_project_requires_model_choice(tmp_path):
    project = json.loads((ROOT / "assets" / "project-template" / "project.json").read_text(encoding="utf-8"))
    path = tmp_path / "project.json"
    path.write_text(json.dumps(project), encoding="utf-8")
    errors, _ = validate_project_file(path)
    assert any("unset" in e for e in errors)
    errors, _ = validate_project_file(path, allow_unset_models=True)
    assert not errors
