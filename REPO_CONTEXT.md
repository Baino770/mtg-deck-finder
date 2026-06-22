# Repository Context

## High-level architecture
- `scraper/` - scrapers for vendor websites plus registry and search orchestration.
- `data/` - simple data models (card, offer).
- `optimiser/` - optimization logic for deck building (if used).
- `api/` - lightweight API layer (if present).
- `tests/` - unit tests.

## Key files
- scraper.search: search orchestration and filtering.
- scraper.scryfall: Scryfall API helpers.
- scraper.*Scraper: individual vendor scrapers.
- tests/*: pytest tests for scraping and search logic.

## How to run
- Install: `pip install -r requirements.txt`
- Run tests: `pytest -q`
- Run search example: `python -m scraper.search`

## Known caveats
- ChaosCards scraper is disabled due to anti-bot measures.
- Some scrapers may require rate limiting and retries.
