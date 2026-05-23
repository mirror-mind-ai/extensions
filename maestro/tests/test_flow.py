"""Tests for Maestro flow board rendering."""

from __future__ import annotations

import argparse

import pytest

from src.flow import FlowBoard, FlowCard, build_flow_board_from_args, parse_flow_card, render_flow_board


def test_flow_card_renders_as_yellow_story_card():
    card = FlowCard(code="S3", title="Validation View Integration")

    assert card.render() == "🟨[S3] Validation View Integration"


def test_flow_card_compact_render_limits_title_to_18_characters():
    card = FlowCard(code="S3", title="Validation View Integration")

    assert card.render_compact() == "🟨[S3] Validation Vi…"


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

    assert "🟨[S4] Flow Board Re…" in rendered
    assert "🟨[S3] Validation Vi…" in rendered


def test_render_flow_board_supports_multiple_cards_in_same_lane():
    board = FlowBoard(
        backlog=(
            FlowCard("S5", "Flow Board Command"),
            FlowCard("S6", "Flow Board Docs"),
        ),
    )

    rendered = render_flow_board(board)

    assert "🟨[S5] Flow Board Co…" in rendered
    assert "🟨[S6] Flow Board Do…" in rendered


def test_render_flow_board_renders_empty_lanes_without_error():
    rendered = render_flow_board(FlowBoard())

    assert "Flow Board" in rendered
    assert rendered.count("|") >= 10


def test_render_flow_board_uses_yellow_only_for_story_cards():
    rendered = render_flow_board(FlowBoard(validate=(FlowCard("S4", "Flow Board Renderer"),)))

    assert "🟨[S4]" in rendered
    assert "🟩[S4]" not in rendered


def test_render_flow_board_truncates_long_card_titles_to_18_characters():
    rendered = render_flow_board(
        FlowBoard(
            done=(
                FlowCard(
                    "S3",
                    "Validation View Integration With A Very Long Title That Would Break The Board",
                ),
            )
        )
    )

    assert "🟨[S3] Validation Vi…" in rendered
    assert "Validation View Integration" not in rendered


def test_parse_flow_card_accepts_code_and_title():
    card = parse_flow_card("S4:Flow Board Renderer")

    assert card == FlowCard("S4", "Flow Board Renderer")


def test_parse_flow_card_rejects_invalid_input():
    with pytest.raises(argparse.ArgumentTypeError, match="CODE:TITLE"):
        parse_flow_card("S4")
    with pytest.raises(argparse.ArgumentTypeError, match="both code and title"):
        parse_flow_card("S4:")


def test_build_flow_board_from_args_uses_explicit_lane_values():
    args = argparse.Namespace(
        backlog=[FlowCard("S5", "Flow Board Command")],
        ready=None,
        doing=[FlowCard("S4", "Flow Board Renderer")],
        validate=None,
        done=[FlowCard("S3", "Validation View Integration")],
    )

    board = build_flow_board_from_args(args)

    assert board.backlog == (FlowCard("S5", "Flow Board Command"),)
    assert board.ready == ()
    assert board.doing == (FlowCard("S4", "Flow Board Renderer"),)
    assert board.validate == ()
    assert board.done == (FlowCard("S3", "Validation View Integration"),)
