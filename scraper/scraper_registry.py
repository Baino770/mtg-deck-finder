import asyncio

from scraper.web_scraper import WebScraper
from data.offer import Offer

class ScraperRegistry:
    """Registry for all web scrapers. Allows for easy management and execution of multiple scrapers."""

    def __init__(self):
        """Initializes the scraper registry with an empty list of scrapers."""

        self._scrapers: list[WebScraper] = []

    def register(self, scraper: WebScraper) -> None:
        """Registers a new web scraper."""
        
        self._scrapers.append(scraper)

    async def scrape_all(self, card_name: str) -> list[Offer]:
        """Scrapes all registered web scrapers for the given card name and returns a combined list of offers."""

        results = await asyncio.gather(
            *[s.scrape(card_name) for s in self._scrapers]
        )
        return [offer for vendor_offers in results for offer in vendor_offers]