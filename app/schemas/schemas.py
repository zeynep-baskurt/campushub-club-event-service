from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

# --- CLUB SCHEMAS ---
class ClubCreate(BaseModel):
    name: str = Field(..., min_length=1, description="Kulüp adı")
    description: Optional[str] = Field(None, description="Kulüp açıklaması")


class ClubResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# --- EVENT SCHEMAS ---
class EventCreate(BaseModel):
    club_id: int = Field(..., alias="clubId", description="Etkinliği düzenleyen kulüp ID")
    title: str = Field(..., min_length=1, description="Etkinlik başlığı")
    description: Optional[str] = Field(None, description="Etkinlik açıklaması")
    start_time: str = Field(..., alias="startTime", description="Etkinlik başlangıç zamanı")
    capacity: int = Field(..., gt=0, description="Etkinlik kontenjanı")

    model_config = ConfigDict(populate_by_name=True)


class EventResponse(BaseModel):
    id: int
    club_id: int = Field(..., serialization_alias="clubId")
    title: str
    description: Optional[str] = None
    start_time: str = Field(..., serialization_alias="startTime")
    capacity: int
    category: str

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


# --- CLUB SCHEMAS ---
class ClubCreate(BaseModel):
    name: str = Field(..., min_length=1, description="Kulüp adı")
    description: Optional[str] = Field(None, description="Kulüp açıklaması")


class ClubResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# --- EVENT SCHEMAS ---
class EventCreate(BaseModel):
    club_id: int = Field(..., alias="clubId", description="Etkinliği düzenleyen kulüp ID")
    title: str = Field(..., min_length=1, description="Etkinlik başlığı")
    description: Optional[str] = Field(None, description="Etkinlik açıklaması")
    start_time: str = Field(..., alias="startTime", description="Etkinlik başlangıç zamanı")
    capacity: int = Field(..., gt=0, description="Etkinlik kontenjanı")

    model_config = ConfigDict(populate_by_name=True)


class EventResponse(BaseModel):
    id: int
    club_id: int = Field(..., serialization_alias="clubId")
    title: str
    description: Optional[str] = None
    start_time: str = Field(..., serialization_alias="startTime")
    capacity: int
    category: str
    created_at: Optional[datetime] = None

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