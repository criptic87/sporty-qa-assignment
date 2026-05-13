from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class MatchesPage:
    URL = "https://qae-assignment-tau.vercel.app/?user-id=candidate-W3qHs1Kb6P"

    # Header
    HEADER_BALANCE = (By.ID, "header-balance")

    # Bet slip
    STAKE_INPUT = (By.ID, "bet-slip-stake-input")
    POTENTIAL_PAYOUT = (By.ID, "bet-slip-potential-payout")
    PLACE_BET_BUTTON = (By.ID, "bet-slip-place-bet")

    # Success receipt modal
    SUCCESS_MODAL = (By.ID, "modal-success")
    RECEIPT_STAKE = (By.ID, "modal-success-stake")
    RECEIPT_ODDS = (By.ID, "modal-success-odds")
    RECEIPT_PAYOUT = (By.ID, "modal-success-payout")
    RECEIPT_CLOSE = (By.ID, "modal-success-close") 

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def load(self):
        self.driver.get(self.URL)
        self.wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "[id^='odds-'][id$='-home']")
        ))
        return self

    def get_balance(self):
        text = self.wait.until(
            EC.visibility_of_element_located(self.HEADER_BALANCE)
        ).text
        # Full element text includes icon label: "account_balance_wallet\nBalance: €120.00"
        # Split on "Balance:" to isolate the numeric part, then strip currency symbol
        raw = text.split("Balance:")[-1].replace("€", "").strip()
        return float(raw)

    def click_home_for_match(self, match_id):
        locator = (By.ID, f"odds-{match_id}-home")
        self.wait.until(EC.element_to_be_clickable(locator)).click()

    def enter_stake(self, stake):
        field = self.wait.until(EC.visibility_of_element_located(self.STAKE_INPUT))
        field.clear()
        field.send_keys(str(stake))

    def potential_payout_text(self):
        return self.wait.until(
            EC.visibility_of_element_located(self.POTENTIAL_PAYOUT)
        ).text

    def place_bet(self):
        self.wait.until(EC.element_to_be_clickable(self.PLACE_BET_BUTTON)).click()

    def wait_for_success_receipt(self):
        self.wait.until(EC.visibility_of_element_located(self.SUCCESS_MODAL))

    def receipt_values(self):
        return {
            "stake": self.driver.find_element(*self.RECEIPT_STAKE).text,
            "odds": self.driver.find_element(*self.RECEIPT_ODDS).text,
            "payout": self.driver.find_element(*self.RECEIPT_PAYOUT).text,
        }

    def close_receipt(self):
        self.wait.until(EC.element_to_be_clickable(self.RECEIPT_CLOSE)).click()
        self.wait.until(EC.invisibility_of_element_located(self.SUCCESS_MODAL))
