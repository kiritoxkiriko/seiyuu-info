from app.services.storage import LocalImageStorage


def test_local_image_storage_builds_stable_media_path(tmp_path):
    storage = LocalImageStorage(tmp_path, public_prefix="/media")

    path = storage.path_for("aoki-hina", "https://example.com/photos/profile.jpg")

    assert path.public_url.startswith("/media/aoki-hina/")
    assert path.file_path.parent == tmp_path / "aoki-hina"
    assert path.file_path.name.endswith(".jpg")
