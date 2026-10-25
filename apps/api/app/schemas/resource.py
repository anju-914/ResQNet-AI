from pydantic import BaseModel, ConfigDict

class ResourceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    type: str  # boat, medical, food, search_rescue
    capacity: int
    status: str
    latitude: float
    longitude: float
