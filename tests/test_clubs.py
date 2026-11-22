def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"service": "club-event-service", "status": "UP", "version": "1.0.0"}


def test_create_club_matches_contract(client):
    resp = client.post("/clubs", json={"name": "Yazılım Kulübü", "description": "Yazılım geliştirme"})
    assert resp.status_code == 201
    body = resp.json()
    assert isinstance(body["id"], int)
    assert body["name"] == "Yazılım Kulübü"


def test_list_clubs(client):
    client.post("/clubs", json={"name": "Yazılım Kulübü"})
    client.post("/clubs", json={"name": "Robotik Kulübü"})
    resp = client.get("/clubs")
    assert resp.status_code == 200
    assert [c["name"] for c in resp.json()] == ["Yazılım Kulübü", "Robotik Kulübü"]


def test_duplicate_club_returns_409(client, club):
    resp = client.post("/clubs", json={"name": club["name"]})
    assert resp.status_code == 409
    assert resp.json()["error"] == "CLUB_ALREADY_EXISTS"


def test_invalid_club_returns_400_in_common_format(client):
    resp = client.post("/clubs", json={"name": "   "})
    assert resp.status_code == 400
    body = resp.json()
    assert body["error"] == "VALIDATION_ERROR"
    assert "name" in body["message"]


def test_get_missing_club_returns_404(client):
    resp = client.get("/clubs/999")
    assert resp.status_code == 404
    assert resp.json() == {"error": "CLUB_NOT_FOUND", "message": "Club 999 does not exist."}


def test_unknown_route_uses_common_error_format(client):
    resp = client.get("/does-not-exist")
    assert resp.status_code == 404
    assert resp.json()["error"] == "NOT_FOUND"


def test_dependency_health(client):
    resp = client.get("/health/dependencies")
    assert resp.status_code == 200
    assert resp.json()[0]["name"] == "ai-service"
    assert resp.json()[0]["status"] == "UP"
