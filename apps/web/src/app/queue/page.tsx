"use client";

import React, { useEffect, useState } from "react";
import { fetchSOSReports } from "@/lib/api";
import { SOSReport } from "@/lib/types";
import SosCard from "@/components/SosCard";
import { Filter, CheckCircle2, Clock, ShieldAlert } from "lucide-react";

export default function VerificationQueuePage() {
  const [reports, setReports] = useState<SOSReport[]>([]);
  const [statusFilter, setStatusFilter] = useState<string>("pending");
  const [languageFilter, setLanguageFilter] = useState<string>("all");
  const [loading, setLoading] = useState(true);

  const loadReports = async () => {
    try {
      setLoading(true);
      const data = await fetchSOSReports(statusFilter === "all" ? undefined : statusFilter);
      setReports(data.items);
    } catch (e) {
      console.error("Queue load error", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadReports();
  }, [statusFilter]);

  const handleStatusChange = (reportId: string, newStatus: string) => {
    setReports((prev) =>
      prev.map((r) => (r.id === reportId ? { ...r, status: newStatus as any } : r))
    );
  };

  const filteredReports = reports.filter((r) => {
    if (languageFilter !== "all" && r.language.toLowerCase() !== languageFilter.toLowerCase()) {
      return false;
    }
    return true;
  });

  return (
    <div className="min-h-full bg-dot-grid p-8 max-w-5xl mx-auto space-y-6">
      {/* Title & Filter bar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-white/10">
        <div>
          <h1 className="font-serif italic text-3xl text-white">
            Verification Queue
          </h1>
          <p className="text-xs text-white/50 mt-1">
            Review model-extracted disaster triage signals before pushing to live map and dispatch routes.
          </p>
        </div>

        {/* Filter controls */}
        <div className="flex items-center gap-3">
          {/* Status filter */}
          <div className="flex items-center bg-white/5 border border-white/10 rounded-full p-1 text-xs">
            <button
              onClick={() => setStatusFilter("pending")}
              className={`px-3 py-1 rounded-full transition-all ${
                statusFilter === "pending"
                  ? "bg-white text-black font-semibold"
                  : "text-white/60 hover:text-white"
              }`}
            >
              Pending ({reports.filter((r) => r.status === "extracted" || r.status === "pending").length})
            </button>
            <button
              onClick={() => setStatusFilter("verified")}
              className={`px-3 py-1 rounded-full transition-all ${
                statusFilter === "verified"
                  ? "bg-white text-black font-semibold"
                  : "text-white/60 hover:text-white"
              }`}
            >
              Verified
            </button>
            <button
              onClick={() => setStatusFilter("all")}
              className={`px-3 py-1 rounded-full transition-all ${
                statusFilter === "all"
                  ? "bg-white text-black font-semibold"
                  : "text-white/60 hover:text-white"
              }`}
            >
              All
            </button>
          </div>

          {/* Language filter */}
          <select
            value={languageFilter}
            onChange={(e) => setLanguageFilter(e.target.value)}
            className="bg-[#141414] border border-white/15 rounded-full px-3 py-1.5 text-xs text-white/80 focus:border-gold outline-none"
          >
            <option value="all">All Languages</option>
            <option value="Hinglish">Hinglish</option>
            <option value="Hindi">Hindi</option>
            <option value="English">English</option>
          </select>
        </div>
      </div>

      {/* Cards List */}
      {loading ? (
        <div className="p-12 text-center text-white/40 text-sm">
          Loading SOS queue...
        </div>
      ) : filteredReports.length === 0 ? (
        <div className="p-16 text-center border border-dashed border-white/10 rounded-panel bg-white/[0.02]">
          <CheckCircle2 className="w-10 h-10 text-emerald-400/60 mx-auto mb-3" />
          <h3 className="text-base font-medium text-white mb-1">Queue is clear</h3>
          <p className="text-xs text-white/50 max-w-sm mx-auto">
            All submitted signals have been verified or triaged. New inbound messages from WhatsApp, Mesh, or App will appear here automatically.
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {filteredReports.map((report) => (
            <SosCard
              key={report.id}
              report={report}
              onStatusChange={handleStatusChange}
            />
          ))}
        </div>
      )}
    </div>
  );
}

