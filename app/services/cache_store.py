import json
from typing import Any, Protocol

from app.core.config import Settings
from app.schemas.voice_actor import Actor, Event, Language, SnsPost
from app.services.database import DataStore, SCHEMA


class CacheStore(Protocol):
    async def init(self) -> None: ...
    async def upsert_actor(self, actor: Actor) -> None: ...
    async def upsert_actors(self, actors: list[Actor]) -> None: ...
    async def list_actors(self) -> list[Actor]: ...
    async def get_actor(self, actor_id: str) -> Actor | None: ...
    async def upsert_events(self, events: list[Event]) -> None: ...
    async def list_events(self, actor_id: str | None = None, language: Language = "original", source: str | None = None) -> list[Event]: ...
    async def upsert_sns_posts(self, posts: list[SnsPost]) -> None: ...
    async def list_sns_posts(self, actor_id: str | None = None, language: Language = "original", source: str | None = None) -> list[SnsPost]: ...
    async def get_sns_post(self, post_id: str, language: Language = "original") -> SnsPost | None: ...
    async def get_job_run(self, job_name: str) -> str | None: ...
    async def touch_job_run(self, job_name: str, ran_at: str, meta_json: str = "{}") -> None: ...


class LocalCacheStore:
    def __init__(self, store: DataStore):
        self.store = store

    async def init(self) -> None:
        self.store.init()

    async def upsert_actor(self, actor: Actor) -> None:
        self.store.upsert_actor(actor)

    async def upsert_actors(self, actors: list[Actor]) -> None:
        self.store.upsert_actors(actors)

    async def list_actors(self) -> list[Actor]:
        return self.store.list_actors()

    async def get_actor(self, actor_id: str) -> Actor | None:
        return self.store.get_actor(actor_id)

    async def upsert_events(self, events: list[Event]) -> None:
        self.store.upsert_events(events)

    async def list_events(self, actor_id: str | None = None, language: Language = "original", source: str | None = None) -> list[Event]:
        return self.store.list_events(actor_id, language, source)

    async def upsert_sns_posts(self, posts: list[SnsPost]) -> None:
        self.store.upsert_sns_posts(posts)

    async def list_sns_posts(self, actor_id: str | None = None, language: Language = "original", source: str | None = None) -> list[SnsPost]:
        return self.store.list_sns_posts(actor_id, language, source)

    async def get_sns_post(self, post_id: str, language: Language = "original") -> SnsPost | None:
        return self.store.get_sns_post(post_id, language)

    async def get_job_run(self, job_name: str) -> str | None:
        return self.store.get_job_run(job_name)

    async def touch_job_run(self, job_name: str, ran_at: str, meta_json: str = "{}") -> None:
        self.store.touch_job_run(job_name, ran_at, meta_json)


