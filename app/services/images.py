from pathlib import Path

from app.schemas.voice_actor import Actor, Photo
from app.services.storage import LocalImageStorage


async def localize_actor_images(actor: Actor, settings) -> Actor:
    storage = LocalImageStorage(Path(settings.media_root), settings.media_public_prefix)
    official_photo = await localize_photo(actor.id, actor.official_photo, storage)
    gallery = [await localize_photo(actor.id, photo, storage) for photo in actor.gallery]
    return actor.model_copy(update={"official_photo": official_photo, "gallery": gallery})


async def localize_actors_images(actors: list[Actor], settings) -> list[Actor]:
    return [await localize_actor_images(actor, settings) for actor in actors]


async def localize_photo(owner_id: str, photo: Photo, storage: LocalImageStorage) -> Photo:
    if photo.url.startswith("/"):
        return photo
    try:
        stored = await storage.store_remote_image(owner_id, photo.url)
    except Exception as error:
        print(f"  image fallback: {owner_id} {error.__class__.__name__}")
        return photo
    return photo.model_copy(update={"url": stored.public_url, "source": f"{photo.source} / local"})
