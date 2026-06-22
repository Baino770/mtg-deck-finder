# Copilot Instructions

## Overview
This repository implements a small MTG price scraper, aggregater and purchase optimiser tool. Use this guidance to act as a helpful coding assistant for contributors.

## Primary Goals
- Keep scrapers reliable and respectful of vendor terms.
- Prioritise correctness, tests, and clear documentation.
- Help add new vendor scrapers, fix tests, and improve search/filtering logic.

## Tone & Style
Concise, friendly, and pragmatic. Provide concrete code suggestions, minimal diffs, and testing steps.

## Do / Don't
- Do: propose focused changes, include unit tests, run existing tests locally.
- Don't: perform heavy refactors without tests; do not recommend scraping tactics that bypass anti-bot protections.

## Context Scope
Focus on these folders: `scraper/`, `optimiser/`, `api/`, `tests/`, and `data/`.

## Quick Commands
- Install deps: `pip install -r requirements.txt`
- Run tests: `pytest -q`
- Run a quick script: `python -m scraper.search` (or `python -c "import asyncio; from scraper.search import find_card_prices; print(asyncio.run(find_card_prices('Lightning Bolt')))"`)
