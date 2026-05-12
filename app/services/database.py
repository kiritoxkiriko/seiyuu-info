import json
import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

from app.schemas.voice_actor import Actor, Event, Language, SnsPost
from app.services.sns import filter_relevant_posts


DEFAULT_DATABASE_URL = "sqlite:///data/nsy.sqlite3"
UNKNOWN_DATE = "9999-12-31"


class DataStore:
    def __init__(self, database_url: str | Path = DEFAULT_DATABASE_URL):
        self.database_path = _sqlite_path(str(database_url))

    def init(self) -> None:
        if self.database_path != ":memory:":
            Path(self.database_path).parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            conn.executescript(SCHEMA)

    def upsert_actor(self, actor: Actor) -> None:
        now = _now()
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO actors (id, payload_json, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    payload_json = excluded.payload_json,
                    updated_at = excluded.updated_at
                """,
                (actor.id, _dump(actor), now),
            )

    def upsert_actors(self, actors: list[Actor]) -> None:
        for actor in actors:
            self.upsert_actor(actor)

    def list_actors(self) -> list[Actor]:
        with self._connect() as conn:
            rows = conn.execute("SELECT payload_json FROM actors ORDER BY id").fetchall()
        return [Actor.model_validate(json.loads(row["payload_json"])) for row in rows]

    def get_actor(self, actor_id: str) -> Actor | None:
        with self._connect() as conn:
            row = conn.execute("SELECT payload_json FROM actors WHERE id = ?", (actor_id,)).fetchone()
        return Actor.model_validate(json.loads(row["payload_json"])) if row else None

    def upsert_events(self, events: list[Event]) -> None:
        now = _now()
        with self._connect() as conn:
            conn.executemany(
                """
                INSERT INTO events (
                    id, actor_id, title, title_zh, date, category, venue, venue_zh, url, source, payload_json, fetched_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    actor_id = excluded.actor_id,
                    title = excluded.title,
                    title_zh = excluded.title_zh,
                    date = excluded.date,
                    category = excluded.category,
                    venue = excluded.venue,
                    venue_zh = excluded.venue_zh,
                    url = excluded.url,
                    source = excluded.source,
                    payload_json = excluded.payload_json,
                    fetched_at = excluded.fetched_at
                """,
                [
                    (
                        event.id,
                        event.actor_id,
                        event.title,
                        event.title_zh,
                        event.date,
                        event.category,
                        event.venue,
                        event.venue_zh,
                        str(event.url) if event.url else None,
                        event.source,
                        _dump(event),
                        now,
                    )
                    for event in events
                ],
            )

    def replace_events(self, actor_id: str, events: list[Event]) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM events WHERE actor_id = ?", (actor_id,))
        self.upsert_events(events)

    def list_events(self, actor_id: str | None = None, language: Language = "original", source: str | None = None) -> list[Event]:
        sql = "SELECT payload_json FROM events"
        conditions: list[str] = []
        params: list[str] = []
        if actor_id:
            conditions.append("actor_id = ?")
            params.append(actor_id)
        if source:
            conditions.append("source = ?")
            params.append(source)
        if conditions:
            sql += " WHERE " + " AND ".join(conditions)
        with self._connect() as conn:
            rows = conn.execute(sql, tuple(params)).fetchall()
        events = [_event_for_language(Event.model_validate(json.loads(row["payload_json"])), language) for row in rows]
        return sorted(events, key=lambda event: event.date if event.date != "未定" else UNKNOWN_DATE, reverse=True)

    def upsert_sns_posts(self, posts: list[SnsPost]) -> None:
        now = _now()
        with self._connect() as conn:
            conn.executemany(
                """
                INSERT INTO sns_posts (
                    id, actor_id, platform, posted_at, text, text_zh, detail_text, detail_text_zh,
                    url, kind, media_urls_json, source, payload_json, fetched_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    actor_id = excluded.actor_id,
                    platform = excluded.platform,
                    posted_at = excluded.posted_at,
                    text = excluded.text,
                    text_zh = excluded.text_zh,
                    detail_text = excluded.detail_text,
                    detail_text_zh = excluded.detail_text_zh,
                    url = excluded.url,
                    kind = excluded.kind,
                    media_urls_json = excluded.media_urls_json,
                    source = excluded.source,
                    payload_json = excluded.payload_json,
                    fetched_at = excluded.fetched_at
                """,
                [
                    (
                        post.id,
                        post.actor_id,
                        post.platform,
                        post.posted_at,
                        post.text,
                        post.text_zh,
                        post.detail_text,
                        post.detail_text_zh,
                        str(post.url),
                        post.kind,
                        json.dumps([str(url) for url in post.media_urls], ensure_ascii=False),
                        post.platform,
                        _dump(post),
                        now,
                    )
                    for post in posts
                ],
            )

    def replace_sns_posts(self, actor_id: str, posts: list[SnsPost]) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM sns_posts WHERE actor_id = ?", (actor_id,))
        self.upsert_sns_posts(posts)

    def list_sns_posts(self, actor_id: str | None = None, language: Language = "original", source: str | None = None) -> list[SnsPost]:
        sql = "SELECT payload_json FROM sns_posts"
        conditions: list[str] = []
        params: list[str] = []
        if actor_id:
            conditions.append("actor_id = ?")
            params.append(actor_id)
        if source:
            conditions.append("source = ?")
            params.append(source)
        if conditions:
            sql += " WHERE " + " AND ".join(conditions)
        with self._connect() as conn:
            rows = conn.execute(sql, tuple(params)).fetchall()
        posts = [_post_for_language(SnsPost.model_validate(json.loads(row["payload_json"])), language) for row in rows]
        return filter_relevant_posts(posts)

    def get_sns_post(self, post_id: str, language: Language = "original") -> SnsPost | None:
        with self._connect() as conn:
            row = conn.execute("SELECT payload_json FROM sns_posts WHERE id = ?", (post_id,)).fetchone()
        if not row:
            return None
        return _post_for_language(SnsPost.model_validate(json.loads(row["payload_json"])), language)

    def get_job_run(self, job_name: str) -> str | None:
        with self._connect() as conn:
            row = conn.execute("SELECT ran_at FROM job_runs WHERE job_name = ?", (job_name,)).fetchone()
        return row["ran_at"] if row else None

    def touch_job_run(self, job_name: str, ran_at: str, meta_json: str = "{}") -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO job_runs (job_name, ran_at, meta_json)
                VALUES (?, ?, ?)
                ON CONFLICT(job_name) DO UPDATE SET
                    ran_at = excluded.ran_at,
                    meta_json = excluded.meta_json
                """,
                (job_name, ran_at, meta_json),
            )

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.database_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()


def get_data_store() -> DataStore:
    return DataStore(os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL))


def _event_for_language(event: Event, language: Language) -> Event:
    if language != "zh":
        return event.model_copy(update={"language": "original"})
    return event.model_copy(
        update={
            "title": event.title_zh or event.title,
            "venue": event.venue_zh or event.venue,
            "language": "zh",
        }
    )


def _post_for_language(post: SnsPost, language: Language) -> SnsPost:
    if language != "zh":
        return post.model_copy(update={"language": "original"})
    return post.model_copy(
        update={
            "text": post.text_zh or post.text,
            "detail_text": post.detail_text_zh or post.detail_text or post.text_zh or post.text,
            "language": "zh",
        }
    )


def _sqlite_path(database_url: str) -> str:
    if database_url.startswith("sqlite:///"):
        return database_url.removeprefix("sqlite:///")
    return database_url


def _dump(model: Actor | Event | SnsPost) -> str:
    return json.dumps(model.model_dump(mode="json", by_alias=True), ensure_ascii=False)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


SCHEMA = """
CREATE TABLE IF NOT EXISTS actors (
    id TEXT PRIMARY KEY,
    payload_json TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS events (
    id TEXT PRIMARY KEY,
    actor_id TEXT NOT NULL,
    title TEXT NOT NULL,
    title_zh TEXT,
    date TEXT NOT NULL,
    category TEXT NOT NULL,
    venue TEXT,
    venue_zh TEXT,
    url TEXT,
    source TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    fetched_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_events_actor_date ON events(actor_id, date DESC);

CREATE TABLE IF NOT EXISTS sns_posts (
    id TEXT PRIMARY KEY,
    actor_id TEXT NOT NULL,
    platform TEXT NOT NULL,
    posted_at TEXT NOT NULL,
    text TEXT NOT NULL,
    text_zh TEXT,
    detail_text TEXT,
    detail_text_zh TEXT,
    url TEXT NOT NULL,
    kind TEXT NOT NULL,
    media_urls_json TEXT NOT NULL,
    source TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    fetched_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_sns_actor_posted_at ON sns_posts(actor_id, posted_at DESC);

CREATE TABLE IF NOT EXISTS job_runs (
    job_name TEXT PRIMARY KEY,
    ran_at TEXT NOT NULL,
    meta_json TEXT NOT NULL
);
"""
