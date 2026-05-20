"""Ariad adoption planning for target projects."""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

from src.doctor import ProjectResolutionError, resolve_project_path

# ``docs/project-templates/index.md`` documents the template set inside the
# canonical Ariad site. It is not itself copied into target projects.
_TEMPLATE_DOC_FILES = {"index.md"}


@dataclass(frozen=True)
class AdoptionPlan:
    project_path: Path
    templates_root: Path
    would_create: tuple[str, ...]
    would_not_overwrite: tuple[str, ...]


class AdoptionPlanError(ValueError):
    """Raised when an adoption plan cannot be built."""


def resolve_templates_root(ariad_root: str | Path) -> Path:
    root = Path(ariad_root).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        raise AdoptionPlanError(f"Ariad root does not exist or is not a directory: {root}")

    templates_root = root / "docs" / "project-templates"
    if not templates_root.exists() or not templates_root.is_dir():
        raise AdoptionPlanError(f"Ariad project templates not found: {templates_root}")
    return templates_root


def iter_template_files(templates_root: Path) -> tuple[str, ...]:
    rel_paths: list[str] = []
    for path in sorted(templates_root.rglob("*")):
        if not path.is_file():
            continue
        rel_path = path.relative_to(templates_root).as_posix()
        if rel_path in _TEMPLATE_DOC_FILES:
            continue
        rel_paths.append(rel_path)
    return tuple(rel_paths)


def build_adoption_plan(project_path: Path, templates_root: Path) -> AdoptionPlan:
    project = project_path.expanduser().resolve()
    if not project.exists() or not project.is_dir():
        raise AdoptionPlanError(f"Project path does not exist or is not a directory: {project}")

    would_create: list[str] = []
    would_not_overwrite: list[str] = []

    for rel_path in iter_template_files(templates_root):
        target = project / rel_path
        if target.exists():
            would_not_overwrite.append(rel_path)
        else:
            would_create.append(rel_path)

    return AdoptionPlan(
        project_path=project,
        templates_root=templates_root,
        would_create=tuple(would_create),
        would_not_overwrite=tuple(would_not_overwrite),
    )


def render_plan(plan: AdoptionPlan) -> str:
    lines: list[str] = []
    lines.append("Ariad adoption plan")
    lines.append("")
    lines.append(f"Project: {plan.project_path}")
    lines.append(f"Canonical templates: {plan.templates_root}")
    lines.append("")

    lines.append("Would create:")
    if plan.would_create:
        for rel_path in plan.would_create:
            lines.append(f"- {rel_path}")
    else:
        lines.append("- (none)")

    lines.append("")
    lines.append("Would not overwrite:")
    if plan.would_not_overwrite:
        for rel_path in plan.would_not_overwrite:
            lines.append(f"- {rel_path}")
    else:
        lines.append("- (none)")

    lines.append("")
    lines.append("Mode: dry-run (no files written)")
    return "\n".join(lines) + "\n"


def cmd_adopt(api, argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Plan Ariad adoption for a project")
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--project-path", "--root", dest="project_path")
    target.add_argument("--journey", dest="journey_id")
    parser.add_argument("--ariad-root", required=True, help="Canonical Ariad repository root")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Required for this first slice. Report planned changes without writing files.",
    )
    args = parser.parse_args(argv)

    if not args.dry_run:
        sys.stderr.write("adopt currently requires --dry-run; no write mode is implemented yet\n")
        return 1

    try:
        project = resolve_project_path(
            api,
            project_path=args.project_path,
            journey_id=args.journey_id,
        )
        templates_root = resolve_templates_root(args.ariad_root)
        plan = build_adoption_plan(project, templates_root)
    except (ProjectResolutionError, AdoptionPlanError) as exc:
        sys.stderr.write(f"{exc}\n")
        return 1

    sys.stdout.write(render_plan(plan))
    return 0
