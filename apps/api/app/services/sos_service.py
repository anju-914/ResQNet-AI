import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from ..db.models import SOSReport, Incident
from ..schemas.sos import SOSCreate, SOSEdit, SOSResponse, SOSListResponse
from .extraction_service import extract_sos_entities
from .incident_service import merge_or_create_incident

def create_sos_report(db: Session, sos_in: SOSCreate) -> SOSReport:
    """
    Ingests an SOS message, executes extraction, and stores it idempotently.
    """
    client_uuid = sos_in.client_uuid or str(uuid.uuid4())
    
    # Idempotency check: if report with client_uuid exists, return it
    existing = db.query(SOSReport).filter(SOSReport.client_uuid == client_uuid).first()
    if existing:
        return existing

    # Perform extraction
    extraction = extract_sos_entities(sos_in.raw_text)
    
    # Synthesize coordinates if location_text recognized and no GPS supplied
    lat = sos_in.latitude
    lon = sos_in.longitude
    if (lat is None or lon is None) and extraction.location_text:
        lat, lon = geocode_synthetic_location(extraction.location_text)

    # If spam score is high, status can remain pending with low confidence
    status = "extracted"
    if extraction.spam_score > 0.85:
        status = "pending"

    report = SOSReport(
        client_uuid=client_uuid,
        source=sos_in.source,
        raw_text=sos_in.raw_text,
        language=extraction.language,
        latitude=lat,
        longitude=lon,
        status=status,
        extracted=extraction.model_dump(),
        confidence=extraction.confidence,
        spam_score=extraction.spam_score,
        received_at=datetime.utcnow()
    )
    
    db.add(report)
    db.commit()
    db.refresh(report)
    return report

def list_sos_reports(
    db: Session,
    status: str | None = None,
    limit: int = 100,
    offset: int = 0
) -> SOSListResponse:
    """Lists SOS reports with aggregate counts for dashboard badges."""
    query = db.query(SOSReport)
    
    total = query.count()
    pending_count = db.query(SOSReport).filter(SOSReport.status.in_(["pending", "extracted"])).count()
    verified_count = db.query(SOSReport).filter(SOSReport.status == "verified").count()
    rejected_count = db.query(SOSReport).filter(SOSReport.status == "rejected").count()

    if status:
        if status == "pending":
            query = query.filter(SOSReport.status.in_(["pending", "extracted"]))
        else:
            query = query.filter(SOSReport.status == status)

    reports = query.order_by(SOSReport.received_at.desc()).offset(offset).limit(limit).all()

    items = [SOSResponse.model_validate(r) for r in reports]
    return SOSListResponse(
        total=total,
        pending_count=pending_count,
        verified_count=verified_count,
        rejected_count=rejected_count,
        items=items
    )

def verify_sos_report(db: Session, report_id: str) -> SOSReport:
    """Verifies an SOS report and groups it into a verified incident."""
    report = db.query(SOSReport).filter(SOSReport.id == report_id).first()
    if not report:
        raise ValueError(f"SOS report {report_id} not found")

    report.status = "verified"
    
    # Merge into an existing incident nearby or create a new incident
    incident = merge_or_create_incident(db, report)
    report.incident_id = incident.id
    
    db.commit()
    db.refresh(report)
    return report

def reject_sos_report(db: Session, report_id: str) -> SOSReport:
    """Marks an SOS report as rejected (spam / invalid)."""
    report = db.query(SOSReport).filter(SOSReport.id == report_id).first()
    if not report:
        raise ValueError(f"SOS report {report_id} not found")

    report.status = "rejected"
    db.commit()
    db.refresh(report)
    return report

def edit_sos_report(db: Session, report_id: str, edit_data: SOSEdit) -> SOSReport:
    """Updates fields of an unverified or verified SOS report."""
    report = db.query(SOSReport).filter(SOSReport.id == report_id).first()
    if not report:
        raise ValueError(f"SOS report {report_id} not found")

    extracted = report.extracted or {}
    if edit_data.need_type:
        extracted["need_type"] = edit_data.need_type
    if edit_data.people_count is not None:
        extracted["people_count"] = edit_data.people_count
    if edit_data.location_text:
        extracted["location_text"] = edit_data.location_text
    
    report.extracted = extracted

    if edit_data.latitude is not None:
        report.latitude = edit_data.latitude
    if edit_data.longitude is not None:
        report.longitude = edit_data.longitude

    db.commit()
    db.refresh(report)
    return report

# Synthetic Geocoding reference map for Delhi NCR demo coordinates
SYNTHETIC_COORDS = {
    "yamuna khadar": (28.6430, 77.2620),
    "kashmere gate": (28.6670, 77.2280),
    "sector 5": (28.6010, 77.3750),
    "sector 14": (28.4720, 77.0420),
    "sector 62": (28.6280, 77.3640),
    "mayur vihar": (28.6080, 77.2960),
    "laxmi nagar": (28.6310, 77.2770),
    "civil lines": (28.6810, 77.2220),
    "ito": (28.6290, 77.2420),
    "okhla": (28.5350, 77.2730),
    "narela": (28.8520, 77.0930),
    "karol bagh": (28.6520, 77.1900),
    "rohini sector 3": (28.7110, 77.1120),
    "dwarka sector 10": (28.5810, 77.0580),
    "boat club": (28.6140, 77.2140),
    "shastri park": (28.6720, 77.2580),
    "sarita vihar": (28.5280, 77.2980)
}

def geocode_synthetic_location(location_text: str) -> tuple[float, float]:
    """Resolves recognized location text to approximate lat/lon coordinates."""
    key = location_text.lower().strip()
    for name, coords in SYNTHETIC_COORDS.items():
        if name in key or key in name:
            return coords
            
    # Default to central Delhi coordinates with small jitter if unrecognized
    import random
    jitter_lat = (random.random() - 0.5) * 0.05
    jitter_lon = (random.random() - 0.5) * 0.05
    return (28.6300 + jitter_lat, 77.2400 + jitter_lon)

