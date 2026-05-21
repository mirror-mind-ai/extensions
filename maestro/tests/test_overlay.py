"""Tests for Ariad workspace overlay commands."""

from __future__ import annotations

from pathlib import Path

from src.overlay import cmd_overlay, get_overlay, has_binding, update_overlay
from tests.conftest import seed_journey
from tests.test_adopt import make_ariad_root


def bind_workspace(api, journey_id: str) -> None:
    api.db.execute(
        """
        INSERT INTO _ext_bindings (extension_id, capability_id, target_kind, target_id, created_at)
        VALUES ('maestro', 'ariad_workspace', 'journey', ?, '2026-05-20T00:00:00+00:00')
        """,
        (journey_id,),
    )
    api.db.commit()


def test_overlay_enable_configures_workspace_without_binding(ariad_api, tmp_path: Path, capsys):
    ariad_root = make_ariad_root(tmp_path)
    project = tmp_path / "project"
    project.mkdir()
    seed_journey(ariad_api, "mirror-mind", project)

    rc = cmd_overlay(
        ariad_api,
        ["enable", "--journey", "mirror-mind", "--ariad-root", str(ariad_root)],
    )

    out = capsys.readouterr().out
    overlay = get_overlay(ariad_api, "mirror-mind")
    assert rc == 0
    assert overlay is not None
    assert overlay.ariad_root == str(ariad_root.resolve())
    assert overlay.repo_contract_policy == "do_not_modify"
    assert overlay.doc_update_policy == "project_relevant_only"
    assert overlay.commit_policy == "after_validated_story"
    assert overlay.push_policy == "ask_before_push"
    assert overlay.worklog_policy == "meaningful_milestones"
    assert overlay.documentation_detail_policy == "smallest_coherent_surface"
    assert overlay.branch_policy == "project_default"
    assert overlay.pr_policy == "project_default"
    assert overlay.project_path_snapshot == str(project.resolve())
    assert "Status: configured, not active in context" in out
    assert "bind ariad_workspace --journey mirror-mind" in out


def test_overlay_status_reports_active_binding(ariad_api, tmp_path: Path, capsys):
    ariad_root = make_ariad_root(tmp_path)
    seed_journey(ariad_api, "mirror-mind", tmp_path / "project")
    cmd_overlay(ariad_api, ["enable", "--journey", "mirror-mind", "--ariad-root", str(ariad_root)])
    capsys.readouterr()
    bind_workspace(ariad_api, "mirror-mind")

    rc = cmd_overlay(ariad_api, ["status", "--journey", "mirror-mind"])

    out = capsys.readouterr().out
    assert rc == 0
    assert "Capability binding: active" in out
    assert "Status: active" in out


def test_overlay_set_changes_contract_properties_immediately(ariad_api, tmp_path: Path):
    ariad_root = make_ariad_root(tmp_path)
    seed_journey(ariad_api, "mirror-mind", tmp_path / "project")
    cmd_overlay(ariad_api, ["enable", "--journey", "mirror-mind", "--ariad-root", str(ariad_root)])

    overlay = update_overlay(
        ariad_api,
        journey_id="mirror-mind",
        repo_contract_policy="ask_before_change",
        checkpoint_policy="compressed_for_trivial",
        validation_policy="when_user_visible",
        commit_policy="after_any_codebase_change",
        push_policy="epic_boundary",
        worklog_policy="every_story",
        documentation_detail_policy="detailed",
        branch_policy="dedicated_branch_per_story",
        pr_policy="pr_per_story",
    )

    assert overlay.repo_contract_policy == "ask_before_change"
    assert overlay.checkpoint_policy == "compressed_for_trivial"
    assert overlay.validation_policy == "when_user_visible"
    assert overlay.commit_policy == "after_any_codebase_change"
    assert overlay.push_policy == "epic_boundary"
    assert overlay.worklog_policy == "every_story"
    assert overlay.documentation_detail_policy == "detailed"
    assert overlay.branch_policy == "dedicated_branch_per_story"
    assert overlay.pr_policy == "pr_per_story"


def test_overlay_disable_removes_configuration(ariad_api, tmp_path: Path, capsys):
    ariad_root = make_ariad_root(tmp_path)
    seed_journey(ariad_api, "mirror-mind", tmp_path / "project")
    cmd_overlay(ariad_api, ["enable", "--journey", "mirror-mind", "--ariad-root", str(ariad_root)])
    capsys.readouterr()

    rc = cmd_overlay(ariad_api, ["disable", "--journey", "mirror-mind"])

    out = capsys.readouterr().out
    assert rc == 0
    assert "disabled Ariad workspace overlay" in out
    assert get_overlay(ariad_api, "mirror-mind") is None


def test_overlay_does_not_write_project_files(ariad_api, tmp_path: Path):
    ariad_root = make_ariad_root(tmp_path)
    project = tmp_path / "project"
    project.mkdir()
    seed_journey(ariad_api, "mirror-mind", project)

    cmd_overlay(ariad_api, ["enable", "--journey", "mirror-mind", "--ariad-root", str(ariad_root)])

    assert list(project.iterdir()) == []


def test_has_binding_detects_journey_binding(ariad_api):
    bind_workspace(ariad_api, "mirror-mind")

    assert has_binding(ariad_api, capability_id="ariad_workspace", journey_id="mirror-mind") is True
    assert has_binding(ariad_api, capability_id="ariad_workspace", journey_id="other") is False
