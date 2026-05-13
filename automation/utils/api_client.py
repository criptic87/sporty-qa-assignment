import requests


class BettingAPIClient:
    def __init__(self, base_url, user_id):
        self.base_url = base_url
        self.headers = {
            "x-user-id": user_id, 
            "Content-Type": "application/json",
        }

    def get_matches(self):
        return requests.get(
            f"{self.base_url}/api/matches", 
            headers=self.headers, 
            timeout=10
            )

    def get_balance(self):
        return requests.get(
            f"{self.base_url}/api/balance", 
            headers=self.headers, 
            timeout=10)

    def place_bet(self, match_id, selection, stake):
        return requests.post(
            f"{self.base_url}/api/place-bet",
            headers=self.headers,
            json={"matchId": match_id, "selection": selection, "stake": stake},
            timeout=10
        )

    def reset_balance(self):
        return requests.post(
            f"{self.base_url}/api/reset-balance", 
            headers=self.headers,
            timeout=10
        )