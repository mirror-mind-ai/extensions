"""Installation and readiness status for Maestro."""

from __future__ import annotations

import argparse
import hashlib
import os
import sys
from dataclasses import dataclass
from typing import Literal
from pathlib import Path

from src.doctor import (
    ProjectResolutionError,
    inspect_project,
    overlay_status_for_journey,
    render_report,
    resolve_project_path,
)

_IGNORE_DIRS = {".git", "__pycache__", ".pytest_cache", ".ruff_cache", ".mypy_cache", ".venv", "node_modules"}
_IGNORE_SUFFIXES = {".pyc"}


@dataclass(frozen=True)
class StatusReport:
    installed_root: Path
    source_root: Path
    ariad_root: Path
    source_exists: bool
    sync_state: Literal["in sync", "out of sync", "stale installed files", "unknown"]
    ariad_ready: bool
    migration_state: str
    migration_pending: tuple[str, ...]
    migration_drift: tuple[str, ...]
    journey_status: str | None = None
    journey_report: str | None = None

    @property
    def ready(self) -> bool:
        return (
            self.source_exists
            and self.sync_state == "in sync"
            and self.ariad_ready
            and self.migration_state == "up to date"
            and (self.journey_status in (None, "ready", "workspace overlay", "canonical"))
        )


def default_extensions_root() -> Path:
    configured = os.environ.get("MIRROR_EXTENSIONS_ROOT")
    if configured:
        return Path(configured).expanduser()
    return Path("~/mirror-extensions").expanduser()


def default_ariad_root() -> Path:
    configured = os.environ.get("ARIAD_ROOT")
    if configured:
        return Path(configured).expanduser()
    return Path("~/ariad").expanduser()


def installed_extension_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _iter_hashable_files(root: Path):
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root)
        if any(part in _IGNORE_DIRS for part in rel.parts):
            continue
        if path.is_file() and path.suffix not in _IGNORE_SUFFIXES:
            yield rel, path


