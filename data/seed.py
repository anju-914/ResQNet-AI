import sys
import json
from pathlib import Path

# Add project root to path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from apps.api.app.db.session import SessionLocal, Base, engine
from apps.api.app.db.models import RoadEdge, Resource, RiskZone, SOSReport, Incident
from apps.api.app.services.gnn_service import predict_edge_weights
from apps.api.app.services.extraction_service import extract_sos_entities
from apps.api.app.services.sos_service import geocode_synthetic_location

def seed_database():
    print("Initializing ResQNet AI Database Schema...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # 1. Clear existing data
        print("Purging existing demo records...")
        db.query(SOSReport).delete()
        db.query(Incident).delete()
        db.query(Resource).delete()
        db.query(RoadEdge).delete()
        db.query(RiskZone).delete()
        db.commit()

        # 2. Seed Road Network
        road_json_path = BASE_DIR / "data" / "road_network_delhi_synthetic.json"
        with open(road_json_path, "r", encoding="utf-8") as f:
            road_data = json.load(f)

        nodes = road_data["nodes"]
        edges = road_data["edges"]

        print(f"Loading {len(edges)} road segments across {len(nodes)} nodes...")
        
        # Build node features for PyG GNN [elevation, flood_hazard_idx, road_density, connectivity]
        node_features = {}
        for nid, ninfo in nodes.items():
            # Synthetic features for PyG GNN demonstration
            hazard_index = 0.8 if "YAMUNA" in nid or "KHADAR" in nid else 0.2
            elevation = 205.0 if "CIVIL" in nid else 198.0
            node_features[nid] = [elevation / 250.0, hazard_index, 0.5, 0.4]

        edge_tuples = [(e["from"], e["to"], e["base_weight"]) for e in edges]
        gnn_weights = predict_edge_weights(node_features, edge_tuples)

        for e in edges:
            predicted_w = gnn_weights.get((e["from"], e["to"]), e["base_weight"])
            road_edge = RoadEdge(
                id=e["id"],
                from_node=e["from"],
                to_node=e["to"],
                base_weight=e["base_weight"],
                predicted_weight=predicted_w,
                is_blocked=False,
                geometry_coords=e["coords"]
            )
            db.add(road_edge)
        db.commit()
        print(f"Road network seeded and adjusted via PyTorch Geometric GNN!")

        # 3. Seed Rescue Resources (Teams, Boats, Ambulances)
        resources_data = [
            {
                "id": "RES_BOAT_01",
                "name": "NDRF Inflatable Boat 1",
                "type": "boat",
                "capacity": 8,
                "status": "idle",
                "latitude": 28.6670,
                "longitude": 77.2280
            },
            {
                "id": "RES_BOAT_02",
                "name": "Civil Defense Boat 2",
                "type": "boat",
                "capacity": 6,
                "status": "idle",
                "latitude": 28.6560,
                "longitude": 77.2380
            },
            {
                "id": "RES_MED_01",
                "name": "Mobile Disaster Medical Unit 1",
                "type": "medical",
                "capacity": 4,
                "status": "idle",
                "latitude": 28.6290,
                "longitude": 77.2420
            },
            {
                "id": "RES_RESCUE_01",
                "name": "NDRF Quick Response Team Alpha",
                "type": "search_rescue",
                "capacity": 10,
                "status": "idle",
                "latitude": 28.6810,
                "longitude": 77.2220
            }
        ]

        print(f"Seeding {len(resources_data)} emergency resources...")
        for r in resources_data:
            res = Resource(**r)
            db.add(res)
        db.commit()

        # 4. Seed Flood Risk Zones (GeoJSON Polygons)
        risk_zones_data = [
            {
                "id": "ZONE_YAMUNA_BASIN",
                "name": "Yamuna River Lowland Inundation Zone",
                "score": 0.88,
                "source": "GNN flood forecast model",
                "polygon_coords": [
                    [
                        [77.2350, 28.6650],
                        [77.2650, 28.6750],
                        [77.2750, 28.6400],
                        [77.2450, 28.6300],
                        [77.2350, 28.6650]
                    ]
                ]
            },
            {
                "id": "ZONE_MAYUR_LOWLAND",
                "name": "Mayur Vihar - Akshardham Spillway Zone",
                "score": 0.65,
                "source": "Synthetic elevation model",
                "polygon_coords": [
                    [
                        [77.2700, 28.6250],
                        [77.2950, 28.6200],
                        [77.3050, 28.6000],
                        [77.2800, 28.6050],
                        [77.2700, 28.6250]
                    ]
                ]
            }
        ]

        print(f"Seeding {len(risk_zones_data)} predictive risk zones...")
        for rz in risk_zones_data:
            zone = RiskZone(**rz)
            db.add(zone)
        db.commit()

        # 5. Seed Initial Pending SOS Messages for Verification Queue
        sample_sos_texts = [
            ("paani bhar gaya hai, 5 log chhat par, sector 5 ke paas please madad karo", "whatsapp"),
            ("यमुना खादर में पानी भर चुका है, 12 लोग फंसे हैं, नाव भेजो", "mesh"),
            ("Urgent medical assistance required at Kashmere Gate ISBT, an elderly woman is bleeding", "app"),
            ("bhookh lagi hai chhat par 4 bache ro rahe hain near sector 5", "whatsapp"),
            ("Laxmi Nagar Vikas Marg par paani 4 feet ho gaya hai, 3 log car me phase hain", "app")
        ]

        print("Seeding initial pending SOS messages for verification queue...")
        import uuid
        for text, source in sample_sos_texts:
            ext = extract_sos_entities(text)
            lat, lon = None, None
            if ext.location_text:
                lat, lon = geocode_synthetic_location(ext.location_text)

            report = SOSReport(
                client_uuid=str(uuid.uuid4()),
                source=source,
                raw_text=text,
                language=ext.language,
                latitude=lat,
                longitude=lon,
                status="extracted",
                extracted=ext.model_dump(),
                confidence=ext.confidence,
                spam_score=ext.spam_score
            )
            db.add(report)
        db.commit()

        print("\nDatabase seeded successfully!")
        print(f"Total Roads:     {db.query(RoadEdge).count()}")
        print(f"Total Resources: {db.query(Resource).count()}")
        print(f"Total Risk Zones:{db.query(RiskZone).count()}")
        print(f"Pending SOS:     {db.query(SOSReport).count()}")

    finally:
        db.close()

if __name__ == "__main__":
    seed_database()