class D1CacheStore:
    def __init__(self, db: Any):
        self.db = db
        self.local_language = DataStore(":memory:")
        self.local_language.init()

    async def init(self) -> None:
        await self.db.exec(SCHEMA)

    async def upsert_actor(self, actor: Actor) -> None:
        await self.db.prepare(
            """
            INSERT INTO actors (id, payload_json, updated_at)
            VALUES (?, ?, datetime('now'))
            ON CONFLICT(id) DO UPDATE SET
                payload_json = excluded.payload_json,
                updated_at = excluded.updated_at
            """
        ).bind(actor.id, _dump(actor)).run()

    async def upsert_actors(self, actors: list[Actor]) -> None:
        for actor in actors:
            await self.upsert_actor(actor)

    async def list_actors(self) -> list[Actor]:
        rows = await self._rows("SELECT payload_json FROM actors ORDER BY id")
        return [Actor.model_validate(json.loads(row["payload_json"])) for row in rows]

    async def get_actor(self, actor_id: str) -> Actor | None:
        row = await self._first("SELECT payload_json FROM actors WHERE id = ?", actor_id)
        return Actor.model_validate(json.loads(row["payload_json"])) if row else None

    async def upsert_events(self, events: list[Event]) -> None:
        for event in events:
            await self.db.prepare(
                """
                INSERT INTO events (
                    id, actor_id, title, title_zh, date, category, venue, venue_zh, url, source, payload_json, fetched_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
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
                """
            ).bind(
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
            ).run()

    async def list_events(self, actor_id: str | None = None, language: Language = "original", source: str | None = None) -> list[Event]:
        rows = await self._rows_for("events", actor_id, source)
        self.local_language.upsert_events([Event.model_validate(json.loads(row["payload_json"])) for row in rows])
        return self.local_language.list_events(actor_id, language, source)

    async def upsert_sns_posts(self, posts: list[SnsPost]) -> None:
        for post in posts:
            await self.db.prepare(
                """
                INSERT INTO sns_posts (
                    id, actor_id, platform, posted_at, text, text_zh, detail_text, detail_text_zh,
                    url, kind, media_urls_json, source, payload_json, fetched_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
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
                """
            ).bind(
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
            ).run()

    async def list_sns_posts(self, actor_id: str | None = None, language: Language = "original", source: str | None = None) -> list[SnsPost]:
        rows = await self._rows_for("sns_posts", actor_id, source)
        self.local_language.upsert_sns_posts([SnsPost.model_validate(json.loads(row["payload_json"])) for row in rows])
        return self.local_language.list_sns_posts(actor_id, language, source)

    async def get_sns_post(self, post_id: str, language: Language = "original") -> SnsPost | None:
        row = await self._first("SELECT payload_json FROM sns_posts WHERE id = ?", post_id)
        if not row:
            return None
        self.local_language.upsert_sns_posts([SnsPost.model_validate(json.loads(row["payload_json"]))])
        return self.local_language.get_sns_post(post_id, language)

    async def get_job_run(self, job_name: str) -> str | None:
        row = await self._first("SELECT ran_at FROM job_runs WHERE job_name = ?", job_name)
        return row["ran_at"] if row else None

    async def touch_job_run(self, job_name: str, ran_at: str, meta_json: str = "{}") -> None:
        await self.db.prepare(
            """
            INSERT INTO job_runs (job_name, ran_at, meta_json)
            VALUES (?, ?, ?)
            ON CONFLICT(job_name) DO UPDATE SET
                ran_at = excluded.ran_at,
                meta_json = excluded.meta_json
            """
        ).bind(job_name, ran_at, meta_json).run()

    async def _rows(self, sql: str, *params: Any) -> list[dict[str, Any]]:
        result = await self._statement(sql, *params).run()
        return _to_py(result.results)

    async def _first(self, sql: str, *params: Any) -> dict[str, Any] | None:
        row = await self._statement(sql, *params).first()
        return _to_py(row) if row else None

    async def _rows_for(self, table: str, actor_id: str | None, source: str | None) -> list[dict[str, Any]]:
        sql = f"SELECT payload_json FROM {table}"
        conditions: list[str] = []
        params: list[Any] = []
        if actor_id:
            conditions.append("actor_id = ?")
            params.append(actor_id)
        if source:
            conditions.append("source = ?")
            params.append(source)
        if conditions:
            sql += " WHERE " + " AND ".join(conditions)
        return await self._rows(sql, *params)

    def _statement(self, sql: str, *params: Any):
        statement = self.db.prepare(sql)
        return statement.bind(*params) if params else statement


def build_cache_store(settings: Settings, env: Any | None = None) -> CacheStore:
    d1_binding = getattr(settings, "d1_binding", "DB")
    db = getattr(env, d1_binding, None) if env else None
    if db:
        return D1CacheStore(db)
    return LocalCacheStore(DataStore(settings.database_url))


def _dump(model: Actor | Event | SnsPost) -> str:
    return json.dumps(model.model_dump(mode="json", by_alias=True), ensure_ascii=False)


def _to_py(value: Any) -> Any:
    if hasattr(value, "to_py"):
        return value.to_py()
    return value
