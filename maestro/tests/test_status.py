"""Tests for Maestro installation status."""

from __future__ import annotations

import shutil
from pathlib import Path

from memory.extensions.migrations import _checksum

from src import status as status_mod
from src.status import build_status_report, cmd_status, render_status
from tests.conftest import seed_journey


def make_canonical_ariad(root: Path) -> Path:
    for rel_path in (
        "mkdocs.yml",
        "docs/method/overview.md",
        "docs/project-templates/AGENTS.md",
        "docs/extension/index.md",
    ):
        path = root / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# marker\n", encoding="utf-8")
    return root


def make_extension_root(root: Path) -> Path:
    (root / "migrations").mkdir(parents=True)
    (root / "migrations" / "001_first.sql").write_text(
        "CREATE TABLE ext_maestro_first (id TEXT);\n",
        encoding="utf-8",
    )
    (root / "skill.yaml").write_text("id: maestro\n", encoding="utf-8")
    (root / "extension.py").write_text("# extension\n", encoding="utf-8")
    return root


def seed_applied_migrations(api, extension_root: Path) -> None:
    for path in sorted((extension_root / "migrations").glob("*.sql")):
        api.db.execute(
            "INSERT INTO _ext_migrations (extension_id, filename, checksum, applied_at) "
            "VALUES (?, ?, ?, '2026-05-21T00:00:00+00:00')",
            (api.extension_id, path.name, _checksum(path.read_text(encoding="utf-8"))),
        )
    api.db.commit()


def test_status_ready_when_clone_ariad_migrations_and_journey_are_ready(
    ariad_api, ready_project: Path, tmp_path: Path, monkeypatch
):
    installed = make_extension_root(tmp_path / "installed" / "maestro")
    source = tmp_path / "mirror-extensions" / "maestro"
    shutil.copytree(installed, source)
    ariad_root = make_canonical_ariad(tmp_path / "ariad")
    seed_applied_migrations(ariad_api, installed)
    seed_journey(ariad_api, "sna", ready_project)
    monkeypatch.setattr(status_mod, "installed_extension_root", lambda: installed)

    report = build_status_report(
        ariad_api,
        extensions_root=source.parent,
        ariad_root=ariad_root,
        journey_id="sna",
    )

    rendered = render_status(report)
    assert report.ready is True
    assert "Installed copy: in sync" in rendered
    assert "Ariad root: ready" in rendered
    assert "Migrations: up to date" in rendered
    assert "Journey readiness: ready" in rendered
    assert "Status: ready" in rendered


def test_status_reports_missing_source_clone(ariad_api, tmp_path: Path, monkeypatch):
    installed = make_extension_root(tmp_path / "installed" / "maestro")
    ariad_root = make_canonical_ariad(tmp_path / "ariad")
    seed_applied_migrations(ariad_api, installed)
    monkeypatch.setattr(status_mod, "installed_extension_root", lambda: installed)

    report = build_status_report(
        ariad_api,
        extensions_root=tmp_path / "missing-extensions",
        ariad_root=ariad_root,
    )

    rendered = render_status(report)
    assert report.ready is False
    assert "Source clone: missing" in rendered
    assert "git clone https://github.com/mirror-mind-ai/extensions.git ~/mirror-extensions" in rendered
    assert "Status: not ready" in rendered


def test_status_reports_out_of_sync_installed_copy(ariad_api, tmp_path: Path, monkeypatch):
    installed = make_extension_root(tmp_path / "installed" / "maestro")
    source = tmp_path / "mirror-extensions" / "maestro"
    shutil.copytree(installed, source)
    (source / "extension.py").write_text("# changed\n", encoding="utf-8")
    ariad_root = make_canonical_ariad(tmp_path / "ariad")
    seed_applied_migrations(ariad_api, installed)
    monkeypatch.setattr(status_mod, "installed_extension_root", lambda: installed)

    report = build_status_report(
        ariad_api,
        extensions_root=source.parent,
        ariad_root=ariad_root,
    )

    rendered = render_status(report)
    assert report.ready is False
    assert "Installed copy: out of sync" in rendered
    assert "extensions install maestro" in rendered


def test_status_reports_stale_installed_files(ariad_api, tmp_path: Path, monkeypatch):
    source = make_extension_root(tmp_path / "mirror-extensions" / "maestro")
    installed = tmp_path / "installed" / "maestro"
    shutil.copytree(source, installed)
    (installed / "src" / "old.py").parent.mkdir(parents=True, exist_ok=True)
    (installed / "src" / "old.py").write_text("# stale\n", encoding="utf-8")
    ariad_root = make_canonical_ariad(tmp_path / "ariad")
    seed_applied_migrations(ariad_api, installed)
    monkeypatch.setattr(status_mod, "installed_extension_root", lambda: installed)

    report = build_status_report(
        ariad_api,
        extensions_root=source.parent,
        ariad_root=ariad_root,
    )

    rendered = render_status(report)
    assert report.ready is False
    assert "Installed copy: stale installed files" in rendered
    assert f"rm -rf {installed}" in rendered
    assert "extensions install maestro" in rendered


def test_status_reports_pending_migrations(ariad_api, tmp_path: Path, monkeypatch):
    installed = make_extension_root(tmp_path / "installed" / "maestro")
    source = tmp_path / "mirror-extensions" / "maestro"
    shutil.copytree(installed, source)
    ariad_root = make_canonical_ariad(tmp_path / "ariad")
    monkeypatch.setattr(status_mod, "installed_extension_root", lambda: installed)

    report = build_status_report(
        ariad_api,
        extensions_root=source.parent,
        ariad_root=ariad_root,
    )

    rendered = render_status(report)
    assert report.ready is False
    assert "Migrations: pending" in rendered
    assert "001_first.sql" in rendered
    assert "uv run python -m memory ext maestro migrate" in rendered


def test_cmd_status_returns_nonzero_when_not_ready(ariad_api, tmp_path: Path, monkeypatch, capsys):
    installed = make_extension_root(tmp_path / "installed" / "maestro")
    monkeypatch.setattr(status_mod, "installed_extension_root", lambda: installed)

    rc = cmd_status(
        ariad_api,
        ["--extensions-root", str(tmp_path / "missing"), "--ariad-root", str(tmp_path / "ariad")],
    )

    out = capsys.readouterr().out
    assert rc == 1
    assert "Status: not ready" in out
