from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.schemas import ClubCreate, ClubResponse, EventResponse
from app.services.service import ClubService, EventService

router = APIRouter(prefix="/clubs", tags=["Clubs"])

_ERRORS = {
    400: {"description": "Invalid input (VALIDATION_ERROR)"},
    404: {"description": "Club not found (CLUB_NOT_FOUND)"},
    409: {"description": "Club name already used (CLUB_ALREADY_EXISTS)"},
}


@router.post(
    "",
    response_model=ClubResponse,
    status_code=status.HTTP_201_CREATED,
    responses={k: _ERRORS[k] for k in (400, 409)},
)
def create_club(club: ClubCreate, db: Session = Depends(get_db)):
    return ClubService.create_club(db, club)


@router.get("", response_model=list[ClubResponse])
def list_clubs(db: Session = Depends(get_db)):
    return ClubService.get_all_clubs(db)


@router.get("/{club_id}", response_model=ClubResponse, responses={404: _ERRORS[404]})
def get_club(club_id: int, db: Session = Depends(get_db)):
    return ClubService.get_club_by_id(db, club_id)


@router.get("/{club_id}/events", response_model=list[EventResponse], responses={404: _ERRORS[404]})
def list_club_events(club_id: int, db: Session = Depends(get_db)):
    return EventService.list_events(db, club_id=club_id)
