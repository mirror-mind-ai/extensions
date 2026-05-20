"""Tests for Ariad adopt dry-run planning."""

from __future__ import annotations

from pathlib import Path

from src.adopt import apply_adoption_plan, build_adoption_plan, cmd_adopt, resolve_templates_root
from tests.conftest import seed_journey


def make_ariad_root(tmp_path: Path) -> Path:
    root = tmp_path / "ariad"
    templates = root / "docs" / "project-templates"
    for rel_path in (
        "AGENTS.md",
        "docs/process/development-guide.md",
        "docs/process/worklog.md",
        "docs/product/principles.md",
        "docs/project/briefing.md",
        "docs/project/decisions.md",
        "docs/project/roadmap/index.md",
        "index.md",
    ):
        path = templates / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"# {rel_path}\n", encoding="utf-8")
    return root


def test_build_adoption_plan_for_empty_project(tmp_path: Path):
    ariad_root = make_ariad_root(tmp_path)
    project = tmp_path / "project"
    project.mkdir()

    plan = build_adoption_plan(project, resolve_templates_root(ariad_root))

    assert "AGENTS.md" in plan.would_create
    assert "docs/process/development-guide.md" in plan.would_create
    assert "index.md" not in plan.would_create
    assert plan.would_not_overwrite == ()


def test_build_adoption_plan_for_partially_adopted_project(tmp_path: Path):
    ariad_root = make_ariad_root(tmp_path)
    project = tmp_path / "project"
    (project / "docs" / "project").mkdir(parents=True)
    (project / "AGENTS.md").write_text("existing\n", encoding="utf-8")
    (project / "docs" / "project" / "decisions.md").write_text("existing\n", encoding="utf-8")

    plan = build_adoption_plan(project, resolve_templates_root(ariad_root))

    assert "AGENTS.md" in plan.would_not_overwrite
    assert "docs/project/decisions.md" in plan.would_not_overwrite
    assert "docs/project/briefing.md" in plan.would_create


def test_cmd_adopt_dry_run_reports_plan(ariad_api, tmp_path: Path, capsys):
    ariad_root = make_ariad_root(tmp_path)
    project = tmp_path / "project"
    project.mkdir()

    rc = cmd_adopt(
        ariad_api,
        ["--project-path", str(project), "--ariad-root", str(ariad_root), "--dry-run"],
    )

    out = capsys.readouterr().out
    assert rc == 0
    assert "Ariad adoption plan" in out
    assert "Would create:" in out
    assert "Mode: dry-run" in out


def test_cmd_adopt_resolves_project_from_journey(ariad_api, tmp_path: Path, capsys):
    ariad_root = make_ariad_root(tmp_path)
    project = tmp_path / "project"
    project.mkdir()
    seed_journey(ariad_api, "diario", project)

    rc = cmd_adopt(
        ariad_api,
        ["--journey", "diario", "--ariad-root", str(ariad_root), "--dry-run"],
    )

    out = capsys.readouterr().out
    assert rc == 0
    assert f"Project: {project.resolve()}" in out


def test_apply_adoption_plan_creates_missing_templates(tmp_path: Path):
    ariad_root = make_ariad_root(tmp_path)
    project = tmp_path / "project"
    project.mkdir()
    plan = build_adoption_plan(project, resolve_templates_root(ariad_root))

    result = apply_adoption_plan(plan)

    assert "AGENTS.md" in result.created
    assert (project / "AGENTS.md").exists()
    assert (project / "docs" / "process" / "development-guide.md").exists()
    assert not (project / "index.md").exists()


def test_apply_adoption_plan_preserves_existing_files(tmp_path: Path):
    ariad_root = make_ariad_root(tmp_path)
    project = tmp_path / "project"
    project.mkdir()
    (project / "AGENTS.md").write_text("existing\n", encoding="utf-8")
    plan = build_adoption_plan(project, resolve_templates_root(ariad_root))

    result = apply_adoption_plan(plan)

    assert "AGENTS.md" in result.skipped_existing
    assert (project / "AGENTS.md").read_text(encoding="utf-8") == "existing\n"
    assert (project / "docs" / "process" / "development-guide.md").exists()


def test_cmd_adopt_write_mode_reports_created_files(ariad_api, tmp_path: Path, capsys):
    ariad_root = make_ariad_root(tmp_path)
    project = tmp_path / "project"
    project.mkdir()

    rc = cmd_adopt(ariad_api, ["--project-path", str(project), "--ariad-root", str(ariad_root)])

    out = capsys.readouterr().out
    assert rc == 0
    assert "Ariad adoption result" in out
    assert "Created:" in out
    assert "Mode: write" in out
    assert (project / "AGENTS.md").exists()


def test_cmd_adopt_dry_run_does_not_write(ariad_api, tmp_path: Path, capsys):
    ariad_root = make_ariad_root(tmp_path)
    project = tmp_path / "project"
    project.mkdir()

    rc = cmd_adopt(
        ariad_api,
        ["--project-path", str(project), "--ariad-root", str(ariad_root), "--dry-run"],
    )

    out = capsys.readouterr().out
    assert rc == 0
    assert "Mode: dry-run" in out
    assert not (project / "AGENTS.md").exists()


def test_cmd_adopt_write_mode_resolves_project_from_journey(ariad_api, tmp_path: Path, capsys):
    ariad_root = make_ariad_root(tmp_path)
    project = tmp_path / "project"
    project.mkdir()
    seed_journey(ariad_api, "diario", project)

    rc = cmd_adopt(ariad_api, ["--journey", "diario", "--ariad-root", str(ariad_root)])

    out = capsys.readouterr().out
    assert rc == 0
    assert f"Project: {project.resolve()}" in out
    assert (project / "AGENTS.md").exists()


def test_cmd_adopt_errors_for_missing_ariad_root(ariad_api, tmp_path: Path, capsys):
    project = tmp_path / "project"
    project.mkdir()

    rc = cmd_adopt(
        ariad_api,
        ["--project-path", str(project), "--ariad-root", str(tmp_path / "missing"), "--dry-run"],
    )

    captured = capsys.readouterr()
    assert rc == 1
    assert "Ariad root does not exist" in captured.err


def test_cmd_adopt_errors_for_missing_templates_root(ariad_api, tmp_path: Path, capsys):
    ariad_root = tmp_path / "ariad"
    ariad_root.mkdir()
    project = tmp_path / "project"
    project.mkdir()

    rc = cmd_adopt(
        ariad_api,
        ["--project-path", str(project), "--ariad-root", str(ariad_root), "--dry-run"],
    )

    captured = capsys.readouterr()
    assert rc == 1
    assert "Ariad project templates not found" in captured.err
