"use client";

import React, { useEffect, useState } from "react";
import { fetchIncidents, fetchResources } from "@/lib/api";
import { Incident, Resource } from "@/lib/types";
import { Activity, Shield, Users, MapPin, ArrowRight } from "lucide-react";
import Link from "next/link";

export default function IncidentsPage() {
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [resources, setResources] = useState<Resource[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([fetchIncidents(), fetchResources()])
      .then(([incData, resData]) => {
        setIncidents(incData);
        setResources(resData);
      })
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="min-h-full bg-dot-grid p-8 max-w-5xl mx-auto space-y-6">
      <div className="flex items-center justify-between pb-4 border-b border-white/10">
        <div>
          <h1 className="font-serif italic text-3xl text-white">
            Verified Incidents
          </h1>
          <p className="text-xs text-white/50 mt-1">
            Aggregated clusters of verified citizen reports requiring emergency response.
          </p>
        </div>

        <Link
          href="/"
          className="flex items-center gap-1.5 text-xs font-semibold bg-white hover:bg-gold-hover text-black px-4 py-2 rounded-full transition-all"
        >
          View on Live Map <ArrowRight className="w-3.5 h-3.5" />
        </Link>
      </div>

      {loading ? (
        <div className="p-12 text-center text-white/40 text-sm">
          Loading incidents...
        </div>
      ) : incidents.length === 0 ? (
        <div className="p-16 text-center border border-dashed border-white/10 rounded-panel bg-white/[0.02]">
          <Activity className="w-10 h-10 text-white/20 mx-auto mb-3" />
          <h3 className="text-base font-medium text-white mb-1">No Active Incidents</h3>
          <p className="text-xs text-white/50 max-w-sm mx-auto">
            Once pending SOS signals in the queue are verified, they will automatically group into incident clusters here.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {incidents.map((inc) => {
            const assignedTeam = resources.find(
              (r) => r.id === inc.assigned_resource_id
            );

            return (
              <div
                key={inc.id}
                className="p-5 bg-white/[0.04] border border-white/10 hover:border-gold/40 rounded-card space-y-3 transition-all"
              >
                <div className="flex items-center justify-between">
                  <span className="font-serif italic text-lg text-white">
                    {inc.need_type}
                  </span>
                  <span
                    className={`px-2.5 py-0.5 rounded-full font-semibold text-[11px] ${
                      inc.priority === "High"
                        ? "bg-red-500/20 text-red-400 border border-red-500/40"
                        : inc.priority === "Medium"
                        ? "bg-amber-500/20 text-amber-400 border border-amber-500/40"
                        : "bg-blue-500/20 text-blue-400 border border-blue-500/40"
                    }`}
                  >
                    ● {inc.priority} Priority
                  </span>
                </div>

                <div className="grid grid-cols-2 gap-2 text-xs">
                  <div className="flex items-center gap-2 bg-white/5 p-2 rounded">
                    <Users className="w-3.5 h-3.5 text-gold" />
                    <span className="text-white/60">People:</span>
                    <span className="font-bold text-white tabular-nums">
                      {inc.people_total}
                    </span>
                  </div>

                  <div className="flex items-center gap-2 bg-white/5 p-2 rounded">
                    <MapPin className="w-3.5 h-3.5 text-gold" />
                    <span className="text-white/60">Centroid:</span>
                    <span className="font-bold text-white tabular-nums text-[11px]">
                      {inc.centroid_lat.toFixed(3)}, {inc.centroid_lon.toFixed(3)}
                    </span>
                  </div>
                </div>

                <div className="pt-2 border-t border-white/5 flex items-center justify-between text-xs">
                  <div className="flex items-center gap-1.5 text-white/70">
                    <Shield className="w-3.5 h-3.5 text-gold-light" />
                    <span>
                      {assignedTeam ? (
                        <span className="text-emerald-400 font-medium">
                          Assigned: {assignedTeam.name}
                        </span>
                      ) : (
                        <span className="text-white/40 italic">Unassigned Unit</span>
                      )}
                    </span>
                  </div>

                  <Link
                    href="/"
                    className="text-gold hover:text-gold-hover font-medium underline text-[11px]"
                  >
                    Dispatch Route →
                  </Link>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

