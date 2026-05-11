from typing import Literal

from pydantic import BaseModel, Field, HttpUrl


class Photo(BaseModel):
    url: HttpUrl
    alt: str
    source: str


class SocialLink(BaseModel):
    platform: Literal["x", "instagram", "youtube", "website"]
    label: str
    url: HttpUrl


class Role(BaseModel):
    title: str
    character: str


class Actor(BaseModel):
    id: str
    name: str
    kana: str
    romanized: str
    agency: str
    birthday: str
    birthplace: str
    profile_url: HttpUrl
    official_photo: Photo = Field(alias="officialPhoto")
    gallery: list[Photo]
    specialties: list[str]
    hobbies: list[str]
    roles: list[Role]
    social_links: list[SocialLink] = Field(alias="socialLinks")
    eventernote_url: HttpUrl | None = Field(default=None, alias="eventernoteUrl")


class Event(BaseModel):
    id: str
    actor_id: str = Field(alias="actorId")
    title: str
    date: str
    category: Literal["live", "stage", "talk", "release", "broadcast", "other"]
    venue: str | None = None
    url: HttpUrl | None = None
    source: str


class SnsPost(BaseModel):
    id: str
    actor_id: str = Field(alias="actorId")
    platform: Literal["x", "instagram", "youtube", "website"]
    posted_at: str = Field(alias="postedAt")
    text: str
    url: HttpUrl
    kind: Literal["original", "repost", "reply", "quote", "story"] = "original"
    media_urls: list[HttpUrl] = Field(default_factory=list, alias="mediaUrls")


class ActorDetail(BaseModel):
    actor: Actor
    events: list[Event]
    sns: list[SnsPost]
