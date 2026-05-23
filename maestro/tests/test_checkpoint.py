"""Tests for Maestro checkpoint rendering."""

from __future__ import annotations

import pytest

from src.checkpoint import (
    CheckpointView,
    EpicProgress,
    EvidenceItem,
    ReleaseIntent,
    ValidationEvidence,
    WorkMap,
    cmd_checkpoint,
    render_checkpoint_view,
    render_validation_panel,
)


def sample_work_map(progress: EpicProgress | None = None) -> WorkMap:
    return WorkMap(
        cv_code="CV2",
        cv_title="Ariad/Maestro Visualization",
        epic_code="E2",
        epic_title="Checkpoint View MVP",
        story_code="S1",
        story_title="Checkpoint Renderer",
        epic_progress=progress,
    )


def test_render_checkpoint_view_shows_birds_eye_map_with_yellow_story_card():
    view = CheckpointView(checkpoint="plan", work_map=sample_work_map())

    rendered = render_checkpoint_view(view)

    assert "🟪[CV2]  Ariad/Maestro Visualization" in rendered
    assert "  🟦[E2]   Checkpoint View MVP" in rendered
    assert "    🟨[S1]  Checkpoint Renderer" in rendered
    assert "🟩[S1]" not in rendered


def test_render_checkpoint_view_shows_epic_progress_when_present():
    view = CheckpointView(checkpoint="plan", work_map=sample_work_map(EpicProgress(done=2, total=3)))

    rendered = render_checkpoint_view(view)

    assert "Stories: 2/3" in rendered
    assert "67%" in rendered
    assert "█████░░░" in rendered


def test_render_checkpoint_view_marks_current_checkpoint_in_stage_ribbon():
    view = CheckpointView(checkpoint="review", work_map=sample_work_map())

    rendered = render_checkpoint_view(view)

    assert "Ariad: ✓ Plan | ✓ Implement | ✓ Validate | ◉ Review | ○ Coherence | ○ Commit" in rendered


def test_render_checkpoint_view_includes_status_sentence_and_recommended_next():
    view = CheckpointView(
        checkpoint="implement",
        work_map=sample_work_map(),
        status_sentence="S1 is in progress. We are at the implement checkpoint.",
        recommended_next="Run renderer tests and then add the CLI command in CV2.E2.S2.",
    )

    rendered = render_checkpoint_view(view)

    assert "S1 is in progress. We are at the implement checkpoint." in rendered
    assert "Recommended next" in rendered
    assert "Run renderer tests and then add the CLI command in CV2.E2.S2." in rendered


def test_render_checkpoint_view_includes_known_release_intent():
    view = CheckpointView(
        checkpoint="plan",
        work_map=sample_work_map(),
        release_intent=ReleaseIntent(
            kind="known",
            title="v0.9.1 - Welcome Release Awareness",
            scope="CV2.E2.S1",
            state="building",
        ),
    )

    rendered = render_checkpoint_view(view)

    assert "Release Intent" in rendered
    assert "[known] v0.9.1 - Welcome Release Awareness" in rendered
    assert "Scope: CV2.E2.S1" in rendered
    assert "State: building" in rendered


def test_render_checkpoint_view_includes_emergent_release_intent_defaults():
    view = CheckpointView(
        checkpoint="plan",
        work_map=sample_work_map(),
        release_intent=ReleaseIntent(kind="emergent"),
    )

    rendered = render_checkpoint_view(view)

    assert "Release Intent" in rendered
    assert "[emergent] no version selected yet" in rendered


def test_render_checkpoint_view_omits_optional_blocks_when_absent():
    view = CheckpointView(checkpoint="plan", work_map=sample_work_map())

    rendered = render_checkpoint_view(view)

    assert "Release Intent" not in rendered
    assert "Recommended next" not in rendered


def test_epic_progress_rejects_invalid_values():
    with pytest.raises(ValueError, match="total"):
        EpicProgress(done=0, total=0)
    with pytest.raises(ValueError, match="negative"):
        EpicProgress(done=-1, total=3)
    with pytest.raises(ValueError, match="exceed"):
        EpicProgress(done=4, total=3)


