from urllib.parse import urlparse

import httpx

from app.schemas.voice_actor import Actor, SnsPost
from app.services.date_window import past_days_start_iso
from app.services.sns import filter_relevant_posts


X_API_BASE_URL = "https://api.x.com/2"


def get_x_username(actor: Actor) -> str | None:
    for link in actor.social_links:
        if link.platform != "x":
            continue
        path = urlparse(str(link.url)).path.strip("/")
        return path.split("/")[0] if path else None
    return None


async def fetch_x_posts(actor: Actor, bearer_token: str, limit: int = 20, past_days: int = 183) -> list[SnsPost]:
    username = get_x_username(actor)
    if not username:
        return []

    headers = {"Authorization": f"Bearer {bearer_token}"}
    async with httpx.AsyncClient(timeout=12.0, headers=headers) as client:
        user_id = await fetch_x_user_id(client, username)
        response = await client.get(
            f"{X_API_BASE_URL}/users/{user_id}/tweets",
            params={
                "exclude": "retweets,replies",
                "max_results": str(limit),
                "start_time": past_days_start_iso(past_days),
                "tweet.fields": "created_at,attachments",
                "expansions": "attachments.media_keys",
                "media.fields": "media_key,type,url,preview_image_url",
            },
        )
        response.raise_for_status()

    payload = response.json()
    media_by_key = media_lookup(payload)
    posts = [tweet_to_post(actor.id, username, item, media_by_key) for item in payload.get("data", []) if item.get("created_at")]
    return filter_relevant_posts(posts)


async def fetch_x_user_id(client: httpx.AsyncClient, username: str) -> str:
    response = await client.get(f"{X_API_BASE_URL}/users/by/username/{username}")
    response.raise_for_status()
    return response.json()["data"]["id"]


def media_lookup(payload: dict) -> dict[str, str]:
    media_items = payload.get("includes", {}).get("media", [])
    result: dict[str, str] = {}
    for media in media_items:
        url = media.get("url") or media.get("preview_image_url")
        if media.get("media_key") and url:
            result[media["media_key"]] = url
    return result


def tweet_to_post(actor_id: str, username: str, item: dict, media_by_key: dict[str, str]) -> SnsPost:
    media_urls = [
        media_by_key[key]
        for key in item.get("attachments", {}).get("media_keys", [])
        if key in media_by_key
    ]
    text = item.get("text", "")
    return SnsPost(
        id=f"x-{item['id']}",
        actorId=actor_id,
        platform="x",
        postedAt=item.get("created_at", ""),
        text=text,
        detailText=text,
        url=f"https://x.com/{username}/status/{item['id']}",
        kind="original",
        mediaUrls=media_urls,
    )
