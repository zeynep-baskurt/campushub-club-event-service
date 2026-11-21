from sqlalchemy.orm import Session
from app.models.models import Club, Event, ClubMembership, EventRegistration
from app.schemas.schemas import (
    ClubCreate,
    EventCreate,
    ClubMembershipCreate,
    EventRegistrationCreate,
)


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
    def get_all_clubs(db: Session, skip: int = 0, limit: int = 100) -> list[Club]:
        return db.query(Club).offset(skip).limit(limit).all()

    @staticmethod
    def get_club_by_id(db: Session, club_id: int) -> Club | None:
        return db.query(Club).filter(Club.id == club_id).first()

    @staticmethod
    def get_club_by_name(db: Session, name: str) -> Club | None:
        return db.query(Club).filter(Club.name == name).first()

    @staticmethod
    def delete_club(db: Session, club_id: int) -> bool:
        db_club = db.query(Club).filter(Club.id == club_id).first()
        if not db_club:
            return False
        db.delete(db_club)
        db.commit()
        return True


class EventRepository:
    @staticmethod
    def create_event(
        db: Session,
        event_data: EventCreate,
        category: str = "OTHER",
        category_confidence: float | None = None,
    ) -> Event:
        db_event = Event(
            club_id=event_data.club_id,
            title=event_data.title,
            description=event_data.description,
            start_time=event_data.start_time,
            capacity=event_data.capacity,
            category=category,
            category_confidence=category_confidence,
        )
        db.add(db_event)
        db.commit()
        db.refresh(db_event)
        return db_event

    @staticmethod
    def get_event_by_id(db: Session, event_id: int) -> Event | None:
        return db.query(Event).filter(Event.id == event_id).first()

    @staticmethod
    def get_all_events(
        db: Session,
        category: str | None = None,
        club_id: int | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Event]:
        query = db.query(Event)
        if category:
            query = query.filter(Event.category == category)
        if club_id is not None:
            query = query.filter(Event.club_id == club_id)
        return query.order_by(Event.start_time, Event.id).offset(skip).limit(limit).all()

    @staticmethod
    def get_events_by_club(db: Session, club_id: int) -> list[Event]:
        return db.query(Event).filter(Event.club_id == club_id).all()

    @staticmethod
    def delete_event(db: Session, event_id: int) -> bool:
        db_event = db.query(Event).filter(Event.id == event_id).first()
        if not db_event:
            return False
        db.delete(db_event)
        db.commit()
        return True


class MembershipRepository:
    @staticmethod
    def add_member(db: Session, membership_data: ClubMembershipCreate) -> ClubMembership:
        db_member = ClubMembership(
            club_id=membership_data.club_id,
            user_id=membership_data.user_id,
            role=membership_data.role
        )
        db.add(db_member)
        db.commit()
        db.refresh(db_member)
        return db_member

    @staticmethod
    def get_membership(db: Session, club_id: int, user_id: int) -> ClubMembership | None:
        return (
            db.query(ClubMembership)
            .filter(ClubMembership.club_id == club_id, ClubMembership.user_id == user_id)
            .first()
        )

    @staticmethod
    def get_club_members(db: Session, club_id: int) -> list[ClubMembership]:
        return db.query(ClubMembership).filter(ClubMembership.club_id == club_id).all()

    @staticmethod
    def remove_member(db: Session, club_id: int, user_id: int) -> bool:
        member = MembershipRepository.get_membership(db, club_id, user_id)
        if not member:
            return False
        db.delete(member)
        db.commit()
        return True


class RegistrationRepository:
    @staticmethod
    def register_user(db: Session, reg_data: EventRegistrationCreate) -> EventRegistration:
        db_reg = EventRegistration(
            event_id=reg_data.event_id,
            user_id=reg_data.user_id,
            status="REGISTERED"
        )
        db.add(db_reg)
        db.commit()
        db.refresh(db_reg)
        return db_reg

    @staticmethod
    def get_registration(db: Session, event_id: int, user_id: int) -> EventRegistration | None:
        return (
            db.query(EventRegistration)
            .filter(EventRegistration.event_id == event_id, EventRegistration.user_id == user_id)
            .first()
        )

    @staticmethod
    def get_active_registration_count(db: Session, event_id: int) -> int:
        return (
            db.query(EventRegistration)
            .filter(EventRegistration.event_id == event_id, EventRegistration.status == "REGISTERED")
            .count()
        )

    @staticmethod
    def cancel_registration(db: Session, event_id: int, user_id: int) -> bool:
        reg = RegistrationRepository.get_registration(db, event_id, user_id)
        if not reg:
            return False
        reg.status = "CANCELLED"
        db.commit()
        return True