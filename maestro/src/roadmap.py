"""Roadmap snapshot model for Ariad/Maestro visualization."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Literal

RoadmapLevel = Literal["cv", "epic", "story"]
RoadmapStatus = Literal["done", "active", "next", "planned", "radar", "blocked"]

_STATUS_MARKERS: dict[RoadmapStatus, str] = {
    "done": "✅",
    "active": "🟡",
    "next": "👉",
    "planned": "⚪",
    "radar": "🔭",
    "blocked": "⛔",
}
_LEVEL_MARKERS: dict[RoadmapLevel, str] = {
    "cv": "🟪",
    "epic": "🟦",
    "story": "🟨",
}


@dataclass(frozen=True)
class Progress:
    """Trustworthy progress for a roadmap item."""

    done: int
    total: int

    def __post_init__(self) -> None:
        if self.total <= 0:
            raise ValueError("Progress total must be greater than zero")
        if self.done < 0:
            raise ValueError("Progress done count cannot be negative")
        if self.done > self.total:
            raise ValueError("Progress done count cannot exceed total")

    @property
    def percent(self) -> int:
        return round((self.done / self.total) * 100)


@dataclass(frozen=True)
class RoadmapItem:
    """One CV, Epic, or Story in a roadmap snapshot."""

    level: RoadmapLevel
    code: str
    title: str
    status: RoadmapStatus
    progress: Progress | None = None
    children: tuple["RoadmapItem", ...] = ()

    def __post_init__(self) -> None:
        if self.level not in _LEVEL_MARKERS:
            raise ValueError(f"Unknown roadmap level: {self.level}")
        if self.status not in _STATUS_MARKERS:
            raise ValueError(f"Unknown roadmap status: {self.status}")

    @property
    def level_marker(self) -> str:
        return _LEVEL_MARKERS[self.level]

    @property
    def status_marker(self) -> str:
        return _STATUS_MARKERS[self.status]


@dataclass(frozen=True)
class RoadmapSnapshot:
    """Explicit roadmap state shown at story close."""

    items: tuple[RoadmapItem, ...]


def _progress_bar(progress: Progress, *, width: int = 8) -> str:
    filled = round((progress.done / progress.total) * width)
    return "█" * filled + "░" * (width - filled)


def _progress_label(item: RoadmapItem) -> str:
    if item.level == "cv":
        return "Epics"
    if item.level == "epic":
        return "Stories"
    return "Progress"


def _status_label(status: RoadmapStatus) -> str:
    return status.replace("_", " ").title()


def _render_item(item: RoadmapItem, *, depth: int = 0) -> list[str]:
    indent = "  " * depth
    line = f"{indent}{item.level_marker} {item.code}  {item.title}"
    if item.progress is not None:
        line += (
            f"  {_progress_label(item)}: {item.progress.done}/{item.progress.total}"
            f"  {_progress_bar(item.progress)} {item.progress.percent}%"
        )
    line += f"  {item.status_marker} {_status_label(item.status)}"

    lines = [line]
    for child in item.children:
        lines.extend(_render_item(child, depth=depth + 1))
    return lines


def nest_roadmap_items(items: tuple[RoadmapItem, ...]) -> tuple[RoadmapItem, ...]:
    """Nest a flat CV/Epic/Story sequence by nearest preceding parent."""

    roots: list[RoadmapItem] = []
    current_cv_index: int | None = None
    current_epic_index: int | None = None

    for item in items:
        if item.level == "cv":
            roots.append(item)
            current_cv_index = len(roots) - 1
            current_epic_index = None
            continue

        if item.level == "epic" and current_cv_index is not None:
            cv = roots[current_cv_index]
            children = (*cv.children, item)
            roots[current_cv_index] = replace(cv, children=children)
            current_epic_index = len(children) - 1
            continue

        if item.level == "story" and current_cv_index is not None and current_epic_index is not None:
            cv = roots[current_cv_index]
            epic = cv.children[current_epic_index]
            updated_epic = replace(epic, children=(*epic.children, item))
            updated_children = tuple(
                updated_epic if index == current_epic_index else child
                for index, child in enumerate(cv.children)
            )
            roots[current_cv_index] = replace(cv, children=updated_children)
            continue

        if item.level == "story" and current_cv_index is not None:
            cv = roots[current_cv_index]
            roots[current_cv_index] = replace(cv, children=(*cv.children, item))
            continue

        roots.append(item)
        current_cv_index = None
        current_epic_index = None

    return tuple(roots)


def render_roadmap_snapshot(snapshot: RoadmapSnapshot) -> str:
    """Render a hierarchical roadmap snapshot."""

    lines = ["Roadmap Snapshot", ""]
    if not snapshot.items:
        lines.append("? No roadmap items provided")
    else:
        for index, item in enumerate(snapshot.items):
            if index > 0:
                lines.append("")
            lines.extend(_render_item(item))
    return "\n".join(lines) + "\n"
