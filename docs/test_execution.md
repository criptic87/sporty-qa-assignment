# Test Execution Report — Single Bet Placement

**Date:** 2026-05-12  
**Tester:** Andrei Ciorogar  
**Environment:** https://qae-assignment-tau.vercel.app  
**User ID:** candidate-W3qHs1Kb6P  
**Browser:** Chrome 148 (Desktop)

---

## Testing Limitations

### Error Modal (spec section 2.5) — Unreachable via UI

The error state could not be triggered through normal UI interaction during this test session. All paths to a server-side rejection are currently blocked:

- **Stake out of range** : the Place Bet button is disabled client-side for any stake below €1.00 or above €100.00, so the API is never called
- **Insufficient balance** : BUG-002: the API accepts bets that exceed the available balance instead of returning a `422`, so no error modal is shown
- **Past matches** : BUG-003: the API accepts bets on past matches instead of returning a `422`

---

## Execution Results

| Scenario | Title                                       | Result | Notes                                                      |
|----------|---------------------------------------------|--------|------------------------------------------------------------|
| TS001    | Full Bet Placement — Happy Path             | FAIL   | → BUG-001 (High), BUG-002 (Critical), BUG-008 (Low)        |
| TS002    | Payout Calculation and Balance Accuracy     | FAIL   | → BUG-001                                                  |
| TS003    | Stake Minimum Boundary                      | PASS   | App enforces €1.00 min correctly; spec inconsistency noted |

---

## Bug Reports

### BUG-001 — Receipt screen displays incorrect Potential Payout after successful bet placement

**Severity:** High  
**Found during:** TS002 — Payout Calculation and Balance Accuracy

**Reproduction Steps:**
1. Navigate to the application
2. Select a match with odds different from `2.00` (example: `2.45`)
3. Enter a stake amount in the Bet Slip (example: `€10.00`)
4. Verify the Potential Payout displayed in the bet slip (`€24.50`)
5. Click **Place Bet**
6. Observe the Potential Payout value displayed in the success receipt modal

**Expected:** The receipt modal should display the same payout value calculated in the bet slip and returned by the API response.
- Stake: `€10.00`
- Odds: `2.45`
- Expected Payout: `€24.50`

**Actual:** The receipt modal displays an incorrect payout value (`€20.00`), inconsistent with:
- the bet slip calculation
- the selected odds
- the API response payload

The issue appears to calculate payout using a fixed multiplier of `2.00` regardless of the actual odds.

**Business Impact:** Users are shown incorrect expected winnings after placing a bet. This is a financial display defect that directly undermines trust in the platform and may generate user complaints and disputes.

**Evidence:** `screenshots/bug-001-incorrect_potential_payout.png`

---

### BUG-002 — Stale balance header allows over-balance bets; API accepts bets into negative balance

**Severity:** Critical  
**Found during:** TS001 — Full Bet Placement — Happy Path / TS002 — Payout Calculation and Balance Accuracy

**Reproduction Steps:**
1. Navigate to the application with a valid `user-id`
2. Confirm starting balance in the header (e.g. `€120.00`)
3. Select an upcoming match and enter a stake of `€100.00` — place the bet
4. Observe the success receipt, then close it
5. Observe the balance in the header
6. Without refreshing, enter a stake of `€100.00` again and place a second bet
7. Observe the receipt and note whether it shows success or failure
8. Call `GET /api/balance` and note the returned value
9. Refresh the page and observe the header balance

**Expected:**
- After step 3, the header balance should immediately update to `€20.00`
- The UI should use the updated balance for stake validation on any subsequent bet
- A `€100.00` stake on step 6 should be blocked at the UI layer (`Insufficient balance`) since only `€20.00` remains
- The API should also reject the second bet with a `422` validation error per the spec rule: *"Stake Must not exceed available balance — UI + API"*

