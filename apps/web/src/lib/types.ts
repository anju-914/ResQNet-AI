export interface ExtractionResult {
  need_type: string;
  people_count: number | null;
  location_text: string | null;
  language: string;
  confidence: number;
  spam_score: number;
}

export interface SOSReport {
  id: string;
  client_uuid: string;
  source: "app" | "whatsapp" | "mesh" | string;
  raw_text: string;
  language: string;
  latitude: number | null;
  longitude: number | null;
  status: "pending" | "extracted" | "verified" | "rejected" | "resolved";
  extracted: ExtractionResult | null;
  confidence: number;
  spam_score: number;
  incident_id: string | null;
  received_at: string;
}

export interface SOSListResponse {
  total: number;
  pending_count: number;
  verified_count: number;
  rejected_count: number;
  items: SOSReport[];
}

export interface Incident {
  id: string;
  centroid_lat: number;
  centroid_lon: number;
  need_type: string;
  people_total: number;
  priority: "High" | "Medium" | "Low";
  status: "active" | "assigned" | "resolved";
  created_at: string;
  reports_count: number;
  assigned_resource_id: string | null;
}

export interface Resource {
  id: string;
  name: string;
  type: "boat" | "medical" | "food" | "search_rescue" | string;
  capacity: number;
  status: "idle" | "dispatched" | "unavailable";
  latitude: number;
  longitude: number;
}

export interface RoadEdge {
  id: string;
  from_node: string;
  to_node: string;
  base_weight: number;
  predicted_weight: number;
  is_blocked: boolean;
  geometry_coords: [number, number][]; // [lon, lat]
}

export interface ActiveRoute {
  id: string;
  resource_id: string;
  incident_id: string;
  route_geojson: {
    type: string;
    coordinates: [number, number][];
  };
  eta_minutes: number;
  distance_km: number;
  status: string;
}

export interface RiskZoneFeature {
  type: "Feature";
  properties: {
    id: string;
    name: string;
    score: number;
    source: string;
  };
  geometry: {
    type: "Polygon";
    coordinates: [number, number][][];
  };
}

