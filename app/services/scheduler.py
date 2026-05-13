import asyncio
import json
import os
from datetime import datetime, timedelta, timezone
from typing import NoReturn

from app.services.cache_store import CacheStore
from app.services.images import localize_actors_images
from app.services.sync_pipeline import collect_events, collect_posts
from app.services.repository import list_actors


EVENT_SYNC_JOB = "event_sync"
SNS_SYNC_JOB = "sns_sync"
MIN_SCHEDULER_POLL_SECONDS = 60


async def run_scheduler_loop(store: CacheStore, settings) -> NoReturn:
    poll_seconds = scheduler_poll_seconds(settings)
    while True:
        try:
            await run_scheduled_syncs(store, settings)
        except Exception as exc:
            print(f"scheduled sync failed: {exc.__class__.__name__}: {exc}", flush=True)
        await asyncio.sleep(poll_seconds)


def scheduler_poll_seconds(settings) -> int:
    shortest_interval = min(
        max(1, settings.sns_sync_interval_minutes),
        max(1, settings.event_sync_interval_minutes),
    )
    return max(MIN_SCHEDULER_POLL_SECONDS, shortest_interval * 60)


async def run_scheduled_syncs(store: CacheStore, settings, now: datetime | None = None) -> dict[str, int]:
    current = now or datetime.now(timezone.utc)
    token = os.getenv("X_BEARER_TOKEN")
    actors = await localize_actors_images(list_actors(), settings)
    await store.upsert_actors(actors)

    result = {"sns": 0, "event": 0}

    if await should_run_job(store, SNS_SYNC_JOB, settings.sns_sync_interval_minutes, current):
        for actor in actors:
            posts = await collect_posts(actor, settings, token)
            await store.upsert_sns_posts(posts)
            result["sns"] += len(posts)
        await store.touch_job_run(SNS_SYNC_JOB, current.isoformat(), json.dumps({"actors": len(actors)}))

    if await should_run_job(store, EVENT_SYNC_JOB, settings.event_sync_interval_minutes, current):
        for actor in actors:
            events = await collect_events(actor, settings)
            await store.upsert_events(events)
            result["event"] += len(events)
        await store.touch_job_run(EVENT_SYNC_JOB, current.isoformat(), json.dumps({"actors": len(actors)}))

    return result


async def should_run_job(store: CacheStore, job_name: str, interval_minutes: int, now: datetime) -> bool:
    last_run = await store.get_job_run(job_name)
    if not last_run:
        return True
    last_time = parse_datetime(last_run)
    return now >= last_time + timedelta(minutes=max(1, interval_minutes))


def parse_datetime(value: str) -> datetime:
    normalized = value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)
