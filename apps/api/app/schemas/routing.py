from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class RoutePlanRequest(BaseModel):
    resource_id: str
    incident_id: str

class RoutePlanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    assignment_id: str
    resource_id: str
    incident_id: str
    distance_km: float
    eta_minutes: float
    status: str
    nodes_path: list[str]
    route_geojson: dict
    blocked_edges_avoided: int = 0
    created_at: datetime
