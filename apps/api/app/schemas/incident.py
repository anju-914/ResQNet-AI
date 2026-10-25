from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class IncidentCreate(BaseModel):
    centroid_lat: float
    centroid_lon: float
    need_type: str = "Rescue"
    people_total: int = 1
    priority: str = "Medium"

class IncidentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    centroid_lat: float
    centroid_lon: float
    need_type: str
    people_total: int
    priority: str
    status: str
    created_at: datetime
    reports_count: int = 0
    assigned_resource_id: str | None = None

class IncidentDetailResponse(IncidentResponse):
    linked_report_ids: list[str] = []
