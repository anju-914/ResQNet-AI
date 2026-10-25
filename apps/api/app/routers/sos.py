from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from ..db.session import get_db
from ..core.security import verify_coordinator_auth
from ..schemas.sos import SOSCreate, SOSEdit, SOSResponse, SOSListResponse
from ..services.sos_service import (
    create_sos_report,
    list_sos_reports,
    verify_sos_report,
    reject_sos_report,
    edit_sos_report,
)

router = APIRouter(prefix="/sos", tags=["SOS Reports"])

@router.post("", status_code=status.HTTP_202_ACCEPTED, response_model=SOSResponse)
def submit_sos(payload: SOSCreate, db: Session = Depends(get_db)):
    """
    Public SOS submission endpoint.
    Accepts raw text (Hinglish/Hindi/English), assigns client_uuid idempotently,
    runs extraction, and enqueues/stores with status 'extracted' or 'pending'.
    """
    try:
        report = create_sos_report(db, payload)
        return SOSResponse.model_validate(report)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to process SOS report: {str(e)}"
        )

@router.get("", response_model=SOSListResponse)
def get_sos_reports(
    status: str | None = Query(None, description="Filter by status: pending, extracted, verified, rejected, resolved"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    # Optional coordinator auth for demo flexibility
):
    """
    Coordinator endpoint: lists SOS reports with aggregate counts.
    """
    return list_sos_reports(db, status=status, limit=limit, offset=offset)

@router.patch("/{report_id}/verify", response_model=SOSResponse)
def verify_sos(
    report_id: str,
    db: Session = Depends(get_db),
):
    """
    Coordinator action: verify an SOS report.
    Automatically merges the report into a nearby verified incident or creates a new incident.
    """
    try:
        report = verify_sos_report(db, report_id)
        return SOSResponse.model_validate(report)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.patch("/{report_id}/reject", response_model=SOSResponse)
def reject_sos(
    report_id: str,
    db: Session = Depends(get_db),
):
    """
    Coordinator action: reject an SOS report (spam or duplicate).
    """
    try:
        report = reject_sos_report(db, report_id)
        return SOSResponse.model_validate(report)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))

@router.patch("/{report_id}/edit", response_model=SOSResponse)
def edit_sos(
    report_id: str,
    payload: SOSEdit,
    db: Session = Depends(get_db),
):
    """
    Coordinator action: edit extracted need, people count, or location.
    """
    try:
        report = edit_sos_report(db, report_id, payload)
        return SOSResponse.model_validate(report)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))

