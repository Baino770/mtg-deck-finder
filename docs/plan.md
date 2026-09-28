# Deck Search Integration Development Plan

This guide breaks the deck search integration into independently startable development prompts. Each prompt is intended for the repository's Coding Agent and specifies scope, relevant files, acceptance criteria, and focused verification. Follow the steps in order: the website's Find Cheapest action will eventually call the Python backend and show quantity-aware purchase recommendations, while background job infrastructure remains out of the initial implementation.

## Development Steps

### 1. Add a deterministic decklist parser

Implement a parser for ordinary lines such as `4 Lightning Bolt`, normalize whitespace, merge duplicate card names, ignore blank lines and supported comments, and reject malformed, zero, or negative quantities with line-specific errors. Keep parsing isolated from network work.

**Kickoff prompt**

> Use Coding Agent to implement and test a deterministic backend decklist parser for lines containing a positive integer quantity and card name. Merge duplicate names, ignore blank lines and `//` comments, return structured validation errors with line numbers, and do not call external services. Follow repository conventions and add focused unit tests. Verify with the parser tests and Ruff on touched Python files.

**Scope:** Add a narrowly named parser module, such as `backend/data/decklist.py`, and focused tests under `backend/tests/`.

**Acceptance criteria:** Valid, blank, duplicate, malformed, and commented lines have deterministic behavior. Parsing has no scraper or API coupling.

**Verification:** From `backend/`, run `pytest -q tests/test_decklist.py` (or the exact chosen test filename) and `ruff check` on touched files.

#### Status 

Feature implemented and verified

Further updates required: Y 

Updates:
- The parser doesn't account for set name, condition or any other property of a MTG card

### 2. Represent purchasable offer availability

Extend the offer/result contract to carry a numeric available quantity only when the vendor provides it. Extract explicit counts where available (Troll Trader variant availability is present in its page text); do not infer arbitrary stock from a boolean. For this first version, omit offers with unknown counts from optimization. Repair nearby broken helper/test contracts only as needed, including the stale Magic Madhouse test import and the Card/Scryfall method mismatch if that helper is used.

**Kickoff prompt**

> Use Coding Agent to make scraped offers quantity-aware for deck purchasing. Add an optional numeric available quantity to the shared offer contract, parse explicit counts from vendor data where present, and keep unknown quantity distinct from out-of-stock. Do not invent stock counts or bypass vendor protections. Add deterministic parser tests using fixtures/mocks; repair adjacent stale imports only if needed for the focused tests. Verify the targeted backend tests and Ruff.

**Scope:** [`backend/data/offer.py`](../backend/data/offer.py), [`backend/scraper/web_scraper.py`](../backend/scraper/web_scraper.py), [`backend/scraper/troll_trader.py`](../backend/scraper/troll_trader.py), [`backend/scraper/magic_madhouse.py`](../backend/scraper/magic_madhouse.py), [`backend/scraper/search.py`](../backend/scraper/search.py), and relevant tests.

**Acceptance criteria:** Offer quantity is serialized consistently. Out-of-stock and unknown quantity cannot be mistaken for confirmed numeric stock. Vendors without explicit counts are excluded from the quantity optimizer.

**Verification:** Use offline tests for parsing fixtures and result conversion; do not rely on live vendor pages for the core contract.

#### Status 

Feature implemented and offline verification complete

Further updates required: Y 

Updates:
- Verify the stock information is in the assumed format for Troll Trader i.e. written "# in stock" in the variant_info
- Identify where this information lives for Magic Madhouse, currently assumed not to contain the quantity data

### 3. Make the optimizer quantity- and shipping-aware

Change the optimizer input to a requirement mapping and explicit per-offer quantities. Allow copies of a card to be allocated across vendors/listings, constrain assignments by confirmed available stock, and minimize unit costs plus configured flat shipping per used vendor. Put active vendor shipping values in one editable backend configuration and label the resulting shipping as an estimate; do not claim shipping thresholds are modeled. Add a clear unavailable/infeasible result when confirmed supply cannot satisfy the requested deck.

**Kickoff prompt**

> Use Coding Agent to extend `optimise_card_purchases` for positive card quantities and offers with explicit stock limits. Permit a requested card quantity to split across vendors, prevent allocations beyond offer stock, and include configurable flat shipping once per used vendor. Unknown stock must be excluded. Return a structured infeasible outcome when supply is insufficient. Add pure unit tests for quantity allocation, split purchasing, shipping activation, insufficient stock, and deterministic totals; do not add database or job-queue infrastructure.

**Scope:** [`backend/optimiser/optimiser.py`](../backend/optimiser/optimiser.py), a small shipping configuration module under `backend/`, and optimizer tests under `backend/tests/`.

**Acceptance criteria:** Allocations sum to each required quantity, never exceed offer availability, include shipping exactly once per used vendor, and report when the deck cannot be fully supplied.

