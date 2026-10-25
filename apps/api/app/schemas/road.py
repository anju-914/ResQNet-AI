from pydantic import BaseModel, ConfigDict, Field

class RoadBlockRequest(BaseModel):
    reported_by: str = "coordinator"
    reason: str | None = None

class RoadEdgeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    from_node: str
    to_node: str
    base_weight: float
    predicted_weight: float
    is_blocked: bool
    geometry_coords: list[list[float]]

class RoadBlockResponse(BaseModel):
    edge_id: str
    is_blocked: bool
    affected_routes_rerouted: int
    message: str
