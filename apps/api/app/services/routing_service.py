import datetime
import math
import networkx as nx
from sqlalchemy.orm import Session
from ..db.models import RoadEdge, RoadBlock, Resource, Incident, Assignment
from ..schemas.routing import RoutePlanResponse
from .gnn_service import predict_edge_weights

class RoutingEngine:
    def __init__(self):
        self.graph: nx.DiGraph = nx.DiGraph()
        self.node_coordinates: dict[str, tuple[float, float]] = {}  # node_id -> (lat, lon)
        self.edge_geometries: dict[str, list[list[float]]] = {}    # edge_id -> [[lon, lat], ...]
        self.edge_by_nodes: dict[tuple[str, str], str] = {}        # (u, v) -> edge_id

    def load_graph_from_db(self, db: Session):
        """Builds or synchronizes the in-memory NetworkX graph from database road_edges."""
        self.graph.clear()
        self.node_coordinates.clear()
        self.edge_geometries.clear()
        self.edge_by_nodes.clear()

        edges = db.query(RoadEdge).all()
        for edge in edges:
            self.edge_geometries[edge.id] = edge.geometry_coords
            self.edge_by_nodes[(edge.from_node, edge.to_node)] = edge.id

            # Extract start and end node coordinates from geometry if available
            coords = edge.geometry_coords
            if coords and len(coords) >= 2:
                # coords are [lon, lat]
                start_lon, start_lat = coords[0]
                end_lon, end_lat = coords[-1]
                self.node_coordinates[edge.from_node] = (start_lat, start_lon)
                self.node_coordinates[edge.to_node] = (end_lat, end_lon)

            # If edge is blocked, give it infinite weight (or skip)
            weight = float('inf') if edge.is_blocked else edge.predicted_weight
            self.graph.add_edge(
                edge.from_node,
                edge.to_node,
                weight=weight,
                edge_id=edge.id,
                base_weight=edge.base_weight,
                is_blocked=edge.is_blocked
            )

    def find_nearest_node(self, lat: float, lon: float) -> str | None:
        """Finds the nearest graph node to given coordinates."""
        if not self.node_coordinates:
            return None

        best_node = None
        min_dist = float('inf')
        for node_id, (n_lat, n_lon) in self.node_coordinates.items():
            dist = (lat - n_lat) ** 2 + (lon - n_lon) ** 2
            if dist < min_dist:
                min_dist = dist
                best_node = node_id

        return best_node

    def calculate_route(
        self,
        from_lat: float,
        from_lon: float,
        to_lat: float,
        to_lon: float
    ) -> tuple[list[str], float, float, dict]:
        """
        Calculates shortest path using Dijkstra algorithm over the weighted road graph.
        Returns: (nodes_path, distance_km, eta_minutes, geojson_linestring)
        """
        start_node = self.find_nearest_node(from_lat, from_lon)
        end_node = self.find_nearest_node(to_lat, to_lon)

        if not start_node or not end_node:
            raise ValueError("Road network has no accessible nodes near given locations")

        if start_node == end_node:
            # Direct reach
            coords = [[from_lon, from_lat], [to_lon, to_lat]]
            return [start_node], 0.5, 2.0, {"type": "LineString", "coordinates": coords}

        try:
            nodes_path = nx.shortest_path(self.graph, source=start_node, target=end_node, weight="weight")
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            raise ValueError(f"No reachable path between {start_node} and {end_node} due to road blocks or disconnects")

        # Reconstruct path coordinates and calculate distance & ETA
        route_coords = [[from_lon, from_lat]]
        total_distance_km = 0.0

        for i in range(len(nodes_path) - 1):
            u, v = nodes_path[i], nodes_path[i + 1]
            edge_data = self.graph.get_edge_data(u, v) or {}
            edge_id = edge_data.get("edge_id")
            
            if edge_id and edge_id in self.edge_geometries:
                geom = self.edge_geometries[edge_id]
                route_coords.extend(geom)
            elif u in self.node_coordinates and v in self.node_coordinates:
                u_lat, u_lon = self.node_coordinates[u]
                v_lat, v_lon = self.node_coordinates[v]
                route_coords.append([u_lon, u_lat])
                route_coords.append([v_lon, v_lat])

            # Increment distance based on base weight (km)
            total_distance_km += edge_data.get("base_weight", 1.5)

        route_coords.append([to_lon, to_lat])
        total_distance_km = round(max(total_distance_km, 0.8), 2)
        
        # Disaster response travel speed assumed ~25 km/h with flood/rubble slowdowns
        eta_minutes = round((total_distance_km / 25.0) * 60.0, 1)

        geojson = {
            "type": "LineString",
            "coordinates": route_coords
        }

        return nodes_path, total_distance_km, eta_minutes, geojson

