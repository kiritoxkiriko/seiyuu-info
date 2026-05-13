import argparse
import asyncio
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.core.config import get_settings
from app.services.database import DataStore
from app.services.images import localize_actors_images
from app.services.repository import list_actors
from app.services.sync_pipeline import collect_events, collect_posts


def load_env(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip("'").strip('"'))


async def sync(args: argparse.Namespace) -> None:
    load_env(ROOT / ".env")
    settings = get_settings()
    store = DataStore(settings.database_url)
    store.init()

    actors = [actor for actor in list_actors() if not args.actor_id or actor.id == args.actor_id]
    if not args.no_images:
        actors = await localize_actors_images(actors, settings)
    if not args.no_actors:
        store.upsert_actors(actors)

    for actor in actors:
        print(f"sync actor: {actor.id}")
        if not args.no_events:
            existing_events = store.list_events(actor.id, source="eventernote")
            events = await collect_events(
                actor,
                settings,
                existing_ids={event.id for event in existing_events},
                since_event_date=latest_event_date(existing_events),
            )
            store.upsert_events(events)
            print(f"  events: {len(events)}")
        if not args.no_sns:
            existing_posts = store.list_sns_posts(actor.id, source="x")
            posts = await collect_posts(
                actor,
                settings,
                os.getenv("X_BEARER_TOKEN"),
                existing_ids={post.id for post in existing_posts},
                since_posted_at=latest_posted_at(existing_posts),
            )
            store.upsert_sns_posts(posts)
            print(f"  sns: {len(posts)}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Incrementally sync configured seiyuu data into the local database.")
    parser.add_argument("--actor-id", help="Only sync one actor id.")
    parser.add_argument("--no-actors", action="store_true", help="Skip actor profile database updates.")
    parser.add_argument("--no-images", action="store_true", help="Skip actor image download/localization.")
    parser.add_argument("--no-events", action="store_true", help="Skip Eventernote/event sync.")
    parser.add_argument("--no-sns", action="store_true", help="Skip SNS sync.")
    return parser.parse_args()


def latest_posted_at(posts) -> str | None:
    if not posts:
        return None
    return max(posts, key=lambda post: parse_datetime(post.posted_at)).posted_at


def latest_event_date(events) -> str | None:
    dated_events = [event for event in events if event.date != "未定"]
    if not dated_events:
        return None
    return max(event.date for event in dated_events)


def parse_datetime(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


if __name__ == "__main__":
    asyncio.run(sync(parse_args()))
