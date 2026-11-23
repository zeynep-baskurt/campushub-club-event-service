from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


# --- CLUB SCHEMAS ---
class ClubCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=120, description="Kulüp adı")
    description: Optional[str] = Field(None, max_length=2000, description="Kulüp açıklaması")

    @field_validator("name")
    @classmethod
    def strip_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("name must not be blank")
        return v


class ClubResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    created_at: Optional[datetime] = Field(None, serialization_alias="createdAt")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


# --- EVENT SCHEMAS ---
class EventCreate(BaseModel):
    club_id: int = Field(..., alias="clubId", gt=0, description="Etkinliği düzenleyen kulüp ID")
    title: str = Field(..., min_length=1, max_length=200, description="Etkinlik başlığı")
    description: Optional[str] = Field(None, max_length=5000, description="Etkinlik açıklaması")
    start_time: str = Field(..., alias="startTime", description="ISO 8601, örn. 2026-12-10T10:00:00")
    capacity: int = Field(..., gt=0, description="Etkinlik kontenjanı")

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("title")
    @classmethod
    def strip_title(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("title must not be blank")
        return v

    @field_validator("start_time")
    @classmethod
    def validate_start_time(cls, v: str) -> str:
        try:
            datetime.fromisoformat(v)
        except ValueError:
            raise ValueError("startTime must be an ISO 8601 date-time, e.g. 2026-12-10T10:00:00")
        return v


class EventResponse(BaseModel):
    id: int
    club_id: int = Field(..., serialization_alias="clubId")
    club_name: Optional[str] = Field(None, serialization_alias="clubName")
    title: str
    description: Optional[str] = None
    start_time: str = Field(..., serialization_alias="startTime")
    capacity: int
    category: str
    category_confidence: Optional[float] = Field(None, serialization_alias="categoryConfidence")
    created_at: Optional[datetime] = Field(None, serialization_alias="createdAt")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


# --- CLUB MEMBERSHIP SCHEMAS ---
class ClubMembershipCreate(BaseModel):
    club_id: int = Field(..., alias="clubId")
    user_id: int = Field(..., alias="userId")
    role: str = Field(default="MEMBER")

    model_config = ConfigDict(populate_by_name=True)


class ClubMembershipResponse(BaseModel):
    id: int
    club_id: int = Field(..., serialization_alias="clubId")
    user_id: int = Field(..., serialization_alias="userId")
    role: str
    joined_at: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


# --- EVENT REGISTRATION SCHEMAS ---
class EventRegistrationCreate(BaseModel):
    event_id: int = Field(..., alias="eventId")
    user_id: int = Field(..., alias="userId")

    model_config = ConfigDict(populate_by_name=True)


class EventRegistrationResponse(BaseModel):
    id: int
    event_id: int = Field(..., serialization_alias="eventId")
    user_id: int = Field(..., serialization_alias="userId")
    status: str
    registered_at: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


# --- HEALTH ---
class DependencyStatus(BaseModel):
    name: str
    url: str
    status: str
    detail: Optional[str] = None
