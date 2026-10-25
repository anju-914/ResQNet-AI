"use client";

import React, { useEffect, useRef, useState } from "react";
import maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import { SOSReport, Incident, Resource, RoadEdge, ActiveRoute, RiskZoneFeature } from "@/lib/types";
import { Layers, Shield, AlertTriangle, Route } from "lucide-react";

interface MapViewProps {
  reports: SOSReport[];
  incidents: Incident[];
  resources: Resource[];
  roads: RoadEdge[];
  routes: ActiveRoute[];
  riskZones: RiskZoneFeature[];
  selectedIncidentId?: string | null;
  onSelectIncident?: (incident: Incident) => void;
}

export default function MapView({
  reports,
  incidents,
  resources,
  roads,
  routes,
  riskZones,
  selectedIncidentId,
  onSelectIncident,
}: MapViewProps) {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<maplibregl.Map | null>(null);
  const markersRef = useRef<maplibregl.Marker[]>([]);

  // Layer toggles
  const [showSOS, setShowSOS] = useState(true);
  const [showTeams, setShowTeams] = useState(true);
  const [showRoads, setShowRoads] = useState(true);
  const [showRisk, setShowRisk] = useState(true);

  // Initialize Map
  useEffect(() => {
    if (!mapContainer.current || map.current) return;

    map.current = new maplibregl.Map({
      container: mapContainer.current,
      style: "https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json",
      center: [77.2700, 28.6350], // Central Delhi / Yamuna Basin
      zoom: 11.5,
      pitch: 15,
    });

    map.current.addControl(new maplibregl.NavigationControl({ showCompass: false }), "bottom-right");

    map.current.on("load", () => {
      // Add Sources and Layers for Roads, Routes, Risk Zones
      if (!map.current) return;

      // 1. Risk Zones Source & Layer
      map.current.addSource("risk-zones", {
        type: "geojson",
        data: { type: "FeatureCollection", features: riskZones as any },
      });

      map.current.addLayer({
        id: "risk-zones-fill",
        type: "fill",
        source: "risk-zones",
        paint: {
          "fill-color": "#ef4444",
          "fill-opacity": 0.22,
        },
      });

      map.current.addLayer({
        id: "risk-zones-outline",
        type: "line",
        source: "risk-zones",
        paint: {
          "line-color": "#f97316",
          "line-width": 1.5,
          "line-dasharray": [2, 2],
        },
      });

      // 2. Road Network Source
      const roadFeatures = roads.map((r) => ({
        type: "Feature",
        properties: { id: r.id, is_blocked: r.is_blocked },
        geometry: { type: "LineString", coordinates: r.geometry_coords },
      }));

      map.current.addSource("roads", {
        type: "geojson",
        data: { type: "FeatureCollection", features: roadFeatures as any },
      });

      map.current.addLayer({
        id: "roads-normal",
        type: "line",
        source: "roads",
        filter: ["==", "is_blocked", false],
        paint: {
          "line-color": "#475569",
          "line-width": 2,
          "line-opacity": 0.6,
        },
      });

      map.current.addLayer({
        id: "roads-blocked",
        type: "line",
        source: "roads",
        filter: ["==", "is_blocked", true],
        paint: {
          "line-color": "#ef4444",
          "line-width": 3.5,
          "line-dasharray": [2, 2],
        },
      });

      // 3. Active Rescue Routes (Gold 4px line)
      const routeFeatures = routes.map((rt) => ({
        type: "Feature",
        properties: { id: rt.id },
        geometry: rt.route_geojson,
      }));

      map.current.addSource("active-routes", {
        type: "geojson",
        data: { type: "FeatureCollection", features: routeFeatures as any },
      });

      map.current.addLayer({
        id: "active-routes-line",
        type: "line",
        source: "active-routes",
        paint: {
          "line-color": "#e8d5b7", // --gold-hover
          "line-width": 4,
          "line-opacity": 0.95,
        },
      });
    });

    return () => {
      map.current?.remove();
      map.current = null;
    };
  }, []);

  // Update GeoJSON sources when data changes
  useEffect(() => {
    if (!map.current || !map.current.isStyleLoaded()) return;

    // Update risk zones
    const riskSrc = map.current.getSource("risk-zones") as maplibregl.GeoJSONSource;
    if (riskSrc) {
      riskSrc.setData({ type: "FeatureCollection", features: riskZones as any });
    }

    // Update roads
    const roadSrc = map.current.getSource("roads") as maplibregl.GeoJSONSource;
    if (roadSrc) {
      const roadFeatures = roads.map((r) => ({
        type: "Feature",
        properties: { id: r.id, is_blocked: r.is_blocked },
        geometry: { type: "LineString", coordinates: r.geometry_coords },
      }));
      roadSrc.setData({ type: "FeatureCollection", features: roadFeatures as any });
    }

    // Update active routes
    const routeSrc = map.current.getSource("active-routes") as maplibregl.GeoJSONSource;
    if (routeSrc) {
      const routeFeatures = routes.map((rt) => ({
        type: "Feature",
        properties: { id: rt.id },
        geometry: rt.route_geojson,
      }));
      routeSrc.setData({ type: "FeatureCollection", features: routeFeatures as any });
    }
  }, [roads, routes, riskZones]);

  // Update Markers (SOS Incident Pins & Team Markers)
  useEffect(() => {
    if (!map.current) return;

    // Clear existing markers
    markersRef.current.forEach((m) => m.remove());
    markersRef.current = [];

    // Add Incident markers
    if (showSOS) {
      incidents.forEach((inc) => {
        const el = document.createElement("div");
        const isSelected = selectedIncidentId === inc.id;

        const color =
          inc.priority === "High"
            ? "#ef4444"
            : inc.priority === "Medium"
            ? "#f59e0b"
            : "#60a5fa";

        el.className = `cursor-pointer transition-all transform flex items-center justify-center ${
          isSelected ? "scale-125 z-30" : "hover:scale-110 z-10"
        }`;

        el.innerHTML = `
          <div style="background-color: ${color}; width: 22px; height: 22px; border-radius: 50%; border: 2px solid #ffffff; box-shadow: 0 0 10px ${color}; display: flex; align-items: center; justify-content: center; font-size: 10px; font-weight: bold; color: black;">
            ${inc.people_total}
          </div>
        `;

        el.addEventListener("click", () => {
          onSelectIncident?.(inc);
        });

        const marker = new maplibregl.Marker({ element: el })
          .setLngLat([inc.centroid_lon, inc.centroid_lat])
          .addTo(map.current!);

        markersRef.current.push(marker);
      });
    }

    // Add Resource markers (Gold-light squares)
    if (showTeams) {
      resources.forEach((res) => {
        const el = document.createElement("div");
        el.className = "cursor-pointer transform hover:scale-110 z-20";
        el.innerHTML = `
          <div style="background-color: #c9b8a0; width: 20px; height: 20px; border-radius: 4px; border: 1.5px solid #ffffff; box-shadow: 0 0 8px rgba(201, 184, 160, 0.7); display: flex; align-items: center; justify-content: center; font-size: 9px; font-weight: bold; color: #0a0a0a;" title="${res.name}">
            ■
          </div>
        `;

        const marker = new maplibregl.Marker({ element: el })
          .setLngLat([res.longitude, res.latitude])
          .addTo(map.current!);

        markersRef.current.push(marker);
      });
    }
  }, [incidents, resources, selectedIncidentId, showSOS, showTeams]);

  // Handle Layer Visibility Toggles
  useEffect(() => {
    if (!map.current || !map.current.isStyleLoaded()) return;

    if (map.current.getLayer("roads-normal")) {
      map.current.setLayoutProperty("roads-normal", "visibility", showRoads ? "visible" : "none");
    }
    if (map.current.getLayer("roads-blocked")) {
      map.current.setLayoutProperty("roads-blocked", "visibility", showRoads ? "visible" : "none");
    }
    if (map.current.getLayer("risk-zones-fill")) {
      map.current.setLayoutProperty("risk-zones-fill", "visibility", showRisk ? "visible" : "none");
    }
    if (map.current.getLayer("risk-zones-outline")) {
      map.current.setLayoutProperty("risk-zones-outline", "visibility", showRisk ? "visible" : "none");
    }
  }, [showRoads, showRisk]);

  return (
    <div className="relative w-full h-full">
      <div ref={mapContainer} className="w-full h-full" />

      {/* Floating Layer Controls (Section 6 of desgin.md: Floating --panel strip) */}
      <div className="absolute top-4 left-4 glass-panel px-3 py-2 rounded-full flex items-center gap-4 text-xs font-medium z-10 shadow-lg">
        <span className="flex items-center gap-1.5 text-white/50 text-[11px] uppercase tracking-wider">
          <Layers className="w-3.5 h-3.5 text-gold" /> Layers:
        </span>

        <label className="flex items-center gap-1.5 cursor-pointer hover:text-white transition-colors">
          <input
            type="checkbox"
            checked={showSOS}
            onChange={(e) => setShowSOS(e.target.checked)}
            className="accent-gold rounded"
          />
          <span className="w-2.5 h-2.5 rounded-full bg-red-500 inline-block" />
          <span>SOS</span>
        </label>

        <label className="flex items-center gap-1.5 cursor-pointer hover:text-white transition-colors">
          <input
            type="checkbox"
            checked={showTeams}
            onChange={(e) => setShowTeams(e.target.checked)}
            className="accent-gold rounded"
          />
          <span className="w-2.5 h-2.5 rounded bg-[#c9b8a0] inline-block" />
          <span>Teams</span>
        </label>

        <label className="flex items-center gap-1.5 cursor-pointer hover:text-white transition-colors">
          <input
            type="checkbox"
            checked={showRoads}
            onChange={(e) => setShowRoads(e.target.checked)}
            className="accent-gold rounded"
          />
          <span className="w-2.5 h-0.5 bg-slate-400 inline-block" />
          <span>Roads</span>
        </label>

        <label className="flex items-center gap-1.5 cursor-pointer hover:text-white transition-colors">
          <input
            type="checkbox"
            checked={showRisk}
            onChange={(e) => setShowRisk(e.target.checked)}
            className="accent-gold rounded"
          />
          <span className="w-2.5 h-2.5 rounded bg-red-500/40 border border-orange-500 inline-block" />
          <span>Risk Zones</span>
        </label>
      </div>
    </div>
  );
}

