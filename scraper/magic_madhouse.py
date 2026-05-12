import asyncio
from playwright.async_api import async_playwright


async def search_card(card_name: str) -> list[dict]:
    """
    Searches Magic Madhouse for a card and returns available listings.
    Magic Madhouse uses Klevu for search, which loads results dynamically via JavaScript, so we use Playwright to scrape.
    """
    results = []
    url = f"https://magicmadhouse.co.uk/search.php?search_query={card_name.replace(' ', '%20')}"

    async with async_playwright() as p:
        # Change headless to False to watch the program open a browser and navigate, can use to debug
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Block images and fonts to speed up scraping
        await page.route("**/*.{png,jpg,jpeg,gif,webp,woff,woff2}", 
                        lambda route: route.abort())

        await page.goto(url)

        # Wait for Klevu to finish rendering results
        # Klevu is a third party search/product discovery platform used by Magic Madhouse. The page results
        # load dynamically via JavaScript
        await page.wait_for_selector(".klevuProduct", timeout=10000)

        # Get all product listings
        products = await page.query_selector_all(".klevuProduct")

        for product in products:
            # Extract card name
            name_el = await product.query_selector(".kuName a")
            name = await name_el.inner_text() if name_el else None

            # Extract price
            price_el = await product.query_selector(".kuSalePrice")
            price_text = await price_el.inner_text() if price_el else None

            # Extract URL
            href = await name_el.get_attribute("href") if name_el else None

            # Check if in stock (button present = in stock)
            in_stock_el = await product.query_selector(".kuAddtocart")
            in_stock = in_stock_el is not None

            # Clean price string to float e.g. "£2.99" -> 2.99
            price_gbp = None
            if price_text:
                try:
                    price_gbp = float(price_text.replace("£", "").strip())
                except ValueError:
                    pass

            if name and price_gbp is not None:
                results.append({
                    "vendor": "Magic Madhouse",
                    "card_name": name.strip(),
                    "price_gbp": price_gbp,
                    "in_stock": in_stock,
                    "url": href
                })

        await browser.close()

    return results


# Test it
if __name__ == "__main__":
    results = asyncio.run(search_card("Lightning Bolt"))
    for r in results:
        print(r)