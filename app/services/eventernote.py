import re
from html.parser import HTMLParser
from typing import Literal

import httpx

from app.schemas.voice_actor import Event
from app.services.repository import sort_events_desc


DATE_PATTERN = re.compile(r"(\d{4}-\d{2}-\d{2})")
EVENT_BASE_URL = "https://www.eventernote.com"


class EventernoteParser(HTMLParser):
    def __init__(self, actor_id: str):
        super().__init__()
        self.actor_id = actor_id
        self.events: list[Event] = []
        self._current: dict[str, str] | None = None
        self._capture: str | None = None
        self._text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = dict(attrs)
        class_name = attrs_dict.get("class", "")
        if tag == "li" and "clearfix" in class_name:
            self._current = {}
        if self._current is None:
            return
        if tag == "p" and "day" in class_name:
            self._capture = "date"
            self._text = []
        if tag == "a":
            href = attrs_dict.get("href")
            if href and href.startswith("/events/") and "title" not in self._current:
                self._current["href"] = href
                self._capture = "title"
                self._text = []
            elif self._capture == "venue":
                self._text = []
        if tag == "div" and "place" in class_name:
            self._capture = "venue"
            self._text = []

    def handle_data(self, data: str) -> None:
        if self._capture:
            self._text.append(data.strip())

    def handle_endtag(self, tag: str) -> None:
        if self._current is None:
            return
        text = " ".join(part for part in self._text if part)
        if tag == "p" and self._capture == "date":
            match = DATE_PATTERN.search(text)
            if match:
                self._current["date"] = match.group(1)
            self._capture = None
        if tag == "a" and self._capture == "title":
            self._current["title"] = text
            self._capture = None
        if tag == "div" and self._capture == "venue":
            venue = text.replace("会場:", "").strip()
            if venue and not venue.startswith("開場") and "venue" not in self._current:
                self._current["venue"] = venue
            self._capture = None
        if tag == "li":
            self._append_current()
            self._current = None
            self._capture = None
        if self._capture is None:
            self._text = []

    def _append_current(self) -> None:
        if not self._current:
            return
        title = self._current.get("title")
        href = self._current.get("href")
        if not title or not href:
            return
        event_id = href.rstrip("/").split("/")[-1]
        url = href if href.startswith("https://") else f"{EVENT_BASE_URL}{href}"
        self.events.append(
            Event(
                id=f"eventernote-{event_id}",
                actorId=self.actor_id,
                title=title,
                date=self._current.get("date", "未定"),
                category=guess_category(title),
                venue=self._current.get("venue"),
                url=url,
                source="eventernote",
            )
        )


async def fetch_eventernote_events(actor_id: str, url: str, limit: int = 30) -> list[Event]:
    last_error: Exception | None = None
    async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
        for _ in range(2):
            try:
                response = await client.get(url, headers={"User-Agent": "nsy-station/0.1"})
                response.raise_for_status()
                break
            except httpx.HTTPError as error:
                last_error = error
        else:
            if last_error:
                raise last_error
    parser = EventernoteParser(actor_id)
    parser.feed(response.text)
    return sort_events_desc(parser.events)[:limit]


def guess_category(title: str) -> Literal["live", "stage", "talk", "release", "broadcast", "other"]:
    lowered = title.lower()
    if any(keyword in lowered for keyword in ["live", "fes", "ライブ", "歌謡祭"]):
        return "live"
    if any(keyword in title for keyword in ["朗読劇", "舞台"]):
        return "stage"
    if any(keyword in lowered for keyword in ["talk", "トーク", "集会", "ステージ"]):
        return "talk"
    if any(keyword in title for keyword in ["配信", "番組"]):
        return "broadcast"
    return "other"
