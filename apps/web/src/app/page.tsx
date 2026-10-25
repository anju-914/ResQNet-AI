"use client";

import React, { useEffect, useState } from "react";
import dynamic from "next/dynamic";
import {
  fetchSOSReports,
  fetchIncidents,
  fetchResources,
  fetchRoads,
  fetchActiveRoutes,
  fetchRiskZones,
} from "@/lib/api";
import {
  SOSReport,
  Incident,
  Resource,
  RoadEdge,
  ActiveRoute,
  RiskZoneFeature,
} from "@/lib/types";
import IncidentPanel from "@/components/IncidentPanel";
import { Radio, AlertCircle, ChevronRight, X } from "lucide-react";
import Link from "next/link";

// Dynamic import of MapView to avoid SSR window/document issues
const MapView = dynamic(() => import("@/components/MapView"), { ssr: false });

export default function DashboardPage() {
  const [reports, setReports] = useState<SOSReport[]>([]);
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [resources, setResources] = useState<Resource[]>([]);
  const [roads, setRoads] = useState<RoadEdge[]>([]);
  const [routes, setRoutes] = useState<ActiveRoute[]>([]);
  const [riskZones, setRiskZones] = useState<RiskZoneFeature[]>([]);
  const [selectedIncident, setSelectedIncident] = useState<Incident | null>(null);
  const [feedOpen, setFeedOpen] = useState(true);

  const loadData = async () => {
    try {
      const [repData, incData, resData, roadData, routeData, riskData] = await Promise.all([
        fetchSOSReports(),
        fetchIncidents(),
        fetchResources(),
        fetchRoads(),
        fetchActiveRoutes(),
        fetchRiskZones(),
      ]);
      setReports(repData.items);
      setIncidents(incData);
      setResources(resData);
      setRoads(roadData);
      setRoutes(routeData);
      setRiskZones(riskData.features || []);
    } catch (e) {
      console.error("Dashboard polling error", e);
    }
  };

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="relative w-full h-full flex overflow-hidden">
      {/* Central Map Canvas */}
      <div className="flex-1 h-full relative">
        <MapView
          reports={reports}
          incidents={incidents}
          resources={resources}
          roads={roads}
          routes={routes}
          riskZones={riskZones}
          selectedIncidentId={selectedIncident?.id}
          onSelectIncident={(inc) => setSelectedIncident(inc)}
        />
      </div>

      {/* Floating Right Side Panel: Incident Dispatch & Live Feed */}
      <div className="w-[380px] h-full border-l border-white/10 bg-[#0a0a0a]/95 backdrop-blur-xl flex flex-col z-20">
        {/* Panel Header */}
        <div className="p-4 border-b border-white/10 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Radio className="w-4 h-4 text-gold animate-pulse" />
            <h2 className="text-sm font-semibold tracking-wide text-white uppercase">
              {selectedIncident ? "Incident Dispatch" : "Live SOS Feed"}
            </h2>
          </div>
          {selectedIncident && (
            <button
              onClick={() => setSelectedIncident(null)}
              className="text-white/40 hover:text-white p-1 rounded-full hover:bg-white/5"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>

        {/* Content Body */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {selectedIncident ? (
            <IncidentPanel
              incident={selectedIncident}
              resources={resources}
              roads={roads}
              onRoutePlanned={loadData}
              onRoadToggled={loadData}
              onClose={() => setSelectedIncident(null)}
            />
          ) : (
            /* Live Incoming SOS Feed */
            <div className="space-y-2.5">
              <div className="flex items-center justify-between text-xs text-white/50 mb-1">
                <span>Recent Incoming Signals</span>
                <Link
                  href="/queue"
                  className="text-gold hover:text-gold-hover flex items-center gap-0.5"
                >
                  View Queue ({reports.filter((r) => r.status === "extracted" || r.status === "pending").length}) <ChevronRight className="w-3 h-3" />
                </Link>
              </div>

              {reports.slice(0, 8).map((rep) => (
                <div
                  key={rep.id}
                  className="p-3 bg-white/[0.03] hover:bg-white/[0.06] border border-white/5 hover:border-gold/30 rounded-card transition-all cursor-pointer"
                  onClick={() => {
                    const matchedInc = incidents.find((i) => i.id === rep.incident_id);
                    if (matchedInc) setSelectedIncident(matchedInc);
                  }}
                >
                  <div className="flex items-center justify-between text-[11px] mb-1">
                    <span
                      className={`font-semibold ${
                        rep.status === "verified"
                          ? "text-emerald-400"
                          : rep.status === "rejected"
                          ? "text-red-400"
                          : "text-amber-400"
                      }`}
                    >
                      ● {rep.status.toUpperCase()}
                    </span>
                    <span className="text-white/40">
                      {new Date(rep.received_at).toLocaleTimeString([], {
                        hour: "2-digit",
                        minute: "2-digit",
                      })}
                    </span>
                  </div>
                  <p className="text-xs text-white/90 line-clamp-2 mb-2 font-medium">
                    "{rep.raw_text}"
                  </p>
                  <div className="flex items-center gap-2 text-[10px] text-white/50">
                    <span className="bg-white/5 px-2 py-0.5 rounded text-gold">
                      {rep.extracted?.need_type || "Rescue"}
                    </span>
                    <span>·</span>
                    <span>{rep.extracted?.location_text || "Unresolved Location"}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

