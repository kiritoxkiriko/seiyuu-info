import asyncio

import httpx

from app.services.eventernote import EventernoteParser, fetch_eventernote_events, page_url


def test_eventernote_parser_reads_events_in_descending_date_order():
    parser = EventernoteParser("aoki-hina")
    parser.feed(
        """
        <ul class="gb_event_list">
          <li class="clearfix">
            <div class="date"><p class="day6">2026-05-09 (<span>土</span>)</p></div>
            <div class="event">
              <h4><a href="/events/454675">昼の部 LIVE</a></h4>
              <div class="place">会場: <a href="/places/1">大阪ホール</a></div>
            </div>
          </li>
          <li class="clearfix">
            <div class="date"><p class="day0">2026-08-09 (<span>日</span>)</p></div>
            <div class="event">
              <h4><a href="/events/466544">LuckyFes’26 DAY2</a></h4>
              <div class="place">会場: <a href="/places/2">国営ひたち海浜公園</a></div>
            </div>
          </li>
        </ul>
        """
    )

    events = sorted(parser.events, key=lambda event: event.date, reverse=True)

    assert [event.date for event in events] == ["2026-08-09", "2026-05-09"]
    assert events[0].title == "LuckyFes’26 DAY2"
    assert events[0].venue == "国営ひたち海浜公園"
    assert str(events[0].url) == "https://www.eventernote.com/events/466544"


def test_page_url_adds_limit_and_page_query():
    assert page_url("https://www.eventernote.com/actors/name/1/events", 2) == "https://www.eventernote.com/actors/name/1/events?limit=20&page=2"
    assert (
        page_url("https://www.eventernote.com/actors/name/1/events?actor_id=1&limit=30", 3)
        == "https://www.eventernote.com/actors/name/1/events?actor_id=1&limit=30&page=3"
    )


def test_fetch_eventernote_events_paginates_until_existing_event(monkeypatch):
    requested_urls = []

    def handler(request: httpx.Request) -> httpx.Response:
        requested_urls.append(str(request.url))
        if "page=2" in str(request.url):
            return httpx.Response(
                200,
                text=events_html(
                    [
                        ("2026-05-02", "/events/old", "Old Event"),
                        ("2026-05-01", "/events/older", "Older Event"),
                    ]
                ),
            )
        return httpx.Response(
            200,
            text=events_html(
                [
                    ("2026-05-04", "/events/new-2", "New Event 2"),
                    ("2026-05-03", "/events/new-1", "New Event 1"),
                ]
            ),
        )

    class MockAsyncClient(httpx.AsyncClient):
        def __init__(self, *args, **kwargs):
            super().__init__(transport=httpx.MockTransport(handler), follow_redirects=True)

    monkeypatch.setattr("app.services.eventernote.httpx.AsyncClient", MockAsyncClient)

    events = asyncio.run(
        fetch_eventernote_events(
            "aoki-hina",
            "https://www.eventernote.com/actors/name/1/events",
            known_ids={"eventernote-old"},
            stop_before_date="2026-05-02",
            max_pages=5,
        )
    )

    assert [event.id for event in events] == ["eventernote-new-2", "eventernote-new-1"]
    assert requested_urls == [
        "https://www.eventernote.com/actors/name/1/events",
        "https://www.eventernote.com/actors/name/1/events?limit=20&page=2",
    ]


def events_html(events: list[tuple[str, str, str]]) -> str:
    items = []
    for event_date, href, title in events:
        items.append(
            f"""
            <li class="clearfix">
              <div class="date"><p class="day6">{event_date} (<span>土</span>)</p></div>
              <div class="event">
                <h4><a href="{href}">{title}</a></h4>
                <div class="place">会場: <a href="/places/1">東京ホール</a></div>
              </div>
            </li>
            """
        )
    return f"<ul class=\"gb_event_list\">{''.join(items)}</ul>"