**Actual:**
- After step 3, the header balance remains `€120.00` — it does not update
- The UI allows a second `€100.00` stake because it validates against the stale `€120.00` display value
- The second bet is accepted by the API with HTTP `200` — a success receipt is shown
- `GET /api/balance` returns a negative value (e.g. `-€80.00`), confirming the API processed both bets and the account balance is now negative
- Refreshing the page reveals the negative balance in the header, at which point the UI correctly blocks further betting

**Business Impact:** Users can place bets they cannot afford. The API accepts stakes that exceed the available balance without returning a validation error, resulting in a negative account balance being persisted. This is a financial integrity failure — the platform is effectively extending unsecured credit to users. In production, this would represent a direct monetary loss for the operator.

**Evidence:** Screenshots bug-002-01 through bug-002-04 in /screenshots folder.
Starting balance €120.00. Two consecutive €100.00 bets both returned HTTP 200.
GET /api/balance returned -€80.00 (bug-002-03). Negative balance confirmed in
header after refresh (bug-002-04)

---

### BUG-003 — Past/completed matches are visible in the match list and bets can be placed on them

**Severity:** High  
**Found during:** Exploratory testing / TS006 — Bet Placement on Past Match

**Reproduction Steps:**
1. Navigate to the application with no date filter applied (or clear any active date filter)
2. Scroll through the match list and identify a match with a `kickoffDate` before today's date
3. Click an odds button on the past match
4. Observe whether the bet slip accepts the selection
5. Enter a valid stake (e.g. `€10.00`) and click **Place Bet**
6. Observe the API response and the balance change

**Expected:** Per the feature specification: *"Event Type: Upcoming/Pre-match events only (no live betting)."* Past matches should either not be returned by `GET /api/matches`, or the application should prevent bet placement on them. The API should return a `422` validation error for bets on past match IDs.

**Actual:** Past matches are visible in the match list with no visual indicator that they are expired. Clicking their odds buttons adds them to the bet slip normally. Placing a bet on a past match returns HTTP `200` — the stake is deducted and a success receipt is displayed. No validation occurs at either the UI or API layer.

**Business Impact:** Users can place bets on matches whose outcomes are already known. This is a fundamental integrity violation that creates direct financial risk for the operator and can be exploited intentionally.

**Evidence:** Screenshots bug-003-01 and bug-003-02 in /screenshots folder.
Match used: Manchester Utd vs Chelsea, kickoffDate 2026-02-27 (confirmed via
GET /api/matches response). Test executed 2026-05-12. Bet accepted with HTTP 200,
balance deducted normally.

---

### BUG-004 — Match kickoff time is missing from match cards (date only shown)

**Severity:** Low  
**Found during:** Exploratory testing

**Reproduction Steps:**
1. Navigate to the application
2. Observe the date/time label displayed on any match card in the list

**Expected:** Per the feature specification section 2.1, each match should display a *"kickoff date/time label"* (e.g. `Fri 09 May, 15:00`).

**Actual:** Only the date is displayed (e.g. `Fri 09 May`). No time component is shown. This is consistent with the API: `GET /api/matches` returns `kickoffDate` as a `YYYY-MM-DD` string with no time — so the missing time originates from the data model, not just the display layer.

**Business Impact:** Users cannot distinguish between multiple matches on the same day by kickoff time, limiting informed betting decisions on same-day fixtures.

**Evidence:** UI and `GET /api/matches` API response both show date only. No time component is returned or displayed.

---

### BUG-005 — POST /api/reset-balance responds with a different balance than it actually persists

**Severity:** High  
**Found during:** Test setup / Exploratory API testing

**Reproduction Steps:**
1. Call `POST /api/reset-balance` with a valid `x-user-id` header
2. Record the `balance` value in the response body
3. Immediately call `GET /api/balance` with the same `x-user-id`
4. Compare the two values

