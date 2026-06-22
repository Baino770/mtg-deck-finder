import httpx


SCRYFALL_BASE = "https://api.scryfall.com"

# Scryfall requests we add a small delay between calls
# Their API docs ask for 50-100ms between requests
HEADERS = {
    "User-Agent": "MTGDeckFinder/0.1 (samuel.bainbridge@ntlworld.com)",
    "Accept": "application/json"
}


async def get_card(card_name: str) -> dict | None:
    """
    Fetch canonical card data from Scryfall by name.

    Uses fuzzy matching so minor typos still work.

    Args:
        card_name: The card name to lookup using Scryfall's fuzzy matching.

    Returns:
        A mapping with canonical card metadata (including `name` and
        `oracle_id`) or ``None`` when the card could not be found.

    Raises:
        httpx.HTTPError: If the underlying HTTP request fails unexpectedly.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{SCRYFALL_BASE}/cards/named",
            params={"fuzzy": card_name},
            headers=HEADERS
        )

        if response.status_code == 404:
            return None

        response.raise_for_status()
        data = response.json()

        eur = data.get("prices", {}).get("eur")

        return {
            "name": data["name"],
            "oracle_id": data["oracle_id"],
            "set_code": data["set"],
            "set_name": data["set_name"],
            "collector_number": data["collector_number"],
            "rarity": data["rarity"],
            "is_foil": data.get("foil", False) and not data.get("nonfoil", False),
            "image_url": data.get("image_uris", {}).get("normal"),
            "price_eur": float(eur) if eur is not None else None,
            "prints_search_uri": data["prints_search_uri"]
        }


async def get_all_printings(oracle_id: str) -> list[dict]:
    """
    Return every printing of a card using its oracle_id.

    Args:
        oracle_id: The Scryfall `oracle_id` for the card.

    Returns:
        A list of mappings describing each printing (set, collector number,
        price and image url).

    Raises:
        httpx.HTTPError: If the underlying HTTP request fails unexpectedly.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{SCRYFALL_BASE}/cards/search",
            params={
                "q": f"oracleid:{oracle_id}",
                "unique": "prints",
                "order": "released"
            },
            headers=HEADERS
        )

        response.raise_for_status()
        data = response.json()

        printings = []
        for card in data.get("data", []):
            eur = card.get("prices", {}).get("eur")

            printings.append({
                "name": card["name"],
                "set_code": card["set"],
                "set_name": card["set_name"],
                "collector_number": card["collector_number"],
                "rarity": card["rarity"],
                "nonfoil": card.get("nonfoil", False),
                "foil": card.get("foil", False),
                "price_eur": float(eur) if eur is not None else None,
                "image_url": card.get("image_uris", {}).get("normal")
            })

        return printings


# Test it
if __name__ == "__main__":
    import asyncio

    async def main():
        print("=== Canonical card ===")
        card = await get_card("Lightning Bolt")
        for k, v in card.items():
            print(f"  {k}: {v}")

        print("\n=== All printings ===")
        printings = await get_all_printings(card["oracle_id"])
        print(f"  Found {len(printings)} printings")
        for p in printings[:5]:  # just show first 5
            print(f"  {p['set_name']} ({p['set_code']}) - EUR: {p['price_eur']}")

    asyncio.run(main())