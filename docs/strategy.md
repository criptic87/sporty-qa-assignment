# Strategy & Recommendations

**Project:** Sports Betting QA — Single Bet Placement  
**Author:** Andrei Ciorogar

---

## Why These 2 Tests Were Selected for Automation

### Test 1 — E2E UI: Single Bet Placement Happy Path

The happy path is the highest-value automation target in a betting product. If a user cannot select an outcome, enter a stake, and receive a confirmed receipt, the platform generates no revenue. This test covers the full chain: UI interaction, API call, receipt rendering in one run. A regression is immediately visible.

It also serves a secondary purpose: it surfaces two known bugs in a structured way. BUG-001 (incorrect receipt payout) is marked `pytest.xfail` with the expected value documented, so it turns green automatically when the bug is fixed. BUG-002 (stale header balance) is handled by asserting via the API instead of the UI, with a comment explaining why, keeping the test meaningful without hiding the bug.

### Test 2 — API: Stake Above Maximum Rejected

Stake limits are a core financial business rule. Testing this at the API layer (not through the browser) verifies that the constraint is enforced independently of UI controls. A user who bypasses the UI and calls the API directly should not be able to place an oversized bet. The test also confirms the balance is unchanged after a rejection, which validates all-or-nothing behavior: a failed bet must not deduct funds.

API-layer tests are faster, more stable, and easier to maintain than UI tests for validation rules. They do not depend on selectors, page load timing, or browser state.

---

## What Was Intentionally Left as Manual Only

**Exploratory edge cases** — filter combinations (date + odds range together), invalid odds range input (min > max), and the error modal flow (Rebet vs Close button behaviour). These benefit from human judgment and observation. The spec describes expected behaviour but leaves some interactions ambiguous; a human tester can adapt in real time where automation would require significant setup for diminishing return.

**Known-broken flows** — automating tests that confirm bugs already documented in `test_execution.md` (BUG-003 past matches, BUG-002 balance display) adds noise to the suite without new signal. These become automation candidates once the bugs are fixed.

**Selection replacement (TS005)** — verifying that clicking a new outcome replaces the previous one in the bet slip. Valuable manual check, lower financial risk than payout accuracy, and the current spec ambiguity around the UI state makes it a weaker automation target until the behaviour is fully specified.

---

## Top Recommendations if This Project Were to Scale

### 1. CI/CD Pipeline

Run the test suite automatically on every pull request. The API tests are fast enough to run on every commit; the UI tests can run on merge to main. This catches regressions before they reach production and removes the dependency on manual test runs. A GitHub Actions workflow with headless Chrome would be the next step for this stack.

### 2. Expand API Test Coverage Before UI Tests

The validation rules table in the spec defines at least 8 testable API behaviours (missing selection, invalid selection value, missing match ID, unknown match ID, stake below minimum, stake above maximum, stake exceeding balance, missing user context). Each of these is a one-request assertion: fast, stable, and independent of UI state. Building these out first gives strong confidence in the backend before investing in more E2E UI tests.

### 3. Resolve Spec Ambiguities and Data Model Gaps Before Expanding Coverage

Two issues will create ongoing test maintenance problems if left unresolved:

- **Minimum stake inconsistency** — the business rules table states €1.00, the validation rules table states €1.01. Tests cannot reliably assert boundary behaviour until this is clarified.
- **Missing kickoff time** (BUG-004) — `GET /api/matches` returns `kickoffDate` as a date only (`YYYY-MM-DD`), not a datetime. The `upcoming_match` fixture filters by date, which means two matches on the same day are indistinguishable by schedule. If the data model is not updated, test data selection will remain imprecise.
