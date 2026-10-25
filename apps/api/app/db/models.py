import datetime
import uuid
from sqlalchemy import (
    Column, String, Float, Integer, Boolean, DateTime, Text, JSON, ForeignKey
)
from sqlalchemy.orm import relationship
from .session import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

class SOSReport(Base):
    __tablename__ = "sos_reports"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    client_uuid = Column(String(64), unique=True, index=True, nullable=False)
    source = Column(String(32), default="app")  # app, whatsapp, mesh
    raw_text = Column(Text, nullable=False)
    language = Column(String(32), default="English")
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    status = Column(String(32), default="pending", index=True)  # pending, extracted, verified, rejected, resolved
    extracted = Column(JSON, nullable=True)  # {need_type, people_count, location_text, language, confidence, spam_score}
    confidence = Column(Float, default=0.0)
    spam_score = Column(Float, default=0.0)
    incident_id = Column(String(36), ForeignKey("incidents.id"), nullable=True)
    received_at = Column(DateTime, default=datetime.datetime.utcnow)

    incident = relationship("Incident", back_populates="reports")


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    centroid_lat = Column(Float, nullable=False)
    centroid_lon = Column(Float, nullable=False)
    need_type = Column(String(64), default="Rescue")
    people_total = Column(Integer, default=1)
    priority = Column(String(16), default="Medium")  # High, Medium, Low
    status = Column(String(32), default="active", index=True)  # active, assigned, resolved
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    reports = relationship("SOSReport", back_populates="incident")
    assignments = relationship("Assignment", back_populates="incident")


class Resource(Base):
    __tablename__ = "resources"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(128), nullable=False)
    type = Column(String(64), default="boat")  # boat, medical, food, search_rescue
    capacity = Column(Integer, default=5)
    status = Column(String(32), default="idle", index=True)  # idle, dispatched, unavailable
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

    assignments = relationship("Assignment", back_populates="resource")


class RoadEdge(Base):
    __tablename__ = "road_edges"

    id = Column(String(64), primary_key=True)
    from_node = Column(String(32), nullable=False, index=True)
    to_node = Column(String(32), nullable=False, index=True)
    base_weight = Column(Float, default=1.0)
    predicted_weight = Column(Float, default=1.0)
    is_blocked = Column(Boolean, default=False, index=True)
    geometry_coords = Column(JSON, nullable=False)  # [[lon, lat], [lon, lat]]


class RoadBlock(Base):
    __tablename__ = "road_blocks"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    edge_id = Column(String(64), ForeignKey("road_edges.id"), nullable=False)
    reported_by = Column(String(128), default="coordinator")
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class Assignment(Base):
    __tablename__ = "assignments"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    resource_id = Column(String(36), ForeignKey("resources.id"), nullable=False)
    incident_id = Column(String(36), ForeignKey("incidents.id"), nullable=False)
    route_geojson = Column(JSON, nullable=True)  # GeoJSON LineString
    eta_minutes = Column(Float, default=0.0)
    distance_km = Column(Float, default=0.0)
    status = Column(String(32), default="dispatched")  # dispatched, on_scene, completed
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    resource = relationship("Resource", back_populates="assignments")
    incident = relationship("Incident", back_populates="assignments")


class RiskZone(Base):
    __tablename__ = "risk_zones"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(128), nullable=False)
    score = Column(Float, default=0.5)  # 0 to 1
    polygon_coords = Column(JSON, nullable=False)  # GeoJSON Polygon coords [[[lon, lat], ...]]
    source = Column(String(64), default="synthetic_flood_model")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

