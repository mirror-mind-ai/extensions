"""Ariad local instance update checks."""

from __future__ import annotations

import argparse
import filecmp
import sys
from dataclasses import dataclass
from pathlib import Path

from src.adopt import AdoptionPlanError, iter_template_files, resolve_project_path, resolve_templates_root


@dataclass(frozen=True)
class UpdateReport:
    project_path: Path
    templates_root: Path
    missing: tuple[str, ...]
    differs: tuple[str, ...]
    up_to_date: tuple[str, ...]

    @property
    def has_changes(self) -> bool:
        return bool(self.missing or self.differs)


def build_update_report(project_path: Path, templates_root: Path) -> UpdateReport:
    project = project_path.expanduser().resolve()
    if not project.exists() or not project.is_dir():
        raise AdoptionPlanError(f"Project path does not exist or is not a directory: {project}")

    missing: list[str] = []
    differs: list[str] = []
    up_to_date: list[str] = []

    for rel_path in iter_template_files(templates_root):
        source = templates_root / rel_path
        target = project / rel_path
        if not target.exists():
            missing.append(rel_path)
        elif not target.is_file():
            differs.append(rel_path)
        elif filecmp.cmp(source, target, shallow=False):
            up_to_date.append(rel_path)
        else:
            differs.append(rel_path)

    return UpdateReport(
        project_path=project,
        templates_root=templates_root,
        missing=tuple(missing),
        differs=tuple(differs),
        up_to_date=tuple(up_to_date),
    )


def render_update_report(report: UpdateReport) -> str:
    lines: list[str] = []
    lines.append("Ariad update report")
    lines.append("")
    lines.append(f"Project: {report.project_path}")
    lines.append(f"Canonical templates: {report.templates_root}")
    lines.append("")

    lines.append("Missing locally:")
    if report.missing:
        for rel_path in report.missing:
            lines.append(f"- {rel_path}")
    else:
        lines.append("- (none)")

    lines.append("")
    lines.append("Different from canonical:")
    if report.differs:
        for rel_path in report.differs:
            lines.append(f"- {rel_path}")
    else:
        lines.append("- (none)")

    lines.append("")
    lines.append("Up to date:")
    if report.up_to_date:
        for rel_path in report.up_to_date:
            lines.append(f"- {rel_path}")
    else:
        lines.append("- (none)")

    lines.append("")
    lines.append("Mode: report-only (no files written)")
    return "\n".join(lines) + "\n"


def cmd_update(api, argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Compare a local Ariad instance to canonical templates")
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--project-path", "--root", dest="project_path")
    target.add_argument("--journey", dest="journey_id")
    parser.add_argument(
        "--ariad-root",
        help="Canonical Ariad repository root. Defaults to ARIAD_ROOT or ~/ariad.",
    )
    args = parser.parse_args(argv)

    try:
        project = resolve_project_path(
            api,
            project_path=args.project_path,
            journey_id=args.journey_id,
        )
        templates_root = resolve_templates_root(args.ariad_root)
        report = build_update_report(project, templates_root)
    except AdoptionPlanError as exc:
        sys.stderr.write(f"{exc}\n")
        return 1

    sys.stdout.write(render_update_report(report))
    return 0
