"use client";

import React, { useState } from "react";
import { Incident, Resource, RoadEdge } from "@/lib/types";
import { Users, Navigation, Shield, AlertOctagon, CheckCircle2, Clock } from "lucide-react";
import { planRoute, blockRoad, unblockRoad } from "@/lib/api";

interface IncidentPanelProps {
  incident: Incident | null;
  resources: Resource[];
  roads: RoadEdge[];
  onRoutePlanned?: () => void;
  onRoadToggled?: () => void;
  onClose?: () => void;
}

export default function IncidentPanel({
  incident,
  resources,
  roads,
  onRoutePlanned,
  onRoadToggled,
  onClose,
}: IncidentPanelProps) {
  const [selectedResourceId, setSelectedResourceId] = useState<string>(
    resources[0]?.id || ""
  );
  const [loading, setLoading] = useState(false);
  const [plannedRouteInfo, setPlannedRouteInfo] = useState<{
    distance_km: number;
    eta_minutes: number;
  } | null>(null);

  if (!incident) {
    return (
      <div className="p-6 text-center text-white/40 text-xs flex flex-col items-center justify-center h-full">
        <Navigation className="w-8 h-8 text-white/20 mb-2 stroke-[1.5]" />
        <span>Select an incident marker on the map to inspect dispatch options and plan a rescue route.</span>
      </div>
    );
  }

  const handlePlanRoute = async () => {
    if (!selectedResourceId) return;
    setLoading(true);
    try {
      const res = await planRoute(selectedResourceId, incident.id);
      setPlannedRouteInfo({
        distance_km: res.distance_km,
        eta_minutes: res.eta_minutes,
      });
      onRoutePlanned?.();
    } catch (e: any) {
      alert(`Routing error: ${e.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleToggleRoad = async (edgeId: string, isBlocked: boolean) => {
    try {
      if (isBlocked) {
        await unblockRoad(edgeId);
      } else {
        await blockRoad(edgeId);
      }
      onRoadToggled?.();
    } catch (e) {
      alert("Error toggling road block");
    }
  };

  return (
    <div className="w-full flex flex-col gap-4 text-xs">
      {/* Header */}
      <div className="flex items-center justify-between pb-3 border-b border-white/10">
        <div>
          <span className="text-[11px] font-bold uppercase tracking-wider text-gold">
            Incident Dispatch
          </span>
          <h3 className="text-base font-semibold text-white">
            {incident.need_type} Emergency
          </h3>
        </div>
        <span
          className={`px-2.5 py-0.5 rounded-full font-semibold ${
            incident.priority === "High"
              ? "bg-red-500/20 text-red-400 border border-red-500/40"
              : incident.priority === "Medium"
              ? "bg-amber-500/20 text-amber-400 border border-amber-500/40"
              : "bg-blue-500/20 text-blue-400 border border-blue-500/40"
          }`}
        >
          ● {incident.priority} Priority
        </span>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-2 gap-2">
        <div className="bg-white/5 border border-white/10 p-2.5 rounded-card flex items-center gap-2">
          <Users className="w-4 h-4 text-gold" />
          <div>
            <div className="text-white/50 text-[10px]">Casualties / Trapped</div>
            <div className="text-sm font-bold text-white tabular-nums">
              {incident.people_total} People
            </div>
          </div>
        </div>

        <div className="bg-white/5 border border-white/10 p-2.5 rounded-card flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          <div>
            <div className="text-white/50 text-[10px]">Linked Reports</div>
            <div className="text-sm font-bold text-white tabular-nums">
              {incident.reports_count} Verified
            </div>
          </div>
        </div>
      </div>

      {/* Team Assignment Selector */}
      <div className="bg-white/5 border border-white/10 p-3 rounded-card flex flex-col gap-2">
        <label className="text-white/70 font-medium flex items-center gap-1.5">
          <Shield className="w-3.5 h-3.5 text-gold-light" /> Assign Rescue Unit
        </label>
        <select
          value={selectedResourceId}
          onChange={(e) => setSelectedResourceId(e.target.value)}
          className="w-full bg-[#141414] border border-white/20 rounded-input px-3 py-2 text-xs text-white focus:border-gold outline-none"
        >
          {resources.map((r) => (
            <option key={r.id} value={r.id}>
              {r.name} ({r.type} · cap: {r.capacity}) - {r.status}
            </option>
          ))}
        </select>
      </div>

      {/* Route Summary */}
      {plannedRouteInfo && (
        <div className="bg-gold/10 border border-gold/40 p-3 rounded-card flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Clock className="w-4 h-4 text-gold-hover animate-pulse" />
            <div>
              <div className="text-white/60 text-[10px]">Calculated ETA</div>
              <div className="text-sm font-bold text-white tabular-nums">
                {plannedRouteInfo.eta_minutes} min
              </div>
            </div>
          </div>
          <div className="text-right">
            <div className="text-white/60 text-[10px]">Total Distance</div>
            <div className="text-sm font-bold text-white tabular-nums">
              {plannedRouteInfo.distance_km} km
            </div>
          </div>
        </div>
      )}

      {/* Primary Action Button (White fill, black text, gold hover) */}
      <button
        onClick={handlePlanRoute}
        disabled={loading}
        className="w-full py-2.5 bg-white hover:bg-gold-hover text-black font-semibold rounded-full flex items-center justify-center gap-2 transition-all shadow-lg active:scale-98"
      >
        <Navigation className="w-4 h-4" />
        {loading ? "Optimizing Route via GNN..." : "Plan Rescue Route ▸"}
      </button>

      {/* Road Blockage Simulation Controls */}
      <div className="mt-2 pt-3 border-t border-white/10">
        <div className="flex items-center justify-between mb-2">
          <span className="text-white/60 text-[11px] font-medium flex items-center gap-1">
            <AlertOctagon className="w-3.5 h-3.5 text-red-400" />
            Simulate Road Blockage
          </span>
          <span className="text-[10px] text-white/40">Dynamic Reroute</span>
        </div>

        <div className="flex flex-col gap-1.5 max-h-36 overflow-y-auto pr-1">
          {roads.slice(0, 6).map((road) => (
            <div
              key={road.id}
              className="flex items-center justify-between p-1.5 bg-white/[0.03] border border-white/5 rounded text-[11px]"
            >
              <span className="truncate max-w-[160px] text-white/70">
                {road.from_node.replace("N_", "")} → {road.to_node.replace("N_", "")}
              </span>
              <button
                onClick={() => handleToggleRoad(road.id, road.is_blocked)}
                className={`px-2 py-0.5 rounded font-medium text-[10px] transition-all ${
                  road.is_blocked
                    ? "bg-red-500 text-white font-bold"
                    : "bg-white/10 hover:bg-red-500/30 text-white/60 hover:text-red-300"
                }`}
              >
                {road.is_blocked ? "✕ Blocked" : "Block"}
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