def test_cmd_checkpoint_renders_explicit_checkpoint_view(ariad_api, capsys):
    rc = cmd_checkpoint(
        ariad_api,
        [
            "--journey",
            "maestro",
            "--checkpoint",
            "validate",
            "--cv-code",
            "CV2",
            "--cv-title",
            "Ariad/Maestro Visualization",
            "--epic-code",
            "E2",
            "--epic-title",
            "Checkpoint View MVP",
            "--epic-progress",
            "1/3",
            "--story",
            "S2 checkpoint Command",
            "--release-kind",
            "emergent",
            "--status-sentence",
            "S2 implemented and validated. We are at the validation checkpoint.",
            "--recommended-next",
            "Prepare the manual smoke route.",
        ],
    )

    out = capsys.readouterr().out
    assert rc == 0
    assert "Maestro checkpoint" in out
    assert "🟪[CV2]  Ariad/Maestro Visualization" in out
    assert "  🟦[E2]   Checkpoint View MVP  Stories: 1/3" in out
    assert "    🟨[S2]  checkpoint Command" in out
    assert "Ariad: ✓ Plan | ✓ Implement | ◉ Validate | ○ Review | ○ Coherence | ○ Commit" in out
    assert "[emergent] no version selected yet" in out
    assert "Recommended next" in out


def test_evidence_item_exposes_marker_for_each_validation_state():
    assert EvidenceItem(label="Automated checks", state="passed").marker == "✅"
    assert EvidenceItem(label="Manual smoke", state="attention").marker == "⚠"
    assert EvidenceItem(label="Release blocker", state="blocked").marker == "⛔"
    assert EvidenceItem(label="Manual validation", state="not_run").marker == "○"
    assert EvidenceItem(label="Risk posture", state="unknown").marker == "?"


def test_evidence_item_rejects_unknown_state():
    with pytest.raises(ValueError, match="Unknown validation state"):
        EvidenceItem(label="Manual smoke", state="yellow")  # type: ignore[arg-type]


def test_validation_evidence_groups_automated_manual_blocker_and_risk():
    evidence = ValidationEvidence(
        automated=EvidenceItem("Automated checks", "passed", "72 tests passed"),
        manual=EvidenceItem("Manual smoke", "not_run"),
        blocker="v0.9.1 is not published yet",
        risk=EvidenceItem("Risk posture", "attention", "release-state blocker only"),
    )

    assert evidence.automated is not None
    assert evidence.automated.marker == "✅"
    assert evidence.manual is not None
    assert evidence.manual.marker == "○"
    assert evidence.blocker == "v0.9.1 is not published yet"
    assert evidence.risk is not None
    assert evidence.risk.marker == "⚠"


def test_attention_marker_does_not_conflict_with_yellow_story_card():
    assert EvidenceItem(label="Manual smoke", state="attention").marker == "⚠"
    assert "🟨" not in EvidenceItem(label="Manual smoke", state="attention").marker


def test_render_validation_panel_shows_all_evidence_sections():
    evidence = ValidationEvidence(
        automated=EvidenceItem("Automated checks", "passed", "76 tests passed"),
        manual=EvidenceItem("Manual validation", "not_run"),
        blocker="none",
        risk=EvidenceItem("Risk posture", "attention", "manual validation pending"),
    )

    rendered = render_validation_panel(evidence)

    assert "Validation Panel" in rendered
    assert "Automated checks: ✅ passed - 76 tests passed" in rendered
    assert "Manual validation: ○ not run" in rendered
    assert "Blocker: none" in rendered
    assert "Risk posture: ⚠ attention - manual validation pending" in rendered
    assert "🟨" not in rendered


def test_render_validation_panel_uses_unknown_for_missing_evidence():
    rendered = render_validation_panel(ValidationEvidence())

    assert "Automated checks: ? unknown" in rendered
    assert "Manual validation: ? unknown" in rendered
    assert "Blocker: none" in rendered
    assert "Risk posture: ? unknown" in rendered


def test_render_validation_panel_shows_blocker_text():
    rendered = render_validation_panel(ValidationEvidence(blocker="release not published"))

    assert "Blocker: release not published" in rendered


def test_render_checkpoint_view_includes_validation_panel():
    view = CheckpointView(
        checkpoint="validate",
        work_map=sample_work_map(),
        validation_evidence=ValidationEvidence(
            automated=EvidenceItem("Automated checks", "passed", "79 tests passed"),
            manual=EvidenceItem("Manual validation", "attention", "Navigator review pending"),
            blocker="none",
            risk=EvidenceItem("Risk posture", "attention", "manual validation pending"),
        ),
    )

    rendered = render_checkpoint_view(view)

    assert "Validation Panel" in rendered
    assert "Automated checks: ✅ passed - 79 tests passed" in rendered
    assert "Manual validation: ⚠ attention - Navigator review pending" in rendered
    assert "Blocker: none" in rendered
    assert "Risk posture: ⚠ attention - manual validation pending" in rendered


