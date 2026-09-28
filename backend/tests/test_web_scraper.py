from scraper.search import _convert_offer_to_result
from scraper.web_scraper import WebScraper


class DummyWebScraper(WebScraper):
    async def search_card(self, card_name: str) -> list[dict]:
        return []


def test_offer_conversion_preserves_quantity_and_stock_state():
    raw_results = [
        {
            "card_name": "Lightning Bolt",
            "price_gbp": 1.25,
            "vendor": "Troll Trader",
            "url": "https://example.com/available",
            "in_stock": True,
            "available_quantity": 3,
        },
        {
            "card_name": "Lightning Bolt",
            "price_gbp": 1.50,
            "vendor": "Magic Madhouse",
            "url": "https://example.com/unknown",
            "in_stock": True,
        },
        {
            "card_name": "Lightning Bolt",
            "price_gbp": 1.75,
            "vendor": "Magic Madhouse",
            "url": "https://example.com/out-of-stock",
            "in_stock": False,
        },
    ]
    scraper = DummyWebScraper()

    offers = scraper.convert_to_offers(raw_results)
    results = [_convert_offer_to_result(offer) for offer in offers]

    assert results[0]["available_quantity"] == 3
    assert results[1]["available_quantity"] is None
    assert results[2]["available_quantity"] is None
    assert results[1]["in_stock"] is True
    assert results[2]["in_stock"] is False