**Verification:** Run focused optimizer tests and Ruff. Confirm the PuLP solver installed in the backend environment can solve those cases.

### 4. Build deck-level search orchestration

Add a service that takes parsed card requirements, calls existing `find_card_prices` once per unique card, retains only in-stock offers with confirmed quantities, aggregates offers into optimizer inputs without losing vendor URLs/listing identity, invokes the optimizer, and produces a JSON-safe response including unresolved cards and partial/infeasible reasons. Keep external Scryfall/vendor calls mockable. Run per-card lookups with bounded concurrency and preserve scraper/vendor politeness; do not make every request unboundedly parallel.

**Kickoff prompt**

> Use Coding Agent to implement a testable deck-search service that accepts normalized deck requirements, resolves/searches each unique card through `find_card_prices`, filters offers to confirmed in-stock numeric quantities, aggregates offers without dropping listing URLs, then invokes the quantity-aware optimizer. Return JSON-safe card assignments, used vendors, shipping estimates, totals, unresolved cards, and clear incomplete-supply errors. Bound concurrency and mock all external calls in tests. Do not expose an HTTP route in this step.

**Scope:** Add an orchestration module under `backend/` (or a service module under `backend/api/`); change [`backend/scraper/search.py`](../backend/scraper/search.py) only if its returned data contract needs the quantity field; add focused service tests.

**Acceptance criteria:** Each normalized unique card is looked up once. No stockless offer is recommended. Incomplete decks are not reported as fully optimized. Result payloads preserve purchase URLs and units/prices.

**Verification:** Run mocked async unit tests without live scraper calls.

### 5. Expose a synchronous FastAPI endpoint

Add FastAPI/Uvicorn dependencies and an app with `POST /api/search` validating a decklist request, invoking the service, and returning structured responses/errors. Configure CORS for the local Next.js origin and configurable allowed origins for deployment. Set reasonable input limits and handle validation, external-service, and unexpected failures without returning tracebacks. Do not introduce Celery, Redis, polling, or a database in this first pass; measure latency and revisit async jobs if practical deck sizes exceed hosting/request limits.

**Kickoff prompt**

> Use Coding Agent to expose the tested deck-search service through FastAPI `POST /api/search`. Add FastAPI and Uvicorn to backend requirements, define request/response validation, configure allowed frontend origins via environment/config with localhost development support, set sensible deck input/card-count limits, and map validation, unresolved-card, insufficient-stock, and upstream failures to clear HTTP responses. Keep the endpoint synchronous for this milestone and do not add Celery/Redis/database dependencies. Add API tests with mocked orchestration and verify them plus Ruff.

**Scope:** [`backend/requirements.txt`](../backend/requirements.txt), add `backend/api/main.py` and request/response schemas or service files under `backend/api/`, and add API tests under `backend/tests/`. The existing [`backend/api/__init__.py`](../backend/api/__init__.py) is empty; create the app in a new module rather than assuming a server already exists.

**Acceptance criteria:** Local launch is documented from the `backend/` working directory. The API schema validates input, allowed-origin preflight works, and mocked tests cover success, invalid input, unresolved cards, insufficient stock, and upstream failure.

**Verification:** Install updated requirements in the backend environment; run targeted API tests and `ruff check` from `backend/`; launch locally and check `/docs` and one mocked or safe development request.

### 6. Connect the Next.js form and render recommendations

Replace the random-guild placeholder submit path with a typed API request using an environment-configured backend base URL. Add submitting, success, validation/error, and timeout states; prevent duplicate submits and retain user input. Render a results view with optimized total, estimated shipping by vendor, assigned quantities/prices, and links to listings. Only update the guild theme using actual resolved-card/color data if that data is deliberately included in the API contract; otherwise remove the random placeholder behavior from this flow. Ensure vendor coverage claims match active supported vendors.

**Kickoff prompt**

> Use Coding Agent to connect the landing decklist form to the FastAPI `POST /api/search` contract using a public environment-configured backend URL. Replace the random-guild placeholder with real submit behavior; implement loading, disabled, success, API validation/error, and timeout states without clearing the deck. Add a results component showing total cost, shipping estimates by vendor, card quantities and allocations, prices, and purchase links. Match existing design conventions and make unsupported/unavailable cards understandable. Update any immediately misleading active-vendor claim only as required by the actual result UI. Run frontend lint and production build.

**Scope:** [`frontend/components/landing/DeckSearchForm.tsx`](../frontend/components/landing/DeckSearchForm.tsx), [`frontend/app/page.tsx`](../frontend/app/page.tsx), a results component under `frontend/components/`, a frontend API/types module, `frontend/.env.example` if consistent with repository conventions, and active vendor copy if required.

**Acceptance criteria:** Clicking Find Cheapest sends the exact decklist to the API. Feedback is accessible and actionable. Results include purchase links and shipping estimates. No result is represented as complete when cards are unavailable.

