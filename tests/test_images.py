import asyncio
from pathlib import Path
from types import SimpleNamespace

import httpx

from app.schemas.voice_actor import Actor
from app.services.images import localize_actor_images
from app.services.storage import LocalImageStorage


def test_localize_actor_images_rewrites_profile_and_gallery_urls(tmp_path, monkeypatch):
    actor = make_actor()
    transport = httpx.MockTransport(lambda request: httpx.Response(200, content=b"image"))
    original_store_remote_image = LocalImageStorage.store_remote_image

    async def fake_store_remote_image(self, owner_id, source_url, client=None):
        async with httpx.AsyncClient(transport=transport) as mock_client:
            return await original_store_remote_image(self, owner_id, source_url, mock_client)

    monkeypatch.setattr(LocalImageStorage, "store_remote_image", fake_store_remote_image)

    localized = asyncio.run(
        localize_actor_images(
            actor,
            SimpleNamespace(media_root=str(tmp_path), media_public_prefix="/media"),
        )
    )

    assert localized.official_photo.url.startswith("/media/aoki-hina/")
    assert localized.gallery[0].url.startswith("/media/aoki-hina/")
    assert Path(tmp_path / "aoki-hina").exists()


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
            "gallery": [
                {
                    "url": "https://example.com/aoki-gallery.jpg",
                    "alt": "青木陽菜 gallery",
                    "source": "example",
                }
            ],
            "specialties": [],
            "hobbies": [],
            "roles": [],
            "socialLinks": [{"platform": "x", "label": "X", "url": "https://x.com/aoki__hina"}],
        }
    )
