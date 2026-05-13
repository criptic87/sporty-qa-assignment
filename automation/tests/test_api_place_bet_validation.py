import pytest


@pytest.mark.api
def test_place_bet_rejects_stake_above_maximum(api_client, upcoming_match):
    """
    API test verifying the stake maximum business rule (€100.00). Chosen 
    because stake limits are a core financial constraint that must be
    validated at the API layer independently of UI controls. Faster than 
    testing through the browser, and confirms the backend cannot be bypassed 
    with higher stake sent directly to the API.
    """
    balance_before = api_client.get_balance().json()["balance"]

    response = api_client.place_bet(
        match_id=upcoming_match["id"],
        selection="HOME",
        stake=100.01,
    )

    assert response.status_code == 422
    assert api_client.get_balance().json()["balance"] == balance_before
