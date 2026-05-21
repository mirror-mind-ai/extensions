"""Workspace overlay commands for local Ariad operation."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from src.adopt import AdoptionPlanError, resolve_ariad_root
from src.doctor import project_path_for_journey

CONTRACT_MODE = "workspace_overlay"
DEFAULT_REPO_CONTRACT_POLICY = "do_not_modify"
DEFAULT_DOC_UPDATE_POLICY = "project_relevant_only"
DEFAULT_CHECKPOINT_POLICY = "ariad_full"
DEFAULT_VALIDATION_POLICY = "required"

VALID_REPO_CONTRACT_POLICIES = ("do_not_modify", "ask_before_change", "allow_if_explicit")
VALID_DOC_UPDATE_POLICIES = ("project_relevant_only", "ariad_required", "manual_only")
VALID_CHECKPOINT_POLICIES = ("ariad_full", "compressed_for_trivial", "manual")
VALID_VALIDATION_POLICIES = ("required", "when_user_visible", "manual")


@dataclass(frozen=True)
class WorkspaceOverlay:
    journey_id: str
    ariad_root: str
    contract_mode: str
    repo_contract_policy: str
    doc_update_policy: str
    checkpoint_policy: str
    validation_policy: str
    project_path_snapshot: str | None
    notes: str | None
    enabled_at: str
    updated_at: str


class OverlayError(ValueError):
    """Raised when workspace overlay configuration fails."""


def ensure_schema(api) -> None:
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
            project_path_snapshot TEXT,
            notes TEXT,
            enabled_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )
    api.commit()


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def validate_policy(name: str, value: str, allowed: tuple[str, ...]) -> str:
    if value not in allowed:
        raise OverlayError(f"invalid {name}: {value} (expected one of: {', '.join(allowed)})")
    return value


def get_overlay(api, journey_id: str) -> WorkspaceOverlay | None:
    ensure_schema(api)
    row = api.read(
        """
        SELECT journey_id, ariad_root, contract_mode, repo_contract_policy,
               doc_update_policy, checkpoint_policy, validation_policy,
               project_path_snapshot, notes, enabled_at, updated_at
        FROM ext_maestro_workspace_overlays
        WHERE journey_id = ?
        """,
        (journey_id,),
    ).fetchone()
    if row is None:
        return None
    return WorkspaceOverlay(
        journey_id=row["journey_id"],
        ariad_root=row["ariad_root"],
        contract_mode=row["contract_mode"],
        repo_contract_policy=row["repo_contract_policy"],
        doc_update_policy=row["doc_update_policy"],
        checkpoint_policy=row["checkpoint_policy"],
        validation_policy=row["validation_policy"],
        project_path_snapshot=row["project_path_snapshot"],
        notes=row["notes"],
        enabled_at=row["enabled_at"],
        updated_at=row["updated_at"],
    )


def has_binding(api, *, capability_id: str, journey_id: str) -> bool:
    row = api.read(
        """
        SELECT 1 FROM _ext_bindings
        WHERE extension_id = ? AND capability_id = ?
          AND target_kind = 'journey' AND target_id = ?
        LIMIT 1
        """,
        (api.extension_id, capability_id, journey_id),
    ).fetchone()
    return row is not None


def upsert_overlay(
    api,
    *,
    journey_id: str,
    ariad_root: Path,
    repo_contract_policy: str = DEFAULT_REPO_CONTRACT_POLICY,
    doc_update_policy: str = DEFAULT_DOC_UPDATE_POLICY,
    checkpoint_policy: str = DEFAULT_CHECKPOINT_POLICY,
    validation_policy: str = DEFAULT_VALIDATION_POLICY,
    notes: str | None = None,
) -> WorkspaceOverlay:
    ensure_schema(api)
    repo_contract_policy = validate_policy(
        "repo_contract_policy", repo_contract_policy, VALID_REPO_CONTRACT_POLICIES
    )
    doc_update_policy = validate_policy(
        "doc_update_policy", doc_update_policy, VALID_DOC_UPDATE_POLICIES
    )
    checkpoint_policy = validate_policy(
        "checkpoint_policy", checkpoint_policy, VALID_CHECKPOINT_POLICIES
    )
    validation_policy = validate_policy(
        "validation_policy", validation_policy, VALID_VALIDATION_POLICIES
    )

    project = project_path_for_journey(api, journey_id)
    project_snapshot = str(project) if project else None
    current = get_overlay(api, journey_id)
    enabled_at = current.enabled_at if current else now_iso()
    updated_at = now_iso()
    if current:
        api.execute(
            """
            UPDATE ext_maestro_workspace_overlays
            SET ariad_root = ?,
                contract_mode = ?,
                repo_contract_policy = ?,
                doc_update_policy = ?,
                checkpoint_policy = ?,
                validation_policy = ?,
                project_path_snapshot = ?,
                notes = ?,
                updated_at = ?
            WHERE journey_id = ?
            """,
            (
                str(ariad_root),
                CONTRACT_MODE,
                repo_contract_policy,
                doc_update_policy,
                checkpoint_policy,
                validation_policy,
                project_snapshot,
                notes,
                updated_at,
                journey_id,
            ),
        )
    else:
        api.execute(
            """
            INSERT INTO ext_maestro_workspace_overlays (
                journey_id, ariad_root, contract_mode, repo_contract_policy,
                doc_update_policy, checkpoint_policy, validation_policy,
                project_path_snapshot, notes, enabled_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                journey_id,
                str(ariad_root),
                CONTRACT_MODE,
                repo_contract_policy,
                doc_update_policy,
                checkpoint_policy,
                validation_policy,
                project_snapshot,
                notes,
                enabled_at,
                updated_at,
            ),
        )
    api.commit()
    overlay = get_overlay(api, journey_id)
    assert overlay is not None
    return overlay


