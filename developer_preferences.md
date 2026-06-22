# Developer Preferences

## Formatting & Linting
- Comply with Ruff for linting and formatting standards

## Docstrings

- Use docstrings for all public modules, classes, and functions.
- Use triple-double-quoted strings `"""..."""`.
- Start with a one-line summary.
- Follow with a blank line before details.

### Function/method docstrings
- Include an `Args:` section for each parameter.
- Include a `Returns:` section for return values.
- Include a `Raises:` section for exceptions that may be raised.

Example:

```python
def get_card_data(name: str) -> dict | None:
    """
    Fetch canonical card data from Scryfall.

    Args:
        name: The card name to search for.

    Returns:
        A dictionary with card metadata, or None if the card is not found.

    Raises:
        httpx.HTTPError: If the HTTP request fails unexpectedly.
    """

## Code Standard
- Follow PEP 8 for Python code

## Typing
- Use type hints throughout the codebase
- Prefer explicit types over overly generic types
- Avoid using 'Any' unless absolutely necessary

## Testing
- New features require unit tests.
- Keep tests deterministic — mock network requests where possible.

## Code Implementation
Code should be:

- Clear and concise
- Use idiomatic Python
- Apply SOLID principles where they add maintainability and testability

## Error Handling
Raise meaningful, context-specific exceptions

Avoid:
- Silent failures
- Bare exception handlers
- Catching broad exceptions without justification
