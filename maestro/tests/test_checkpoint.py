"""Tests for Maestro checkpoint rendering."""

from __future__ import annotations

import pytest

from src.checkpoint import CheckpointView, EpicProgress, ReleaseIntent, WorkMap, render_checkpoint_view


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
