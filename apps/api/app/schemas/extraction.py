from pydantic import BaseModel, Field

class ExtractionResult(BaseModel):
    need_type: str = Field(description="Categorized need, e.g. Rescue, Medical, Food, Water, Shelter, Evacuation")
    people_count: int | None = Field(default=None, description="Extracted count of individuals needing assistance, or None if unspecified")
    location_text: str | None = Field(default=None, description="Named location, landmark, sector, or address from message")
    language: str = Field(default="English", description="Hinglish, Hindi, or English")
    confidence: float = Field(default=0.8, ge=0.0, le=1.0, description="Model extraction confidence score (0 to 1)")
    spam_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Spam or test probability (0 to 1)")