# Singleton instance
routing_engine = RoutingEngine()

def plan_resource_route(db: Session, resource_id: str, incident_id: str) -> Assignment:
    """Plans and saves a route from a rescue team resource to an incident."""
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    incident = db.query(Incident).filter(Incident.id == incident_id).first()

    if not resource:
        raise ValueError(f"Resource {resource_id} not found")
    if not incident:
        raise ValueError(f"Incident {incident_id} not found")

    # Ensure engine graph is loaded
    if len(routing_engine.graph.nodes) == 0:
        routing_engine.load_graph_from_db(db)

    nodes_path, distance_km, eta_minutes, route_geojson = routing_engine.calculate_route(
        resource.latitude, resource.longitude,
        incident.centroid_lat, incident.centroid_lon
    )

    # Check for existing assignment or create new
    assignment = db.query(Assignment).filter(
        Assignment.resource_id == resource_id,
        Assignment.incident_id == incident_id
    ).first()

    if not assignment:
        assignment = Assignment(
            resource_id=resource_id,
            incident_id=incident_id,
            route_geojson=route_geojson,
            eta_minutes=eta_minutes,
            distance_km=distance_km,
            status="dispatched"
        )
        db.add(assignment)
    else:
        assignment.route_geojson = route_geojson
        assignment.eta_minutes = eta_minutes
        assignment.distance_km = distance_km
        assignment.status = "dispatched"

    resource.status = "dispatched"
    incident.status = "assigned"

    db.commit()
    db.refresh(assignment)
    return assignment

def block_road_and_reroute(db: Session, edge_id: str, reported_by: str = "coordinator") -> tuple[RoadEdge, int]:
    """
    Marks a road edge as blocked and automatically re-routes all active team assignments
    passing through that segment.
    """
    edge = db.query(RoadEdge).filter(RoadEdge.id == edge_id).first()
    if not edge:
        raise ValueError(f"Road edge {edge_id} not found")

    edge.is_blocked = True
    
    # Record in road_blocks audit
    road_block = RoadBlock(
        edge_id=edge_id,
        reported_by=reported_by,
        active=True
    )
    db.add(road_block)
    db.commit()

    # Update in-memory graph
    routing_engine.load_graph_from_db(db)

    # Re-route affected active assignments
    active_assignments = db.query(Assignment).filter(
        Assignment.status.in_(["dispatched", "on_scene"])
    ).all()

    rerouted_count = 0
    for assign in active_assignments:
        try:
            # Recompute path
            res = db.query(Resource).filter(Resource.id == assign.resource_id).first()
            inc = db.query(Incident).filter(Incident.id == assign.incident_id).first()
            if res and inc:
                nodes_path, dist, eta, geojson = routing_engine.calculate_route(
                    res.latitude, res.longitude, inc.centroid_lat, inc.centroid_lon
                )
                assign.route_geojson = geojson
                assign.distance_km = dist
                assign.eta_minutes = eta
                rerouted_count += 1
        except Exception:
            # Destination might become completely unreachable
            continue

    db.commit()
    db.refresh(edge)
    return edge, rerouted_count

def unblock_road(db: Session, edge_id: str) -> RoadEdge:
    """Unblocks a road segment and restores normal routing weight."""
    edge = db.query(RoadEdge).filter(RoadEdge.id == edge_id).first()
    if not edge:
        raise ValueError(f"Road edge {edge_id} not found")

    edge.is_blocked = False
    
    # Mark active blocks inactive
    db.query(RoadBlock).filter(RoadBlock.edge_id == edge_id).update({"active": False})
    db.commit()

    routing_engine.load_graph_from_db(db)
    db.refresh(edge)
    return edge