def test_cmd_checkpoint_accepts_validation_evidence(ariad_api, capsys):
    rc = cmd_checkpoint(
        ariad_api,
        [
            "--checkpoint",
            "validate",
            "--story",
            "S3 Validation View Integration",
            "--automated",
            "Automated checks:passed:79 tests passed",
            "--manual",
            "Manual validation:not_run",
            "--blocker",
            "none",
            "--risk",
            "Risk posture:attention:manual validation pending",
        ],
    )

    out = capsys.readouterr().out
    assert rc == 0
    assert "Validation Panel" in out
    assert "Automated checks: ✅ passed - 79 tests passed" in out
    assert "Manual validation: ○ not run" in out
    assert "Blocker: none" in out
    assert "Risk posture: ⚠ attention - manual validation pending" in out


def test_render_checkpoint_view_includes_flow_board():
    from src.flow import FlowBoard, FlowCard

    view = CheckpointView(
        checkpoint="implement",
        work_map=sample_work_map(),
        flow_board=FlowBoard(doing=(FlowCard("S4", "Flow Board Renderer"),), done=(FlowCard("S3", "Validation View Integration"),)),
    )

    rendered = render_checkpoint_view(view)

    assert "Flow Board" in rendered
    assert "🟨[S4] Flow Board Re…" in rendered
    assert "🟨[S3] Validation Vi…" in rendered


def test_cmd_checkpoint_accepts_explicit_flow_cards(ariad_api, capsys):
    rc = cmd_checkpoint(
        ariad_api,
        [
            "--checkpoint",
            "implement",
            "--story",
            "S4 Flow Board Renderer",
            "--doing",
            "S4:Flow Board Renderer",
            "--done",
            "S3:Validation View Integration",
        ],
    )

    out = capsys.readouterr().out
    assert rc == 0
    assert "Flow Board" in out
    assert "🟨[S4] Flow Board Re…" in out
    assert "🟨[S3] Validation Vi…" in out


def test_render_checkpoint_view_includes_coherence_matrix():
    from src.coherence import CoherenceItem, CoherenceMatrix

    view = CheckpointView(
        checkpoint="coherence",
        work_map=sample_work_map(),
        coherence_matrix=CoherenceMatrix(
            items=(
                CoherenceItem("Roadmap", "checked", "CV2.E5.S3 updated"),
                CoherenceItem("Release notes", "not_applicable", "No release boundary"),
            )
        ),
    )

    rendered = render_checkpoint_view(view)

    assert "Coherence Matrix" in rendered
    assert "✓ Roadmap - CV2.E5.S3 updated" in rendered
    assert "- Release notes - No release boundary" in rendered


def test_cmd_checkpoint_accepts_coherence_items(ariad_api, capsys):
    rc = cmd_checkpoint(
        ariad_api,
        [
            "--checkpoint",
            "coherence",
            "--story",
            "S3 Closeout View Integration",
            "--coherence",
            "Roadmap:checked:CV2.E5.S3 updated",
            "--coherence",
            "Release notes:not_applicable:No release boundary",
            "--coherence",
            "Internal links:unknown",
        ],
    )

    out = capsys.readouterr().out
    assert rc == 0
    assert "Coherence Matrix" in out
    assert "✓ Roadmap - CV2.E5.S3 updated" in out
    assert "- Release notes - No release boundary" in out
    assert "? Internal links" in out


def test_cmd_checkpoint_accepts_known_release(ariad_api, capsys):
    rc = cmd_checkpoint(
        ariad_api,
        [
            "--checkpoint",
            "plan",
            "--story",
            "S1 Checkpoint Renderer",
            "--release-kind",
            "known",
            "--release",
            "v0.1.0 - Ariad Visualization",
            "--release-scope",
            "CV2.E2",
            "--release-state",
            "building",
        ],
    )

    out = capsys.readouterr().out
    assert rc == 0
    assert "[known] v0.1.0 - Ariad Visualization" in out
    assert "Scope: CV2.E2" in out
    assert "State: building" in out
