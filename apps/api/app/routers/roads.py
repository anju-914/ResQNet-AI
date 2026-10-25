from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..db.session import get_db
from ..db.models import RoadEdge
from ..schemas.road import RoadEdgeResponse, RoadBlockResponse, RoadBlockRequest
from ..services.routing_service import block_road_and_reroute, unblock_road

router = APIRouter(prefix="/roads", tags=["Road Network & Blockages"])

@router.get("", response_model=list[RoadEdgeResponse])
def get_all_roads(db: Session = Depends(get_db)):
    """Returns all road edges with geometry and blockage status."""
    edges = db.query(RoadEdge).all()
    return [RoadEdgeResponse.model_validate(e) for e in edges]

@router.post("/{edge_id}/block", response_model=RoadBlockResponse)
def block_road_segment(
    edge_id: str,
    payload: RoadBlockRequest | None = None,
    db: Session = Depends(get_db)
):
    """
    Blocks a road segment due to flood water, debris, or hazard.
    Recalculates all active assignments traversing this road segment.
    """
    reported_by = payload.reported_by if payload else "coordinator"
    try:
        edge, rerouted_count = block_road_and_reroute(db, edge_id, reported_by=reported_by)
        return RoadBlockResponse(
            edge_id=edge.id,
            is_blocked=edge.is_blocked,
            affected_routes_rerouted=rerouted_count,
            message=f"Road {edge_id} marked as blocked. {rerouted_count} rescue routes recalculated."
        )
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.delete("/{edge_id}/block", response_model=RoadBlockResponse)
def unblock_road_segment(edge_id: str, db: Session = Depends(get_db)):
    """Unblocks a cleared road segment."""
    try:
        edge = unblock_road(db, edge_id)
        return RoadBlockResponse(
            edge_id=edge.id,
            is_blocked=edge.is_blocked,
            affected_routes_rerouted=0,
            message=f"Road {edge_id} cleared and reopened."
        )
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

