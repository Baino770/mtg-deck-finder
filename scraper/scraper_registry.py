import asyncio

from scraper.web_scraper import WebScraper

class ScraperRegistry:
    """
    Registry for managing web scrapers and executing them concurrently.

    The registry holds a collection of `WebScraper` instances. Callers should
    use the public methods to register scrapers and to run them.
    """

    def __init__(self):
        """
        Initializes the scraper registry with an empty list of scrapers.

        The internal list is private; consumers should not access ``_scrapers``
        directly. If external access is required a public accessor may be added.
        """

        self._scrapers: list[WebScraper] = []

    def register(self, scraper: WebScraper) -> None:
        """
        Register a new web scraper with the registry.

        Args:
            scraper: An instance of a class implementing `WebScraper`.

        Returns:
            None
        """
        self._scrapers.append(scraper)

    async def scrape_all(self, card_name: str) -> list:
        """Execute `scrape` on all registered scrapers concurrently.

        Args:
            card_name: The card name to pass to each scraper's `scrape` method.

        Returns:
            A list containing either the successful results from each scraper
            (typically lists of offers) or an Exception instance when a scraper
            failed. The order corresponds to the registration order.
        """

        return await asyncio.gather(
            *[s.scrape(card_name) for s in self._scrapers],
            return_exceptions=True
        )
