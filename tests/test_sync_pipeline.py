import asyncio
from types import SimpleNamespace

from app.schemas.voice_actor import Actor, Event, SnsPost
from app.services import sync_pipeline


def test_collect_events_filters_existing_ids(monkeypatch):
    actor = make_actor()

    captured = {}

    async def fake_fetch_eventernote_events(actor_id, url, limit=100, known_ids=None, stop_before_date=None):
        captured["known_ids"] = known_ids
        captured["stop_before_date"] = stop_before_date
        return [
            Event(
                id="event-old",
                actorId=actor_id,
                title="old",
                date="2026-05-01",
                category="talk",
                source="eventernote",
            ),
            Event(
                id="event-new",
                actorId=actor_id,
                title="new",
                date="2026-05-02",
                category="talk",
                source="eventernote",
            ),
        ]

    monkeypatch.setattr(sync_pipeline, "fetch_eventernote_events", fake_fetch_eventernote_events)

    events = asyncio.run(collect_events(actor, existing_ids={"event-old"}, since_event_date="2026-05-01"))

    assert [event.id for event in events] == ["event-new"]
    assert captured == {"known_ids": {"event-old"}, "stop_before_date": "2026-05-01"}


def test_collect_posts_passes_since_time_and_filters_existing_ids(monkeypatch):
    actor = make_actor()
    captured = {}

    async def fake_fetch_x_posts(current_actor, token, limit=20, past_days=183, start_time=None):
        captured["start_time"] = start_time
        return [
            SnsPost(
                id="x-old",
                actorId=current_actor.id,
                platform="x",
                postedAt="2026-05-01T00:00:00Z",
                text="old",
                detailText="old",
                url="https://x.com/aoki__hina/status/1",
                kind="original",
                mediaUrls=[],
            ),
            SnsPost(
                id="x-new",
                actorId=current_actor.id,
                platform="x",
                postedAt="2026-05-02T00:00:00Z",
                text="new",
                detailText="new",
                url="https://x.com/aoki__hina/status/2",
                kind="original",
                mediaUrls=[],
            ),
        ]

    monkeypatch.setattr(sync_pipeline, "fetch_x_posts", fake_fetch_x_posts)

    posts = asyncio.run(collect_posts(actor, existing_ids={"x-old"}, since_posted_at="2026-05-01T00:00:00Z"))

    assert captured["start_time"] == "2026-05-01T00:00:00Z"
    assert [post.id for post in posts] == ["x-new"]


def collect_events(actor: Actor, existing_ids: set[str], since_event_date: str):
    return sync_pipeline.collect_events(actor, make_settings(), existing_ids=existing_ids, since_event_date=since_event_date)


def collect_posts(actor: Actor, existing_ids: set[str], since_posted_at: str):
    return sync_pipeline.collect_posts(actor, make_settings(), "token", existing_ids=existing_ids, since_posted_at=since_posted_at)


def make_settings():
    return SimpleNamespace(event_fetch_past_days=183, event_fetch_future_days=183, sns_fetch_past_days=183)


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
            "eventernoteUrl": "https://www.eventernote.com/actors/test/events",
        }
    )
