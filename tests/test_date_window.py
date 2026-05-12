from datetime import date

from app.schemas.voice_actor import Event, SnsPost
from app.services.date_window import filter_events_in_window, filter_posts_in_window


def test_filters_events_to_one_year_before_and_after_today():
    events = [
        make_event("too-old", "2025-05-11"),
        make_event("within-past", "2025-05-12"),
        make_event("within-future", "2027-05-12"),
        make_event("too-future", "2027-05-13"),
        make_event("unknown", "未定"),
    ]

    filtered = filter_events_in_window(events, today=date(2026, 5, 12), past_days=365, future_days=365)

    assert [event.id for event in filtered] == ["within-future", "within-past"]


def test_filters_posts_to_last_year():
    posts = [
        make_post("old", "2025-05-11T23:59:59+09:00"),
        make_post("fresh", "2025-05-12T00:00:00+09:00"),
        make_post("newer", "2026-05-12T08:00:00+09:00"),
    ]

    filtered = filter_posts_in_window(posts, today=date(2026, 5, 12), past_days=365)

    assert [post.id for post in filtered] == ["newer", "fresh"]


def make_event(event_id: str, event_date: str) -> Event:
    return Event(
        id=event_id,
        actorId="aoki-hina",
        title="原文 Event",
        date=event_date,
        category="talk",
        venue="原文会場",
        url="https://example.com/event",
        source="test",
    )


def make_post(post_id: str, posted_at: str) -> SnsPost:
    return SnsPost(
        id=post_id,
        actorId="aoki-hina",
        platform="x",
        postedAt=posted_at,
        text="原文 tweet",
        url="https://x.com/example/status/1",
        kind="original",
        mediaUrls=[],
    )
