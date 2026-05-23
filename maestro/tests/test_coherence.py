"""Tests for Maestro coherence matrix model."""

from __future__ import annotations

import pytest

from src.coherence import CoherenceItem, CoherenceMatrix


def test_coherence_item_exposes_marker_for_each_state():
    assert CoherenceItem("Roadmap", "checked").marker == "✓"
    assert CoherenceItem("Decisions", "attention").marker == "⚠"
    assert CoherenceItem("Worklog", "missing").marker == "✕"
    assert CoherenceItem("Release notes", "not_applicable").marker == "-"
    assert CoherenceItem("Internal links", "unknown").marker == "?"


def test_coherence_item_rejects_unknown_state():
    with pytest.raises(ValueError, match="Unknown coherence state"):
        CoherenceItem("Roadmap", "green")  # type: ignore[arg-type]


def test_coherence_matrix_groups_items_without_global_status():
    matrix = CoherenceMatrix(
        items=(
            CoherenceItem("Roadmap", "checked", "CV2.E5.S1 planned"),
            CoherenceItem("Decisions", "attention", "No new decision needed"),
            CoherenceItem("Release notes", "not_applicable"),
            CoherenceItem("Internal links", "unknown"),
        )
    )

    assert len(matrix.items) == 4
    assert matrix.items[0].marker == "✓"
    assert matrix.items[1].marker == "⚠"
    assert matrix.items[2].state == "not_applicable"
    assert matrix.items[3].state == "unknown"
    assert not hasattr(matrix, "ready")


def test_not_applicable_is_legitimate_non_failure_state():
    item = CoherenceItem("Release notes", "not_applicable", "No release boundary")

    assert item.marker == "-"
    assert item.detail == "No release boundary"


def test_unknown_state_exists_to_prevent_false_green():
    item = CoherenceItem("Internal links", "unknown")

    assert item.marker == "?"
    assert item.state == "unknown"
