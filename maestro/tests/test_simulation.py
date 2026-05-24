"""Tests for the Maestro simulation harness."""

from __future__ import annotations

import pytest

from src.checkpoint import render_checkpoint_view
from src.simulation import (
    SimulationRoadmap,
    SimulationStory,
    cmd_simulate,
    render_simulation_frames,
    render_simulation_transcript,
    render_traversal_report,
    sandbox_pet_store_roadmap,
    simulate_roadmap_run,
    simulate_story_run,
)


def test_sandbox_pet_store_roadmap_is_synthetic_and_public_safe():
    roadmap = sandbox_pet_store_roadmap()

    assert roadmap.cv_code == "CV1"
    assert roadmap.cv_title == "Sandbox Pet Store"
    assert roadmap.epic_title == "Cart Flow"
    assert [story.code for story in roadmap.stories] == ["S1", "S2", "S3", "S4", "S5"]
    assert [story.title for story in roadmap.stories] == [
        "Add item to cart",
        "Update quantity",
        "Remove item from cart",
        "Enter shipping address",
        "Confirm payment",
    ]


def test_simulation_roadmap_requires_at_least_one_story():
    with pytest.raises(ValueError, match="at least one story"):
        SimulationRoadmap("CV1", "Empty", "E1", "Empty Epic", stories=())


def test_simulate_story_run_generates_full_checkpoint_sequence():
    frames = simulate_story_run(sandbox_pet_store_roadmap(), story_index=0)

    assert [frame.checkpoint for frame in frames] == [
        "plan",
        "implement",
        "validate",
        "coherence",
        "commit",
    ]
    assert all(frame.story.code == "S1" for frame in frames)


def test_simulated_frames_render_real_checkpoint_views():
    frames = simulate_story_run(sandbox_pet_store_roadmap(), story_index=0)

    rendered = [render_checkpoint_view(frame.view) for frame in frames]

    assert "Ariad: ◉ Plan | ○ Implement | ○ Validate | ○ Review | ○ Coherence | ○ Commit" in rendered[0]
    assert "Ariad: ✓ Plan | ◉ Implement | ○ Validate | ○ Review | ○ Coherence | ○ Commit" in rendered[1]
    assert "Ariad: ✓ Plan | ✓ Implement | ◉ Validate | ○ Review | ○ Coherence | ○ Commit" in rendered[2]
    assert "Ariad: ✓ Plan | ✓ Implement | ✓ Validate | ✓ Review | ◉ Coherence | ○ Commit" in rendered[3]
    assert "Ariad: ✓ Plan | ✓ Implement | ✓ Validate | ✓ Review | ✓ Coherence | ◉ Commit" in rendered[4]


def test_validate_checkpoint_includes_validation_panel():
    validate_frame = simulate_story_run(sandbox_pet_store_roadmap(), story_index=0)[2]

    rendered = render_checkpoint_view(validate_frame.view)

    assert "Validation Panel" in rendered
    assert "Automated checks: ✅ passed - synthetic tests passed" in rendered
    assert "Manual validation: ✅ passed - simulated Navigator acceptance" in rendered
    assert "Risk posture: ✅ passed - no project files mutated" in rendered


def test_coherence_checkpoint_includes_coherence_matrix():
    coherence_frame = simulate_story_run(sandbox_pet_store_roadmap(), story_index=0)[3]

    rendered = render_checkpoint_view(coherence_frame.view)

    assert "Coherence Matrix" in rendered
    assert "✓ Roadmap - synthetic roadmap state supplied explicitly" in rendered
    assert "- Worklog - simulation does not mutate docs" in rendered
    assert "✓ Project files - simulation is read-only" in rendered


def test_commit_checkpoint_includes_roadmap_snapshot_with_completed_story_and_next_story():
    commit_frame = simulate_story_run(sandbox_pet_store_roadmap(), story_index=0)[4]

    rendered = render_checkpoint_view(commit_frame.view)

    assert "Roadmap Snapshot" in rendered
    assert "🟪 CV1  Sandbox Pet Store  🟡 Active" in rendered
    assert "🟦 E1  Cart Flow  Stories: 1/5" in rendered
    assert "🟨 S1  Add item to cart  ✅ Done" in rendered
    assert "🟨 S2  Update quantity  👉 Next" in rendered
    assert "Recommended next" in rendered
    assert "Move to S2 Update quantity." in rendered


def test_flow_board_moves_current_story_between_lanes():
    implement_frame = simulate_story_run(sandbox_pet_store_roadmap(), story_index=1)[1]
    validate_frame = simulate_story_run(sandbox_pet_store_roadmap(), story_index=1)[2]
    commit_frame = simulate_story_run(sandbox_pet_store_roadmap(), story_index=1)[4]

    implement_rendered = render_checkpoint_view(implement_frame.view)
    validate_rendered = render_checkpoint_view(validate_frame.view)
    commit_rendered = render_checkpoint_view(commit_frame.view)

    assert "Flow Board" in implement_rendered
    assert "🟨[S2] Update quanti…" in implement_rendered
    assert "🟨[S2] Update quanti…" in validate_rendered
    assert "🟨[S2] Update quanti…" in commit_rendered
    assert "🟨[S1] Add item to c…" in commit_rendered


