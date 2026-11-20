from sqlalchemy.orm import Session
from app.models.models import Club, Event
from app.schemas.schemas import ClubCreate, EventCreate


class ClubRepository:
    @staticmethod
    def create_club(db: Session, club_data: ClubCreate) -> Club:
        db_club = Club(
            name=club_data.name,
            description=club_data.description
        )
        db.add(db_club)
        db.commit()
        db.refresh(db_club)
        return db_club

    @staticmethod
    def get_all_clubs(db: Session) -> list[Club]:
        return db.query(Club).all()

    @staticmethod
    def get_club_by_id(db: Session, club_id: int) -> Club | None:
        return db.query(Club).filter(Club.id == club_id).first()

    @staticmethod
    def get_club_by_name(db: Session, name: str) -> Club | None:
        return db.query(Club).filter(Club.name == name).first()


class EventRepository:
    @staticmethod
    def create_event(db: Session, event_data: EventCreate, category: str = "GENERAL") -> Event:
        db_event = Event(
            club_id=event_data.club_id,
            title=event_data.title,
            description=event_data.description,
            start_time=event_data.start_time,
            capacity=event_data.capacity,
            category=category
        )
        db.add(db_event)
        db.commit()
        db.refresh(db_event)
        return db_event

    @staticmethod
    def get_event_by_id(db: Session, event_id: int) -> Event | None:
        return db.query(Event).filter(Event.id == event_id).first()