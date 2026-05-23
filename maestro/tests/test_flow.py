"""Tests for Maestro flow board rendering."""

from __future__ import annotations

from src.flow import FlowBoard, FlowCard, render_flow_board


def test_flow_card_renders_as_yellow_story_card():
    card = FlowCard(code="S3", title="Validation View Integration")

    assert card.render() == "🟨[S3] Validation View Integration"


def test_render_flow_board_shows_lane_headers():
    rendered = render_flow_board(FlowBoard())

    assert "Flow Board" in rendered
    assert "Backlog" in rendered
    assert "Ready" in rendered
    assert "Doing" in rendered
    assert "Validate" in rendered
    assert "Done" in rendered


def test_render_flow_board_shows_cards_in_their_lanes():
    board = FlowBoard(
        doing=(FlowCard("S4", "Flow Board Renderer"),),
        done=(FlowCard("S3", "Validation View Integration"),),
    )

    rendered = render_flow_board(board)

    assert "🟨[S4] Flow Board Renderer" in rendered
    assert "🟨[S3] Validation View Integration" in rendered


def test_render_flow_board_supports_multiple_cards_in_same_lane():
    board = FlowBoard(
        backlog=(
            FlowCard("S5", "Flow Board Command"),
            FlowCard("S6", "Flow Board Docs"),
        ),
    )

    rendered = render_flow_board(board)

    assert "🟨[S5] Flow Board Command" in rendered
    assert "🟨[S6] Flow Board Docs" in rendered


def test_render_flow_board_renders_empty_lanes_without_error():
    rendered = render_flow_board(FlowBoard())

    assert "Flow Board" in rendered
    assert rendered.count("|") >= 10


def test_render_flow_board_uses_yellow_only_for_story_cards():
    rendered = render_flow_board(FlowBoard(validate=(FlowCard("S4", "Flow Board Renderer"),)))

    assert "🟨[S4]" in rendered
    assert "🟩[S4]" not in rendered