def test_simulate_roadmap_run_generates_frames_for_every_story():
    roadmap = sandbox_pet_store_roadmap()

    frames = simulate_roadmap_run(roadmap)

    assert len(frames) == len(roadmap.stories) * 5
    assert frames[0].story.code == "S1"
    assert frames[-1].story.code == "S5"
    assert frames[-1].checkpoint == "commit"
    assert frames[-1].view.recommended_next == "Simulation roadmap complete."


def test_simulate_story_run_rejects_out_of_range_index():
    roadmap = SimulationRoadmap(
        "CV1",
        "Tiny Simulation",
        "E1",
        "Tiny Epic",
        stories=(SimulationStory("S1", "Only story"),),
    )

    with pytest.raises(IndexError, match="out of range"):
        simulate_story_run(roadmap, story_index=1)


def test_render_simulation_frames_adds_story_and_checkpoint_boundaries():
    frames = simulate_story_run(sandbox_pet_store_roadmap(), story_index=0)

    rendered = render_simulation_frames(frames)

    assert rendered.startswith("Maestro simulation")
    assert "Simulation frame: S1 Add item to cart / plan" in rendered
    assert "Simulation frame: S1 Add item to cart / commit" in rendered
    assert "Maestro checkpoint" in rendered
    assert "---" in rendered


def test_cmd_simulate_renders_single_story_by_default(ariad_api, capsys):
    rc = cmd_simulate(ariad_api, [])

    out = capsys.readouterr().out
    assert rc == 0
    assert "Maestro simulation" in out
    assert "Simulation frame: S1 Add item to cart / plan" in out
    assert "Simulation frame: S1 Add item to cart / commit" in out
    assert "Simulation frame: S2 Update quantity / plan" not in out


def test_cmd_simulate_can_render_all_stories(ariad_api, capsys):
    rc = cmd_simulate(ariad_api, ["--all"])

    out = capsys.readouterr().out
    assert rc == 0
    assert "Simulation frame: S1 Add item to cart / plan" in out
    assert "Simulation frame: S5 Confirm payment / commit" in out
    assert "Simulation roadmap complete." in out


def test_render_simulation_transcript_wraps_checkpoints_in_driver_navigator_conversation():
    frames = simulate_story_run(sandbox_pet_store_roadmap(), story_index=0)

    rendered = render_simulation_transcript(frames)

    assert rendered.startswith("Maestro simulation transcript")
    assert "Driver:\nI loaded the synthetic roadmap. The active story is S1 Add item to cart." in rendered
    assert "Navigator:\nApproved. Keep the scope narrow" in rendered
    assert "Maestro:\nMaestro checkpoint" in rendered
    assert "Driver:\nS1 Add item to cart is ready to close in the synthetic traversal." in rendered


def test_render_traversal_report_summarizes_full_project_traversal():
    roadmap = sandbox_pet_store_roadmap()
    frames = simulate_roadmap_run(roadmap)

    rendered = render_traversal_report(roadmap, frames)

    assert "Traversal Report" in rendered
    assert "Project: Sandbox Pet Store" in rendered
    assert "Stories traversed: 5/5" in rendered
    assert "✅ S1 Add item to cart — Done" in rendered
    assert "✅ S5 Confirm payment — Done" in rendered
    assert "✅ Plan: 5" in rendered
    assert "✅ Commit: 5" in rendered
    assert "S1 → S2 → S3 → S4 → S5" in rendered
    assert "CV1 Sandbox Pet Store complete." in rendered
    assert "Did the checkpoint views interrupt too much?" in rendered


def test_render_traversal_report_marks_partial_story_run():
    roadmap = sandbox_pet_store_roadmap()
    frames = simulate_story_run(roadmap, story_index=0)

    rendered = render_traversal_report(roadmap, frames)

    assert "Stories traversed: 1/5" in rendered
    assert "✅ S1 Add item to cart — Done" in rendered
    assert "⚪ S2 Update quantity — Not traversed" in rendered
    assert "CV1 Sandbox Pet Store partially traversed." in rendered


def test_cmd_simulate_can_render_transcript_and_report(ariad_api, capsys):
    rc = cmd_simulate(ariad_api, ["--all", "--transcript", "--report"])

    out = capsys.readouterr().out
    assert rc == 0
    assert "Maestro simulation transcript" in out
    assert "Driver:" in out
    assert "Navigator:" in out
    assert "Traversal Report" in out
    assert "Stories traversed: 5/5" in out


def test_cmd_simulate_rejects_out_of_range_story_index(ariad_api):
    with pytest.raises(SystemExit):
        cmd_simulate(ariad_api, ["--story-index", "99"])
