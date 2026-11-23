import logging

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.clients.ai_client import AIClient, CATEGORIES
from app.errors import ApiError, ConflictError, NotFoundError
from app.repositories.repository import ClubRepository, EventRepository
from app.schemas.schemas import ClubCreate, EventCreate

logger = logging.getLogger(__name__)


class ClubService:
    @staticmethod
    def create_club(db: Session, club_data: ClubCreate):
        if ClubRepository.get_club_by_name(db, club_data.name):
            raise ConflictError("CLUB_ALREADY_EXISTS", f"Club '{club_data.name}' already exists.")
        try:
            return ClubRepository.create_club(db, club_data)
        except IntegrityError:
            # Ayni anda gelen iki istek unique kisitina takilabilir
            db.rollback()
            raise ConflictError("CLUB_ALREADY_EXISTS", f"Club '{club_data.name}' already exists.")

    @staticmethod
    def get_all_clubs(db: Session):
        return ClubRepository.get_all_clubs(db)

    @staticmethod
    def get_club_by_id(db: Session, club_id: int):
        club = ClubRepository.get_club_by_id(db, club_id)
        if not club:
            raise NotFoundError("CLUB_NOT_FOUND", f"Club {club_id} does not exist.")
        return club


class EventService:
    @staticmethod
    def build_classification_text(event_data: EventCreate) -> str:
        # Baslik + aciklama birlikte gonderilir; aciklama bos olsa bile baslik siniflandirilabilir.
        parts = [event_data.title, event_data.description or ""]
        return ". ".join(p.strip() for p in parts if p and p.strip())

    @staticmethod
    async def create_event(db: Session, event_data: EventCreate, ai_client: AIClient):
        ClubService.get_club_by_id(db, event_data.club_id)

        result = await ai_client.classify(EventService.build_classification_text(event_data))
        logger.info(
            "Event '%s' classified as %s (confidence=%s, source=%s)",
            event_data.title, result.category, result.confidence, result.source,
        )
        return EventRepository.create_event(
            db, event_data, category=result.category, category_confidence=result.confidence
        )

    @staticmethod
    def get_event_by_id(db: Session, event_id: int):
        event = EventRepository.get_event_by_id(db, event_id)
        if not event:
            raise NotFoundError("EVENT_NOT_FOUND", f"Event {event_id} does not exist.")
        return event

    @staticmethod
    def list_events(db: Session, club_id: int | None = None, category: str | None = None):
        if category:
            category = category.upper()
            if category not in CATEGORIES:
                raise ApiError(
                    400, "INVALID_CATEGORY",
                    f"Unknown category '{category}'. Allowed: {', '.join(sorted(CATEGORIES))}.",
                )
        if club_id is not None:
            ClubService.get_club_by_id(db, club_id)
        return EventRepository.get_all_events(db, category=category, club_id=club_id)
