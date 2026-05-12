from app.services.eventernote import EventernoteParser


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
