import requests
from app.blogger.token_manager import refresh_blogger_token

BLOGGER_API = "https://www.googleapis.com/blogger/v3"

def publish_post(token, refresh_token, blog_id, title, html):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    payload = {
        "kind": "blogger#post",
        "title": title,
        "content": html,
    }

    res = requests.post(
        f"{BLOGGER_API}/blogs/{blog_id}/posts/",
        headers=headers,
        json=payload,
    )

    # 🔁 If token expired → refresh & retry once
    if res.status_code == 401:
        new_token = refresh_blogger_token(refresh_token)

        headers["Authorization"] = f"Bearer {new_token}"
        res = requests.post(
            f"{BLOGGER_API}/blogs/{blog_id}/posts/",
            headers=headers,
            json=payload,
        )

        if res.status_code >= 400:
            raise Exception("Blogger publish failed after refresh")

        return new_token, res.json()["url"]

    if res.status_code >= 400:
        raise Exception(res.text)

    return token, res.json()["url"]
