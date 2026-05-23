"""Flow board rendering for Ariad/Maestro visualization."""

from __future__ import annotations

import argparse
import unicodedata
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
_MAX_CARD_TITLE_WIDTH = 14


@dataclass(frozen=True)
class FlowCard:
    """One card rendered inside a flow lane."""

    code: str
    title: str

    def render(self) -> str:
        return f"🟨[{self.code}] {self.title}"

    def render_compact(self, *, title_width: int = _MAX_CARD_TITLE_WIDTH) -> str:
        return f"🟨[{self.code}] {_truncate(self.title, title_width)}"


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


def _char_width(char: str) -> int:
    if unicodedata.combining(char):
        return 0
    if unicodedata.east_asian_width(char) in {"F", "W"}:
        return 2
    codepoint = ord(char)
    if 0x1F000 <= codepoint <= 0x1FAFF:
        return 2
    return 1


def _display_width(value: str) -> int:
    return sum(_char_width(char) for char in value)


def _truncate(value: str, max_width: int) -> str:
    if _display_width(value) <= max_width:
        return value
    if max_width <= 1:
        return "…"

    result: list[str] = []
    width = 0
    for char in value:
        char_width = _char_width(char)
        if width + char_width > max_width - 1:
            break
        result.append(char)
        width += char_width
    return "".join(result) + "…"


def _cell_widths(board: FlowBoard) -> dict[FlowLane, int]:
    widths: dict[FlowLane, int] = {}
    for lane in _LANE_ORDER:
        values = [_LANE_LABELS[lane], *(card.render_compact() for card in board.lane(lane))]
        widths[lane] = max(_display_width(value) for value in values)
    return widths


def _render_separator(widths: dict[FlowLane, int]) -> str:
    cells = ["-" * (widths[lane] + 2) for lane in _LANE_ORDER]
    return "+" + "+".join(cells) + "+"


def _pad_display(value: str, width: int) -> str:
    return value + " " * max(0, width - _display_width(value))


def _render_row(values: dict[FlowLane, str], widths: dict[FlowLane, int]) -> str:
    cells = [f" {_pad_display(values.get(lane, ''), widths[lane])} " for lane in _LANE_ORDER]
    return "|" + "|".join(cells) + "|"


def parse_flow_card(value: str) -> FlowCard:
    """Parse a flow card from CODE:TITLE."""

    try:
        code, title = value.split(":", maxsplit=1)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Flow cards must use CODE:TITLE, for example S4:Flow Board Renderer") from exc
    code = code.strip()
    title = title.strip()
    if not code or not title:
        raise argparse.ArgumentTypeError("Flow cards must include both code and title")
    return FlowCard(code=code, title=title)


def build_flow_board_from_args(args: argparse.Namespace) -> FlowBoard:
    """Build a flow board from argparse lane values."""

    return FlowBoard(
        backlog=tuple(args.backlog or ()),
        ready=tuple(args.ready or ()),
        doing=tuple(args.doing or ()),
        validate=tuple(args.validate or ()),
        done=tuple(args.done or ()),
    )


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
                    row[lane] = cards[index].render_compact()
            lines.append(_render_row(row, widths))

    lines.append(_render_separator(widths))
    return "\n".join(lines) + "\n"
