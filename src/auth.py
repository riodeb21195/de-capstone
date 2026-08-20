import requests
from datetime import datetime, timedelta

from config import OPENSKY_TOKEN_URL, OPENSKY_CLIENT_ID, OPENSKY_CLIENT_SECRET

TOKEN_REFRESH_MARGIN_SECONDS = 30


class TokenManager:
    def __init__(self):
        self.token = None
        self.expires_at = None

    def get_token(self) -> str:
        if self.token and self.expires_at and datetime.now() < self.expires_at:
            return self.token
        return self._refresh()

    def _refresh(self) -> str:
        response = requests.post(
            OPENSKY_TOKEN_URL,
            data={
                "grant_type": "client_credentials",
                "client_id": OPENSKY_CLIENT_ID,
                "client_secret": OPENSKY_CLIENT_SECRET,
            },
        )
        response.raise_for_status()
        data = response.json()

        self.token = data["access_token"]
        expires_in = data.get("expires_in", 1800)
        self.expires_at = datetime.now() + timedelta(seconds=expires_in - TOKEN_REFRESH_MARGIN_SECONDS)

        print("[auth] Neues Access Token erhalten")
        return self.token

    def headers(self) -> dict:
        return {"Authorization": f"Bearer {self.get_token()}"}


token_manager = TokenManager()