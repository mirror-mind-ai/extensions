"""Tests for Maestro coherence matrix model."""

from __future__ import annotations

import pytest

from src.coherence import CoherenceItem, CoherenceMatrix, render_coherence_matrix


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


def test_render_coherence_matrix_shows_title_and_all_states():
    matrix = CoherenceMatrix(
        items=(
            CoherenceItem("Roadmap", "checked", "CV2.E5.S2 updated"),
            CoherenceItem("Decisions", "attention", "No new decision needed"),
            CoherenceItem("Worklog", "missing"),
            CoherenceItem("Release notes", "not_applicable", "No release boundary"),
            CoherenceItem("Internal links", "unknown"),
        )
    )

    rendered = render_coherence_matrix(matrix)

    assert "Coherence Matrix" in rendered
    assert "✓ Roadmap - CV2.E5.S2 updated" in rendered
    assert "⚠ Decisions - No new decision needed" in rendered
    assert "✕ Worklog" in rendered
    assert "- Release notes - No release boundary" in rendered
    assert "? Internal links" in rendered


def test_render_coherence_matrix_omits_detail_when_absent():
    rendered = render_coherence_matrix(CoherenceMatrix(items=(CoherenceItem("Internal links", "unknown"),)))

    assert "? Internal links\n" in rendered
    assert "? Internal links -" not in rendered


def test_render_coherence_matrix_does_not_include_global_status():
    rendered = render_coherence_matrix(CoherenceMatrix(items=(CoherenceItem("Roadmap", "checked"),)))

    assert "Status:" not in rendered
    assert "ready" not in rendered.lower()


def test_render_coherence_matrix_handles_empty_matrix_as_unknown():
    rendered = render_coherence_matrix(CoherenceMatrix(items=()))

    assert "? No coherence surfaces provided" in rendered
