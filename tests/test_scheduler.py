import asyncio
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

from app.schemas.voice_actor import Actor, Event, SnsPost
from app.services.cache_store import LocalCacheStore
from app.services.database import DataStore
from app.services.scheduler import EVENT_SYNC_JOB, SNS_SYNC_JOB, parse_datetime, run_scheduled_syncs, should_run_job


def test_should_run_job_respects_interval(tmp_path):
    store = LocalCacheStore(DataStore(tmp_path / "nsy.sqlite3"))
    asyncio.run(store.init())
    now = datetime(2026, 5, 12, 0, 0, tzinfo=timezone.utc)

    assert asyncio.run(should_run_job(store, SNS_SYNC_JOB, 10, now)) is True

    asyncio.run(store.touch_job_run(SNS_SYNC_JOB, now.isoformat()))

    assert asyncio.run(should_run_job(store, SNS_SYNC_JOB, 10, now + timedelta(minutes=9))) is False
    assert asyncio.run(should_run_job(store, SNS_SYNC_JOB, 10, now + timedelta(minutes=10))) is True


def test_parse_datetime_normalizes_utc():
    assert parse_datetime("2026-05-12T08:00:00Z") == datetime(2026, 5, 12, 8, 0, tzinfo=timezone.utc)
    assert parse_datetime("2026-05-12T08:00:00").tzinfo == timezone.utc


def test_run_scheduled_syncs_tracks_sns_and_event_intervals(tmp_path, monkeypatch):
    store = LocalCacheStore(DataStore(tmp_path / "nsy.sqlite3"))
    asyncio.run(store.init())

    actor = make_actor()
    settings = SimpleNamespace(sns_sync_interval_minutes=10, event_sync_interval_minutes=60)
    calls = {"sns": 0, "event": 0}

    async def fake_collect_posts(current_actor, current_settings, token):
        calls["sns"] += 1
        return [
            SnsPost(
                id=f"x-{calls['sns']}",
                actorId=current_actor.id,
                platform="x",
                postedAt="2026-05-12T08:00:00+09:00",
                text="tweet",
                detailText="tweet detail",
                url=f"https://x.com/{current_actor.id}/status/{calls['sns']}",
                kind="original",
                mediaUrls=[],
            )
        ]

    async def fake_collect_events(current_actor, current_settings):
        calls["event"] += 1
        return [
            Event(
                id=f"event-{calls['event']}",
                actorId=current_actor.id,
                title="event",
                date="2026-06-01",
                category="live",
                venue="Tokyo",
                url=f"https://example.com/events/{calls['event']}",
                source="eventernote",
            )
        ]

    monkeypatch.setattr("app.services.scheduler.list_actors", lambda: [actor])
    monkeypatch.setattr("app.services.scheduler.collect_posts", fake_collect_posts)
    monkeypatch.setattr("app.services.scheduler.collect_events", fake_collect_events)

    start = datetime(2026, 5, 12, 0, 0, tzinfo=timezone.utc)
    first = asyncio.run(run_scheduled_syncs(store, settings, now=start))
    second = asyncio.run(run_scheduled_syncs(store, settings, now=start + timedelta(minutes=5)))
    third = asyncio.run(run_scheduled_syncs(store, settings, now=start + timedelta(minutes=15)))
    fourth = asyncio.run(run_scheduled_syncs(store, settings, now=start + timedelta(minutes=65)))

    assert first == {"sns": 1, "event": 1}
    assert second == {"sns": 0, "event": 0}
    assert third == {"sns": 1, "event": 0}
    assert fourth == {"sns": 1, "event": 1}
    assert asyncio.run(store.get_job_run(SNS_SYNC_JOB)) == (start + timedelta(minutes=65)).isoformat()
    assert asyncio.run(store.get_job_run(EVENT_SYNC_JOB)) == (start + timedelta(minutes=65)).isoformat()


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
