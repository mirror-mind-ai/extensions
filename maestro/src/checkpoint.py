"""Checkpoint view rendering for Ariad/Maestro visualization."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

CheckpointName = Literal["plan", "implement", "validate", "review", "coherence", "commit"]
ReleaseIntentKind = Literal["known", "emergent"]

_CHECKPOINTS: tuple[CheckpointName, ...] = (
    "plan",
    "implement",
    "validate",
    "review",
    "coherence",
    "commit",
)
_CHECKPOINT_LABELS: dict[CheckpointName, str] = {
    "plan": "Plan",
    "implement": "Implement",
    "validate": "Validate",
    "review": "Review",
    "coherence": "Coherence",
    "commit": "Commit",
}


@dataclass(frozen=True)
class EpicProgress:
    """Progress metadata for the active epic."""

    done: int
    total: int

    def __post_init__(self) -> None:
        if self.total <= 0:
            raise ValueError("Epic progress total must be greater than zero")
        if self.done < 0:
            raise ValueError("Epic progress done count cannot be negative")
        if self.done > self.total:
            raise ValueError("Epic progress done count cannot exceed total")


@dataclass(frozen=True)
class WorkMap:
    """Roadmap location for the active work."""

    cv_code: str
    cv_title: str
    epic_code: str
    epic_title: str
    story_code: str
    story_title: str
    epic_progress: EpicProgress | None = None


@dataclass(frozen=True)
class ReleaseIntent:
    """Release context shown when it matters for the checkpoint."""

    kind: ReleaseIntentKind
    title: str | None = None
    scope: str | None = None
    state: str | None = None
    note: str | None = None


@dataclass(frozen=True)
class CheckpointView:
    """Data needed to render a compact checkpoint view."""

    checkpoint: CheckpointName
    work_map: WorkMap
    status_sentence: str | None = None
    release_intent: ReleaseIntent | None = None
    recommended_next: str | None = None


def _progress_bar(progress: EpicProgress, *, width: int = 8) -> str:
    filled = round((progress.done / progress.total) * width)
    return "█" * filled + "░" * (width - filled)


def _render_work_map(work_map: WorkMap) -> list[str]:
    epic_line = f"  🟦[{work_map.epic_code}]   {work_map.epic_title}"
    if work_map.epic_progress is not None:
        progress = work_map.epic_progress
        percent = round((progress.done / progress.total) * 100)
        epic_line += f"  Stories: {progress.done}/{progress.total}  {_progress_bar(progress)} {percent}%"

    return [
        f"🟪[{work_map.cv_code}]  {work_map.cv_title}",
        epic_line,
        f"    🟨[{work_map.story_code}]  {work_map.story_title}",
    ]


def _render_stage_ribbon(current: CheckpointName) -> str:
    current_index = _CHECKPOINTS.index(current)
    parts: list[str] = []
    for index, checkpoint in enumerate(_CHECKPOINTS):
        if index < current_index:
            marker = "✓"
        elif index == current_index:
            marker = "◉"
        else:
            marker = "○"
        parts.append(f"{marker} {_CHECKPOINT_LABELS[checkpoint]}")
    return "Ariad: " + " | ".join(parts)


def _render_release_intent(release: ReleaseIntent) -> list[str]:
    lines = ["Release Intent"]
    if release.kind == "known":
        title = release.title or "unnamed release"
        lines.append(f"[known] {title}")
    else:
        title = release.title or "no version selected yet"
        lines.append(f"[emergent] {title}")

    if release.scope:
        lines.append(f"Scope: {release.scope}")
    if release.state:
        lines.append(f"State: {release.state}")
    if release.note:
        lines.append(release.note)
    return lines


def render_checkpoint_view(view: CheckpointView) -> str:
    """Render a textual checkpoint view."""

    lines: list[str] = ["Maestro checkpoint", ""]
    lines.extend(_render_work_map(view.work_map))
    lines.append("")
    lines.append(_render_stage_ribbon(view.checkpoint))

    if view.status_sentence:
        lines.append("")
        lines.append(view.status_sentence)

    if view.release_intent:
        lines.append("")
        lines.extend(_render_release_intent(view.release_intent))

    if view.recommended_next:
        lines.append("")
        lines.append("Recommended next")
        lines.append(view.recommended_next)

    return "\n".join(lines) + "\n"
