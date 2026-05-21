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


def overlay_status_for_journey(api, journey_id: str | None) -> WorkspaceOverlayStatus | None:
    if not journey_id:
        return None
    try:
        api.execute(
            """
            CREATE TABLE IF NOT EXISTS ext_maestro_workspace_overlays (
                journey_id TEXT PRIMARY KEY,
                ariad_root TEXT NOT NULL,
                contract_mode TEXT NOT NULL DEFAULT 'workspace_overlay',
                repo_contract_policy TEXT NOT NULL DEFAULT 'do_not_modify',
                doc_update_policy TEXT NOT NULL DEFAULT 'project_relevant_only',
                checkpoint_policy TEXT NOT NULL DEFAULT 'ariad_full',
                validation_policy TEXT NOT NULL DEFAULT 'required',
                commit_policy TEXT NOT NULL DEFAULT 'after_validated_story',
                push_policy TEXT NOT NULL DEFAULT 'ask_before_push',
                worklog_policy TEXT NOT NULL DEFAULT 'meaningful_milestones',
                documentation_detail_policy TEXT NOT NULL DEFAULT 'smallest_coherent_surface',
                branch_policy TEXT NOT NULL DEFAULT 'project_default',
                pr_policy TEXT NOT NULL DEFAULT 'project_default',
                project_path_snapshot TEXT,
                notes TEXT,
                enabled_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        api.commit()
        row = api.read(
            """
            SELECT ariad_root, repo_contract_policy, doc_update_policy,
                   checkpoint_policy, validation_policy,
                   commit_policy, push_policy, worklog_policy,
                   documentation_detail_policy, branch_policy, pr_policy
            FROM ext_maestro_workspace_overlays
            WHERE journey_id = ?
            """,
            (journey_id,),
        ).fetchone()
        binding = api.read(
            """
            SELECT 1 FROM _ext_bindings
            WHERE extension_id = ? AND capability_id = 'ariad_workspace'
              AND target_kind = 'journey' AND target_id = ?
            LIMIT 1
            """,
            (api.extension_id, journey_id),
        ).fetchone()
    except Exception:
        return None

    if row is None:
        return WorkspaceOverlayStatus(configured=False, binding_active=binding is not None)
    return WorkspaceOverlayStatus(
        configured=True,
        binding_active=binding is not None,
        ariad_root=row["ariad_root"],
        repo_contract_policy=row["repo_contract_policy"],
        doc_update_policy=row["doc_update_policy"],
        checkpoint_policy=row["checkpoint_policy"],
        validation_policy=row["validation_policy"],
        commit_policy=row["commit_policy"],
        push_policy=row["push_policy"],
        worklog_policy=row["worklog_policy"],
        documentation_detail_policy=row["documentation_detail_policy"],
        branch_policy=row["branch_policy"],
        pr_policy=row["pr_policy"],
    )


def render_report(
    report: DoctorReport,
    *,
    next_step: str | None = None,
    overlay: WorkspaceOverlayStatus | None = None,
) -> str:
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
        lines.append("Repository adoption: canonical")
        lines.append("Workspace overlay: active" if overlay and overlay.active else "Workspace overlay: inactive")
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
    if report.ready:
        lines.append("Repository adoption: ready")
    elif report.exists:
        lines.append("Repository adoption: not adopted")

    if overlay is not None:
        if overlay.active:
            lines.append("Workspace overlay: active")
            if overlay.ariad_root:
                lines.append(f"Ariad root: {overlay.ariad_root}")
            if overlay.repo_contract_policy:
                lines.append(f"Repo contract policy: {overlay.repo_contract_policy}")
            if overlay.doc_update_policy:
                lines.append(f"Doc update policy: {overlay.doc_update_policy}")
            if overlay.checkpoint_policy:
                lines.append(f"Checkpoint policy: {overlay.checkpoint_policy}")
            if overlay.validation_policy:
                lines.append(f"Validation policy: {overlay.validation_policy}")
            if overlay.commit_policy:
                lines.append(f"Commit policy: {overlay.commit_policy}")
            if overlay.push_policy:
                lines.append(f"Push policy: {overlay.push_policy}")
            if overlay.worklog_policy:
                lines.append(f"Worklog policy: {overlay.worklog_policy}")
            if overlay.documentation_detail_policy:
                lines.append(
                    f"Documentation detail policy: {overlay.documentation_detail_policy}"
                )
            if overlay.branch_policy:
                lines.append(f"Branch policy: {overlay.branch_policy}")
            if overlay.pr_policy:
                lines.append(f"PR policy: {overlay.pr_policy}")
        elif overlay.configured:
            lines.append("Workspace overlay: configured, not active in context")
        elif overlay.binding_active:
            lines.append("Workspace overlay: binding active, not configured")
        else:
            lines.append("Workspace overlay: inactive")

    if report.ready:
        status = "ready"
    elif overlay and overlay.active:
        status = "workspace overlay"
    else:
        status = "not ready"

    lines.append("")
    lines.append(f"Status: {status}")
    if next_step and report.exists and status == "not ready" and not report.canonical:
        lines.append("")
        lines.append("Next step:")
        lines.append(f"  {next_step}")
    return "\n".join(lines) + "\n"


@dataclass(frozen=True)
class WorkspaceOverlayStatus:
    configured: bool
    binding_active: bool
    ariad_root: str | None = None
    repo_contract_policy: str | None = None
    doc_update_policy: str | None = None
    checkpoint_policy: str | None = None
    validation_policy: str | None = None
    commit_policy: str | None = None
    push_policy: str | None = None
    worklog_policy: str | None = None
    documentation_detail_policy: str | None = None
    branch_policy: str | None = None
    pr_policy: str | None = None

    @property
    def active(self) -> bool:
        return self.configured and self.binding_active


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
    overlay = overlay_status_for_journey(api, args.journey_id)
    sys.stdout.write(render_report(report, next_step=next_step, overlay=overlay))
    return 0 if report.ok or (overlay and overlay.active) else 1
