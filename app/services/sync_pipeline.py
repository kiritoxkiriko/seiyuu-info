from app.services.date_window import filter_events_in_window, filter_posts_in_window
from app.services.enrichment import translate_events, translate_posts
from app.services.eventernote import fetch_eventernote_events
from app.services.repository import list_events, list_sns_posts
from app.services.x import fetch_x_posts


async def collect_events(actor, settings):
    if actor.eventernote_url:
        try:
            events = await fetch_eventernote_events(actor.id, str(actor.eventernote_url), limit=100)
            return await translate_events(
                filter_events_in_window(
                    events,
                    past_days=settings.event_fetch_past_days,
                    future_days=settings.event_fetch_future_days,
                )
            )
        except Exception as error:
            print(f"  eventernote fallback: {error.__class__.__name__}")
    return await translate_events(
        filter_events_in_window(
            list_events(actor.id),
            past_days=settings.event_fetch_past_days,
            future_days=settings.event_fetch_future_days,
        )
    )


async def collect_posts(actor, settings, token: str | None):
    if token:
        try:
            posts = await fetch_x_posts(actor, token, past_days=settings.sns_fetch_past_days)
            if posts:
                return await translate_posts(filter_posts_in_window(posts, past_days=settings.sns_fetch_past_days))
        except Exception as error:
            print(f"  x fallback: {error.__class__.__name__}")
    return await translate_posts(filter_posts_in_window(list_sns_posts(actor.id), past_days=settings.sns_fetch_past_days))
