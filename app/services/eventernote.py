import re
from html.parser import HTMLParser
from typing import Literal
from urllib.parse import urlencode, urlsplit, urlunsplit, parse_qsl

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


async def fetch_eventernote_events(
    actor_id: str,
    url: str,
    limit: int = 30,
    known_ids: set[str] | None = None,
    stop_before_date: str | None = None,
    max_pages: int = 10,
) -> list[Event]:
    collected: list[Event] = []
    seen_ids: set[str] = set()
    known_event_ids = known_ids or set()
    async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
        for page in range(1, max_pages + 1):
            response = await _fetch_eventernote_page(client, page_url(url, page))
            parser = EventernoteParser(actor_id)
            parser.feed(response.text)
            page_events = sort_events_desc(parser.events)
            if not page_events:
                break

            should_stop = False
            for event in page_events:
                if event.id in seen_ids:
                    continue
                seen_ids.add(event.id)
                if event.id in known_event_ids:
                    should_stop = True
                    continue
                if stop_before_date and _known_dated_event_is_old(event.date, stop_before_date):
                    should_stop = True
                    continue
                collected.append(event)
                if len(collected) >= limit:
                    should_stop = True
                    break
            if should_stop:
                break
    return sort_events_desc(collected)[:limit]


async def _fetch_eventernote_page(client: httpx.AsyncClient, url: str) -> httpx.Response:
    last_error: Exception | None = None
    for _ in range(2):
        try:
            response = await client.get(url, headers={"User-Agent": "nsy-station/0.1"})
            response.raise_for_status()
            return response
        except httpx.HTTPError as error:
            last_error = error
    if last_error:
        raise last_error
    raise RuntimeError("eventernote fetch failed")


def page_url(url: str, page: int) -> str:
    if page <= 1:
        return url
    parts = urlsplit(url)
    query = dict(parse_qsl(parts.query, keep_blank_values=True))
    query["limit"] = query.get("limit", "20")
    query["page"] = str(page)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment))


def _known_dated_event_is_old(event_date: str, stop_before_date: str) -> bool:
    if event_date == "未定":
        return False
    return event_date <= stop_before_date


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
