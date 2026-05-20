"""Ariad readiness checks for target projects."""

from __future__ import annotations

import argparse
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

    @property
    def missing(self) -> tuple[str, ...]:
        return tuple(check.path for check in self.checks if not check.ok)

    @property
    def ready(self) -> bool:
        return self.exists and not self.missing and not self.warnings


def inspect_project(project_path: Path) -> DoctorReport:
    root = project_path.expanduser().resolve()
    if not root.exists() or not root.is_dir():
        return DoctorReport(
            project_path=root,
            exists=False,
            checks=(),
            warnings=(f"Project path does not exist or is not a directory: {root}",),
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


def render_report(report: DoctorReport) -> str:
    lines: list[str] = []
    lines.append("Ariad readiness report")
    lines.append("")
    lines.append(f"Project: {report.project_path}")
    lines.append("")

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
    return "\n".join(lines) + "\n"


def cmd_doctor(_api, argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Inspect Ariad readiness for a project")
    parser.add_argument("--project-path", "--root", dest="project_path", required=True)
    args = parser.parse_args(argv)

    report = inspect_project(Path(args.project_path))
    sys.stdout.write(render_report(report))
    return 0 if report.ready else 1
