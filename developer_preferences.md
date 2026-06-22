# Developer Preferences

## Formatting & Linting
- Comply with Ruff for linting and formatting standards

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
