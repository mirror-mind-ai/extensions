"""Synthetic Maestro simulation harness.

The simulation harness builds explicit checkpoint views for synthetic roadmaps.
It does not read project files, mutate repositories, or infer state from Markdown.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from typing import Literal

from src.checkpoint import (
    CheckpointName,
    CheckpointView,
    EpicProgress,
    EvidenceItem,
    ValidationEvidence,
    WorkMap,
    render_checkpoint_view,
)
from src.coherence import CoherenceItem, CoherenceMatrix
from src.flow import FlowBoard, FlowCard
from src.roadmap import Progress, RoadmapItem, RoadmapSnapshot

_SIMULATION_CHECKPOINTS: tuple[CheckpointName, ...] = (
    "plan",
    "implement",
    "validate",
    "coherence",
    "commit",
)

SimulationStoryStatus = Literal["done", "active", "next", "planned"]
TranscriptRole = Literal["Driver", "Navigator", "Maestro"]


@dataclass(frozen=True)
class SimulationStory:
    """One synthetic story in a simulated roadmap."""

    code: str
    title: str


@dataclass(frozen=True)
class SimulationRoadmap:
    """Synthetic one-CV, one-epic roadmap used to exercise Maestro views."""

    cv_code: str
    cv_title: str
    epic_code: str
    epic_title: str
    stories: tuple[SimulationStory, ...]

    def __post_init__(self) -> None:
        if not self.stories:
            raise ValueError("Simulation roadmap must include at least one story")


@dataclass(frozen=True)
class SimulationCheckpointFrame:
    """A generated checkpoint frame for one simulated story."""

    story: SimulationStory
    story_index: int
    checkpoint: CheckpointName
    view: CheckpointView


@dataclass(frozen=True)
class SimulationTranscriptTurn:
    """One Driver/Navigator/Maestro turn in a synthetic simulation transcript."""

    role: TranscriptRole
    content: str


def sandbox_pet_store_roadmap() -> SimulationRoadmap:
    """Return the canonical synthetic roadmap for Maestro simulation tests."""

    return SimulationRoadmap(
        cv_code="CV1",
        cv_title="Sandbox Pet Store",
        epic_code="E1",
        epic_title="Cart Flow",
        stories=(
            SimulationStory("S1", "Add item to cart"),
            SimulationStory("S2", "Update quantity"),
            SimulationStory("S3", "Remove item from cart"),
            SimulationStory("S4", "Enter shipping address"),
            SimulationStory("S5", "Confirm payment"),
        ),
    )


def simulate_story_run(
    roadmap: SimulationRoadmap,
    *,
    story_index: int = 0,
) -> tuple[SimulationCheckpointFrame, ...]:
    """Generate checkpoint views for one story in a synthetic roadmap."""

    _validate_story_index(roadmap, story_index)
    story = roadmap.stories[story_index]
    frames: list[SimulationCheckpointFrame] = []
    for checkpoint in _SIMULATION_CHECKPOINTS:
        frames.append(
            SimulationCheckpointFrame(
                story=story,
                story_index=story_index,
                checkpoint=checkpoint,
                view=_build_view(roadmap, story_index=story_index, checkpoint=checkpoint),
            )
        )
    return tuple(frames)


def simulate_roadmap_run(roadmap: SimulationRoadmap) -> tuple[SimulationCheckpointFrame, ...]:
    """Generate checkpoint views for every story in a synthetic roadmap."""

    frames: list[SimulationCheckpointFrame] = []
    for story_index in range(len(roadmap.stories)):
        frames.extend(simulate_story_run(roadmap, story_index=story_index))
    return tuple(frames)


def render_simulation_frames(frames: tuple[SimulationCheckpointFrame, ...]) -> str:
    """Render generated simulation frames with explicit story/checkpoint boundaries."""

    lines = ["Maestro simulation", ""]
    if not frames:
        lines.append("? No simulation frames generated")
        return "\n".join(lines) + "\n"

    for index, frame in enumerate(frames):
        if index > 0:
            lines.append("---")
            lines.append("")
        lines.append(f"Simulation frame: {frame.story.code} {frame.story.title} / {frame.checkpoint}")
        lines.append("")
        lines.extend(render_checkpoint_view(frame.view).rstrip().splitlines())
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def render_simulation_transcript(frames: tuple[SimulationCheckpointFrame, ...]) -> str:
    """Render a synthetic Driver/Navigator transcript with Maestro checkpoint views."""

    lines = ["Maestro simulation transcript", ""]
    if not frames:
        lines.append("? No simulation frames generated")
        return "\n".join(lines) + "\n"

    for index, frame in enumerate(frames):
        if index > 0:
            lines.append("---")
            lines.append("")
        for turn in _transcript_turns_for_frame(frame):
            lines.append(f"{turn.role}:")
            lines.extend(turn.content.splitlines())
            lines.append("")
        lines.append("Maestro:")
        lines.extend(render_checkpoint_view(frame.view).rstrip().splitlines())
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def render_traversal_report(
    roadmap: SimulationRoadmap,
    frames: tuple[SimulationCheckpointFrame, ...],
) -> str:
    """Render a final traversal report for a synthetic simulation run."""

    commit_frames = tuple(frame for frame in frames if frame.checkpoint == "commit")
    committed_codes = {frame.story.code for frame in commit_frames}
    coverage = {checkpoint: 0 for checkpoint in _SIMULATION_CHECKPOINTS}
    for frame in frames:
        coverage[frame.checkpoint] += 1

    lines = ["Traversal Report", "", f"Project: {roadmap.cv_title}"]
    lines.append(f"Scope: {roadmap.cv_code} / {roadmap.epic_code} / {len(roadmap.stories)} stories")
    lines.append(f"Stories traversed: {len(committed_codes)}/{len(roadmap.stories)}")
    lines.append("")
    lines.append("Story outcomes:")
    for story in roadmap.stories:
        marker = "✅" if story.code in committed_codes else "⚪"
        state = "Done" if story.code in committed_codes else "Not traversed"
        lines.append(f"{marker} {story.code} {story.title} — {state}")

    lines.append("")
    lines.append("Checkpoint coverage:")
    for checkpoint in _SIMULATION_CHECKPOINTS:
        lines.append(f"✅ {checkpoint.title()}: {coverage[checkpoint]}")

    lines.append("")
    lines.append("Evidence:")
    lines.append("✅ Automated checks: synthetic checks passed for traversed stories")
    lines.append("✅ Manual validation: simulated Navigator acceptance for traversed stories")
    lines.append("✓ Coherence reviewed for traversed stories")
    lines.append("✓ No real project files mutated")

    lines.append("")
    lines.append("Flow:")
    if commit_frames:
        lines.append(" → ".join(frame.story.code for frame in commit_frames))
    else:
        lines.append("? No committed stories")

    lines.append("")
    lines.append("Final state:")
    if len(committed_codes) == len(roadmap.stories):
        lines.append(f"{roadmap.cv_code} {roadmap.cv_title} complete.")
    else:
        lines.append(f"{roadmap.cv_code} {roadmap.cv_title} partially traversed.")

    lines.append("")
    lines.append("Open questions:")
    lines.append("- Did the checkpoint views interrupt too much?")
    lines.append("- Was the Roadmap Snapshot readable across multiple stories?")
    lines.append("- Should Driver/Navigator transcript be more compact?")
    return "\n".join(lines) + "\n"


def cmd_simulate(api, argv: list[str]) -> int:
    """Render a synthetic Maestro simulation run."""

    parser = argparse.ArgumentParser(description="Render a synthetic Maestro checkpoint simulation")
    parser.add_argument(
        "--fixture",
        choices=("sandbox-pet-store",),
        default="sandbox-pet-store",
        help="Synthetic fixture to simulate.",
    )
    parser.add_argument(
        "--story-index",
        type=int,
        default=0,
        help="Zero-based story index to simulate when --all is not provided.",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Simulate every story in the synthetic roadmap.",
    )
    parser.add_argument(
        "--transcript",
        action="store_true",
        help="Render a synthetic Driver/Navigator transcript around Maestro checkpoint views.",
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Append a final traversal report.",
    )
    args = parser.parse_args(argv)

    roadmap = sandbox_pet_store_roadmap()
    try:
        frames = simulate_roadmap_run(roadmap) if args.all else simulate_story_run(roadmap, story_index=args.story_index)
    except IndexError as exc:
        parser.error(str(exc))

    output = render_simulation_transcript(frames) if args.transcript else render_simulation_frames(frames)
    if args.report:
        output = output.rstrip() + "\n\n" + render_traversal_report(roadmap, frames)
    sys.stdout.write(output)
    return 0


def _transcript_turns_for_frame(frame: SimulationCheckpointFrame) -> tuple[SimulationTranscriptTurn, ...]:
    story_label = f"{frame.story.code} {frame.story.title}"
    if frame.checkpoint == "plan":
        return (
            SimulationTranscriptTurn("Driver", f"I loaded the synthetic roadmap. The active story is {story_label}."),
            SimulationTranscriptTurn("Navigator", "Approved. Keep the scope narrow and make the next checkpoint visible."),
        )
    if frame.checkpoint == "implement":
        return (
            SimulationTranscriptTurn("Driver", f"I am simulating implementation work for {story_label}."),
            SimulationTranscriptTurn("Navigator", "Proceed to validation when the synthetic implementation evidence is ready."),
        )
    if frame.checkpoint == "validate":
        return (
            SimulationTranscriptTurn("Driver", f"Synthetic implementation evidence for {story_label} is ready to validate."),
            SimulationTranscriptTurn("Navigator", "Validate with automated and manual evidence, then surface residual risk."),
        )
    if frame.checkpoint == "coherence":
        return (
            SimulationTranscriptTurn("Driver", f"{story_label} has validation evidence. I am checking coherence surfaces."),
            SimulationTranscriptTurn("Navigator", "Confirm what changed, what did not change, and whether project memory stays coherent."),
        )
    return (
        SimulationTranscriptTurn("Driver", f"{story_label} is ready to close in the synthetic traversal."),
        SimulationTranscriptTurn("Navigator", "Record the transition and show the next movement before continuing."),
    )


def _validate_story_index(roadmap: SimulationRoadmap, story_index: int) -> None:
    if story_index < 0 or story_index >= len(roadmap.stories):
        raise IndexError("Simulation story index is out of range")


def _build_view(
    roadmap: SimulationRoadmap,
    *,
    story_index: int,
    checkpoint: CheckpointName,
) -> CheckpointView:
    story = roadmap.stories[story_index]
    done_count = story_index + 1 if checkpoint == "commit" else story_index
    work_map = WorkMap(
        cv_code=roadmap.cv_code,
        cv_title=roadmap.cv_title,
        epic_code=roadmap.epic_code,
        epic_title=roadmap.epic_title,
        story_code=story.code,
        story_title=story.title,
        epic_progress=EpicProgress(done=done_count, total=len(roadmap.stories)),
    )

    return CheckpointView(
        checkpoint=checkpoint,
        work_map=work_map,
        status_sentence=_status_sentence(story, checkpoint),
        validation_evidence=_validation_evidence(checkpoint),
        flow_board=_flow_board(roadmap, story_index=story_index, checkpoint=checkpoint),
        coherence_matrix=_coherence_matrix(checkpoint),
        roadmap_snapshot=_roadmap_snapshot(roadmap, story_index=story_index, checkpoint=checkpoint),
        recommended_next=_recommended_next(roadmap, story_index=story_index, checkpoint=checkpoint),
    )


def _status_sentence(story: SimulationStory, checkpoint: CheckpointName) -> str:
    return f"{story.code} {story.title} is at the {checkpoint} checkpoint in the Maestro simulation."


def _validation_evidence(checkpoint: CheckpointName) -> ValidationEvidence | None:
    if checkpoint not in {"validate", "commit"}:
        return None
    return ValidationEvidence(
        automated=EvidenceItem("Automated checks", "passed", "synthetic tests passed"),
        manual=EvidenceItem("Manual validation", "passed", "simulated Navigator acceptance"),
        blocker="none",
        risk=EvidenceItem("Risk posture", "passed", "no project files mutated"),
    )


def _coherence_matrix(checkpoint: CheckpointName) -> CoherenceMatrix | None:
    if checkpoint not in {"coherence", "commit"}:
        return None
    return CoherenceMatrix(
        items=(
            CoherenceItem("Roadmap", "checked", "synthetic roadmap state supplied explicitly"),
            CoherenceItem("Worklog", "not_applicable", "simulation does not mutate docs"),
            CoherenceItem("Decisions", "not_applicable", "no method decision created"),
            CoherenceItem("Project files", "checked", "simulation is read-only"),
        )
    )


def _flow_board(
    roadmap: SimulationRoadmap,
    *,
    story_index: int,
    checkpoint: CheckpointName,
) -> FlowBoard | None:
    if checkpoint not in {"implement", "validate", "commit"}:
        return None

    done_stories = roadmap.stories[:story_index]
    current_story = roadmap.stories[story_index]
    next_story = roadmap.stories[story_index + 1] if story_index + 1 < len(roadmap.stories) else None
    later_stories = roadmap.stories[story_index + 2 :]

    done_cards = tuple(_flow_card(story) for story in done_stories)
    if checkpoint == "commit":
        done_cards = (*done_cards, _flow_card(current_story))

    return FlowBoard(
        backlog=tuple(_flow_card(story) for story in later_stories),
        ready=(_flow_card(next_story),) if next_story is not None and checkpoint != "commit" else (),
        doing=(_flow_card(current_story),) if checkpoint == "implement" else (),
        validate=(_flow_card(current_story),) if checkpoint == "validate" else (),
        done=done_cards,
    )


def _flow_card(story: SimulationStory) -> FlowCard:
    return FlowCard(code=story.code, title=story.title)


def _roadmap_snapshot(
    roadmap: SimulationRoadmap,
    *,
    story_index: int,
    checkpoint: CheckpointName,
) -> RoadmapSnapshot:
    done_count = story_index + 1 if checkpoint == "commit" else story_index
    stories = tuple(
        RoadmapItem(
            level="story",
            code=story.code,
            title=story.title,
            status=_story_status(index, story_index=story_index, checkpoint=checkpoint),
        )
        for index, story in enumerate(roadmap.stories)
    )
    epic = RoadmapItem(
        level="epic",
        code=roadmap.epic_code,
        title=roadmap.epic_title,
        status="done" if done_count == len(roadmap.stories) else "active",
        progress=Progress(done=done_count, total=len(roadmap.stories)),
        children=stories,
    )
    cv = RoadmapItem(
        level="cv",
        code=roadmap.cv_code,
        title=roadmap.cv_title,
        status="done" if done_count == len(roadmap.stories) else "active",
        children=(epic,),
    )
    return RoadmapSnapshot(items=(cv,))


def _story_status(
    index: int,
    *,
    story_index: int,
    checkpoint: CheckpointName,
) -> SimulationStoryStatus:
    if index < story_index:
        return "done"
    if index == story_index:
        return "done" if checkpoint == "commit" else "active"
    if index == story_index + 1:
        return "next"
    return "planned"


def _recommended_next(
    roadmap: SimulationRoadmap,
    *,
    story_index: int,
    checkpoint: CheckpointName,
) -> str:
    story = roadmap.stories[story_index]
    if checkpoint == "plan":
        return f"Simulate implementation evidence for {story.code}."
    if checkpoint == "implement":
        return f"Simulate validation evidence for {story.code}."
    if checkpoint == "validate":
        return f"Run coherence review for {story.code}."
    if checkpoint == "coherence":
        return f"Render commit checkpoint for {story.code}."
    next_story = roadmap.stories[story_index + 1] if story_index + 1 < len(roadmap.stories) else None
    if next_story is None:
        return "Simulation roadmap complete."
    return f"Move to {next_story.code} {next_story.title}."
