import asyncio
from types import SimpleNamespace

from app.core.config import get_settings
from app.schemas.voice_actor import Actor, Event, SnsPost
from app.services.database import DataStore
from scripts import sync_data


def test_sync_data_is_incremental_when_fetch_returns_empty(tmp_path, monkeypatch):
    db_url = f"sqlite:///{tmp_path / 'nsy.sqlite3'}"
    actor = make_actor()
    event = Event(
        id="event-existing",
        actorId=actor.id,
        title="Existing Event",
        date="2026-06-01",
        category="live",
        venue="Tokyo",
        url="https://example.com/event-existing",
        source="eventernote",
    )
    post = SnsPost(
        id="x-existing",
        actorId=actor.id,
        platform="x",
        postedAt="2026-05-12T08:00:00+09:00",
        text="existing tweet",
        detailText="existing tweet full detail",
        url="https://x.com/aoki__hina/status/1",
        kind="original",
        mediaUrls=[],
    )

    store = DataStore(db_url)
    store.init()
    store.upsert_actor(actor)
    store.upsert_events([event])
    store.upsert_sns_posts([post])

    async def fake_collect_events(current_actor, settings):
        return []

    async def fake_collect_posts(current_actor, settings, token):
        return []

    async def fake_localize_actors_images(actors, settings):
        return actors

    monkeypatch.setenv("DATABASE_URL", db_url)
    monkeypatch.setattr(sync_data, "load_env", lambda path: None)
    monkeypatch.setattr(sync_data, "list_actors", lambda: [actor])
    monkeypatch.setattr(sync_data, "localize_actors_images", fake_localize_actors_images)
    monkeypatch.setattr(sync_data, "collect_events", fake_collect_events)
    monkeypatch.setattr(sync_data, "collect_posts", fake_collect_posts)

    get_settings.cache_clear()
    try:
        asyncio.run(sync_data.sync(SimpleNamespace(actor_id=None, no_events=False, no_sns=False)))
    finally:
        get_settings.cache_clear()

    refreshed = DataStore(db_url)
    assert [item.id for item in refreshed.list_events(actor.id)] == ["event-existing"]
    assert [item.id for item in refreshed.list_sns_posts(actor.id)] == ["x-existing"]


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
