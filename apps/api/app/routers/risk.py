from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..db.session import get_db
from ..db.models import RiskZone

router = APIRouter(prefix="/risk-zones", tags=["Risk Map"])

@router.get("")
def get_risk_zones(db: Session = Depends(get_db)):
    """Returns predictive flood and inundation hazard polygons."""
    zones = db.query(RiskZone).all()
    features = []
    for z in zones:
        features.append({
            "type": "Feature",
            "properties": {
                "id": z.id,
                "name": z.name,
                "score": z.score,
                "source": z.source
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": z.polygon_coords
            }
        })
    return {
        "type": "FeatureCollection",
        "features": features
    }

