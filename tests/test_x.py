from app.schemas.voice_actor import Actor
from app.services.x import get_x_username, media_lookup, tweet_to_post


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
