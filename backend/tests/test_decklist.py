import pytest

from data.decklist import DecklistParseError, parse_decklist


def test_parse_decklist_normalizes_and_merges_card_names():
    decklist = "4 Lightning Bolt\n  2   lightning   bolt  \n3 Wear // Tear\n"

    assert parse_decklist(decklist) == {
        "Lightning Bolt": 6,
        "Wear // Tear": 3,
    }


def test_parse_decklist_ignores_blank_and_comment_lines():
    decklist = "\n// Main deck\n4 Sol Ring\n   // note\n"

    assert parse_decklist(decklist) == {"Sol Ring": 4}


def test_parse_decklist_returns_empty_mapping_for_no_cards():
    assert parse_decklist("\n// no cards\n") == {}


def test_parse_decklist_collects_structured_line_errors():
    decklist = "not a quantity Card\n0 Black Lotus\n-1 Mox\n2\n1.5 Sol Ring\n"

    with pytest.raises(DecklistParseError) as exc_info:
        parse_decklist(decklist)

    errors = exc_info.value.errors
    assert [error.line_number for error in errors] == [1, 2, 3, 4, 5]
    assert [error.line for error in errors] == decklist.splitlines()
    assert all("quantity" in error.message.lower() or "expected" in error.message.lower() for error in errors)