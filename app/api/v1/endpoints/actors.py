import os
from typing import Literal

import httpx
from fastapi import APIRouter, HTTPException, Request

from app.core.config import get_settings
from app.schemas.voice_actor import Actor, ActorDetail, Event, Language, SnsPost
from app.services.cache_store import CacheStore, build_cache_store
from app.services.date_window import filter_events_in_window, filter_posts_in_window
from app.services.enrichment import translate_events, translate_posts
from app.services.eventernote import fetch_eventernote_events
from app.services.repository import (
    event_for_language,
    get_actor,
    get_sns_post,
    list_actors,
    list_events,
    list_sns_posts,
    post_for_language,
)
from app.services.x import fetch_x_posts


router = APIRouter()


@router.get("/actors", response_model=list[Actor])
async def actors(request: Request, cache: bool | None = None) -> list[Actor]:
    store = await _store(cache, request)
    configured = _sort_actors_by_romanized(list_actors())
    if store:
        cached = await store.list_actors()
        if cached:
            cached_by_id = {actor.id: actor for actor in cached}
            missing = [actor for actor in configured if actor.id not in cached_by_id]
            if missing:
                await store.upsert_actors(missing)
            return _sort_actors_by_romanized([cached_by_id.get(actor.id, actor) for actor in configured])
        await store.upsert_actors(configured)
    return configured


@router.get("/actors/{actor_id}", response_model=ActorDetail)
async def actor_detail(
    actor_id: str,
    request: Request,
    event_source: Literal["seed", "eventernote"] = "seed",
    sns_source: Literal["seed", "x"] = "seed",
    language: Language = "original",
    cache: bool | None = None,
) -> ActorDetail:
    settings = get_settings()
    store = await _store(cache, request)
    actor = await _get_actor(actor_id, store)
    if actor is None:
        raise HTTPException(status_code=404, detail="actor not found")
    events = await _events_for_actor(actor, event_source, language, store, settings=settings)
    sns_posts = await _sns_for_actor(actor, sns_source, language, store, settings=settings)
    return ActorDetail(actor=actor, events=events, sns=sns_posts)


@router.get("/events", response_model=list[Event])
async def events(
    request: Request,
    actor_id: str | None = None,
    source: Literal["seed", "eventernote"] = "seed",
    language: Language = "original",
    cache: bool | None = None,
) -> list[Event]:
    settings = get_settings()
    store = await _store(cache, request)
    if actor_id and await _get_actor(actor_id, store) is None:
        raise HTTPException(status_code=404, detail="actor not found")
    if source == "eventernote":
        if not actor_id:
            raise HTTPException(status_code=400, detail="actor_id is required for eventernote source")
        actor = await _get_actor(actor_id, store)
        if actor is None or actor.eventernote_url is None:
            raise HTTPException(status_code=404, detail="eventernote source not configured")
        return await _events_for_actor(actor, source, language, store, strict=True, settings=settings)
    if store:
        cached = _filter_events(await store.list_events(actor_id, language, source), settings)
        if cached:
            return cached
    return _filter_events(list_events(actor_id, language), settings)


@router.get("/sns", response_model=list[SnsPost])
async def sns(
    request: Request,
    actor_id: str | None = None,
    source: Literal["seed", "x"] = "seed",
    language: Language = "original",
    cache: bool | None = None,
) -> list[SnsPost]:
    settings = get_settings()
    store = await _store(cache, request)
    if actor_id and await _get_actor(actor_id, store) is None:
        raise HTTPException(status_code=404, detail="actor not found")
    if source == "x":
        if not actor_id:
            raise HTTPException(status_code=400, detail="actor_id is required for x source")
        actor = await _get_actor(actor_id, store)
        if actor is None:
            raise HTTPException(status_code=404, detail="actor not found")
        return await _sns_for_actor(actor, source, language, store, strict=True, settings=settings)
    return _filter_posts(list_sns_posts(actor_id, language), settings)


