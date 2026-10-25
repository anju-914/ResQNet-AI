import {
  SOSReport,
  SOSListResponse,
  Incident,
  Resource,
  RoadEdge,
  ActiveRoute,
  RiskZoneFeature,
} from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/v1";

export async function fetchSOSReports(status?: string): Promise<SOSListResponse> {
  const url = status ? `${API_BASE}/sos?status=${status}` : `${API_BASE}/sos`;
  const res = await fetch(url, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch SOS reports");
  return res.json();
}

export async function submitSOS(rawText: string, source: string = "app"): Promise<SOSReport> {
  const res = await fetch(`${API_BASE}/sos`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ raw_text: rawText, source }),
  });
  if (!res.ok) throw new Error("Failed to submit SOS");
  return res.json();
}

export async function verifySOS(reportId: string): Promise<SOSReport> {
  const res = await fetch(`${API_BASE}/sos/${reportId}/verify`, {
    method: "PATCH",
  });
  if (!res.ok) throw new Error("Failed to verify SOS");
  return res.json();
}

export async function rejectSOS(reportId: string): Promise<SOSReport> {
  const res = await fetch(`${API_BASE}/sos/${reportId}/reject`, {
    method: "PATCH",
  });
  if (!res.ok) throw new Error("Failed to reject SOS");
  return res.json();
}

export async function editSOS(
  reportId: string,
  data: { need_type?: string; people_count?: number; location_text?: string }
): Promise<SOSReport> {
  const res = await fetch(`${API_BASE}/sos/${reportId}/edit`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Failed to edit SOS");
  return res.json();
}

export async function fetchIncidents(): Promise<Incident[]> {
  const res = await fetch(`${API_BASE}/incidents`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch incidents");
  return res.json();
}

export async function fetchResources(): Promise<Resource[]> {
  const res = await fetch(`${API_BASE}/resources`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch resources");
  return res.json();
}

export async function fetchRoads(): Promise<RoadEdge[]> {
  const res = await fetch(`${API_BASE}/roads`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch roads");
  return res.json();
}

export async function blockRoad(edgeId: string): Promise<any> {
  const res = await fetch(`${API_BASE}/roads/${edgeId}/block`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ reported_by: "coordinator" }),
  });
  if (!res.ok) throw new Error("Failed to block road");
  return res.json();
}

export async function unblockRoad(edgeId: string): Promise<any> {
  const res = await fetch(`${API_BASE}/roads/${edgeId}/block`, {
    method: "DELETE",
  });
  if (!res.ok) throw new Error("Failed to unblock road");
  return res.json();
}

export async function planRoute(resourceId: string, incidentId: string): Promise<any> {
  const res = await fetch(`${API_BASE}/routes/plan`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ resource_id: resourceId, incident_id: incidentId }),
  });
  if (!res.ok) throw new Error("Failed to plan route");
  return res.json();
}

export async function fetchActiveRoutes(): Promise<ActiveRoute[]> {
  const res = await fetch(`${API_BASE}/routes/active`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch active routes");
  return res.json();
}

export async function fetchRiskZones(): Promise<{ features: RiskZoneFeature[] }> {
  const res = await fetch(`${API_BASE}/risk-zones`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch risk zones");
  return res.json();
}

