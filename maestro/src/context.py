"""Mirror context providers for Maestro."""

from __future__ import annotations

from memory.extensions.api import ContextRequest, ExtensionAPI

from src.overlay import get_overlay


def provide_ariad_workspace(api: ExtensionAPI, ctx: ContextRequest) -> str | None:
    """Inject local Ariad workspace overlay instructions for a bound journey."""
    if not ctx.journey_id:
        return None

    overlay = get_overlay(api, ctx.journey_id)
    if overlay is None:
        return None

    lines: list[str] = []
    lines.append(f"Ariad workspace overlay is active for journey `{ctx.journey_id}`.")
    lines.append("")
    lines.append("This is not repository adoption. It is a local runtime contract for this Mirror home and this journey.")
    lines.append("")
    lines.append(f"Canonical Ariad root: `{overlay.ariad_root}`")
    lines.append(f"Contract mode: `{overlay.contract_mode}`")
    lines.append(f"Repo contract policy: `{overlay.repo_contract_policy}`")
    lines.append(f"Doc update policy: `{overlay.doc_update_policy}`")
    lines.append(f"Checkpoint policy: `{overlay.checkpoint_policy}`")
    lines.append(f"Validation policy: `{overlay.validation_policy}`")
    if overlay.notes:
        lines.append(f"Notes: {overlay.notes}")
    lines.append("")
    lines.append("Operate this local session through Ariad's Driver/Navigator method:")
    lines.append("- use Driver/Navigator roles;")
    lines.append("- follow the story lifecycle;")
    lines.append("- stop at checkpoints according to the checkpoint policy;")
    lines.append("- prepare a concrete validation route according to the validation policy;")
    lines.append("- run documentation and coherence review before commit.")
    lines.append("")
    lines.append("Repository boundary:")
    if overlay.repo_contract_policy == "do_not_modify":
        lines.append("- do not edit AGENTS.md, CLAUDE.md, or equivalent agent contract files to declare Ariad;")
    elif overlay.repo_contract_policy == "ask_before_change":
        lines.append("- ask before editing AGENTS.md, CLAUDE.md, or equivalent agent contract files to declare Ariad;")
    else:
        lines.append("- repository contract files may mention Ariad only when explicitly requested for this story;")

    if overlay.doc_update_policy == "project_relevant_only":
        lines.append("- project docs may be updated only when the change is true for the project itself;")
    elif overlay.doc_update_policy == "ariad_required":
        lines.append("- keep the local Ariad documentation surface coherent with the work;")
    else:
        lines.append("- do not update project docs unless the Navigator explicitly asks;")

    lines.append("- Ariad governs local conduct; project docs govern public project truth.")
    return "\n".join(lines)
