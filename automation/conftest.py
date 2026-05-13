import pytest
from datetime import date
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from utils.api_client import BettingAPIClient

BASE_URL = "https://qae-assignment-tau.vercel.app"
USER_ID = "candidate-W3qHs1Kb6P"


@pytest.fixture(scope="session")
def api_client():
    return BettingAPIClient(BASE_URL, USER_ID)


@pytest.fixture(scope="session")
def upcoming_match(api_client):
    """
    Returns the first upcoming match from the API.
    Filters out past matches to avoid testing on top of BUG-003
    (past matches are bettable when they shouldn't be).
    """
    today = date.today().isoformat()  # same format the API uses - "YYYY-MM-DD"
    matches = api_client.get_matches().json()
    upcoming = [m for m in matches if m["kickoffDate"] >= today]
    assert upcoming, "No upcoming matches found — cannot run tests"
    return upcoming[0]


@pytest.fixture(scope="function")
def driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    d = webdriver.Chrome(options=options)
    d.implicitly_wait(0)
    yield d
    d.quit()


@pytest.fixture(autouse=True)
def reset_balance(api_client):
    """
    Resets balance before every test.
    Note: API responds with 125.50 but persists 120.00 (known bug BUG-005).
    Fixture verifies actual persisted state, not the response value.
    """
    api_client.reset_balance()
    actual = api_client.get_balance().json()["balance"]
    assert actual == 120.0, f"Balance reset failed. Expected 120.0, got {actual}"
    yield
