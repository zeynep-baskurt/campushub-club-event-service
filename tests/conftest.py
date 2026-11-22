import os
import tempfile

# app import edilmeden once: gercek DB dosyasina dokunma, AI'ya gercek istek atma
os.environ["DATABASE_URL"] = "sqlite:///" + os.path.join(tempfile.gettempdir(), "campushub_events_test.db")
os.environ["AI_SERVICE_URL"] = "http://ai-service.test"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.clients.ai_client import ClassificationResult
from app.database import Base, get_db
from app.dependencies import get_ai_client
from app.main import app


class FakeAIClient:
    """AI Service yerine gecen sahte client. Testler sonucu degistirebilir."""

    base_url = "http://fake-ai"

    def __init__(self):
        self.result = ClassificationResult(category="TECHNOLOGY", confidence=0.91, source="ai")
        self.calls: list[str] = []

    async def classify(self, text):
        self.calls.append(text)
        return self.result

    async def check_health(self):
        return "UP", None


@pytest.fixture
def db_session():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    session = Session()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


@pytest.fixture
def fake_ai():
    return FakeAIClient()


@pytest.fixture
def client(db_session, fake_ai):
    app.dependency_overrides[get_db] = lambda: db_session
    app.dependency_overrides[get_ai_client] = lambda: fake_ai
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def club(client):
    resp = client.post("/clubs", json={"name": "Yazılım Kulübü", "description": "Yazılım topluluğu"})
    assert resp.status_code == 201
    return resp.json()
