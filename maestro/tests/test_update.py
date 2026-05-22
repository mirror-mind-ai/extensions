"""Tests for Ariad update report."""

from __future__ import annotations

from pathlib import Path

from src.adopt import apply_adoption_plan, build_adoption_plan, resolve_templates_root
from src.update import build_update_report, cmd_update, render_update_report
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
    assert report.local_only == ()
    assert report.status == "up to date"
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
    assert report.status == "drift detected"


def test_update_report_detects_local_only_ariad_files(tmp_path: Path):
    ariad_root = make_ariad_root(tmp_path)
    project = tmp_path / "project"
    project.mkdir()
    plan = build_adoption_plan(project, resolve_templates_root(ariad_root))
    apply_adoption_plan(plan)
    (project / "docs" / "process" / "local-policy.md").write_text("# local\n", encoding="utf-8")
    (project / "docs" / "random.md").parent.mkdir(parents=True, exist_ok=True)
    (project / "docs" / "random.md").write_text("# random\n", encoding="utf-8")

    report = build_update_report(project, resolve_templates_root(ariad_root))

    assert "docs/process/local-policy.md" in report.local_only
    assert "docs/random.md" not in report.local_only


def test_render_update_report_recommends_actions_for_each_drift_type(tmp_path: Path):
    ariad_root = make_ariad_root(tmp_path)
    project = tmp_path / "project"
    project.mkdir()
    plan = build_adoption_plan(project, resolve_templates_root(ariad_root))
    apply_adoption_plan(plan)
    (project / "AGENTS.md").write_text("changed\n", encoding="utf-8")
    (project / "docs" / "process" / "development-guide.md").unlink()
    (project / "docs" / "process" / "local-policy.md").write_text("# local\n", encoding="utf-8")

    report = build_update_report(project, resolve_templates_root(ariad_root))
    rendered = render_update_report(report)

    assert "Summary:" in rendered
    assert "Local-only Ariad files:" in rendered
    assert "adopt --journey <slug> --dry-run" in rendered
    assert "Preserve local project truth by default" in rendered
    assert "Promote ideas to Ariad templates only if they are generalizable" in rendered
    assert "Status: drift detected" in rendered


def test_render_update_report_for_up_to_date_project_recommends_no_action(tmp_path: Path):
    ariad_root = make_ariad_root(tmp_path)
    project = tmp_path / "project"
    project.mkdir()
    plan = build_adoption_plan(project, resolve_templates_root(ariad_root))
    apply_adoption_plan(plan)

    report = build_update_report(project, resolve_templates_root(ariad_root))
    rendered = render_update_report(report)

    assert "No action needed" in rendered
    assert "Status: up to date" in rendered


def test_cmd_update_reports_status(ariad_api, tmp_path: Path, capsys):
    ariad_root = make_ariad_root(tmp_path)
    project = tmp_path / "project"
    project.mkdir()

    rc = cmd_update(ariad_api, ["--project-path", str(project), "--ariad-root", str(ariad_root)])

    out = capsys.readouterr().out
    assert rc == 0
    assert "Ariad update report" in out
    assert "Summary:" in out
    assert "Missing locally:" in out
    assert "Recommended next actions:" in out
    assert "Mode: report-only" in out
    assert "Status: drift detected" in out


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
