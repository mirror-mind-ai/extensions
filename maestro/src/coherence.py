"""Coherence matrix model for Ariad/Maestro closeout visualization."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

CoherenceState = Literal["checked", "attention", "missing", "not_applicable", "unknown"]

_COHERENCE_STATE_MARKERS: dict[CoherenceState, str] = {
    "checked": "✓",
    "attention": "⚠",
    "missing": "✕",
    "not_applicable": "-",
    "unknown": "?",
}


@dataclass(frozen=True)
class CoherenceItem:
    """One surface considered during the coherence checkpoint."""

    surface: str
    state: CoherenceState
    detail: str | None = None

    def __post_init__(self) -> None:
        if self.state not in _COHERENCE_STATE_MARKERS:
            raise ValueError(f"Unknown coherence state: {self.state}")

    @property
    def marker(self) -> str:
        return _COHERENCE_STATE_MARKERS[self.state]


@dataclass(frozen=True)
class CoherenceMatrix:
    """Explicit coherence-check state for project memory surfaces."""

    items: tuple[CoherenceItem, ...]


def render_coherence_matrix(matrix: CoherenceMatrix) -> str:
    """Render a coherence matrix without computing a global ready state."""

    lines = ["Coherence Matrix", ""]
    if not matrix.items:
        lines.append("? No coherence surfaces provided")
    else:
        for item in matrix.items:
            line = f"{item.marker} {item.surface}"
            if item.detail:
                line += f" - {item.detail}"
            lines.append(line)
    return "\n".join(lines) + "\n"
