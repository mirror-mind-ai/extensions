"""Ariad readiness checks for target projects."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path

REQUIRED_DOCS = (
    "docs/process/development-guide.md",
    "docs/project/briefing.md",
    "docs/project/decisions.md",
    "docs/project/roadmap/index.md",
    "docs/product/principles.md",
)

CANONICAL_MARKERS = (
    "mkdocs.yml",
    "docs/method/overview.md",
    "docs/project-templates/AGENTS.md",
    "docs/extension/index.md",
)


@dataclass(frozen=True)
class Check:
    path: str
    ok: bool
    message: str


@dataclass(frozen=True)
class DoctorReport:
    project_path: Path
    exists: bool
    checks: tuple[Check, ...]
    warnings: tuple[str, ...]
    canonical: bool = False

    @property
    def missing(self) -> tuple[str, ...]:
        return tuple(check.path for check in self.checks if not check.ok)

    @property
    def ready(self) -> bool:
        return self.exists and not self.canonical and not self.missing and not self.warnings

    @property
    def ok(self) -> bool:
        return self.ready or self.canonical


def inspect_project(project_path: Path) -> DoctorReport:
    root = project_path.expanduser().resolve()
    if not root.exists() or not root.is_dir():
        return DoctorReport(
            project_path=root,
            exists=False,
            checks=(),
            warnings=(f"Project path does not exist or is not a directory: {root}",),
        )

    if is_canonical_ariad_repo(root):
        return DoctorReport(
            project_path=root,
            exists=True,
            checks=(),
            warnings=(),
            canonical=True,
        )

    checks: list[Check] = []
    warnings: list[str] = []

    agents_path = root / "AGENTS.md"
    if agents_path.exists():
        content = agents_path.read_text(encoding="utf-8", errors="replace")
        mentions_ariad = "ariad" in content.lower()
        mentions_local_instance = "local ariad instance" in content.lower()
        if mentions_ariad:
            checks.append(Check("AGENTS.md", True, "exists and mentions Ariad"))
            if not mentions_local_instance:
                warnings.append("AGENTS.md mentions Ariad but does not mention a local Ariad instance")
        else:
            checks.append(Check("AGENTS.md", False, "exists but does not mention Ariad"))
    else:
        checks.append(Check("AGENTS.md", False, "missing"))

    for rel_path in REQUIRED_DOCS:
        path = root / rel_path
        checks.append(
            Check(
                rel_path,
                path.exists() and path.is_file(),
                "exists" if path.exists() and path.is_file() else "missing",
            )
        )

    return DoctorReport(
        project_path=root,
        exists=True,
        checks=tuple(checks),
        warnings=tuple(warnings),
    )


def is_canonical_ariad_repo(root: Path) -> bool:
    return all((root / marker).exists() for marker in CANONICAL_MARKERS)


def render_report(report: DoctorReport, *, next_step: str | None = None) -> str:
    lines: list[str] = []
    lines.append("Ariad readiness report")
    lines.append("")
    lines.append(f"Project: {report.project_path}")
    lines.append("")

    if report.canonical:
        lines.append(
            "This appears to be the canonical Ariad repository, not a local Ariad project instance."
        )
        lines.append("")
        lines.append("Status: canonical")
        return "\n".join(lines) + "\n"

    if not report.exists:
        lines.append("Status: not ready")
        lines.append("")
        lines.append("Errors:")
        for warning in report.warnings:
            lines.append(f"- {warning}")
        return "\n".join(lines) + "\n"

    for check in report.checks:
        icon = "✅" if check.ok else "❌"
        lines.append(f"{icon} {check.path} — {check.message}")

    if report.missing:
        lines.append("")
        lines.append("Missing:")
        for item in report.missing:
            lines.append(f"- {item}")

    if report.warnings:
        lines.append("")
        lines.append("Warnings:")
        for warning in report.warnings:
            lines.append(f"- {warning}")

    lines.append("")
    lines.append(f"Status: {'ready' if report.ready else 'not ready'}")
    if next_step and report.exists and not report.ready and not report.canonical:
        lines.append("")
        lines.append("Next step:")
        lines.append(f"  {next_step}")
    return "\n".join(lines) + "\n"


class ProjectResolutionError(ValueError):
    """Raised when a project path cannot be resolved for doctor."""


def project_path_for_journey(api, journey_id: str) -> Path | None:
    row = api.read(
        "SELECT metadata FROM identity WHERE layer = 'journey' AND key = ?",
        (journey_id,),
    ).fetchone()
    if row is None or not row["metadata"]:
        return None
    try:
        metadata = json.loads(row["metadata"])
    except (TypeError, json.JSONDecodeError):
        return None
    project_path = metadata.get("project_path")
    if not isinstance(project_path, str) or not project_path.strip():
        return None
    return Path(project_path).expanduser().resolve()


def resolve_project_path(api, *, project_path: str | None, journey_id: str | None) -> Path:
    if project_path:
        return Path(project_path).expanduser().resolve()
    if journey_id:
        resolved = project_path_for_journey(api, journey_id)
        if resolved is None:
            raise ProjectResolutionError(
                f"journey '{journey_id}' has no project_path configured; "
                f"run: python -m memory journey set-path {journey_id} /path/to/project"
            )
        return resolved
    raise ProjectResolutionError("doctor requires --project-path PATH or --journey SLUG")


def cmd_doctor(api, argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Inspect Ariad readiness for a project")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--project-path", "--root", dest="project_path")
    group.add_argument("--journey", dest="journey_id")
    args = parser.parse_args(argv)

    try:
        target = resolve_project_path(api, project_path=args.project_path, journey_id=args.journey_id)
    except ProjectResolutionError as exc:
        sys.stderr.write(f"{exc}\n")
        return 1

    next_step = None
    if args.project_path:
        next_step = (
            "uv run python -m memory ext maestro adopt "
            f"--project-path {target} --dry-run"
        )
    elif args.journey_id:
        next_step = (
            "uv run python -m memory ext maestro adopt "
            f"--journey {args.journey_id} --dry-run"
        )

    report = inspect_project(target)
    sys.stdout.write(render_report(report, next_step=next_step))
    return 0 if report.ok else 1
