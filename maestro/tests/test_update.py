"""Tests for Ariad update report."""

from __future__ import annotations

from pathlib import Path

from src.adopt import apply_adoption_plan, build_adoption_plan, resolve_templates_root
from src.update import build_update_report, cmd_update
from tests.conftest import seed_journey
from tests.test_adopt import make_ariad_root


def test_update_report_detects_up_to_date_project(tmp_path: Path):
    ariad_root = make_ariad_root(tmp_path)
    project = tmp_path / "project"
    project.mkdir()
    plan = build_adoption_plan(project, resolve_templates_root(ariad_root))
    apply_adoption_plan(plan)

    report = build_update_report(project, resolve_templates_root(ariad_root))

    assert report.missing == ()
    assert report.differs == ()
    assert "AGENTS.md" in report.up_to_date


def test_update_report_detects_missing_and_different_files(tmp_path: Path):
    ariad_root = make_ariad_root(tmp_path)
    project = tmp_path / "project"
    project.mkdir()
    plan = build_adoption_plan(project, resolve_templates_root(ariad_root))
    apply_adoption_plan(plan)
    (project / "AGENTS.md").write_text("changed\n", encoding="utf-8")
    (project / "docs" / "process" / "development-guide.md").unlink()

    report = build_update_report(project, resolve_templates_root(ariad_root))

    assert "AGENTS.md" in report.differs
    assert "docs/process/development-guide.md" in report.missing


def test_cmd_update_reports_status(ariad_api, tmp_path: Path, capsys):
    ariad_root = make_ariad_root(tmp_path)
    project = tmp_path / "project"
    project.mkdir()

    rc = cmd_update(ariad_api, ["--project-path", str(project), "--ariad-root", str(ariad_root)])

    out = capsys.readouterr().out
    assert rc == 0
    assert "Ariad update report" in out
    assert "Missing locally:" in out
    assert "Mode: report-only" in out


def test_cmd_update_resolves_project_from_journey(ariad_api, tmp_path: Path, capsys):
    ariad_root = make_ariad_root(tmp_path)
    project = tmp_path / "project"
    project.mkdir()
    seed_journey(ariad_api, "diario", project)

    rc = cmd_update(ariad_api, ["--journey", "diario", "--ariad-root", str(ariad_root)])

    out = capsys.readouterr().out
    assert rc == 0
    assert f"Project: {project.resolve()}" in out


def test_cmd_update_errors_for_missing_project(ariad_api, tmp_path: Path, capsys):
    ariad_root = make_ariad_root(tmp_path)
    project = tmp_path / "missing"

    rc = cmd_update(ariad_api, ["--project-path", str(project), "--ariad-root", str(ariad_root)])

    captured = capsys.readouterr()
    assert rc == 1
    assert "Project path does not exist" in captured.err
