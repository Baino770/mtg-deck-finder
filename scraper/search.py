import asyncio

from scraper.scraper_registry import ScraperRegistry
from scraper.scryfall import get_card as scryfall_get_card
from scraper.magic_madhouse import MagicMadhouseScraper
from scraper.troll_trader import TrollTraderScraper
from scraper.chaos_cards import ChaosCardsScraper


def is_relevant_result(result: dict, canonical_name: str) -> bool:
    """
    Filters vendor results to only include listings that match
    the canonical card name from Scryfall.
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
    return {
        "vendor": offer.vendor,
        "card_name": offer.card_name,
        "price_gbp": offer.price_gbp,
        "in_stock": offer.in_stock,
        "url": offer.url
    }


async def search_all_vendors(card_name: str) -> list[dict]:
    """Searches all registered vendor scrapers in parallel and returns combined results."""
    
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
    """Looks up canonical card data, searches vendors, and returns filtered results."""
    
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