from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import relationship
from app.database import Base


class Club(Base):
    __tablename__ = "clubs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    events = relationship("Event", back_populates="club", cascade="all, delete-orphan")
    members = relationship("ClubMembership", back_populates="club", cascade="all, delete-orphan")


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    club_id = Column(Integer, ForeignKey("clubs.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    start_time = Column(String, nullable=False)
    capacity = Column(Integer, nullable=False)
    # AI Service (Grup 5) tarafindan belirlenen kategori; AI ulasilamazsa "OTHER"
    category = Column(String, default="OTHER", index=True)
    category_confidence = Column(Float, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (
        CheckConstraint("capacity > 0", name="check_event_capacity_positive"),
    )

    club = relationship("Club", back_populates="events")
    registrations = relationship("EventRegistration", back_populates="event", cascade="all, delete-orphan")

    @property
    def club_name(self) -> str | None:
        return self.club.name if self.club else None


class ClubMembership(Base):
    __tablename__ = "club_memberships"

    id = Column(Integer, primary_key=True, index=True)
    club_id = Column(Integer, ForeignKey("clubs.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, nullable=False, index=True)  # User Service'den gelen öğrenci ID
    role = Column(String, default="MEMBER", nullable=False)  # MEMBER, PRESIDENT, BOARD
    joined_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (
        UniqueConstraint("club_id", "user_id", name="uq_club_user_membership"),
    )

    club = relationship("Club", back_populates="members")


class EventRegistration(Base):
    __tablename__ = "event_registrations"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, nullable=False, index=True)  # User Service'den gelen öğrenci ID
    status = Column(String, default="REGISTERED", nullable=False)  # REGISTERED, ATTENDED, CANCELLED
    registered_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (
        UniqueConstraint("event_id", "user_id", name="uq_event_user_registration"),
    )

    event = relationship("Event", back_populates="registrations")