**Expected:** Per the feature specification: *"Response body and persisted state must be consistent after reset."* The domain context also states: *"Balance — The user's available funds. Starts at €125.50."* Both the reset response and a subsequent balance query should return `125.50`.

**Actual:** `POST /api/reset-balance` responds with `balance: 125.5`, but `GET /api/balance` immediately after returns `balance: 120.0`. The endpoint reports resetting to `€125.50` but actually persists `€120.00`.

**Business Impact:** Tests and automation relying on the reset response value will operate with incorrect assumptions about the account state, potentially masking balance-related defects. The inconsistency also directly violates the explicit spec contract for this endpoint.

**Evidence:** `screenshots/bug-005-wrong-api-balance-response.png`

---

### BUG-006 — Match list count header always shows total match count regardless of active filters

**Severity:** Medium  
**Found during:** Exploratory testing

**Reproduction Steps:**
1. Navigate to the application and note the match count shown in the list header (e.g. `"103 matches"`)
2. Apply a date filter for a single specific day and observe the count label
3. Remove the date filter; apply an odds range filter and observe the count label
4. Apply a combination of both filters and observe the count label

**Expected:** The match count label should update to reflect the number of matches currently visible after filters are applied. For example, if a date filter reduces the visible list to 4 matches, the label should read `"4 matches"`.

**Actual:** The count label always shows the unfiltered total (e.g. `"103 matches"`) regardless of which filters are active. The match list itself filters correctly, only the count label is incorrect.

**Business Impact:** Users receive misleading information about the number of available matches when filtering, reducing confidence in the filter functionality and the accuracy of the interface.

**Evidence:** `screenshots/bug-006-wrong-total-matches-number.png`

---

### BUG-007 — API returns `"USD"` as currency instead of `"EUR"` for place-bet

**Severity:** Medium  
**Found during:** Exploratory API testing

**Reproduction Steps:**
1. Call `GET /api/balance` with a valid `x-user-id` header
2. Check the `currency` field in the response body
3. Call `POST /api/place-bet` with valid parameters
4. Check the `currency` field in the `200` response

**Expected:** Per the feature specification section 3 (Business Rules): *"Currency: EUR (€)."* The response schemas for `POST /api/place-bet` specify `currency: "EUR"`.

**Actual:** Endpoint return `currency: "USD"`.

Example response:
- `POST /api/place-bet` → `{ ..., "balance": 110.0, "currency": "USD" }`

**Business Impact:** Any downstream integration, display layer, or financial reporting system consuming the `currency` field would process or display the wrong currency. In a regulated betting environment, incorrect currency metadata creates compliance and financial reporting risk.

**Evidence:** `screenshots/bug-007-place-bet-returns-USD-in-response.png`

---

### BUG-008 — Success receipt modal displays teams in Away vs Home order instead of Home vs Away

**Severity:** Low  
**Found during:** TS001 — Full Bet Placement — Happy Path

**Reproduction Steps:**
1. Navigate to the application
2. Select any match from the list (e.g. `Real Madrid vs Barcelona`)
3. Note the match name displayed on the match card: `Home Team vs Away Team`
4. Enter a valid stake and click **Place Bet**
5. Observe the match name displayed in the success receipt modal

**Expected:** The receipt modal should display the match in the same `Home vs Away` order as the match card and the API response (which lists `homeTeam` before `awayTeam`).

**Actual:** The success receipt modal displays the teams in reverse order — `Away Team vs Home Team`. For example, if the match card shows `Real Madrid vs Barcelona`, the receipt shows `Barcelona vs Real Madrid`.

**Business Impact:** Low risk financially, but the reversed team order in the receipt is inconsistent with every other representation of the match in the UI and the API. For a user reviewing their bet confirmation, seeing the teams in a different order than expected undermines trust in the receipt's accuracy — especially relevant for users who bet on the away team and might misread the displayed selection.

**Evidence:** Screenshots bug-008-01 and bug-008-02 in /screenshots folder.
