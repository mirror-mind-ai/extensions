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
    lines.append("Maestro checkpoint visualization:")
    lines.append("- command-first rule: at each non-trivial checkpoint, run `uv run python -m memory ext maestro checkpoint` when you can supply explicit state safely;")
    lines.append("- if you cannot run the command, render a compact fallback using Maestro's exact grammar instead of inventing a new visual language;")
    lines.append("- checkpoint names are exactly: Plan, Implement, Validate, Review, Coherence, Commit;")
    lines.append("- stage markers are exactly: `✓` completed, `◉` current, `○` pending;")
    lines.append("- Ariad Stage Ribbon format is exactly: `Ariad: ✓ Plan | ◉ Implement | ○ Validate | ○ Review | ○ Coherence | ○ Commit`;")
    lines.append("- do not use alternate lifecycle labels such as Read and Orient, Test and Validate, Document, or Record History in the Maestro ribbon;")
    lines.append("- a ribbon alone is not enough for a non-trivial checkpoint; include the checkpoint-specific visual surface below;")
    lines.append("- Plan checkpoint minimum: Bird's-Eye Map plus Ariad Stage Ribbon;")
    lines.append("- Implement checkpoint minimum: Bird's-Eye Map plus Ariad Stage Ribbon, and Flow Board when neighboring work is known;")
    lines.append("- Validate checkpoint minimum: Ariad Stage Ribbon plus Validation Panel; include automated checks, manual validation, blockers, and risk posture when known;")
    lines.append("- Review checkpoint minimum: Ariad Stage Ribbon plus concise change/refactoring/debt summary;")
    lines.append("- Coherence checkpoint minimum: Ariad Stage Ribbon plus Coherence Matrix; do not replace it with a plain prose checklist when surfaces are known;")
    lines.append("- Commit/story-close checkpoint minimum: Ariad Stage Ribbon plus Roadmap Snapshot; include Validation Panel and Coherence Matrix when evidence exists;")
    lines.append("- do not invent validation, roadmap, release, or coherence state just to render a view; unknown is acceptable.")
    lines.append("")
    lines.append("Fallback visual templates when the command is not practical:")
    lines.append("```text")
    lines.append("Bird's-Eye Map")
    lines.append("🟪[CV1]  Cart Flow")
    lines.append("  🟦[E1]   Basic Cart Behavior")
    lines.append("    🟨[S1]  Add item to cart")
    lines.append("")
    lines.append("Ariad: ◉ Plan | ○ Implement | ○ Validate | ○ Review | ○ Coherence | ○ Commit")
    lines.append("")
    lines.append("Validation Panel")
    lines.append("Automated checks: ? unknown")
    lines.append("Manual validation: ? unknown")
    lines.append("Blocker: none")
    lines.append("Risk posture: ? unknown")
    lines.append("")
    lines.append("Coherence Matrix")
    lines.append("? Roadmap")
    lines.append("? Decisions")
    lines.append("? Worklog")
    lines.append("? README")
    lines.append("")
    lines.append("Roadmap Snapshot")
    lines.append("🟪 CV1  Cart Flow  🟡 Active")
    lines.append("  🟦 E1  Basic Cart Behavior  🟡 Active")
    lines.append("    🟨 S1  Add item to cart  🟡 Active")
    lines.append("```")
    lines.append("")
    lines.append("Low-friction command examples:")
    lines.append("`uv run python -m memory ext maestro checkpoint quick --journey <journey> --checkpoint plan --cv-code CV1 --cv-title \"Cart Flow\" --epic-code E1 --epic-title \"Basic Cart Behavior\" --story \"S1 Add item to cart\"`")
    lines.append("`uv run python -m memory ext maestro checkpoint quick --journey <journey> --checkpoint validate --story \"S1 Add item to cart\"`")
    lines.append("`uv run python -m memory ext maestro checkpoint quick --journey <journey> --checkpoint coherence --story \"S1 Add item to cart\"`")
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
