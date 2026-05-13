from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


Language = Literal["original", "zh"]


class Photo(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    url: str
    alt: str
    source: str


class SocialLink(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    platform: Literal["x", "instagram", "youtube", "website"]
    label: str
    url: HttpUrl


class Role(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    title: str
    character: str


class Actor(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    name: str
    kana: str
    romanized: str
    agency: str
    birthday: str
    birthplace: str
    bio: str | None = None
    profile_url: HttpUrl
    official_photo: Photo = Field(alias="officialPhoto")
    gallery: list[Photo]
    specialties: list[str]
    hobbies: list[str]
    roles: list[Role]
    social_links: list[SocialLink] = Field(alias="socialLinks")
    eventernote_url: HttpUrl | None = Field(default=None, alias="eventernoteUrl")


class Event(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    actor_id: str = Field(alias="actorId")
    title: str
    title_zh: str | None = Field(default=None, alias="titleZh")
    date: str
    category: Literal["live", "stage", "talk", "release", "broadcast", "other"]
    venue: str | None = None
    venue_zh: str | None = Field(default=None, alias="venueZh")
    url: HttpUrl | None = None
    source: str
    language: Language = "original"


class SnsPost(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    actor_id: str = Field(alias="actorId")
    platform: Literal["x", "instagram", "youtube", "website"]
    posted_at: str = Field(alias="postedAt")
    text: str
    text_zh: str | None = Field(default=None, alias="textZh")
    detail_text: str | None = Field(default=None, alias="detailText")
    detail_text_zh: str | None = Field(default=None, alias="detailTextZh")
    url: HttpUrl
    kind: Literal["original", "repost", "reply", "quote", "story"] = "original"
    media_urls: list[HttpUrl] = Field(default_factory=list, alias="mediaUrls")
    language: Language = "original"


class ActorDetail(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    actor: Actor
    events: list[Event]
    sns: list[SnsPost]
