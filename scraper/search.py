import asyncio
from scraper.scryfall import get_card
from scraper.magic_madhouse import search_card as magic_madhouse_search
from scraper.troll_trader import search_card as troll_trader_search


def is_relevant_result(result: dict, canonical_name: str) -> bool:
    """
    Filters vendor results to only include listings that match
    the canonical card name from Scryfall.
    """
    result_name = result["card_name"].lower()
    canonical = canonical_name.lower()
    return result_name.startswith(canonical)


async def search_all_vendors(card_name: str) -> list[dict]:
    """
    Searches all vendors in parallel for a given card name.
    Returns combined raw results.
    """
    print(f"  Searching all vendors for '{card_name}'...")

    # Run all vendor scrapers concurrently
    results = await asyncio.gather(
        magic_madhouse_search(card_name),
        troll_trader_search(card_name),
        return_exceptions=True
    )

    combined = []
    vendor_names = ["Magic Madhouse", "Troll Trader"]

    for vendor_name, vendor_results in zip(vendor_names, results):
        if isinstance(vendor_results, Exception):
            print(f"  Warning: {vendor_name} scraper failed: "
                  f"{vendor_results}")
        else:
            combined.extend(vendor_results)
            print(f"  {vendor_name}: {len(vendor_results)} results")

    return combined


async def find_card_prices(card_name: str) -> dict:
    """
    Main search function. Given a card name:
    1. Looks up canonical data from Scryfall
    2. Searches all vendors in parallel
    3. Filters and returns relevant results
    """

    # Step 1: Get canonical card data from Scryfall
    print(f"Looking up '{card_name}' on Scryfall...")
    card = await get_card(card_name)

    if card is None:
        return {
            "error": f"Card '{card_name}' not found on Scryfall",
            "results": []
        }

    canonical_name = card["name"]
    print(f"Found: {canonical_name} ({card['set_name']})")

    # Step 2: Search all vendors in parallel
    raw_results = await search_all_vendors(canonical_name)
    print(f"Total raw results: {len(raw_results)}")

    # Step 3: Filter to relevant results only
    filtered_results = [
        r for r in raw_results
        if is_relevant_result(r, canonical_name)
    ]

    # Step 4: Sort by price ascending
    filtered_results.sort(key=lambda r: r["price_gbp"])

    print(f"Filtered to {len(filtered_results)} relevant results")

    return {
        "card": card,
        "results": filtered_results
    }


# Test it
if __name__ == "__main__":
    async def main():
        output = await find_card_prices("Lightning Bolt")

        print(f"\n=== Results for {output['card']['name']} ===")
        for r in output["results"]:
            print(f"  £{r['price_gbp']:.2f} - "
                  f"[{r['vendor']}] {r['card_name']}")

    asyncio.run(main())