**Verification:** Run `npm run lint` and `npm run build` from `frontend/`; manually exercise empty input, valid response, backend validation error, and backend unavailable states with mocked or local API responses.

### 7. Run integration checks and align project docs

Add or finish mocked end-to-end backend tests across parsing, search, optimization, and API boundaries. Perform a local frontend-to-backend smoke test with a small representative deck. Record measured runtime, current active vendor coverage, numeric-stock limitations, flat estimated shipping assumptions, and how to start both dev servers. Update architecture/roadmap claims so planned Celery/Redis/database components remain clearly marked as future work rather than implemented behavior.

**Kickoff prompt**

> Use Coding Agent to complete verification and documentation for the deck-search vertical slice. Add or refine deterministic mocked tests spanning deck parsing through API JSON, run backend tests/lint and frontend lint/build, then perform a local small-deck frontend-to-backend smoke test if vendor access permits. Record measured response time, active vendor support, exact-stock-count exclusions, flat estimated shipping limits, and local run commands. Update `docs/architecture.md`, `docs/roadmap.md`, and relevant READMEs without implying async jobs, persistence, shipping thresholds, or unsupported vendor integrations already exist.

**Scope:** `backend/tests/`, [`docs/architecture.md`](architecture.md), [`docs/roadmap.md`](roadmap.md), [`README.md`](../README.md), and `frontend/README.md` as needed.

**Acceptance criteria:** Tests and builds pass, or pre-existing failures are recorded separately. Documentation accurately distinguishes shipped behavior from future architecture. Measured latency informs whether a background-job follow-up is needed.

**Verification:** Run `pytest -q` and `ruff check` from `backend/`; run `npm run lint` and `npm run build` from `frontend/`; perform a manual local smoke test with both servers running.

## Relevant Existing Files

- [`backend/scraper/search.py`](../backend/scraper/search.py) contains the current per-card Scryfall-to-vendor workflow, including `find_card_prices`.
- [`backend/scraper/scraper_registry.py`](../backend/scraper/scraper_registry.py) runs vendor scrapers concurrently for one card.
- [`backend/data/offer.py`](../backend/data/offer.py) and [`backend/scraper/web_scraper.py`](../backend/scraper/web_scraper.py) define the offer/result contract that needs confirmed stock quantity.
- [`backend/optimiser/optimiser.py`](../backend/optimiser/optimiser.py) is the existing PuLP optimizer; it currently accepts card names and vendor price mappings, not quantities or listings.
- [`backend/api/__init__.py`](../backend/api/__init__.py) is currently empty.
- [`frontend/components/landing/DeckSearchForm.tsx`](../frontend/components/landing/DeckSearchForm.tsx) contains the placeholder submit handler.
- [`frontend/app/page.tsx`](../frontend/app/page.tsx) composes the current page and does not render recommendation results.
- [`docs/architecture.md`](architecture.md) and [`docs/roadmap.md`](roadmap.md) describe planned components beyond the current implementation and should be reconciled after the vertical slice works.

## Verification Strategy

1. Run the narrow tests and linter listed in each step before beginning the next dependent step.
2. Mock Scryfall, vendor scrapers, and orchestration at appropriate boundaries. Live-network tests are not the acceptance gate for parser, optimizer, or API correctness.
3. After steps 1-5, use FastAPI's local docs and API tests to confirm the contract. After step 6, run frontend lint/build and exercise request states. After step 7, run broader backend/frontend checks and a representative local flow.
4. For the manual integration test, start FastAPI from `backend/` and Next.js from `frontend/`, configure the frontend API URL and backend allowed origin, submit a small deck whose listings expose numeric stock, and compare each assignment, shipping charge, and total against the API JSON.

## Decisions

- Initial API is synchronous `POST /api/search`; job creation, polling, Celery, and Redis are excluded until measured latency or deployment limits justify them.
- Duplicate card lines merge into quantities. Requested copies may split across vendors/listings.
- Only explicitly numeric stock quantities are eligible. Unknown stock is not assumed sufficient; current vendor integrations may therefore yield limited or no eligible offers until counts are exposed.
- Initial shipping is an editable flat cost per active vendor and must be presented as an estimate, not threshold-aware shipping.
- The current enabled vendor registry is Magic Madhouse and Troll Trader. Chaos Cards is intentionally disabled and must not be implied as available. No new vendor or anti-bot bypass work is in scope.
- No database, caching, user accounts, deployment, or persistent job state is included in this development slice.

## Further Considerations

1. A real deck may have many unique cards and vendor requests can be slow. Step 7's measurement is the gate for a separate asynchronous-job plan; do not quietly stretch request timeouts to mask this.
2. Exact quantity extraction may not be possible from every active vendor's current search page. Report those offers as unknown and identify the vendor limitation rather than guessing. Revisit the stock rule as a deliberate product decision if it blocks useful results.