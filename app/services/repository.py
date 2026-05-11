import json
from functools import lru_cache
from pathlib import Path

from app.schemas.voice_actor import Actor, Event, SnsPost
from app.services.sns import filter_relevant_posts


DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "actors.json"


@lru_cache(maxsize=1)
def load_data() -> dict:
    with DATA_PATH.open(encoding="utf-8") as file:
        return json.load(file)


def list_actors() -> list[Actor]:
    return [Actor.model_validate(actor) for actor in load_data()["actors"]]


def get_actor(actor_id: str) -> Actor | None:
    return next((actor for actor in list_actors() if actor.id == actor_id), None)


def list_events(actor_id: str | None = None) -> list[Event]:
    events = [Event.model_validate(event) for event in load_data()["events"]]
    if actor_id is None:
        return sorted(events, key=lambda event: event.date)
    return sorted((event for event in events if event.actor_id == actor_id), key=lambda event: event.date)


def list_sns_posts(actor_id: str | None = None) -> list[SnsPost]:
    posts = [SnsPost.model_validate(post) for post in load_data()["sns"]]
    if actor_id is not None:
        posts = [post for post in posts if post.actor_id == actor_id]
    return filter_relevant_posts(posts)
