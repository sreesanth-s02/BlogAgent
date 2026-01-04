import requests
from app.core.config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET

def refresh_blogger_token(refresh_token: str) -> str:
    res = requests.post(
        "https://oauth2.googleapis.com/token",
        data={
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        },
    )

    data = res.json()

    if "access_token" not in data:
        raise Exception("Failed to refresh Blogger token")

    return data["access_token"]