def update_overlay(
    api,
    *,
    journey_id: str,
    ariad_root: Path | None = None,
    repo_contract_policy: str | None = None,
    doc_update_policy: str | None = None,
    checkpoint_policy: str | None = None,
    validation_policy: str | None = None,
    notes: str | None = None,
) -> WorkspaceOverlay:
    current = get_overlay(api, journey_id)
    if current is None:
        raise OverlayError(f"workspace overlay is not configured for journey '{journey_id}'")
    return upsert_overlay(
        api,
        journey_id=journey_id,
        ariad_root=ariad_root or Path(current.ariad_root),
        repo_contract_policy=repo_contract_policy or current.repo_contract_policy,
        doc_update_policy=doc_update_policy or current.doc_update_policy,
        checkpoint_policy=checkpoint_policy or current.checkpoint_policy,
        validation_policy=validation_policy or current.validation_policy,
        notes=notes if notes is not None else current.notes,
    )


def disable_overlay(api, journey_id: str) -> bool:
    ensure_schema(api)
    cursor = api.execute(
        "DELETE FROM ext_maestro_workspace_overlays WHERE journey_id = ?",
        (journey_id,),
    )
    api.commit()
    return cursor.rowcount > 0


def render_overlay_status(api, journey_id: str) -> str:
    overlay = get_overlay(api, journey_id)
    project = project_path_for_journey(api, journey_id)
    binding_active = has_binding(api, capability_id="ariad_workspace", journey_id=journey_id)
    lines: list[str] = []
    lines.append("Ariad workspace overlay")
    lines.append("")
    lines.append(f"Journey: {journey_id}")
    if project:
        lines.append(f"Project path: {project}")
    else:
        lines.append("Project path: (not configured)")

    if overlay is None:
        lines.append("Overlay: disabled")
        lines.append("Capability binding: active" if binding_active else "Capability binding: inactive")
        lines.append("")
        lines.append("Status: disabled")
        return "\n".join(lines) + "\n"

    lines.append(f"Ariad root: {overlay.ariad_root}")
    lines.append("Repository adoption: not implied by overlay")
    lines.append(f"Contract mode: {overlay.contract_mode}")
    lines.append(f"Repo contract policy: {overlay.repo_contract_policy}")
    lines.append(f"Doc update policy: {overlay.doc_update_policy}")
    lines.append(f"Checkpoint policy: {overlay.checkpoint_policy}")
    lines.append(f"Validation policy: {overlay.validation_policy}")
    if overlay.project_path_snapshot:
        lines.append(f"Project path snapshot: {overlay.project_path_snapshot}")
    if overlay.notes:
        lines.append(f"Notes: {overlay.notes}")
    lines.append("Capability binding: active" if binding_active else "Capability binding: inactive")
    lines.append("")
    if binding_active:
        lines.append("Status: active")
    else:
        lines.append("Status: configured, not active in context")
        lines.append("")
        lines.append("Next step:")
        lines.append(f"  uv run python -m memory ext maestro bind ariad_workspace --journey {journey_id}")
    return "\n".join(lines) + "\n"


