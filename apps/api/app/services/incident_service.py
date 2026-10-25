import math
from datetime import datetime
from sqlalchemy.orm import Session
from ..db.models import Incident, SOSReport, Assignment
from ..schemas.incident import IncidentResponse, IncidentDetailResponse

def calculate_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Haversine distance between two lat/lon points."""
    R = 6371.0  # Earth radius in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def calculate_priority(need_type: str, people_total: int) -> str:
    """Computes priority based on urgency and casualty count."""
    if need_type == "Medical" or people_total >= 10:
        return "High"
    elif need_type == "Rescue" or people_total >= 4:
        return "Medium"
    return "Low"

def merge_or_create_incident(db: Session, report: SOSReport, radius_km: float = 2.0) -> Incident:
    """
    Finds an existing active incident within radius_km and matching need_type,
    or creates a new Incident.
    """
    extracted = report.extracted or {}
    need_type = extracted.get("need_type", "Rescue")
    people_count = extracted.get("people_count") or 1
    
    rep_lat = report.latitude or 28.6300
    rep_lon = report.longitude or 77.2400

    # Look for nearby active incident
    active_incidents = db.query(Incident).filter(
        Incident.status == "active",
        Incident.need_type == need_type
    ).all()

    target_incident = None
    for inc in active_incidents:
        dist = calculate_distance_km(rep_lat, rep_lon, inc.centroid_lat, inc.centroid_lon)
        if dist <= radius_km:
            target_incident = inc
            break

    if target_incident:
        # Merge: update centroid and aggregate people total
        existing_reports_count = len(target_incident.reports) + 1
        target_incident.centroid_lat = (target_incident.centroid_lat + rep_lat) / 2.0
        target_incident.centroid_lon = (target_incident.centroid_lon + rep_lon) / 2.0
        target_incident.people_total += people_count
        target_incident.priority = calculate_priority(target_incident.need_type, target_incident.people_total)
        db.commit()
        db.refresh(target_incident)
        return target_incident
    else:
        # Create new incident
        priority = calculate_priority(need_type, people_count)
        new_inc = Incident(
            centroid_lat=rep_lat,
            centroid_lon=rep_lon,
            need_type=need_type,
            people_total=people_count,
            priority=priority,
            status="active",
            created_at=datetime.utcnow()
        )
        db.add(new_inc)
        db.commit()
        db.refresh(new_inc)
        return new_inc

def list_incidents(db: Session) -> list[IncidentResponse]:
    """Returns active and assigned incidents with report counts and assignment status."""
    incidents = db.query(Incident).all()
    results = []
    
    for inc in incidents:
        # Check if there is an active assignment
        active_assignment = db.query(Assignment).filter(
            Assignment.incident_id == inc.id,
            Assignment.status.in_(["dispatched", "on_scene"])
        ).first()
        
        assigned_res = active_assignment.resource_id if active_assignment else None
        report_count = db.query(SOSReport).filter(SOSReport.incident_id == inc.id).count()

        results.append(IncidentResponse(
            id=inc.id,
            centroid_lat=inc.centroid_lat,
            centroid_lon=inc.centroid_lon,
            need_type=inc.need_type,
            people_total=inc.people_total,
            priority=inc.priority,
            status=inc.status,
            created_at=inc.created_at,
            reports_count=report_count,
            assigned_resource_id=assigned_res
        ))
        
    return results

def get_incident_detail(db: Session, incident_id: str) -> IncidentDetailResponse | None:
    inc = db.query(Incident).filter(Incident.id == incident_id).first()
    if not inc:
        return None
        
    linked_reports = db.query(SOSReport.id).filter(SOSReport.incident_id == inc.id).all()
    report_ids = [r[0] for r in linked_reports]
    
    active_assignment = db.query(Assignment).filter(
        Assignment.incident_id == inc.id
    ).first()
    
    assigned_res = active_assignment.resource_id if active_assignment else None
    
    return IncidentDetailResponse(
        id=inc.id,
        centroid_lat=inc.centroid_lat,
        centroid_lon=inc.centroid_lon,
        need_type=inc.need_type,
        people_total=inc.people_total,
        priority=inc.priority,
        status=inc.status,
        created_at=inc.created_at,
        reports_count=len(report_ids),
        assigned_resource_id=assigned_res,
        linked_report_ids=report_ids
    )

