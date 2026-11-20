from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.schemas import ClubCreate, ClubResponse
from app.services.service import ClubService

router = APIRouter(prefix="/clubs", tags=["Clubs"])


@router.post("", response_model=ClubResponse, status_code=status.HTTP_201_CREATED)
def create_club(club: ClubCreate, db: Session = Depends(get_db)):
    return ClubService.create_club(db, club)


@router.get("", response_model=list[ClubResponse])
def list_clubs(db: Session = Depends(get_db)):
    return ClubService.get_all_clubs(db)