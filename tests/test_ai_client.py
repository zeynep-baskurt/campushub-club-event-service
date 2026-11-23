"""AIClient'in AI Service'in her turlu davranisina dayanikliligini test eder."""
import asyncio

import httpx

from app.clients.ai_client import AIClient


def make_client(handler, **kwargs) -> AIClient:
    return AIClient("http://ai-service.test", transport=httpx.MockTransport(handler), **kwargs)


def classify(client: AIClient, text="Python atölyesi"):
    return asyncio.run(client.classify(text))


def test_success_sends_contract_request():
    seen = {}

    def handler(request: httpx.Request):
        seen["path"] = request.url.path
        seen["body"] = request.read().decode()
        return httpx.Response(200, json={"category": "TECHNOLOGY", "confidence": 0.94})

    result = classify(make_client(handler))
    assert (result.category, result.confidence, result.source) == ("TECHNOLOGY", 0.94, "ai")
    assert seen["path"] == "/ai/classify"
    assert '"text"' in seen["body"]


def test_lowercase_category_is_normalized():
    result = classify(make_client(lambda r: httpx.Response(200, json={"category": "sport", "confidence": 0.7})))
    assert result.category == "SPORT"


def test_timeout_falls_back():
    def handler(request):
        raise httpx.ReadTimeout("too slow", request=request)

    result = classify(make_client(handler))
    assert (result.category, result.source) == ("OTHER", "fallback")


def test_connection_refused_falls_back():
    def handler(request):
        raise httpx.ConnectError("refused", request=request)

    assert classify(make_client(handler)).source == "fallback"


def test_server_error_falls_back():
    assert classify(make_client(lambda r: httpx.Response(500, text="boom"))).source == "fallback"


def test_unknown_category_falls_back():
    result = classify(make_client(lambda r: httpx.Response(200, json={"category": "FOOD", "confidence": 0.9})))
    assert result.category == "OTHER"


def test_non_json_falls_back():
    assert classify(make_client(lambda r: httpx.Response(200, text="not json"))).source == "fallback"


def test_bad_confidence_is_dropped_but_category_kept():
    result = classify(make_client(lambda r: httpx.Response(200, json={"category": "ART", "confidence": 7})))
    assert (result.category, result.confidence) == ("ART", None)


def test_empty_text_or_disabled_skips_network():
    def handler(request):
        raise AssertionError("should not call AI")

    assert classify(make_client(handler), text="  ").source == "fallback"
    assert classify(make_client(handler, enabled=False)).source == "fallback"


def test_health_check():
    up = make_client(lambda r: httpx.Response(200, json={"status": "UP"}))
    assert asyncio.run(up.check_health()) == ("UP", None)

    def handler(request):
        raise httpx.ConnectError("refused", request=request)

    assert asyncio.run(make_client(handler).check_health())[0] == "DOWN"
