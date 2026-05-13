import asyncio

import httpx

from app.services.storage import LocalImageStorage


def test_local_image_storage_builds_stable_media_path(tmp_path):
    storage = LocalImageStorage(tmp_path, public_prefix="/media")

    path = storage.path_for("aoki-hina", "https://example.com/photos/profile.jpg")

    assert path.public_url.startswith("/media/aoki-hina/")
    assert path.file_path.parent == tmp_path / "aoki-hina"
    assert path.file_path.name.endswith(".jpg")


def test_local_image_storage_downloads_remote_image(tmp_path):
    storage = LocalImageStorage(tmp_path, public_prefix="/media")
    transport = httpx.MockTransport(lambda request: httpx.Response(200, content=b"image-bytes"))

    async def run():
        async with httpx.AsyncClient(transport=transport) as client:
            return await storage.store_remote_image("aoki-hina", "https://example.com/profile.jpg", client)

    path = asyncio.run(run())

    assert path.public_url.startswith("/media/aoki-hina/")
    assert path.file_path.read_bytes() == b"image-bytes"
