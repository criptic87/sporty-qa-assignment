# Test Plan — Single Bet Placement
**Application:** Sports Betting QA — `https://qae-assignment-tau.vercel.app`  
**Feature:** Single Bet Placement  
**Prepared by:** Andrei Ciorogar  
**Date:** 2026-05-11

---

## Scope

**In scope:** Match list display, bet slip interaction, stake validation, bet placement flow, success receipt, error modal, balance deduction, filter behavior.  
**Out of scope:** Live betting, accumulator/multi-bets, other sports, mobile layout

---

## Scenario Summary

| ID    | Title                                        | Priority |
|-------|----------------------------------------------|----------|
| TS001 | Place a single bet, happy path               | Critical |
| TS002 | Payout calculation and balance accuracy      | Critical |
| TS003 | Minimum stake Boundary                       | High     |
| TS004 | Stake Exceeds Available Balance              | High     |
| TS005 | Active Selection Replacement                 | High     |
| TS006 | Bet Placement on Past Match                  | High     |

---

### TS001 — Place a single bet, happy path

**Priority:** Critical

**Risk Rationale:**  
This is the path the product is built around. If it doesn't work, nothing else matters; 
balance, receipt, and history all hang off it. First thing I'd run on every regression cycle.

**Preconditions:**
- Valid `user-id`
- Balance reset via `POST /api/reset-balance`
- At least one upcoming match is visible in the match list

**Steps:**
1. Navigate to the application with a valid `user-id`
2. Note the header balance
3. Pick an upcoming match and click its Home (1) odds button
4. Verify the bet slip panel appears on the right side
5. Verify the bet slip shows: correct match name, "Match Winner: Home", and correct odds
6. Enter €10.00 as stake in the input field
7. Verify the Potential Payout updates to `stake × odds`
8. Click **Place Bet**
9. Verify the button enters a loading/in-progress state ("Placing...")
10. Verify the success receipt modal appears

**Expected Result:**  
The receipt modal displays:
- A non-empty Bet ID
- Correct match name (home team vs away team)
- Correct selection (Home)
- Stake: €10.00
- Odds: matching the value shown before placement
- Potential Payout: `10.00 × odds` (correct to 2 decimal places)
- A valid placement timestamp
The header balance decreases by exactly €10.00.  
Closing the receipt returns the user to the main view with an empty bet slip.

---

### TS002 — Payout Calculation and Balance Accuracy

**Priority:** Critical

**Risk Rationale:**  
Incorrect payout calculation is a major financial problem. In a betting market,even tiny rounding errors
(like a fraction of a penny) add up over time. This scenario verifies that `payout = stake × odds` is 
applied correctly and that the balance deduction is exact, not approximate.

**Preconditions:**
- Balance reset via `POST /api/reset-balance`
- Starting balance confirmed via `GET /api/balance`

**Steps:**
1. Note the starting balance via `GET /api/balance`
2. Select a match and note the exact odds displayed on the button
3. Enter a stake that produces a result with more than two decimals (e.g. €7.33 at odds 2.20 → expected payout: €16.126)
4. Verify the Potential Payout in the bet slip matches `round(stake × odds, 2)`
5. Click **Place Bet**
6. On the receipt, note: stake, odds, and payout
7. Verify receipt payout matches `round(stake × odds, 2)`
8. Call `GET /api/balance` and note the new balance

**Expected Result:**  
- Bet slip payout = receipt payout = `round(stake × odds, 2)`
- New balance = starting balance − stake (exact, no rounding on the deduction)
- No discrepancy between the slip, the receipt, and the API balance
- €16.126 should round to €16.13 (half-up), not truncate to €16.12.

---

### TS003 — Minimum stake Boundary 

**Priority:** High

**Risk Rationale:**  
The spec contradicts itself: the business rules table says min stake is €1.00, the validation rules table says €1.01. 
So either the spec is wrong or one of the rules doesn't match the implementation. Worth clarifying before writing 
automation against either rule.

**Preconditions:**
- A selection is active in the bet slip

**Steps:**
1. Enter stake €0.99 — record the error message shown
2. Clear and enter stake €1.00, try to place the bet and record the outcome
3. Clear and enter stake €1.01, try to place the bet and record the outcome
4. Note the exact error message copy at each boundary

**Expected Result (per spec):**  
- €0.99: rejected with a min stake error
- €1.00: ambiguous. Business rules say valid, validation rules say invalid. Document the actual behaviour.
- €1.01: accepted
The error copy in the spec reads "Minimum stake is €1.00." If the app rejects €1.00 with that same message, the message is also wrong.

---

### TS004 — Stake Exceeds Available Balance

**Priority:** High

**Risk Rationale:**  
Allowing a bet above the user's available balance would represent a credit
risk, the platform accepting a liability it cannot cover from the user's
funds. This is a business-critical validation at both the UI and API layer.
The validation must be enforced consistently: a UI-only check is insufficient
if the API accepts an over-balance request directly.

**Preconditions:**
- Starting balance is known (e.g. €120.00 after reset)
- A selection is active in the bet slip

**Steps:**
1. Enter stake equal to the exact current balance (e.g. €120.00) and note outcome
2. Enter stake €120.01 (one cent over balance) and note the error message shown
3. Enter stake €200.00 (well over balance) and note the error message shown
4. Via API (`POST /api/place-bet`), submit a bet with `stake` exceeding the balance and note the response

**Expected Result:**  
- Stake equal to balance: should be accepted (no rule prohibits this)
- Stake exceeding balance: rejected with an "insufficient balance" message at UI layer
- API: returns 422 with a clear validation error when stake exceeds balance
- Error messages match the spec copy: *"Insufficient balance"*

---

### TS005 — Active Selection Replacement

**Priority:** High

**Risk Rationale:**  
The spec states: *"Selecting a new odds button replaces the previous selection."*
If the bet slip retains a stale selection after a new one is chosen, the user
could place a bet on an unintended outcome. In a sportsbook context, a user
selecting the wrong outcome due to a UI state bug is both a UX failure and a
potential dispute trigger.

**Preconditions:**
- Match list contains at least two visible matches

**Steps:**
1. Click the Home (1) button on Match A and verify it appears in the bet slip
2. Click the Draw (X) button on the same Match A and verify the slip updates to Draw
3. Click the Home (1) button on a different Match B and verify the slip updates to Match B / Home
4. Verify at no point does the slip show more than one active selection
5. Verify the previously highlighted odds button on Match A is no longer active/highlighted

**Expected Result:**  
At each step, the bet slip contains exactly one selection reflecting the most
recently clicked odds button. Previously selected buttons return to their
default (unselected) visual state. The slip never accumulates multiple
selections.

---

### TS006 — Bet Placement on Past Match

**Priority:** High

**Risk Rationale:**  
During exploration I noticed past matches show up in the list when the date filter is 
cleared, and the app doesn't seem to stop you from picking odds on them. If that holds
up at the API too, it's a serious bug because the outcome is already known.

**Preconditions:**
- Date filter is cleared
- A match with a past kickoff date is visible

**Steps:**
1. Remove the date filter so all matches are visible
2. Find a match with a kickoff date in the past
3. Click an odds button on that match
4. Verify if the bet slip accepts the selection
5. If the slip accepts it, enter a valid stake and try to place the bet
6. Check the API response

**Expected Result:**  
Past matches shouldn't appear in the bettable list, or the app should reject placement 
with a clear error. API should refuse bets on past match IDs.

**Actual Behavior (observed during exploration):**  
Past matches are visible without a date filter and the bet placement flow
proceeds without restriction. See bug report BUG-003 for full details.
