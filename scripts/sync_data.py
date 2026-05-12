import argparse
import asyncio
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.core.config import get_settings
from app.services.database import DataStore
from app.services.repository import list_actors, list_events, list_sns_posts
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
    store.upsert_actors(actors)

    for actor in actors:
        print(f"sync actor: {actor.id}")
        if not args.no_events:
            events = await collect_events(actor, settings)
            store.replace_events(actor.id, events)
            print(f"  events: {len(events)}")
        if not args.no_sns:
            posts = await collect_posts(actor, settings, os.getenv("X_BEARER_TOKEN"))
            store.replace_sns_posts(actor.id, posts)
            print(f"  sns: {len(posts)}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sync configured seiyuu data into the local database.")
    parser.add_argument("--actor-id", help="Only sync one actor id.")
    parser.add_argument("--no-events", action="store_true", help="Skip Eventernote/event sync.")
    parser.add_argument("--no-sns", action="store_true", help="Skip SNS sync.")
    return parser.parse_args()


if __name__ == "__main__":
    asyncio.run(sync(parse_args()))
