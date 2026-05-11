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


def test_sns_filters_reposts_and_replies():
    response = client.get("/api/v1/sns?actor_id=aoki-hina")
    assert response.status_code == 200
    kinds = {post["kind"] for post in response.json()}
    assert "repost" not in kinds
    assert "reply" not in kinds


def test_unknown_actor_returns_404():
    response = client.get("/api/v1/actors/unknown")
    assert response.status_code == 404
