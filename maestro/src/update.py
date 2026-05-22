"""Ariad local instance update checks."""

from __future__ import annotations

import argparse
import filecmp
import sys
from dataclasses import dataclass
from pathlib import Path

from src.adopt import AdoptionPlanError, iter_template_files, resolve_project_path, resolve_templates_root

_LOCAL_INSTANCE_ROOTS = (
    "AGENTS.md",
    "docs/process",
    "docs/product",
    "docs/project",
)


@dataclass(frozen=True)
class UpdateReport:
    project_path: Path
    templates_root: Path
    missing: tuple[str, ...]
    differs: tuple[str, ...]
    up_to_date: tuple[str, ...]
    local_only: tuple[str, ...]

    @property
    def has_changes(self) -> bool:
        return bool(self.missing or self.differs or self.local_only)

    @property
    def status(self) -> str:
        if not self.has_changes:
            return "up to date"
        return "drift detected"


def _is_within_local_instance_surface(rel_path: str) -> bool:
    if rel_path == "AGENTS.md":
        return True
    return any(rel_path.startswith(f"{root}/") for root in _LOCAL_INSTANCE_ROOTS if root != "AGENTS.md")


def iter_local_instance_files(project: Path) -> tuple[str, ...]:
    rel_paths: list[str] = []
    for root in _LOCAL_INSTANCE_ROOTS:
        path = project / root
        if path.is_file():
            rel_paths.append(root)
            continue
        if not path.exists() or not path.is_dir():
            continue
        for child in sorted(path.rglob("*")):
            if child.is_file():
                rel_paths.append(child.relative_to(project).as_posix())
    return tuple(sorted(set(rel_paths)))


def build_update_report(project_path: Path, templates_root: Path) -> UpdateReport:
    project = project_path.expanduser().resolve()
    if not project.exists() or not project.is_dir():
        raise AdoptionPlanError(f"Project path does not exist or is not a directory: {project}")

    missing: list[str] = []
    differs: list[str] = []
    up_to_date: list[str] = []

    template_files = set(iter_template_files(templates_root))

    for rel_path in sorted(template_files):
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

    local_only = tuple(
        rel_path
        for rel_path in iter_local_instance_files(project)
        if _is_within_local_instance_surface(rel_path) and rel_path not in template_files
    )

    return UpdateReport(
        project_path=project,
        templates_root=templates_root,
        missing=tuple(missing),
        differs=tuple(differs),
        up_to_date=tuple(up_to_date),
        local_only=local_only,
    )


def _append_list(lines: list[str], values: tuple[str, ...]) -> None:
    if values:
        for rel_path in values:
            lines.append(f"- {rel_path}")
    else:
        lines.append("- (none)")


def render_update_report(report: UpdateReport) -> str:
    lines: list[str] = []
    lines.append("Ariad update report")
    lines.append("")
    lines.append(f"Project: {report.project_path}")
    lines.append(f"Canonical templates: {report.templates_root}")
    lines.append("")
    lines.append("Summary:")
    lines.append(f"- Missing locally: {len(report.missing)}")
    lines.append(f"- Different from canonical: {len(report.differs)}")
    lines.append(f"- Local-only Ariad files: {len(report.local_only)}")
    lines.append(f"- Up to date: {len(report.up_to_date)}")
    lines.append("")

    lines.append("Missing locally:")
    _append_list(lines, report.missing)

    lines.append("")
    lines.append("Different from canonical:")
    _append_list(lines, report.differs)

    lines.append("")
    lines.append("Local-only Ariad files:")
    _append_list(lines, report.local_only)

    lines.append("")
    lines.append("Up to date:")
    _append_list(lines, report.up_to_date)

    lines.append("")
    lines.append("Recommended next actions:")
    if not report.has_changes:
        lines.append("- No action needed. The local Ariad instance matches the canonical templates.")
    else:
        if report.missing:
            lines.append(
                "- For missing files, run `uv run python -m memory ext maestro adopt --journey <slug> --dry-run` or the equivalent `--project-path` command, then adopt only after Navigator review."
            )
        if report.differs:
            lines.append(
                "- For different files, review the local content against canonical Ariad. Preserve local project truth by default; reconcile through Driver/Navigator review, not blind overwrite."
            )
        if report.local_only:
            lines.append(
                "- For local-only files, keep them if they express local project truth. Promote ideas to Ariad templates only if they are generalizable."
            )

    lines.append("")
    lines.append("Mode: report-only (no files written)")
    lines.append(f"Status: {report.status}")
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
