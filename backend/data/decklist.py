"""Parse plain-text decklists into normalized card quantities."""

from dataclasses import dataclass


@dataclass(frozen=True)
class DecklistLineError:
    """A validation error associated with one decklist line."""

    line_number: int
    line: str
    message: str


class DecklistParseError(ValueError):
    """Raised when one or more decklist lines cannot be parsed."""

    def __init__(self, errors: list[DecklistLineError]) -> None:
        self.errors = tuple(errors)
        details = "; ".join(
            f"Line {error.line_number}: {error.message}"
            for error in self.errors
        )
        super().__init__(details)


def parse_decklist(decklist: str) -> dict[str, int]:
    """Parse quantity-and-name lines, merging repeated card names.

    Blank lines and full-line comments beginning with ``//`` are ignored.
    Card names are normalized to single spaces and merged case-insensitively;
    the spelling from the first occurrence is retained.

    Raises:
        DecklistParseError: If any non-comment line is malformed or has a
            quantity that is not a positive integer.
    """
    quantities: dict[str, int] = {}
    names_by_key: dict[str, str] = {}
    errors: list[DecklistLineError] = []

    for line_number, original_line in enumerate(decklist.splitlines(), start=1):
        line = original_line.strip()
        if not line or line.startswith("//"):
            continue

        parts = line.split(maxsplit=1)
        if len(parts) != 2:
            errors.append(DecklistLineError(
                line_number=line_number,
                line=original_line,
                message="Expected a quantity followed by a card name.",
            ))
            continue

        quantity_text, card_name = parts
        if not quantity_text.isdecimal():
            errors.append(DecklistLineError(
                line_number=line_number,
                line=original_line,
                message="Quantity must be a positive integer.",
            ))
            continue

        quantity = int(quantity_text)
        if quantity <= 0:
            errors.append(DecklistLineError(
                line_number=line_number,
                line=original_line,
                message="Quantity must be a positive integer.",
            ))
            continue

        normalized_name = " ".join(card_name.split())
        if not normalized_name:
            errors.append(DecklistLineError(
                line_number=line_number,
                line=original_line,
                message="Card name cannot be empty.",
            ))
            continue

        name_key = normalized_name.casefold()
        names_by_key.setdefault(name_key, normalized_name)
        display_name = names_by_key[name_key]
        quantities[display_name] = quantities.get(display_name, 0) + quantity

    if errors:
        raise DecklistParseError(errors)

    return quantities