import scraper.scryfall as scryfall

class Card:
    def __init__(self, name: str) -> None:
        self.name = name
        self.canonical_name = ""
        self.oracle_id = ""

    def set_card_data(self) -> None:
        """
        Fetches canonical card data from Scryfall by name.
        Uses fuzzy matching so minor typos still work.
        Raises ValueError if card not found.
        """
        
        card_data = scryfall.get_card_data(self.name)
        if card_data is None:
            raise ValueError(f"Card '{self.name}' not found on Scryfall")

        self.canonical_name = card_data["name"]
        self.oracle_id = card_data["oracle_id"]

        return 

