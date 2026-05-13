[![API Tests](https://github.com/criptic87/sporty-qa-assignment/actions/workflows/tests.yml/badge.svg)](https://github.com/criptic87/sporty-qa-assignment/actions/workflows/tests.yml)

# Sports Betting QA — Automation Framework

Automation framework for the Sporty Group QA take-home assignment.  
Tests the Single Bet Placement feature of the demo application.  
Built with **Python**, **pytest**, and **Selenium WebDriver**.

**App under test:** https://qae-assignment-tau.vercel.app/?user-id=candidate-W3qHs1Kb6P  
**API docs:** https://qae-assignment-tau.vercel.app/api/docs

---

## Project Structure

```
sporty-qa-assignment/
├── .github/
│   └── workflows/
│       └── tests.yml           # CI workflow — runs API tests on push to main
├── automation/
│   ├── pages/
│   │   └── matches_page.py     # Page Object Model for the main betting page
│   ├── screenshots/            # Evidence screenshots for bug reports
│   ├── tests/
│   │   ├── test_ui_single_bet.py            # E2E UI test — happy path
│   │   └── test_api_place_bet_validation.py # API test — stake validation
│   ├── utils/
│   │   └── api_client.py       # Wrapper for all API calls
│   ├── conftest.py             # Shared fixtures (driver, api_client, upcoming_match)
│   ├── pytest.ini              # Pytest configuration and markers
│   └── requirements.txt        # Python dependencies
├── docs/
│   ├── test_plan.md        # 6 prioritized test scenarios (Part A)
│   ├── test_execution.md   # Execution results and bug reports (Part A)
│   └── strategy.md         # Automation strategy and recommendations (Part C)
└── README.md
```

---

## Prerequisites

- Python 3.10+
- Google Chrome (latest)
- ChromeDriver matching your Chrome version (or let `selenium` manage it automatically)

---

## Setup

**1. Clone the repository**
```bash
git clone <repo-url>
cd sporty-qa-assignment
```

**2. Navigate to the automation folder**
```bash
cd automation
```

**3. Create and activate a virtual environment**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

**4. Install dependencies**
```bash
pip install -r requirements.txt
```

---

## Running the Tests

**Run all tests:**
```bash
pytest
```

**Run only UI tests:**
```bash
pytest -m ui
```

**Run only API tests:**
```bash
pytest -m api
```

---

## Test Results

| Test | Type | Expected Result |
|------|------|----------------|
| `test_user_can_select_single_bet_and_place_it` | UI | XFAIL (BUG-001) |
| `test_place_bet_rejects_stake_above_maximum` | API | PASS |

**XFAIL** means the test ran successfully up to a known bug and stopped intentionally.  
It will turn green automatically once BUG-001 is fixed and the `pytest.xfail` line is removed.

---

## Known Issues

Two bugs affect the automated tests directly. Both are documented in `docs/test_execution.md`.

- **BUG-001** — Receipt payout uses a hardcoded `× 2.00` multiplier instead of actual odds. The UI test is marked `xfail` for this assertion.
- **BUG-002** — Header balance does not update after a bet is placed. The UI test asserts balance deduction via the API instead of the UI header.

---

## Design Decisions

- **Page Object Model** — all selectors and page interactions live in `automation/pages/matches_page.py`. Tests contain no selectors, only method calls. If the UI changes, only the page object needs updating.
- **Dynamic match selection** — the `upcoming_match` fixture calls `GET /api/matches` and filters for future matches at runtime. No match IDs are hardcoded, which prevents tests from breaking as matches move to the past.
- **`implicitly_wait(0)`** — all waits are explicit (`WebDriverWait`). This gives control over timeout behaviour per element rather than a global implicit wait that can hide real timing issues.
