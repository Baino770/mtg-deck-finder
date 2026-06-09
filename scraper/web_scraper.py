from abc import ABC, abstractmethod

from data.offer import Offer

class WebScraper (ABC):
    """Abstract class for web scrapers. All web scrapers should inherit from this class and implement the scrape method."""

    async def scrape(self, card_name: str) -> list[Offer]:
        """Scrapes the website for the given card name and returns a list of offers."""
        
        results = await self.search_card(card_name)
        return self.convert_to_offers(results)
    
    @abstractmethod
    async def search_card(self, card_name: str) -> list[dict]:
        """Searches the website for the given card name and returns a list of dictionaries."""
        pass

    def convert_to_offers(self, results: list[dict]) -> list[Offer]:
        """Converts raw scraper results to a list of Offer objects."""
        offers = []
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