from datetime import date, datetime, timedelta

from app.schemas.voice_actor import Event, SnsPost


def filter_events_in_window(
    events: list[Event],
    today: date | None = None,
    past_days: int = 183,
    future_days: int = 183,
) -> list[Event]:
    anchor = today or date.today()
    start = anchor - timedelta(days=past_days)
    end = anchor + timedelta(days=future_days)
    filtered = [event for event in events if _date_in_range(event.date, start, end)]
    return sorted(filtered, key=lambda event: event.date, reverse=True)


def filter_posts_in_window(posts: list[SnsPost], today: date | None = None, past_days: int = 183) -> list[SnsPost]:
    anchor = today or date.today()
    start = anchor - timedelta(days=past_days)
    filtered = [post for post in posts if _post_date(post.posted_at) >= start]
    return sorted(filtered, key=lambda post: post.posted_at, reverse=True)


def past_days_start_iso(past_days: int = 183, today: date | None = None) -> str:
    anchor = today or date.today()
    start = anchor - timedelta(days=past_days)
    return f"{start.isoformat()}T00:00:00Z"


def _date_in_range(value: str, start: date, end: date) -> bool:
    try:
        parsed = date.fromisoformat(value)
    except ValueError:
        return False
    return start <= parsed <= end


def _post_date(value: str) -> date:
    normalized = value.replace("Z", "+00:00")
    return datetime.fromisoformat(normalized).date()
