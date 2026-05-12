import json
from functools import lru_cache
from pathlib import Path

from app.schemas.voice_actor import Actor, Event, Language, SnsPost
from app.services.sns import filter_relevant_posts


DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "actors.json"
UNKNOWN_DATE = "9999-12-31"


@lru_cache(maxsize=1)
def load_data() -> dict:
    with DATA_PATH.open(encoding="utf-8") as file:
        return json.load(file)


def list_actors() -> list[Actor]:
    return [Actor.model_validate(actor) for actor in load_data()["actors"]]


def get_actor(actor_id: str) -> Actor | None:
    return next((actor for actor in list_actors() if actor.id == actor_id), None)


def list_events(actor_id: str | None = None, language: Language = "original") -> list[Event]:
    events = [Event.model_validate(event) for event in load_data()["events"]]
    if actor_id is None:
        return sort_events_desc([event_for_language(event, language) for event in events])
    return sort_events_desc([event_for_language(event, language) for event in events if event.actor_id == actor_id])


def list_sns_posts(actor_id: str | None = None, language: Language = "original") -> list[SnsPost]:
    posts = [SnsPost.model_validate(post) for post in load_data()["sns"]]
    if actor_id is not None:
        posts = [post for post in posts if post.actor_id == actor_id]
    return filter_relevant_posts([post_for_language(post, language) for post in posts])


def get_sns_post(post_id: str, language: Language = "original") -> SnsPost | None:
    posts = [SnsPost.model_validate(post) for post in load_data()["sns"]]
    post = next((item for item in posts if item.id == post_id), None)
    return post_for_language(post, language) if post else None


def sort_events_desc(events: list[Event]) -> list[Event]:
    return sorted(events, key=lambda event: event.date if event.date != "未定" else UNKNOWN_DATE, reverse=True)


def event_for_language(event: Event, language: Language) -> Event:
    if language != "zh":
        return event.model_copy(update={"language": "original"})
    return event.model_copy(
        update={
            "title": event.title_zh or event.title,
            "venue": event.venue_zh or event.venue,
            "language": "zh",
        }
    )


def post_for_language(post: SnsPost, language: Language) -> SnsPost:
    if language != "zh":
        return post.model_copy(update={"language": "original"})
    return post.model_copy(
        update={
            "text": post.text_zh or post.text,
            "detail_text": post.detail_text_zh or post.detail_text or post.text_zh or post.text,
            "language": "zh",
        }
    )
