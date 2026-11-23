import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.clients.ai_client import AIClient
from app.config import get_settings
from app.database import Base, engine
from app.errors import register_error_handlers
from app.routers import club_router, event_router, health_router


def create_app() -> FastAPI:
    settings = get_settings()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

    Base.metadata.create_all(bind=engine)

    app = FastAPI(title="CampusHub Club & Event Service", version=settings.app_version)

    app.state.ai_client = AIClient(
        base_url=settings.ai_service_url,
        timeout_seconds=settings.ai_timeout_seconds,
        enabled=settings.ai_enabled,
    )

    origins = settings.cors_origin_list
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials="*" not in origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_error_handlers(app)

    app.include_router(health_router.router)
    app.include_router(club_router.router)
    app.include_router(event_router.router)
    return app


app = create_app()
