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
    lines.append(f"Commit policy: `{overlay.commit_policy}`")
    lines.append(f"Push policy: `{overlay.push_policy}`")
    lines.append(f"Worklog policy: `{overlay.worklog_policy}`")
    lines.append(f"Documentation detail policy: `{overlay.documentation_detail_policy}`")
    lines.append(f"Branch policy: `{overlay.branch_policy}`")
    lines.append(f"PR policy: `{overlay.pr_policy}`")
    if overlay.notes:
        lines.append(f"Notes: {overlay.notes}")
    lines.append("")
    lines.append("Operate this local session through Ariad's Driver/Navigator method:")
    lines.append("- use Driver/Navigator roles;")
    lines.append("- follow the story lifecycle;")
    lines.append("- stop at checkpoints according to the checkpoint policy;")
    lines.append("- prepare a concrete validation route according to the validation policy;")
    lines.append("- run documentation and coherence review before recording project history.")
    lines.append("")
    lines.append("Navigator preference defaults and overrides:")
    if overlay.commit_policy == "after_validated_story":
        lines.append("- commit after a coherent story or meaningful change has been validated and accepted;")
    elif overlay.commit_policy == "after_any_codebase_change":
        lines.append("- commit whenever the codebase has a coherent change worth preserving, even if the broader story continues;")
    else:
        lines.append("- do not commit unless the Navigator explicitly asks;")

    if overlay.push_policy == "ask_before_push":
        lines.append("- ask before pushing to a shared remote;")
    elif overlay.push_policy == "after_accepted_story":
        lines.append("- push after each accepted story unless the Navigator redirects;")
    elif overlay.push_policy == "epic_boundary":
        lines.append("- defer push until an epic boundary unless the Navigator asks otherwise;")
    else:
        lines.append("- do not push unless the Navigator explicitly asks;")

    if overlay.worklog_policy == "meaningful_milestones":
        lines.append("- update the worklog only for meaningful milestones;")
    elif overlay.worklog_policy == "every_story":
        lines.append("- update the worklog for every completed story;")
    else:
        lines.append("- update the worklog only when the Navigator explicitly asks;")

    if overlay.documentation_detail_policy == "smallest_coherent_surface":
        lines.append("- update the smallest documentation surface that keeps the project coherent;")
    elif overlay.documentation_detail_policy == "detailed":
        lines.append("- favor detailed documentation when project truth changes;")
    else:
        lines.append("- do not update documentation unless the Navigator explicitly asks;")

    if overlay.branch_policy == "ask_before_branch":
        lines.append("- ask before creating a branch;")
    elif overlay.branch_policy == "dedicated_branch_per_story":
        lines.append("- use a dedicated branch per story;")
    else:
        lines.append("- follow the project's existing branch policy;")

    if overlay.pr_policy == "ask_before_pr":
        lines.append("- ask before opening a pull request;")
    elif overlay.pr_policy == "pr_per_story":
        lines.append("- open one pull request per completed story when remote collaboration is in scope;")
    elif overlay.pr_policy == "no_pr":
        lines.append("- do not open pull requests unless the Navigator asks;")
    else:
        lines.append("- follow the project's existing pull request policy;")
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
