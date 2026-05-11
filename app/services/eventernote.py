from html.parser import HTMLParser

import httpx

from app.schemas.voice_actor import Event


class EventernoteParser(HTMLParser):
    def __init__(self, actor_id: str):
        super().__init__()
        self.actor_id = actor_id
        self.events: list[Event] = []
        self._href: str | None = None
        self._text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "a":
            return
        attrs_dict = dict(attrs)
        href = attrs_dict.get("href")
        if href and "/events/" in href:
            self._href = href
            self._text = []

    def handle_data(self, data: str) -> None:
        if self._href:
            self._text.append(data.strip())

    def handle_endtag(self, tag: str) -> None:
        if tag != "a" or not self._href:
            return
        title = " ".join(part for part in self._text if part)
        if title:
            event_id = self._href.rstrip("/").split("/")[-1]
            url = self._href if self._href.startswith("https://") else f"https://www.eventernote.com{self._href}"
            self.events.append(
                Event(
                    id=f"eventernote-{event_id}",
                    actorId=self.actor_id,
                    title=title,
                    date="未定",
                    category="other",
                    venue=None,
                    url=url,
                    source="eventernote",
                )
            )
        self._href = None
        self._text = []


async def fetch_eventernote_events(actor_id: str, url: str) -> list[Event]:
    async with httpx.AsyncClient(timeout=8.0, follow_redirects=True) as client:
        response = await client.get(url, headers={"User-Agent": "nsy-station/0.1"})
        response.raise_for_status()
    parser = EventernoteParser(actor_id)
    parser.feed(response.text)
    return parser.events
