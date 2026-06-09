from dataclasses import dataclass

@dataclass(frozen=True)
class Offer:
    """Class representing an offer for a card from a vendor."""

    card_name: str
    price: float
    vendor: str
    url: str
    in_stock: bool