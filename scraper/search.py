import asyncio
from scraper.scryfall import get_card
from scraper.magic_madhouse import search_card


def is_relevant_result(result: dict, canonical_name: str) -> bool:
    """
    Filters vendor results to only include listings that match
    the canonical card name from Scryfall.
    We do a case-insensitive check that the result name 
    starts with the canonical name.
    """
    result_name = result["card_name"].lower()
    canonical = canonical_name.lower()
    return result_name.startswith(canonical)


async def find_card_prices(card_name: str) -> dict:
    """
    Main search function. Given a card name:
    1. Looks up canonical data from Scryfall
    2. Searches vendors using canonical name
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

    # Step 2: Search vendors
    print(f"Searching vendors for '{canonical_name}'...")
    raw_results = await search_card(canonical_name)

    # Step 3: Filter to relevant results only
    filtered_results = [
        r for r in raw_results
        if is_relevant_result(r, canonical_name)
    ]

    print(f"Found {len(raw_results)} raw results, "
          f"{len(filtered_results)} after filtering")

    # Step 4: Sort by price ascending
    filtered_results.sort(key=lambda r: r["price_gbp"])

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
            print(f"  £{r['price_gbp']:.2f} - {r['card_name']}")
            print(f"    {r['url']}")

    asyncio.run(main())