from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.clients.ai_client import AIClient
from app.database import get_db
from app.dependencies import get_ai_client
from app.schemas.schemas import EventCreate, EventResponse
from app.services.service import EventService

router = APIRouter(prefix="/events", tags=["Events"])


@router.post(
    "",
    response_model=EventResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"description": "Invalid input (VALIDATION_ERROR)"},
        404: {"description": "Club not found (CLUB_NOT_FOUND)"},
    },
    summary="Create an event (category is assigned by the AI Service)",
)
async def create_event(
    event: EventCreate,
    db: Session = Depends(get_db),
    ai_client: AIClient = Depends(get_ai_client),
):
    return await EventService.create_event(db, event, ai_client)


@router.get("", response_model=list[EventResponse])
def list_events(
    club_id: Optional[int] = Query(None, alias="clubId"),
    category: Optional[str] = Query(None, description="TECHNOLOGY, SPORT, ART, CAREER, SOCIAL, OTHER"),
    db: Session = Depends(get_db),
):
    return EventService.list_events(db, club_id=club_id, category=category)


@router.get(
    "/{event_id}",
    response_model=EventResponse,
    responses={404: {"description": "Event not found (EVENT_NOT_FOUND)"}},
    summary="Get an event (used by Registration Service to check existence and capacity)",
)
def get_event(event_id: int, db: Session = Depends(get_db)):
    return EventService.get_event_by_id(db, event_id)
