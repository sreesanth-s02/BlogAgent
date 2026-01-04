import requests
from app.core.config import UNSPLASH_API_KEY

def search_unsplash(query: str, per_page: int = 6):
    url = "https://api.unsplash.com/search/photos"
    res = requests.get(
        url,
        params={
            "query": query,
            "per_page": per_page,
            "orientation": "landscape"
        },
        headers={
            "Authorization": f"Client-ID {UNSPLASH_API_KEY}"
        }
    )

    data = res.json()
    return [
        {
            "url": img["urls"]["regular"],
            "author": img["user"]["name"]
        }
        for img in data.get("results", [])
    ]
