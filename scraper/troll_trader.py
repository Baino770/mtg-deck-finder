import asyncio
from dataclasses import dataclass
import httpx
from bs4 import BeautifulSoup

from scraper.web_scraper import WebScraper

@dataclass(frozen=True)
class TrollTraderScraperConfig:
    """Configuration for Troll Trader scraper."""
    
    BASE_URL: str = "https://www.trolltradercards.com"
    HEADERS: dict[str, str] = {
        "User-Agent": (
            "MTGDeckFinder/0.1 "
            "(samuel.bainbridge@ntlworld.com)"
        )
        }
    MAX_PAGES: int = 10  # Limit to first 10 pages to avoid long runtimes


class TrollTraderScraper(WebScraper):
    """Scraper for Troll Trader website. Uses httpx and BeautifulSoup to scrape static HTML content."""
    CONFIG = TrollTraderScraperConfig()

    async def search_card(self, card_name: str) -> list[dict]:
        """
        Searches Troll Trader for a card across all pages.
        Returns all in-stock listings.
        """
        results = []
        page = 1

        async with httpx.AsyncClient(headers=self.CONFIG.HEADERS) as client:
            while page <= self.CONFIG.MAX_PAGES:
                url = (
                    f"{self.CONFIG.BASE_URL}/products/search"
                    f"?q={card_name.replace(' ', '+')}&page={page}"
                )
                print(f"  Fetching page {page}...")

                try:
                    response = await client.get(url, timeout=15)
                    response.raise_for_status()
                except httpx.RemoteProtocolError:
                    print(f"  Server disconnected on page {page}, stopping.")
                    break
                except httpx.HTTPStatusError as e:
                    print(f"  HTTP error on page {page}: {e}")
                    break

                page_results = self.__parse_page(response.text)

                if not page_results and page > 1:
                    break

                results.extend(page_results)

                # Check if there is a next page
                soup = BeautifulSoup(response.text, "html.parser")
                next_page = soup.select_one("a.next_page")
                if not next_page:
                    break

                page += 1

                # Polite delay between requests — avoids rate limiting
                await asyncio.sleep(1)

        return results    
    
    def __parse_page(self, html: str) -> list[dict]:
        """Parse product listings from a single page of HTML.
        TO NOTE: A 1 second delay between requests is recommended to avoid rate limiting. This is very slow
        performance optimisation needs to be performed. Celery could help here. The number of pages searched
        is limited to 10 to avoid long runtimes.
        """
        soup = BeautifulSoup(html, "html.parser")
        results = []

        products = soup.select("li.product")

        for product in products:
            # Check stock — skip if out of stock indicator present
            oos = product.select_one(".stock-indicator.no-stock")
            if oos:
                continue

            # Card name
            name_el = product.select_one("h4.name")
            name = name_el.get_text(strip=True) if name_el else None

            # Product URL
            link_el = product.select_one("a[itemprop='url']")
            href = link_el["href"] if link_el else None
            full_url = f"{self.CONFIG.BASE_URL}{href}" if href else None

            # Get all in-stock variants with their prices
            variant_rows = product.select(".variant-row.row:not(.no-stock)")

            if not variant_rows:
                continue

            for variant in variant_rows:
                # Variant description e.g. "Light Play, English"
                info_el = variant.select_one(".variant-short-info")
                variant_info = info_el.get_text(strip=True) if info_el else ""

                # Skip variants with 0 in stock
                if "0 In Stock" in variant_info:
                    continue

                # Price
                price_el = variant.select_one(".regular.price")
                price_text = price_el.get_text(strip=True) if price_el else None

                price_gbp = None
                if price_text:
                    try:
                        price_gbp = float(
                            price_text.replace("£", "").strip()
                        )
                    except ValueError:
                        pass

                if name and price_gbp is not None:
                    # Include variant info in name for clarity
                    full_name = (
                        f"{name} ({variant_info})"
                        if variant_info else name
                    )
                    results.append({
                        "vendor": "Troll Trader",
                        "card_name": full_name,
                        "price_gbp": price_gbp,
                        "in_stock": True,
                        "url": full_url
                    })

        return results