"""
Search orchestration helpers for vendor scrapers.

This module provides functions that lookup canonical card data via Scryfall
and then query all registered vendor scrapers for available offers.
"""

import asyncio

from scraper.scraper_registry import ScraperRegistry
from scraper.scryfall import get_card as scryfall_get_card
from scraper.magic_madhouse import MagicMadhouseScraper
from scraper.troll_trader import TrollTraderScraper


def is_relevant_result(result: dict, canonical_name: str) -> bool:
    """
    Return whether a vendor result corresponds to the canonical card name.

    Args:
        result: A vendor result mapping containing at least the key ``card_name``.
        canonical_name: The canonical card name from Scryfall to match against.

    Returns:
        True if the vendor result's `card_name` starts with the canonical name
        (case-insensitive), otherwise False.
    """
    result_name = result["card_name"].lower()
    canonical = canonical_name.lower()
    return result_name.startswith(canonical)


SCRAPER_REGISTRY = ScraperRegistry()
SCRAPER_REGISTRY.register(MagicMadhouseScraper())
SCRAPER_REGISTRY.register(TrollTraderScraper())
# Chaos Cards scraper is currently disabled due to their site's anti-bot measures. Uncomment the line below to enable it if you have a solution for bypassing those measures.
# SCRAPER_REGISTRY.register(ChaosCardsScraper())


def _convert_offer_to_result(offer) -> dict:
    """
    Convert an `Offer` object into a simple result dictionary.

    Args:
        offer: An `Offer` instance (from `data.offer`).

    Returns:
        A dictionary suitable for presentation or further filtering with keys
        ``vendor``, ``card_name``, ``price_gbp``, ``in_stock`` and ``url``.
    """
    return {
        "vendor": offer.vendor,
        "card_name": offer.card_name,
        "price_gbp": offer.price_gbp,
        "in_stock": offer.in_stock,
        "url": offer.url
    }


async def search_all_vendors(card_name: str) -> list[dict]:
    """Search all registered vendor scrapers concurrently.

    Args:
        card_name: The canonical card name to search for on vendor sites.

    Returns:
        A flat list of vendor result dictionaries produced by registered scrapers.
    """

    print(f"  Searching all vendors for '{card_name}'...")

    results = await SCRAPER_REGISTRY.scrape_all(card_name)

    combined = []
    for scraper, vendor_results in zip(SCRAPER_REGISTRY._scrapers, results):
        vendor_name = scraper.__class__.__name__

        if isinstance(vendor_results, Exception):
            print(f"  Warning: {vendor_name} scraper failed: {vendor_results}")
            continue

        converted = [_convert_offer_to_result(offer) for offer in vendor_results]
        combined.extend(converted)
        print(f"  {vendor_name}: {len(converted)} results")

    return combined


async def find_card_prices(card_name: str) -> dict:
    """Lookup canonical card data on Scryfall then query all vendors.

    Args:
        card_name: The user-supplied card name (may be fuzzy/misspelled).

    Returns:
        A dictionary with keys:
        - ``card``: canonical card metadata from Scryfall or ``None`` when not found.
        - ``results``: list of filtered vendor result dictionaries.

        If the card is not found the ``card`` value will be ``None`` and an
        ``error`` key will be present with an explanatory message.
    """

    print(f"Looking up '{card_name}' on Scryfall...")
    card = await scryfall_get_card(card_name)

    if card is None:
        return {
            "error": f"Card '{card_name}' not found on Scryfall",
            "results": []
        }

    canonical_name = card["name"]
    print(f"Found: {canonical_name} ({card['set_name']})")

    raw_results = await search_all_vendors(canonical_name)
    print(f"Total raw results: {len(raw_results)}")

    filtered_results = [
        r for r in raw_results
        if is_relevant_result(r, canonical_name)
    ]

    filtered_results.sort(key=lambda r: r["price_gbp"])
    print(f"Filtered to {len(filtered_results)} relevant results")

    return {
        "card": card,
        "results": filtered_results
    }


if __name__ == "__main__":
    async def main():
        output = await find_card_prices("Lightning Bolt")

        print(f"\n=== Results for {output['card']['name']} ===")
        for r in output["results"]:
            print(f"  £{r['price_gbp']:.2f} - [{r['vendor']}] {r['card_name']}")

    asyncio.run(main())