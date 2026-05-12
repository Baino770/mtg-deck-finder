import pytest
from unittest.mock import AsyncMock
from scraper.search import is_relevant_result, find_card_prices


# --- Pure logic tests (no mocking needed) ---

def test_is_relevant_result_matches_exact_name():
    """Exact card name match should return True."""
    result = {"card_name": "Lightning Bolt"}
    assert is_relevant_result(result, "Lightning Bolt") is True


def test_is_relevant_result_matches_variant():
    """Card name with variant suffix should return True."""
    result = {"card_name": "Lightning Bolt (MagicFest Non-Foil)"}
    assert is_relevant_result(result, "Lightning Bolt") is True


def test_is_relevant_result_rejects_different_card():
    """A completely different card should return False."""
    result = {"card_name": "SV Black Bolt 031/086 Eelektrik"}
    assert is_relevant_result(result, "Lightning Bolt") is False


def test_is_relevant_result_rejects_double_faced_card():
    """A double faced card where the target is not the primary
    face should return False."""
    result = {"card_name": "Emeritus of Conflict // Lightning Bolt"}
    assert is_relevant_result(result, "Lightning Bolt") is False


def test_is_relevant_result_case_insensitive():
    """Matching should be case insensitive."""
    result = {"card_name": "lightning bolt (foil)"}
    assert is_relevant_result(result, "Lightning Bolt") is True


# --- Coordination logic tests (mocking used here
#     to test the logic in find_card_prices,
#     not the scrapers themselves) ---

@pytest.mark.asyncio
async def test_find_card_prices_returns_error_for_unknown_card(mocker):
    """find_card_prices should return an error dict for unknown cards."""
    mocker.patch(
        "scraper.search.get_card",
        return_value=None
    )

    result = await find_card_prices("NotARealCard")

    assert "error" in result
    assert result["results"] == []


@pytest.mark.asyncio
async def test_find_card_prices_sorts_by_price(mocker):
    """Results should be sorted by price ascending."""
    mocker.patch("scraper.search.get_card", return_value={
        "name": "Lightning Bolt",
        "oracle_id": "4457ed35",
        "set_name": "Ravnica: Clue Edition"
    })
    mocker.patch("scraper.search.search_card", return_value=[
        {
            "vendor": "Magic Madhouse",
            "card_name": "Lightning Bolt (Foil)",
            "price_gbp": 9.99,
            "in_stock": True,
            "url": "https://magicmadhouse.co.uk/a"
        },
        {
            "vendor": "Magic Madhouse",
            "card_name": "Lightning Bolt",
            "price_gbp": 2.49,
            "in_stock": True,
            "url": "https://magicmadhouse.co.uk/b"
        },
        {
            "vendor": "Magic Madhouse",
            "card_name": "Lightning Bolt (MagicFest)",
            "price_gbp": 2.99,
            "in_stock": True,
            "url": "https://magicmadhouse.co.uk/c"
        }
    ])

    result = await find_card_prices("Lightning Bolt")
    prices = [r["price_gbp"] for r in result["results"]]

    assert prices == sorted(prices)


@pytest.mark.asyncio
async def test_find_card_prices_filters_irrelevant_results(mocker):
    """Pokemon cards and double faced cards should be filtered out."""
    mocker.patch("scraper.search.get_card", return_value={
        "name": "Lightning Bolt",
        "oracle_id": "4457ed35",
        "set_name": "Ravnica: Clue Edition"
    })
    mocker.patch("scraper.search.search_card", return_value=[
        {
            "vendor": "Magic Madhouse",
            "card_name": "Lightning Bolt",
            "price_gbp": 2.49,
            "in_stock": True,
            "url": "https://magicmadhouse.co.uk/a"
        },
        {
            "vendor": "Magic Madhouse",
            "card_name": "SV Black Bolt 031/086 Eelektrik",
            "price_gbp": 1.95,
            "in_stock": True,
            "url": "https://magicmadhouse.co.uk/b"
        },
        {
            "vendor": "Magic Madhouse",
            "card_name": "Emeritus of Conflict // Lightning Bolt",
            "price_gbp": 14.99,
            "in_stock": False,
            "url": "https://magicmadhouse.co.uk/c"
        }
    ])

    result = await find_card_prices("Lightning Bolt")
    card_names = [r["card_name"] for r in result["results"]]

    assert not any("Eelektrik" in name for name in card_names)
    assert not any(
        name.startswith("Emeritus") for name in card_names
    )
    assert len(result["results"]) == 1