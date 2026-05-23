"""Flow board rendering for Ariad/Maestro visualization."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

FlowLane = Literal["backlog", "ready", "doing", "validate", "done"]

_LANE_ORDER: tuple[FlowLane, ...] = ("backlog", "ready", "doing", "validate", "done")
_LANE_LABELS: dict[FlowLane, str] = {
    "backlog": "Backlog",
    "ready": "Ready",
    "doing": "Doing",
    "validate": "Validate",
    "done": "Done",
}


@dataclass(frozen=True)
class FlowCard:
    """One card rendered inside a flow lane."""

    code: str
    title: str

    def render(self) -> str:
        return f"🟨[{self.code}] {self.title}"


@dataclass(frozen=True)
class FlowBoard:
    """Explicit flow-board card state."""

    backlog: tuple[FlowCard, ...] = ()
    ready: tuple[FlowCard, ...] = ()
    doing: tuple[FlowCard, ...] = ()
    validate: tuple[FlowCard, ...] = ()
    done: tuple[FlowCard, ...] = ()

    def lane(self, name: FlowLane) -> tuple[FlowCard, ...]:
        return getattr(self, name)


def _cell_widths(board: FlowBoard) -> dict[FlowLane, int]:
    widths: dict[FlowLane, int] = {}
    for lane in _LANE_ORDER:
        values = [_LANE_LABELS[lane], *(card.render() for card in board.lane(lane))]
        widths[lane] = max(len(value) for value in values)
    return widths


def _render_separator(widths: dict[FlowLane, int]) -> str:
    cells = ["-" * (widths[lane] + 2) for lane in _LANE_ORDER]
    return "+" + "+".join(cells) + "+"


def _render_row(values: dict[FlowLane, str], widths: dict[FlowLane, int]) -> str:
    cells = [f" {values.get(lane, ''):<{widths[lane]}} " for lane in _LANE_ORDER]
    return "|" + "|".join(cells) + "|"


def render_flow_board(board: FlowBoard) -> str:
    """Render a horizontal flow board from explicit card state."""

    widths = _cell_widths(board)
    lines = ["Flow Board", "", _render_separator(widths)]
    lines.append(_render_row({lane: _LANE_LABELS[lane] for lane in _LANE_ORDER}, widths))
    lines.append(_render_separator(widths))

    max_rows = max((len(board.lane(lane)) for lane in _LANE_ORDER), default=0)
    if max_rows == 0:
        lines.append(_render_row({}, widths))
    else:
        for index in range(max_rows):
            row: dict[FlowLane, str] = {}
            for lane in _LANE_ORDER:
                cards = board.lane(lane)
                if index < len(cards):
                    row[lane] = cards[index].render()
            lines.append(_render_row(row, widths))

    lines.append(_render_separator(widths))
    return "\n".join(lines) + "\n"
