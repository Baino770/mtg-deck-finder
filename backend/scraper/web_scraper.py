from abc import ABC, abstractmethod

from data.offer import Offer


class WebScraper(ABC):
    """
    Abstract base class for vendor web scrapers.

    Concrete scrapers should implement `search_card` to return raw results
    which are then converted to `Offer` objects by `convert_to_offers`.
    """

    async def scrape(self, card_name: str) -> list[Offer]:
        """
        High-level scrape entry point used by the registry.

        Args:
            card_name: The card name to search for.

        Returns:
            A list of `Offer` objects produced by this scraper.
        """

        results = await self.search_card(card_name)
        return self.convert_to_offers(results)

    @abstractmethod
    async def search_card(self, card_name: str) -> list[dict]:
        """
        Search the vendor site for the given card name and return raw results.

        Args:
            card_name: The card name to search for.

        Returns:
            A list of dictionaries where each dictionary represents a raw
            vendor result. The expected keys are documented in
            `convert_to_offers`.
        """

        pass

    def convert_to_offers(self, results: list[dict]) -> list[Offer]:
        """
        Convert raw scraper result dictionaries to `Offer` objects.

        Args:
            results: A list of dictionaries produced by `search_card`.

        Returns:
            A list of validated `Offer` instances. Invalid result entries are
            skipped and a warning is emitted.
        """

        offers: list[Offer] = []
        for result in results:
            try:
                offer = Offer(
                    card_name=result["card_name"],
                    price_gbp=result["price_gbp"],
                    url=result["url"],
                    vendor=result["vendor"],
                    in_stock=result["in_stock"]
                )
                offers.append(offer)
            except KeyError as e:
                print(f"  Warning: Missing expected field {e} in result: {result}")
        return offers