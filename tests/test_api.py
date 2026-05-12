from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_returns_ok():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_list_actors_contains_configured_names():
    response = client.get("/api/v1/actors")
    assert response.status_code == 200
    names = {actor["name"] for actor in response.json()}
    assert {"羊宮妃那", "青木陽菜"} == names


def test_actor_detail_includes_events_and_sns():
    response = client.get("/api/v1/actors/aoki-hina")
    assert response.status_code == 200
    payload = response.json()
    assert payload["actor"]["id"] == "aoki-hina"
    assert len(payload["events"]) >= 1
    assert len(payload["sns"]) >= 1


def test_events_are_returned_in_descending_date_order():
    response = client.get("/api/v1/events?actor_id=aoki-hina")
    assert response.status_code == 200
    dates = [event["date"] for event in response.json()]
    assert dates == sorted(dates, reverse=True)


def test_sns_filters_reposts_and_replies():
    response = client.get("/api/v1/sns?actor_id=aoki-hina")
    assert response.status_code == 200
    posts = response.json()
    kinds = {post["kind"] for post in posts}
    platforms = {post["platform"] for post in posts}
    assert "repost" not in kinds
    assert "reply" not in kinds
    assert "instagram" not in platforms
    dates = [post["postedAt"] for post in posts]
    assert dates == sorted(dates, reverse=True)


def test_actor_detail_accepts_language_switch():
    response = client.get("/api/v1/actors/aoki-hina?language=zh")
    assert response.status_code == 200
    payload = response.json()
    assert payload["events"][0]["language"] == "zh"
    assert payload["sns"][0]["language"] == "zh"


def test_actor_detail_with_x_source_falls_back_without_token(monkeypatch):
    monkeypatch.delenv("X_BEARER_TOKEN", raising=False)
    response = client.get("/api/v1/actors/aoki-hina?sns_source=x")
    assert response.status_code == 200
    assert len(response.json()["sns"]) >= 1


def test_explicit_x_sns_source_requires_token(monkeypatch):
    monkeypatch.delenv("X_BEARER_TOKEN", raising=False)
    response = client.get("/api/v1/sns?actor_id=aoki-hina&source=x")
    assert response.status_code == 503


def test_unknown_actor_returns_404():
    response = client.get("/api/v1/actors/unknown")
    assert response.status_code == 404
