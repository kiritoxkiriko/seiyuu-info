from app.schemas.voice_actor import Actor, Event, SnsPost
from app.services.database import DataStore


def test_data_store_persists_actor_events_and_posts_with_language_switch(tmp_path):
    store = DataStore(tmp_path / "nsy.sqlite3")
    store.init()

    actor = make_actor()
    event = Event(
        id="event-1",
        actorId=actor.id,
        title="Original Event",
        date="2026-06-01",
        category="live",
        venue="Original Venue",
        url="https://example.com/event",
        source="test",
        titleZh="中文活动",
        venueZh="中文会场",
    )
    post = SnsPost(
        id="x-1",
        actorId=actor.id,
        platform="x",
        postedAt="2026-05-12T08:00:00+09:00",
        text="Original tweet",
        url="https://x.com/aoki__hina/status/1",
        kind="original",
        mediaUrls=[],
        textZh="中文推文",
        detailText="Original tweet full detail",
        detailTextZh="中文推文完整内容",
    )

    store.upsert_actor(actor)
    store.upsert_events([event])
    store.upsert_sns_posts([post])

    assert store.get_actor(actor.id).id == actor.id
    assert store.list_events(actor.id, language="zh")[0].title == "中文活动"
    assert store.list_events(actor.id, language="original")[0].title == "Original Event"
    assert store.list_sns_posts(actor.id, language="zh")[0].text == "中文推文"
    assert store.list_sns_posts(actor.id, language="original")[0].detail_text == "Original tweet full detail"


def test_data_store_persists_job_run(tmp_path):
    store = DataStore(tmp_path / "nsy.sqlite3")
    store.init()

    store.touch_job_run("sns_sync", "2026-05-12T00:00:00+00:00", '{"actors": 2}')

    assert store.get_job_run("sns_sync") == "2026-05-12T00:00:00+00:00"


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
