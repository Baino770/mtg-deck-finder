from playwright.async_api import async_playwright

from scraper.web_scraper import WebScraper

class ChaosCardsScraper(WebScraper):
    """Scraper for Chaos Cards website. Uses Playwright to handle dynamic content loaded by Hawksearch."""


    async def search_card(self, card_name: str) -> list[dict]:
        """
        Searches Chaos Cards for a card and returns available listings.
            Chaos Cards uses Hawksearch for search, which loads results dynamically via JavaScript, so we use Playwright to scrape.
        TO NOTE: Chaos Cards uses Cloudfalre bot protection bot. Neither Playwright nor Playwright-stealth can bypass this. 
        Scraping this website should not be pursued. There is the option to contact the owners in the future.
        """
        results = []
        url = (f"https://www.chaoscards.co.uk/search/"
            f"{card_name.replace(' ', '%20')}")

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            # Block images and fonts to speed up scraping
            await page.route(
                "**/*.{png,jpg,jpeg,gif,webp,woff,woff2}",
                lambda route: route.abort()
            )

            await page.goto(url)

            # Wait for Hawksearch to finish loading results
            await page.wait_for_selector(".prod-el", timeout=15000)

            # Get all product listings
            products = await page.query_selector_all(".prod-el")

            for product in products:

                # Extract card name from title element
                name_el = await product.query_selector(".prod-el__title span")
                name = await name_el.inner_text() if name_el else None

                # Extract price
                price_el = await product.query_selector(
                    ".prod-el__pricing-price"
                )
                price_text = await price_el.inner_text() if price_el else None

                # Extract URL
                link_el = await product.query_selector(".prod-el__link")
                href = await link_el.get_attribute("href") if link_el else None

                # Out of stock if the oos element is present
                oos_el = await product.query_selector(
                    ".prod-el__availability-oos"
                )
                in_stock = oos_el is None

                # Clean price string to float e.g. "£3.49" -> 3.49
                price_gbp = None
                if price_text:
                    try:
                        price_gbp = float(
                            price_text.replace("£", "").strip()
                        )
                    except ValueError:
                        pass

                if name and price_gbp is not None:
                    # Build full URL if href is relative
                    full_url = (
                        f"https://www.chaoscards.co.uk{href}"
                        if href and href.startswith("/")
                        else href
                    )

                    results.append({
                        "vendor": "Chaos Cards",
                        "card_name": name.strip(),
                        "price_gbp": price_gbp,
                        "in_stock": in_stock,
                        "url": full_url
                    })

            await browser.close()

        return results