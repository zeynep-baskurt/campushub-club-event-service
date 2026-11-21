"""Servis ayarlari. Tum degerler environment variable'lardan (.env) okunur."""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "club-event-service"
    app_version: str = "1.0.0"
    app_port: int = 8003

    database_url: str = "sqlite:///./campushub_events.db"

    # Grup 5 - AI Inference Service
    ai_service_url: str = "http://ai-service:8005"
    ai_timeout_seconds: float = 3.0
    ai_enabled: bool = True

    # Gateway / web arayuzu icin izin verilen origin'ler (virgulle ayrilmis)
    cors_origins: str = "*"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
