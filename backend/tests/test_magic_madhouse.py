import pytest
from scraper.magic_madhouse import search_card


@pytest.mark.asyncio
async def test_search_card_returns_results():
    """Searching a common card should return at least one result."""
    results = await search_card("Lightning Bolt")

    assert isinstance(results, list)
    assert len(results) > 0


@pytest.mark.asyncio
async def test_search_card_result_structure():
    """Every result should have the expected fields."""
    results = await search_card("Lightning Bolt")

    for result in results:
        assert "vendor" in result
        assert "card_name" in result
        assert "price_gbp" in result
        assert "in_stock" in result
        assert "url" in result


@pytest.mark.asyncio
async def test_search_card_vendor_name():
    """Vendor field should always be Magic Madhouse."""
    results = await search_card("Lightning Bolt")

    for result in results:
        assert result["vendor"] == "Magic Madhouse"


@pytest.mark.asyncio
async def test_search_card_prices_are_positive_floats():
    """All prices should be floats greater than zero."""
    results = await search_card("Lightning Bolt")

    for result in results:
        assert isinstance(result["price_gbp"], float)
        assert result["price_gbp"] > 0


@pytest.mark.asyncio
async def test_search_card_in_stock_is_bool():
    """in_stock should always be a boolean."""
    results = await search_card("Lightning Bolt")

    for result in results:
        assert isinstance(result["in_stock"], bool)


@pytest.mark.asyncio
async def test_search_card_urls_are_valid():
    """All URLs should point to Magic Madhouse."""
    results = await search_card("Lightning Bolt")

    for result in results:
        assert result["url"].startswith("https://magicmadhouse.co.uk")


@pytest.mark.asyncio
async def test_search_card_unknown_card_returns_empty():
    """Searching for a non-existent card should return an empty list."""
    results = await search_card("XYZNOTAREALCARDXYZ")

    assert isinstance(results, list)
    assert len(results) == 0