from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..db.session import get_db
from ..schemas.incident import IncidentResponse, IncidentDetailResponse
from ..services.incident_service import list_incidents, get_incident_detail

router = APIRouter(prefix="/incidents", tags=["Incidents"])

@router.get("", response_model=list[IncidentResponse])
def get_all_incidents(db: Session = Depends(get_db)):
    """Retrieves all active, assigned, and resolved incidents."""
    return list_incidents(db)

@router.get("/{incident_id}", response_model=IncidentDetailResponse)
def get_incident(incident_id: str, db: Session = Depends(get_db)):
    """Retrieves incident details along with linked SOS report IDs."""
    inc = get_incident_detail(db, incident_id)
    if not inc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident {incident_id} not found"
        )
    return inc

