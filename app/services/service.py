import os
import httpx
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.repositories.repository import ClubRepository, EventRepository
from app.schemas.schemas import ClubCreate, EventCreate

AI_SERVICE_URL = os.getenv("AI_SERVICE_URL", "http://ai-service:8000")


class ClubService:
    @staticmethod
    def create_club(db: Session, club_data: ClubCreate):
        existing = ClubRepository.get_club_by_name(db, club_data.name)
        if existing:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "CLUB_ALREADY_EXISTS",
                    "message": f"Club '{club_data.name}' already exists."
                }
            )
        return ClubRepository.create_club(db, club_data)

    @staticmethod
    def get_all_clubs(db: Session):
        return ClubRepository.get_all_clubs(db)


class EventService:
    @staticmethod
    async def classify_event_category(description: str | None) -> str:
        if not description:
            return "GENERAL"
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                response = await client.post(
                    f"{AI_SERVICE_URL}/ai/classify",
                    json={"text": description}
                )
                if response.status_code == 200:
                    data = response.json()
                    return data.get("category", "GENERAL")
        except Exception:
            # Grup 5 AI servisi kapalıysa veya zaman aşımına uğrarsa servis çökmez
            pass
        return "GENERAL"

    @staticmethod
    async def create_event(db: Session, event_data: EventCreate):
        club = ClubRepository.get_club_by_id(db, event_data.club_id)
        if not club:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "CLUB_NOT_FOUND",
                    "message": f"Club {event_data.club_id} does not exist."
                }
            )

        category = await EventService.classify_event_category(event_data.description)
        return EventRepository.create_event(db, event_data, category=category)

    @staticmethod
    def get_event_by_id(db: Session, event_id: int):
        event = EventRepository.get_event_by_id(db, event_id)
        if not event:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "EVENT_NOT_FOUND",
                    "message": f"Event {event_id} does not exist."
                }
            )
        return event