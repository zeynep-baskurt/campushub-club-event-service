"""Grup 5 - AI Inference Service ile konusan HTTP client.

Sozlesme (proje dokumani Bolum 13):
    POST {AI_SERVICE_URL}/ai/classify
    Input : {"text": "..."}
    Output: {"category": "TECHNOLOGY", "confidence": 0.91}

Dayaniklilik (Bolum 37-38): AI servisi kapaliysa, timeout olursa veya bozuk cevap
donerse etkinlik olusturma ENGELLENMEZ. Kategori "OTHER" olarak kaydedilir ve
servis cokmez.
"""
import logging
from dataclasses import dataclass

import httpx

logger = logging.getLogger(__name__)

CATEGORIES = {"TECHNOLOGY", "SPORT", "ART", "CAREER", "SOCIAL", "OTHER"}
FALLBACK_CATEGORY = "OTHER"


@dataclass(frozen=True)
class ClassificationResult:
    category: str
    confidence: float | None
    # "ai" -> AI servisi cevap verdi, "fallback" -> AI'ya ulasilamadi / gecersiz cevap
    source: str

    @classmethod
    def fallback(cls) -> "ClassificationResult":
        return cls(category=FALLBACK_CATEGORY, confidence=None, source="fallback")


class AIClient:
    def __init__(
        self,
        base_url: str,
        timeout_seconds: float = 3.0,
        enabled: bool = True,
        transport: httpx.AsyncBaseTransport | None = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = httpx.Timeout(timeout_seconds)
        self.enabled = enabled
        # transport testlerde sahte AI servisi enjekte etmek icin kullanilir
        self._transport = transport

    def _client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout, transport=self._transport)

    async def classify(self, text: str | None) -> ClassificationResult:
        if not self.enabled or not text or not text.strip():
            return ClassificationResult.fallback()

        try:
            async with self._client() as client:
                response = await client.post("/ai/classify", json={"text": text})
        except httpx.TimeoutException:
            logger.warning("AI service timed out after %ss", self.timeout.read)
            return ClassificationResult.fallback()
        except httpx.HTTPError as exc:
            logger.warning("AI service unreachable: %s", exc)
            return ClassificationResult.fallback()

        if response.status_code != 200:
            logger.warning("AI service returned HTTP %s: %s", response.status_code, response.text[:200])
            return ClassificationResult.fallback()

        return self._parse(response)

    @staticmethod
    def _parse(response: httpx.Response) -> ClassificationResult:
        try:
            data = response.json()
        except ValueError:
            logger.warning("AI service returned non-JSON body")
            return ClassificationResult.fallback()

        if not isinstance(data, dict):
            logger.warning("AI service returned unexpected body: %r", data)
            return ClassificationResult.fallback()

        category = str(data.get("category", "")).strip().upper()
        if category not in CATEGORIES:
            logger.warning("AI service returned unknown category %r", data.get("category"))
            return ClassificationResult.fallback()

        confidence = data.get("confidence")
        try:
            confidence = float(confidence) if confidence is not None else None
        except (TypeError, ValueError):
            confidence = None
        if confidence is not None and not 0.0 <= confidence <= 1.0:
            confidence = None

        return ClassificationResult(category=category, confidence=confidence, source="ai")

    async def check_health(self) -> tuple[str, str | None]:
        """AI servisinin /health endpoint'ini yoklar. ("UP"|"DOWN", detay) doner."""
        if not self.enabled:
            return "DISABLED", None
        try:
            async with self._client() as client:
                response = await client.get("/health")
        except httpx.HTTPError as exc:
            return "DOWN", type(exc).__name__
        if response.status_code == 200:
            return "UP", None
        return "DOWN", f"HTTP {response.status_code}"
