import asyncio
from datetime import date

import httpx

from app.schemas.voice_actor import Actor
from app.services.x import fetch_x_posts, get_x_username, media_lookup, tweet_to_post, x_start_time, x_timeline_params


def test_get_x_username_from_actor_social_links():
    actor = Actor.model_validate(
        {
            "id": "aoki-hina",
            "name": "青木陽菜",
            "kana": "あおき ひな",
            "romanized": "Hina Aoki",
            "agency": "響",
            "birthday": "1月5日",
            "birthplace": "宮城県",
            "profile_url": "https://hibiki-cast.jp/hibiki_f/aoki_hina/",
            "officialPhoto": {
                "url": "https://example.com/aoki.jpg",
                "alt": "青木陽菜",
                "source": "example",
            },
            "gallery": [],
            "specialties": [],
            "hobbies": [],
            "roles": [],
            "socialLinks": [
                {"platform": "x", "label": "X", "url": "https://x.com/aoki__hina"},
            ],
        }
    )

    assert get_x_username(actor) == "aoki__hina"


def test_tweet_to_post_maps_photo_and_preview_media_urls():
    payload = {
        "includes": {
            "media": [
                {"media_key": "3_1", "type": "photo", "url": "https://pbs.twimg.com/media/photo.jpg"},
                {"media_key": "7_2", "type": "video", "preview_image_url": "https://pbs.twimg.com/media/preview.jpg"},
            ]
        }
    }
    tweet = {
        "id": "123",
        "created_at": "2026-05-12T08:00:00Z",
        "text": "photo tweet",
        "attachments": {"media_keys": ["3_1", "7_2"]},
    }

    post = tweet_to_post("aoki-hina", "aoki__hina", tweet, media_lookup(payload))

    assert [str(url) for url in post.media_urls] == [
        "https://pbs.twimg.com/media/photo.jpg",
        "https://pbs.twimg.com/media/preview.jpg",
    ]
    assert post.detail_text == "photo tweet"


def test_x_start_time_uses_latest_seen_post_plus_one_second(monkeypatch):
    monkeypatch.setattr("app.services.date_window.date", FixedDate)

    assert x_start_time("2026-05-12T08:00:00+09:00", past_days=183) == "2026-05-11T23:00:01Z"


def test_x_start_time_respects_fetch_window_when_latest_seen_is_old(monkeypatch):
    monkeypatch.setattr("app.services.date_window.date", FixedDate)

    assert x_start_time("2025-01-01T00:00:00Z", past_days=183) == "2025-11-11T00:00:00Z"


def test_x_timeline_params_caps_page_size_and_sets_next_token():
    params = x_timeline_params("2026-05-01T00:00:00Z", 500, "next-page")

    assert params["max_results"] == "100"
    assert params["pagination_token"] == "next-page"


def test_fetch_x_posts_paginates_until_limit(monkeypatch):
    actor = make_actor()
    requested_params = []

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/users/by/username/aoki__hina"):
            return httpx.Response(200, json={"data": {"id": "user-1"}})
        requested_params.append(dict(request.url.params))
        if request.url.params.get("pagination_token") == "page-2":
            return httpx.Response(
                200,
                json={
                    "data": [
                        {
                            "id": "2",
                            "created_at": "2026-05-02T00:00:00Z",
                            "text": "second",
                        }
                    ],
                    "meta": {},
                },
            )
        return httpx.Response(
            200,
            json={
                "data": [
                    {
                        "id": "1",
                        "created_at": "2026-05-03T00:00:00Z",
                        "text": "first",
                    }
                ],
                "meta": {"next_token": "page-2"},
            },
        )

    class MockAsyncClient(httpx.AsyncClient):
        def __init__(self, *args, **kwargs):
            super().__init__(transport=httpx.MockTransport(handler), headers=kwargs.get("headers"))

    monkeypatch.setattr("app.services.x.httpx.AsyncClient", MockAsyncClient)

    posts = asyncio.run(fetch_x_posts(actor, "token", limit=2, past_days=183))

    assert [post.id for post in posts] == ["x-1", "x-2"]
    assert requested_params[1]["pagination_token"] == "page-2"


class FixedDate(date):
    @classmethod
    def today(cls):
        return cls(2026, 5, 13)


def make_actor() -> Actor:
    return Actor.model_validate(
        {
            "id": "aoki-hina",
            "name": "青木陽菜",
            "kana": "あおき ひな",
            "romanized": "Hina Aoki",
            "agency": "響",
            "birthday": "1月5日",
            "birthplace": "宮城県",
            "profile_url": "https://hibiki-cast.jp/hibiki_f/aoki_hina/",
            "officialPhoto": {
                "url": "https://example.com/aoki.jpg",
                "alt": "青木陽菜",
                "source": "example",
            },
            "gallery": [],
            "specialties": [],
            "hobbies": [],
            "roles": [],
            "socialLinks": [{"platform": "x", "label": "X", "url": "https://x.com/aoki__hina"}],
        }
    )
