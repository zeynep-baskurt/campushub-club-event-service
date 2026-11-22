from fastapi import Request

from app.clients.ai_client import AIClient


def get_ai_client(request: Request) -> AIClient:
    """main.py'de olusturulan tek AIClient ornegini verir (testlerde override edilir)."""
    return request.app.state.ai_client
