from fastapi import APIRouter, HTTPException

from app.schemas.voice_actor import Actor, ActorDetail, Event, SnsPost
from app.services.repository import get_actor, list_actors, list_events, list_sns_posts


router = APIRouter()


@router.get("/actors", response_model=list[Actor])
async def actors() -> list[Actor]:
    return list_actors()


@router.get("/actors/{actor_id}", response_model=ActorDetail)
async def actor_detail(actor_id: str) -> ActorDetail:
    actor = get_actor(actor_id)
    if actor is None:
        raise HTTPException(status_code=404, detail="actor not found")
    return ActorDetail(actor=actor, events=list_events(actor_id), sns=list_sns_posts(actor_id))


@router.get("/events", response_model=list[Event])
async def events(actor_id: str | None = None) -> list[Event]:
    if actor_id and get_actor(actor_id) is None:
        raise HTTPException(status_code=404, detail="actor not found")
    return list_events(actor_id)


@router.get("/sns", response_model=list[SnsPost])
async def sns(actor_id: str | None = None) -> list[SnsPost]:
    if actor_id and get_actor(actor_id) is None:
        raise HTTPException(status_code=404, detail="actor not found")
    return list_sns_posts(actor_id)
