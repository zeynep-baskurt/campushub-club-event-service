from app.clients.ai_client import ClassificationResult

EVENT = {
    "title": "Python ile Yapay Zeka Atölyesi",
    "description": "Başlangıç seviyesinde Python ve yapay zeka uygulamaları.",
    "startTime": "2026-12-10T10:00:00",
    "capacity": 100,
}


def _create(client, club_id, **overrides):
    return client.post("/events", json={**EVENT, "clubId": club_id, **overrides})


def test_create_event_is_classified_by_ai(client, club, fake_ai):
    resp = _create(client, club["id"])
    assert resp.status_code == 201
    body = resp.json()
    # Dokumandaki sozlesme alanlari
    assert body["clubId"] == club["id"]
    assert body["title"] == EVENT["title"]
    assert body["capacity"] == 100
    # AI entegrasyonu
    assert body["category"] == "TECHNOLOGY"
    assert body["categoryConfidence"] == 0.91
    assert body["clubName"] == club["name"]
    # AI'ya baslik + aciklama gonderildi
    assert fake_ai.calls == [f"{EVENT['title']}. {EVENT['description']}"]


def test_event_is_still_created_when_ai_is_down(client, club, fake_ai):
    fake_ai.result = ClassificationResult.fallback()
    resp = _create(client, club["id"])
    assert resp.status_code == 201
    assert resp.json()["category"] == "OTHER"
    assert resp.json()["categoryConfidence"] is None


def test_create_event_for_missing_club_returns_404_and_skips_ai(client, fake_ai):
    resp = _create(client, 999)
    assert resp.status_code == 404
    assert resp.json()["error"] == "CLUB_NOT_FOUND"
    assert fake_ai.calls == []


def test_create_event_invalid_input_returns_400(client, club):
    resp = _create(client, club["id"], capacity=0, startTime="yarın")
    assert resp.status_code == 400
    body = resp.json()
    assert body["error"] == "VALIDATION_ERROR"
    assert "capacity" in body["message"] and "startTime" in body["message"]


def test_get_event_for_registration_service(client, club):
    event_id = _create(client, club["id"]).json()["id"]
    resp = client.get(f"/events/{event_id}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] == event_id
    assert body["title"] == EVENT["title"]
    assert body["capacity"] == 100


def test_get_missing_event_returns_contract_error(client):
    resp = client.get("/events/31")
    assert resp.status_code == 404
    assert resp.json() == {"error": "EVENT_NOT_FOUND", "message": "Event 31 does not exist."}


def test_list_events_filters(client, club, fake_ai):
    other = client.post("/clubs", json={"name": "Robotik Kulübü"}).json()
    _create(client, club["id"])
    fake_ai.result = ClassificationResult(category="SPORT", confidence=0.8, source="ai")
    _create(client, other["id"], title="Robot Yarışması")

    assert len(client.get("/events").json()) == 2
    robotik = client.get(f"/clubs/{other['id']}/events").json()
    assert [e["title"] for e in robotik] == ["Robot Yarışması"]
    assert [e["title"] for e in client.get(f"/events?clubId={other['id']}").json()] == ["Robot Yarışması"]
    assert [e["category"] for e in client.get("/events?category=technology").json()] == ["TECHNOLOGY"]


def test_list_events_bad_category_and_missing_club(client):
    assert client.get("/events?category=FOOD").json()["error"] == "INVALID_CATEGORY"
    assert client.get("/clubs/999/events").status_code == 404
