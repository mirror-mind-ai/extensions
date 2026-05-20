"""Tests for Ariad doctor readiness checks."""

from __future__ import annotations

from pathlib import Path

from src.doctor import cmd_doctor, inspect_project, render_report


def test_ready_project_passes(ready_project: Path):
    report = inspect_project(ready_project)

    assert report.ready is True
    assert report.missing == ()
    assert report.warnings == ()

    rendered = render_report(report)
    assert "Ariad readiness report" in rendered
    assert "✅ AGENTS.md" in rendered
    assert "Status: ready" in rendered


def test_missing_agents_fails(ready_project: Path):
    (ready_project / "AGENTS.md").unlink()

    report = inspect_project(ready_project)

    assert report.ready is False
    assert "AGENTS.md" in report.missing
    assert "❌ AGENTS.md" in render_report(report)


def test_agents_without_ariad_fails(ready_project: Path):
    (ready_project / "AGENTS.md").write_text("Generic agent instructions.\n", encoding="utf-8")

    report = inspect_project(ready_project)

    assert report.ready is False
    assert "AGENTS.md" in report.missing
    assert "exists but does not mention Ariad" in render_report(report)


def test_agents_without_local_instance_warns(ready_project: Path):
    (ready_project / "AGENTS.md").write_text("This project uses Ariad.\n", encoding="utf-8")

    report = inspect_project(ready_project)

    assert report.ready is False
    assert report.missing == ()
    assert report.warnings == (
        "AGENTS.md mentions Ariad but does not mention a local Ariad instance",
    )
    assert "Warnings:" in render_report(report)


def test_missing_required_docs_are_reported(ready_project: Path):
    (ready_project / "docs" / "project" / "briefing.md").unlink()
    (ready_project / "docs" / "product" / "principles.md").unlink()

    report = inspect_project(ready_project)

    assert report.ready is False
    assert "docs/project/briefing.md" in report.missing
    assert "docs/product/principles.md" in report.missing


def test_nonexistent_project_path_fails(tmp_path: Path):
    missing = tmp_path / "missing"

    report = inspect_project(missing)

    assert report.ready is False
    assert report.exists is False
    assert "Project path does not exist" in render_report(report)


def test_canonical_ariad_repo_is_detected(tmp_path: Path):
    for rel_path in (
        "mkdocs.yml",
        "docs/method/overview.md",
        "docs/project-templates/AGENTS.md",
        "docs/extension/index.md",
    ):
        path = tmp_path / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# marker\n", encoding="utf-8")

    report = inspect_project(tmp_path)

    assert report.canonical is True
    assert report.ok is True
    assert report.ready is False
    rendered = render_report(report)
    assert "canonical Ariad repository" in rendered
    assert "Status: canonical" in rendered


def test_cmd_doctor_returns_zero_for_canonical_repo(ariad_api, tmp_path: Path, capsys):
    for rel_path in (
        "mkdocs.yml",
        "docs/method/overview.md",
        "docs/project-templates/AGENTS.md",
        "docs/extension/index.md",
    ):
        path = tmp_path / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# marker\n", encoding="utf-8")

    rc = cmd_doctor(ariad_api, ["--project-path", str(tmp_path)])

    out = capsys.readouterr().out
    assert rc == 0
    assert "Status: canonical" in out


def test_cmd_doctor_returns_zero_for_ready_project(ariad_api, ready_project: Path, capsys):
    rc = cmd_doctor(ariad_api, ["--project-path", str(ready_project)])

    out = capsys.readouterr().out
    assert rc == 0
    assert "Status: ready" in out


def test_cmd_doctor_returns_one_for_not_ready_project(ariad_api, tmp_path: Path, capsys):
    rc = cmd_doctor(ariad_api, ["--project-path", str(tmp_path)])

    out = capsys.readouterr().out
    assert rc == 1
    assert "Status: not ready" in out
