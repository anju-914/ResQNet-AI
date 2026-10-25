from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..db.session import get_db
from ..db.models import Assignment
from ..schemas.routing import RoutePlanRequest, RoutePlanResponse
from ..services.routing_service import plan_resource_route

router = APIRouter(prefix="/routes", tags=["Routing Engine"])

@router.post("/plan", response_model=RoutePlanResponse)
def plan_route(payload: RoutePlanRequest, db: Session = Depends(get_db)):
    """
    Computes an optimal path for a rescue resource to an incident
    using Dijkstra on the GNN-adjusted road graph.
    """
    try:
        assignment = plan_resource_route(db, payload.resource_id, payload.incident_id)
        return RoutePlanResponse(
            assignment_id=assignment.id,
            resource_id=assignment.resource_id,
            incident_id=assignment.incident_id,
            distance_km=assignment.distance_km,
            eta_minutes=assignment.eta_minutes,
            status=assignment.status,
            nodes_path=[],
            route_geojson=assignment.route_geojson,
            created_at=assignment.created_at
        )
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/active")
def get_active_routes(db: Session = Depends(get_db)):
    """Returns all active routes for map polyline rendering."""
    assignments = db.query(Assignment).filter(
        Assignment.status.in_(["dispatched", "on_scene"])
    ).all()
    
    return [
        {
            "id": a.id,
            "resource_id": a.resource_id,
            "incident_id": a.incident_id,
            "route_geojson": a.route_geojson,
            "eta_minutes": a.eta_minutes,
            "distance_km": a.distance_km,
            "status": a.status
        }
        for a in assignments
    ]

