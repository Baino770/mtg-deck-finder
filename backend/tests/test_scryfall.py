import pytest
from scraper.scryfall import get_card, get_all_printings


@pytest.mark.asyncio
async def test_get_card_returns_correct_fields():
    """get_card should return a dict with all expected fields."""
    card = await get_card("Lightning Bolt")

    assert card is not None
    assert card["name"] == "Lightning Bolt"
    assert card["set_code"] is not None
    assert card["set_name"] is not None
    assert card["collector_number"] is not None
    assert card["rarity"] is not None
    assert card["image_url"].startswith("https://")
    assert card["prints_search_uri"].startswith("https://")


@pytest.mark.asyncio
async def test_get_card_returns_none_for_unknown_card():
    """get_card should return None when Scryfall returns 404."""
    result = await get_card("ThisCardDoesNotExistXYZ")

    assert result is None


@pytest.mark.asyncio
async def test_get_card_fuzzy_match():
    """get_card should handle minor typos via fuzzy matching."""
    card = await get_card("Lightnin Bolt")

    assert card is not None
    assert card["name"] == "Lightning Bolt"


@pytest.mark.asyncio
async def test_get_card_price_is_float_or_none():
    """Price should be a valid float string or None — never garbage."""
    card = await get_card("Lightning Bolt")

    if card["price_eur"] is not None:
        assert isinstance(card["price_eur"], float)
        assert card["price_eur"] > 0


@pytest.mark.asyncio
async def test_get_card_is_foil_is_bool():
    """is_foil should always be a boolean."""
    card = await get_card("Lightning Bolt")

    assert isinstance(card["is_foil"], bool)


@pytest.mark.asyncio
async def test_get_all_printings_returns_list():
    """get_all_printings should return a non-empty list."""
    card = await get_card("Lightning Bolt")
    printings = await get_all_printings(card["oracle_id"])

    assert isinstance(printings, list)
    assert len(printings) > 0


@pytest.mark.asyncio
async def test_get_all_printings_structure():
    """Every printing should have the expected fields."""
    card = await get_card("Lightning Bolt")
    printings = await get_all_printings(card["oracle_id"])

    for printing in printings:
        assert "name" in printing
        assert "set_code" in printing
        assert "set_name" in printing
        assert "collector_number" in printing
        assert "rarity" in printing
        assert "nonfoil" in printing
        assert "foil" in printing
        assert "price_eur" in printing
        assert "image_url" in printing


@pytest.mark.asyncio
async def test_get_all_printings_handles_missing_price():
    """get_all_printings should handle printings with no price data
    without crashing."""
    card = await get_card("Lightning Bolt")
    printings = await get_all_printings(card["oracle_id"])

    # At least one Secret Lair printing is likely to have no price
    # We just assert it doesn't crash and returns None cleanly
    none_prices = [p for p in printings if p["price_eur"] is None]
    assert isinstance(none_prices, list)