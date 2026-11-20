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