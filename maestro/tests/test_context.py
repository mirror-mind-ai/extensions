"""Tests for Maestro Mirror context providers."""

from __future__ import annotations

from pathlib import Path

from memory.extensions.api import ContextRequest
from src.context import provide_ariad_workspace
from src.overlay import cmd_overlay, update_overlay
from tests.conftest import seed_journey
from tests.test_adopt import make_ariad_root


def test_ariad_workspace_context_returns_none_without_overlay(ariad_api):
    ctx = ContextRequest(
        persona_id="engineer",
        journey_id="mirror-mind",
        user="test",
        query=None,
        binding_kind="journey",
        binding_target="mirror-mind",
    )

    assert provide_ariad_workspace(ariad_api, ctx) is None


def test_ariad_workspace_context_renders_overlay_contract(ariad_api, tmp_path: Path):
    ariad_root = make_ariad_root(tmp_path)
    seed_journey(ariad_api, "mirror-mind", tmp_path / "project")
    cmd_overlay(ariad_api, ["enable", "--journey", "mirror-mind", "--ariad-root", str(ariad_root)])
    ctx = ContextRequest(
        persona_id="engineer",
        journey_id="mirror-mind",
        user="test",
        query=None,
        binding_kind="journey",
        binding_target="mirror-mind",
    )

    text = provide_ariad_workspace(ariad_api, ctx)

    assert text is not None
    assert "Ariad workspace overlay is active" in text
    assert "This is not repository adoption" in text
    assert "Repo contract policy: `do_not_modify`" in text
    assert "Commit policy: `after_validated_story`" in text
    assert "Push policy: `ask_before_push`" in text
    assert "commit after a coherent story" in text
    assert "ask before pushing" in text
    assert "do not edit AGENTS.md" in text
    assert "Maestro checkpoint visualization" in text
    assert "command-first rule" in text
    assert "uv run python -m memory ext maestro checkpoint" in text
    assert "Ariad: ✓ Plan | ◉ Implement | ○ Validate | ○ Review | ○ Coherence | ○ Commit" in text
    assert "do not use alternate lifecycle labels" in text
    assert "Read and Orient" in text
    assert "a ribbon alone is not enough" in text
    assert "Plan checkpoint minimum: Bird's-Eye Map plus Ariad Stage Ribbon" in text
    assert "Validate checkpoint minimum: Ariad Stage Ribbon plus Validation Panel" in text
    assert "Coherence checkpoint minimum: Ariad Stage Ribbon plus Coherence Matrix" in text
    assert "Commit/story-close checkpoint minimum: Ariad Stage Ribbon plus Roadmap Snapshot" in text
    assert "Fallback visual templates" in text
    assert "Validation Panel" in text
    assert "Coherence Matrix" in text
    assert "Roadmap Snapshot" in text
    assert "do not invent validation" in text
    assert "Low-friction command examples" in text
    assert "checkpoint quick --journey <journey> --checkpoint validate" in text
    assert str(ariad_root.resolve()) in text


def test_ariad_workspace_context_reflects_policy_changes(ariad_api, tmp_path: Path):
    ariad_root = make_ariad_root(tmp_path)
    seed_journey(ariad_api, "mirror-mind", tmp_path / "project")
    cmd_overlay(ariad_api, ["enable", "--journey", "mirror-mind", "--ariad-root", str(ariad_root)])
    ctx = ContextRequest(
        persona_id="engineer",
        journey_id="mirror-mind",
        user="test",
        query=None,
        binding_kind="journey",
        binding_target="mirror-mind",
    )

    before = provide_ariad_workspace(ariad_api, ctx)
    update_overlay(
        ariad_api,
        journey_id="mirror-mind",
        repo_contract_policy="ask_before_change",
        doc_update_policy="manual_only",
        commit_policy="after_any_codebase_change",
        push_policy="epic_boundary",
    )
    after = provide_ariad_workspace(ariad_api, ctx)

    assert before is not None and "do_not_modify" in before
    assert after is not None
    assert "ask_before_change" in after
    assert "after_any_codebase_change" in after
    assert "epic_boundary" in after
    assert "ask before editing AGENTS.md" in after
    assert "whenever the codebase has a coherent change worth preserving" in after
    assert "defer push until an epic boundary" in after
    assert "do not update project docs unless the Navigator explicitly asks" in after


def test_ariad_workspace_context_requires_journey(ariad_api, tmp_path: Path):
    ariad_root = make_ariad_root(tmp_path)
    seed_journey(ariad_api, "mirror-mind", tmp_path / "project")
    cmd_overlay(ariad_api, ["enable", "--journey", "mirror-mind", "--ariad-root", str(ariad_root)])
    ctx = ContextRequest(
        persona_id="engineer",
        journey_id=None,
        user="test",
        query=None,
        binding_kind="global",
        binding_target=None,
    )

    assert provide_ariad_workspace(ariad_api, ctx) is None
