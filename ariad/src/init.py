"""Ariad project initialization."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from src.adopt import (
    AdoptionPlanError,
    apply_adoption_plan,
    build_adoption_plan,
    render_plan,
    render_result,
    resolve_templates_root,
)


def cmd_init(_api, argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Initialize a project with Ariad templates")
    parser.add_argument("--project-path", "--root", dest="project_path", required=True)
    parser.add_argument(
        "--ariad-root",
        help="Canonical Ariad repository root. Defaults to ARIAD_ROOT or ~/ariad.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report planned initialization without writing files.",
    )
    args = parser.parse_args(argv)

    project = Path(args.project_path).expanduser().resolve()

    try:
        templates_root = resolve_templates_root(args.ariad_root)
    except AdoptionPlanError as exc:
        sys.stderr.write(f"{exc}\n")
        return 1

    if args.dry_run:
        if project.exists() and not project.is_dir():
            sys.stderr.write(f"Project path exists but is not a directory: {project}\n")
            return 1
        # For dry-run, plan against an existing temp-like view. If the
        # directory does not exist yet, every template is missing.
        if project.exists():
            plan = build_adoption_plan(project, templates_root)
        else:
            from src.adopt import AdoptionPlan, iter_template_files

            plan = AdoptionPlan(
                project_path=project,
                templates_root=templates_root,
                would_create=iter_template_files(templates_root),
                would_not_overwrite=(),
            )
        sys.stdout.write(render_plan(plan).replace("Ariad adoption plan", "Ariad initialization plan", 1))
        return 0

    try:
        if project.exists() and not project.is_dir():
            raise AdoptionPlanError(f"Project path exists but is not a directory: {project}")
        project.mkdir(parents=True, exist_ok=True)
        plan = build_adoption_plan(project, templates_root)
        result = apply_adoption_plan(plan)
    except AdoptionPlanError as exc:
        sys.stderr.write(f"{exc}\n")
        return 1

    sys.stdout.write(render_result(result).replace("Ariad adoption result", "Ariad initialization result", 1))
    return 0
