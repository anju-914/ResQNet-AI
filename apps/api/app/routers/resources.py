from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..db.session import get_db
from ..db.models import Resource
from ..schemas.resource import ResourceResponse

router = APIRouter(prefix="/resources", tags=["Rescue Resources"])

@router.get("", response_model=list[ResourceResponse])
def get_all_resources(db: Session = Depends(get_db)):
    """Retrieves all rescue teams, boats, and medical units."""
    resources = db.query(Resource).all()
    return [ResourceResponse.model_validate(r) for r in resources]

@router.get("/{resource_id}", response_model=ResourceResponse)
def get_resource(resource_id: str, db: Session = Depends(get_db)):
    res = db.query(Resource).filter(Resource.id == resource_id).first()
    if not res:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resource {resource_id} not found"
        )
    return ResourceResponse.model_validate(res)