def tree_digest(root: Path) -> str:
    digest = hashlib.sha256()
    for rel, path in _iter_hashable_files(root):
        digest.update(str(rel).encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def _file_set(root: Path) -> set[Path]:
    return {rel for rel, _path in _iter_hashable_files(root)}


def sync_state(installed_root: Path, source_root: Path) -> Literal["in sync", "out of sync", "stale installed files", "unknown"]:
    if not source_root.exists() or not source_root.is_dir():
        return "unknown"
    if installed_root.resolve() == source_root.resolve():
        return "in sync"

    source_files = _file_set(source_root)
    installed_files = _file_set(installed_root)
    common = source_files & installed_files

    missing_from_installed = source_files - installed_files
    if missing_from_installed:
        return "out of sync"

    for rel in common:
        if (source_root / rel).read_bytes() != (installed_root / rel).read_bytes():
            return "out of sync"

    extra_installed = installed_files - source_files
    if extra_installed:
        return "stale installed files"

    return "in sync"


def migration_status(api, installed_root: Path) -> tuple[str, tuple[str, ...], tuple[str, ...]]:
    migrations_dir = installed_root / "migrations"
    if not migrations_dir.exists():
        return "up to date", (), ()

    from memory.extensions.migrations import _checksum

    pending: list[str] = []
    drift: list[str] = []
    for path in sorted(migrations_dir.glob("*.sql")):
        row = api.read(
            "SELECT checksum FROM _ext_migrations WHERE extension_id = ? AND filename = ?",
            (api.extension_id, path.name),
        ).fetchone()
        if row is None:
            pending.append(path.name)
            continue
        expected = _checksum(path.read_text(encoding="utf-8"))
        if row["checksum"] != expected:
            drift.append(path.name)

    if drift:
        return "drift", tuple(pending), tuple(drift)
    if pending:
        return "pending", tuple(pending), tuple(drift)
    return "up to date", tuple(pending), tuple(drift)


def _status_from_doctor_output(output: str) -> str | None:
    for line in reversed(output.splitlines()):
        if line.startswith("Status: "):
            return line.removeprefix("Status: ").strip()
    return None


def build_status_report(
    api,
    *,
    extensions_root: Path,
    ariad_root: Path,
    journey_id: str | None = None,
    project_path: str | None = None,
) -> StatusReport:
    installed_root = installed_extension_root()
    source_root = (extensions_root / "maestro").expanduser().resolve()
    ariad_root = ariad_root.expanduser().resolve()

    sync = sync_state(installed_root, source_root)
    migration_state, pending, drift = migration_status(api, installed_root)

    journey_status = None
    journey_report = None
    if journey_id or project_path:
        try:
            target = resolve_project_path(api, project_path=project_path, journey_id=journey_id)
            report = inspect_project(target)
            overlay = overlay_status_for_journey(api, journey_id)
            journey_report = render_report(report, overlay=overlay).strip()
            journey_status = _status_from_doctor_output(journey_report)
        except ProjectResolutionError as exc:
            journey_report = str(exc)
            journey_status = "not ready"

    return StatusReport(
        installed_root=installed_root,
        source_root=source_root,
        ariad_root=ariad_root,
        source_exists=source_root.exists() and source_root.is_dir(),
        sync_state=sync,
        ariad_ready=inspect_project(ariad_root).canonical,
        migration_state=migration_state,
        migration_pending=pending,
        migration_drift=drift,
        journey_status=journey_status,
        journey_report=journey_report,
    )


def render_status(report: StatusReport) -> str:
    lines: list[str] = []
    lines.append("Maestro status report")
    lines.append("")
    lines.append(f"Installed extension: ready ({report.installed_root})")

    if report.source_exists:
        lines.append(f"Source clone: ready ({report.source_root})")
        lines.append(f"Installed copy: {report.sync_state}")
    else:
        lines.append(f"Source clone: missing ({report.source_root})")
        lines.append("Installed copy: unknown")

    if report.ariad_ready:
        lines.append(f"Ariad root: ready ({report.ariad_root})")
    else:
        lines.append(f"Ariad root: not ready ({report.ariad_root})")

    lines.append(f"Migrations: {report.migration_state}")
    if report.migration_pending:
        lines.append("Pending migrations:")
        for filename in report.migration_pending:
            lines.append(f"- {filename}")
    if report.migration_drift:
        lines.append("Migration drift:")
        for filename in report.migration_drift:
            lines.append(f"- {filename}")

    if report.journey_status is not None:
        lines.append(f"Journey readiness: {report.journey_status}")

    lines.append("")
    lines.append(f"Status: {'ready' if report.ready else 'not ready'}")

    next_steps = next_steps_for(report)
    if next_steps:
        lines.append("")
        lines.append("Next step:")
        for step in next_steps:
            lines.append(f"  {step}")

    if report.journey_report:
        lines.append("")
        lines.append("Journey report:")
        lines.append(report.journey_report)

    return "\n".join(lines) + "\n"


def next_steps_for(report: StatusReport) -> list[str]:
    if report.ready:
        return []
    steps: list[str] = []
    if not report.source_exists:
        steps.append("git clone https://github.com/mirror-mind-ai/extensions.git ~/mirror-extensions")
    elif report.sync_state == "out of sync":
        steps.append(
            "uv run python -m memory extensions install maestro "
            f"--extensions-root {report.source_root.parent} --mirror-home $MIRROR_HOME"
        )
    elif report.sync_state == "stale installed files":
        steps.append(f"rm -rf {report.installed_root}")
        steps.append(
            "uv run python -m memory extensions install maestro "
            f"--extensions-root {report.source_root.parent} --mirror-home $MIRROR_HOME"
        )
    if not report.ariad_ready:
        steps.append("git clone https://github.com/mirror-mind-ai/ariad.git ~/ariad")
    if report.migration_state in {"pending", "drift"}:
        steps.append("uv run python -m memory ext maestro migrate")
    if report.journey_status == "not ready":
        steps.append("uv run python -m memory ext maestro doctor --journey <slug>")
    return steps


def cmd_status(api, argv: list[str]) -> int:
    """Inspect Maestro installation, source clone, Ariad root, migrations, and optional journey readiness."""
    parser = argparse.ArgumentParser(description="Inspect Maestro installation status")
    parser.add_argument("--extensions-root", default=str(default_extensions_root()))
    parser.add_argument("--ariad-root", default=str(default_ariad_root()))
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--journey", dest="journey_id")
    group.add_argument("--project-path", dest="project_path")
    args = parser.parse_args(argv)

    report = build_status_report(
        api,
        extensions_root=Path(args.extensions_root),
        ariad_root=Path(args.ariad_root),
        journey_id=args.journey_id,
        project_path=args.project_path,
    )
    sys.stdout.write(render_status(report))
    return 0 if report.ready else 1
