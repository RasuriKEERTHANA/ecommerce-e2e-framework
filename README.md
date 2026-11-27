# E-commerce E2E Test Automation Framework

![Smoke tests](https://github.com/<your-username>/<your-repo>/actions/workflows/smoke.yml/badge.svg)
![Nightly regression](https://github.com/<your-username>/<your-repo>/actions/workflows/regression.yml/badge.svg)

An end-to-end test framework built with **Playwright, Pytest and Python**. It validates a small e-commerce app at three layers: **UI, REST API and SQL database**.

## What is in this repo

- `shop_app/`: the application under test (FastAPI + SQLite) with login, products, cart and checkout pages and a REST API.
- `pages/`: Page Object Model classes (`BasePage`, `LoginPage`, `ProductsPage`, `CartPage`, `CheckoutPage`).
- `utils/`: API client, JSON schemas and SQL helper.
- `tests/ui`, `tests/api`, `tests/db`, `tests/hybrid`: the test suites.
- `conftest.py`: fixtures that start the app, reset the database before every test, and provide logged-in browser and API sessions.
- `.github/workflows/`: CI pipelines.

## Test coverage

| Suite | Tests | Covers |
|---|---|---|
| UI | 27 | Login, search, category filter, cart, quantity limits, checkout, negative flows |
| API | 41 | Auth, products, cart, orders, status codes, JSON schema validation, error cases |
| Database | 13 | Saved rows, stock changes, constraints, per-user data isolation |
| Hybrid | 3 | One flow checked through UI, then API, then SQL |

## Key design choices

- **Page Object Model** with a shared `BasePage`, so a UI change is fixed in one place.
- **Stable locators** using `data-testid` attributes with `get_by_test_id`.
- **Test isolation:** the database is reset before every test, and each test gets a fresh browser context.
- **Separate test database and port**, so tests never touch development data.
- **Markers** (`smoke`, `regression`, `api`, `db`, `hybrid`) to run subsets.
- **Schema validation** with `jsonschema` (unexpected fields fail the test).
- **Failure artifacts:** HTML report with embedded screenshot, plus Playwright traces.

## Setup

```bash
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Mac/Linux
pip install -r requirements.txt
playwright install chromium
```

## Running the tests

```bash
pytest                    # everything
pytest -m smoke           # quick checks
pytest -m api             # API tests only
pytest -m db              # database tests only
pytest -m hybrid          # UI + API + SQL tests
pytest --headed --slowmo 500   # watch the browser
```

Pytest starts the app on port 8001 with its own `test_shop.db`, so you don't need to start anything manually. To explore the app yourself:

```bash
cd shop_app
python seed.py
uvicorn main:app --reload
```

Open http://127.0.0.1:8000/login (user `test@example.com`, password `Password123`). Interactive API docs are at `/docs`.

## Reports and debugging

- `reports/report.html`: self-contained HTML report (failed UI tests include a screenshot).
- `test-results/`: Playwright traces for failed tests. Open one with `playwright show-trace <path-to-trace.zip>`.

## CI/CD (GitHub Actions)

- **Smoke tests** run on every pull request.
- **Nightly regression** runs the full suite on a schedule.
- Both upload the report, traces and screenshots as downloadable artifacts.

## Known simplifications

- Passwords are stored as plain text and tokens are simple strings (`token-<id>`). This is a test app, and real systems use hashing and JWTs.
- SQLite does not enforce foreign keys unless enabled, so integrity is checked with queries.
- Card validation happens in the browser, not on the server.