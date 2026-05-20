"""Tests for Ariad init command."""

from __future__ import annotations

from pathlib import Path

from src.init import cmd_init
from tests.test_adopt import make_ariad_root


def test_cmd_init_creates_project_and_templates(ariad_api, tmp_path: Path, capsys):
    ariad_root = make_ariad_root(tmp_path)
    project = tmp_path / "new-project"

    rc = cmd_init(ariad_api, ["--project-path", str(project), "--ariad-root", str(ariad_root)])

    out = capsys.readouterr().out
    assert rc == 0
    assert "Ariad initialization result" in out
    assert (project / "AGENTS.md").exists()
    assert (project / "docs" / "process" / "development-guide.md").exists()


def test_cmd_init_dry_run_does_not_create_project(ariad_api, tmp_path: Path, capsys):
    ariad_root = make_ariad_root(tmp_path)
    project = tmp_path / "new-project"

    rc = cmd_init(
        ariad_api,
        ["--project-path", str(project), "--ariad-root", str(ariad_root), "--dry-run"],
    )

    out = capsys.readouterr().out
    assert rc == 0
    assert "Ariad initialization plan" in out
    assert "Mode: dry-run" in out
    assert not project.exists()


def test_cmd_init_preserves_existing_files(ariad_api, tmp_path: Path, capsys):
    ariad_root = make_ariad_root(tmp_path)
    project = tmp_path / "project"
    project.mkdir()
    (project / "AGENTS.md").write_text("existing\n", encoding="utf-8")

    rc = cmd_init(ariad_api, ["--project-path", str(project), "--ariad-root", str(ariad_root)])

    out = capsys.readouterr().out
    assert rc == 0
    assert "Skipped existing:" in out
    assert (project / "AGENTS.md").read_text(encoding="utf-8") == "existing\n"


def test_cmd_init_errors_if_project_path_is_file(ariad_api, tmp_path: Path, capsys):
    ariad_root = make_ariad_root(tmp_path)
    project = tmp_path / "not-dir"
    project.write_text("x", encoding="utf-8")

    rc = cmd_init(ariad_api, ["--project-path", str(project), "--ariad-root", str(ariad_root)])

    captured = capsys.readouterr()
    assert rc == 1
    assert "not a directory" in captured.err
