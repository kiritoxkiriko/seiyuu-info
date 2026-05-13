from app.services.date_window import filter_events_in_window, filter_posts_in_window
from app.services.enrichment import translate_events, translate_posts
from app.services.eventernote import fetch_eventernote_events
from app.services.repository import list_events, list_sns_posts
from app.services.x import fetch_x_posts


async def collect_events(actor, settings, existing_ids: set[str] | None = None, since_event_date: str | None = None):
    known_ids = existing_ids or set()
    if actor.eventernote_url:
        try:
            events = await fetch_eventernote_events(
                actor.id,
                str(actor.eventernote_url),
                limit=100,
                known_ids=known_ids,
                stop_before_date=since_event_date,
            )
            events = [event for event in events if event.id not in known_ids]
            return await translate_events(
                filter_events_in_window(
                    events,
                    past_days=settings.event_fetch_past_days,
                    future_days=settings.event_fetch_future_days,
                )
            )
        except Exception as error:
            print(f"  eventernote fallback: {error.__class__.__name__}")
    seed_events = [event for event in list_events(actor.id) if event.id not in known_ids]
    return await translate_events(
        filter_events_in_window(
            seed_events,
            past_days=settings.event_fetch_past_days,
            future_days=settings.event_fetch_future_days,
        )
    )


async def collect_posts(
    actor,
    settings,
    token: str | None,
    existing_ids: set[str] | None = None,
    since_posted_at: str | None = None,
    limit: int = 100,
):
    known_ids = existing_ids or set()
    if token:
        try:
            posts = await fetch_x_posts(actor, token, limit=limit, past_days=settings.sns_fetch_past_days, start_time=since_posted_at)
            posts = [post for post in posts if post.id not in known_ids]
            return await translate_posts(filter_posts_in_window(posts, past_days=settings.sns_fetch_past_days))
        except Exception as error:
            print(f"  x fallback: {error.__class__.__name__}")
    seed_posts = [post for post in list_sns_posts(actor.id) if post.id not in known_ids]
    return await translate_posts(filter_posts_in_window(seed_posts, past_days=settings.sns_fetch_past_days))
