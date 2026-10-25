from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from .extraction import ExtractionResult

class SOSCreate(BaseModel):
    raw_text: str = Field(..., min_length=3, description="Raw SOS text in English, Hindi, or Hinglish")
    client_uuid: str | None = Field(default=None, description="Client-side UUID for idempotent sync")
    source: str = Field(default="app", description="Source channel: app, whatsapp, or mesh")
    latitude: float | None = Field(default=None, description="Optional GPS latitude")
    longitude: float | None = Field(default=None, description="Optional GPS longitude")

class SOSEdit(BaseModel):
    need_type: str | None = None
    people_count: int | None = None
    location_text: str | None = None
    latitude: float | None = None
    longitude: float | None = None

class SOSResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    client_uuid: str
    source: str
    raw_text: str
    language: str
    latitude: float | None = None
    longitude: float | None = None
    status: str
    extracted: ExtractionResult | dict | None = None
    confidence: float
    spam_score: float
    incident_id: str | None = None
    received_at: datetime

class SOSListResponse(BaseModel):
    total: int
    pending_count: int
    verified_count: int
    rejected_count: int
    items: list[SOSResponse]
