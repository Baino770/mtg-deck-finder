import pytest
from unittest.mock import AsyncMock
from data.offer import Offer
from scraper.search import SCRAPER_REGISTRY, is_relevant_result, find_card_prices


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
    mocker.patch.object(
        SCRAPER_REGISTRY,
        "scrape_all",
        AsyncMock(return_value=[
            [
                Offer(
                    card_name="Lightning Bolt (Foil)",
                    price=9.99,
                    vendor="Magic Madhouse",
                    url="https://magicmadhouse.co.uk/a",
                    in_stock=True
                ),
                Offer(
                    card_name="Lightning Bolt",
                    price=2.49,
                    vendor="Magic Madhouse",
                    url="https://magicmadhouse.co.uk/b",
                    in_stock=True
                ),
                Offer(
                    card_name="Lightning Bolt (MagicFest)",
                    price=2.99,
                    vendor="Magic Madhouse",
                    url="https://magicmadhouse.co.uk/c",
                    in_stock=True
                )
            ]
        ])
    )

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
    mocker.patch.object(
        SCRAPER_REGISTRY,
        "scrape_all",
        AsyncMock(return_value=[
            [
                Offer(
                    card_name="Lightning Bolt",
                    price=2.49,
                    vendor="Magic Madhouse",
                    url="https://magicmadhouse.co.uk/a",
                    in_stock=True
                ),
                Offer(
                    card_name="SV Black Bolt 031/086 Eelektrik",
                    price=1.95,
                    vendor="Magic Madhouse",
                    url="https://magicmadhouse.co.uk/b",
                    in_stock=True
                ),
                Offer(
                    card_name="Emeritus of Conflict // Lightning Bolt",
                    price=14.99,
                    vendor="Magic Madhouse",
                    url="https://magicmadhouse.co.uk/c",
                    in_stock=False
                )
            ],
            []
        ])
    )

    result = await find_card_prices("Lightning Bolt")
    card_names = [r["card_name"] for r in result["results"]]

    assert not any("Eelektrik" in name for name in card_names)
    assert not any(
        name.startswith("Emeritus") for name in card_names
    )
    assert len(result["results"]) == 1
    

@pytest.mark.asyncio
async def test_find_card_prices_combines_vendor_results(mocker):
    """Results from multiple vendors should be combined and sorted."""
    mocker.patch("scraper.search.get_card", return_value={
        "name": "Lightning Bolt",
        "oracle_id": "4457ed35",
        "set_name": "Ravnica: Clue Edition"
    })
    mocker.patch.object(
        SCRAPER_REGISTRY,
        "scrape_all",
        AsyncMock(return_value=[
            [
                Offer(
                    card_name="Lightning Bolt",
                    price=2.99,
                    vendor="Magic Madhouse",
                    url="https://magicmadhouse.co.uk/a",
                    in_stock=True
                )
            ],
            [
                Offer(
                    card_name="Lightning Bolt (NM-Mint, English,1 In Stock)",
                    price=1.87,
                    vendor="Troll Trader",
                    url="https://trolltradercards.com/a",
                    in_stock=True
                )
            ]
        ])
    )

    result = await find_card_prices("Lightning Bolt")

    assert len(result["results"]) == 2

    for r in result["results"]:
        if r["vendor"] == "Magic Madhouse":
            assert r["price_gbp"] == 2.99
        elif r["vendor"] == "Troll Trader":
            assert r["price_gbp"] == 1.87


@pytest.mark.asyncio
async def test_find_card_prices_handles_vendor_failure(mocker):
    """If one vendor fails the other results should still be returned."""
    mocker.patch("scraper.search.get_card", return_value={
        "name": "Lightning Bolt",
        "oracle_id": "4457ed35",
        "set_name": "Ravnica: Clue Edition"
    })
    mocker.patch.object(
        SCRAPER_REGISTRY,
        "scrape_all",
        AsyncMock(return_value=[
            Exception("Scraper failed"),
            [
                Offer(
                    card_name="Lightning Bolt (NM-Mint, English,1 In Stock)",
                    price=1.87,
                    vendor="Troll Trader",
                    url="https://trolltradercards.com/a",
                    in_stock=True
                )
            ]
        ])
    )

    result = await find_card_prices("Lightning Bolt")

    assert len(result["results"]) == 1
    assert result["results"][0]["vendor"] == "Troll Trader"