def overlay_to_json(api, journey_id: str) -> str:
    overlay = get_overlay(api, journey_id)
    project = project_path_for_journey(api, journey_id)
    binding_active = has_binding(api, capability_id="ariad_workspace", journey_id=journey_id)
    payload = {
        "journey_id": journey_id,
        "project_path": str(project) if project else None,
        "binding_active": binding_active,
        "overlay": None if overlay is None else overlay.__dict__,
    }
    return json.dumps(payload, indent=2, sort_keys=True)


def _add_policy_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--repo-contract-policy", choices=VALID_REPO_CONTRACT_POLICIES)
    parser.add_argument("--doc-update-policy", choices=VALID_DOC_UPDATE_POLICIES)
    parser.add_argument("--checkpoint-policy", choices=VALID_CHECKPOINT_POLICIES)
    parser.add_argument("--validation-policy", choices=VALID_VALIDATION_POLICIES)
    parser.add_argument("--notes")


def cmd_overlay(api, argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Manage local Ariad workspace overlays")
    sub = parser.add_subparsers(dest="command", required=True)

    p_enable = sub.add_parser("enable", help="Configure a workspace overlay for a journey")
    p_enable.add_argument("--journey", required=True, dest="journey_id")
    p_enable.add_argument("--ariad-root", help="Canonical Ariad root. Defaults to ARIAD_ROOT or ~/ariad.")
    _add_policy_args(p_enable)

    p_set = sub.add_parser("set", help="Update overlay contract properties")
    p_set.add_argument("--journey", required=True, dest="journey_id")
    p_set.add_argument("--ariad-root", help="Update canonical Ariad root")
    _add_policy_args(p_set)

    p_status = sub.add_parser("status", help="Show overlay status")
    p_status.add_argument("--journey", required=True, dest="journey_id")
    p_status.add_argument("--json", action="store_true")

    p_disable = sub.add_parser("disable", help="Disable a workspace overlay")
    p_disable.add_argument("--journey", required=True, dest="journey_id")

    args = parser.parse_args(argv)

    try:
        if args.command == "enable":
            ariad_root = resolve_ariad_root(args.ariad_root)
            overlay = upsert_overlay(
                api,
                journey_id=args.journey_id,
                ariad_root=ariad_root,
                repo_contract_policy=args.repo_contract_policy or DEFAULT_REPO_CONTRACT_POLICY,
                doc_update_policy=args.doc_update_policy or DEFAULT_DOC_UPDATE_POLICY,
                checkpoint_policy=args.checkpoint_policy or DEFAULT_CHECKPOINT_POLICY,
                validation_policy=args.validation_policy or DEFAULT_VALIDATION_POLICY,
                notes=args.notes,
            )
            sys.stdout.write(render_overlay_status(api, overlay.journey_id))
            return 0

        if args.command == "set":
            ariad_root = resolve_ariad_root(args.ariad_root) if args.ariad_root else None
            overlay = update_overlay(
                api,
                journey_id=args.journey_id,
                ariad_root=ariad_root,
                repo_contract_policy=args.repo_contract_policy,
                doc_update_policy=args.doc_update_policy,
                checkpoint_policy=args.checkpoint_policy,
                validation_policy=args.validation_policy,
                notes=args.notes,
            )
            sys.stdout.write(render_overlay_status(api, overlay.journey_id))
            return 0

        if args.command == "status":
            if args.json:
                sys.stdout.write(overlay_to_json(api, args.journey_id) + "\n")
            else:
                sys.stdout.write(render_overlay_status(api, args.journey_id))
            return 0

        if args.command == "disable":
            removed = disable_overlay(api, args.journey_id)
            if removed:
                sys.stdout.write(f"disabled Ariad workspace overlay for journey/{args.journey_id}\n")
            else:
                sys.stdout.write(f"no Ariad workspace overlay configured for journey/{args.journey_id}\n")
            return 0

    except (AdoptionPlanError, OverlayError) as exc:
        sys.stderr.write(f"{exc}\n")
        return 1

    return 1