@router.get("/sns/{post_id}", response_model=SnsPost)
async def sns_detail(post_id: str, request: Request, language: Language = "original", cache: bool | None = None) -> SnsPost:
    store = await _store(cache, request)
    post = await store.get_sns_post(post_id, language) if store else None
    if post is None:
        post = get_sns_post(post_id, language)
    if post is None:
        raise HTTPException(status_code=404, detail="sns post not found")
    return post


async def _events_for_actor(
    actor: Actor,
    event_source: str,
    language: Language,
    store: CacheStore | None,
    settings,
    strict: bool = False,
) -> list[Event]:
    if event_source != "eventernote":
        if store:
            cached_seed = _filter_events(await store.list_events(actor.id, language, "seed"), settings)
            if cached_seed:
                return cached_seed
        return _filter_events(list_events(actor.id, language), settings)
    if store:
        cached = _filter_events(await store.list_events(actor.id, language, "eventernote"), settings)
        if cached:
            return cached
    if actor.eventernote_url is None:
        return _filter_events(list_events(actor.id, language), settings)
    try:
        events = await fetch_eventernote_events(actor.id, str(actor.eventernote_url), limit=100)
    except httpx.HTTPError as error:
        if strict:
            raise HTTPException(status_code=502, detail=f"eventernote fetch failed: {error.__class__.__name__}") from error
        return _filter_events(list_events(actor.id, language), settings)
    translated = await translate_events(_filter_events(events, settings))
    if store:
        await store.upsert_events(translated)
    return [event_for_language(event, language) for event in translated] or _filter_events(list_events(actor.id, language), settings)


async def _sns_for_actor(
    actor: Actor,
    sns_source: str,
    language: Language,
    store: CacheStore | None,
    settings,
    strict: bool = False,
) -> list[SnsPost]:
    if sns_source != "x":
        return _filter_posts(list_sns_posts(actor.id, language), settings)
    if store:
        cached = _filter_posts(await store.list_sns_posts(actor.id, language, "x"), settings)
        if cached:
            return cached
    token = os.getenv("X_BEARER_TOKEN")
    if not token:
        if strict:
            raise HTTPException(status_code=503, detail="X_BEARER_TOKEN is not configured")
        return _filter_posts(list_sns_posts(actor.id, language), settings)
    try:
        posts = await fetch_x_posts(actor, token, past_days=settings.sns_fetch_past_days)
    except httpx.HTTPError as error:
        if strict:
            raise HTTPException(status_code=502, detail=f"x fetch failed: {error.__class__.__name__}") from error
        return _filter_posts(list_sns_posts(actor.id, language), settings)
    translated = await translate_posts(_filter_posts(posts, settings))
    if store:
        await store.upsert_sns_posts(translated)
    return [post_for_language(post, language) for post in translated] or _filter_posts(list_sns_posts(actor.id, language), settings)


async def _get_actor(actor_id: str, store: CacheStore | None) -> Actor | None:
    if store:
        cached = await store.get_actor(actor_id)
        if cached:
            return cached
    actor = get_actor(actor_id)
    if actor and store:
        await store.upsert_actor(actor)
    if actor:
        return actor
    return None


async def _store(cache: bool | None, request: Request | None) -> CacheStore | None:
    settings = get_settings()
    enabled = settings.data_cache_enabled if cache is None else cache
    if not enabled:
        return None
    env = request.scope.get("env") if request else None
    store = build_cache_store(settings, env)
    await store.init()
    return store


def _filter_events(events: list[Event], settings) -> list[Event]:
    return filter_events_in_window(
        events,
        past_days=settings.event_display_past_days,
        future_days=settings.event_display_future_days,
    )


def _filter_posts(posts: list[SnsPost], settings) -> list[SnsPost]:
    return filter_posts_in_window(posts, past_days=settings.sns_display_past_days)


def _sort_actors_by_romanized(actors: list[Actor]) -> list[Actor]:
    return sorted(actors, key=lambda actor: actor.romanized.casefold())
