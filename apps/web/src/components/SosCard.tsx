"use client";

import React, { useState } from "react";
import { SOSReport } from "@/lib/types";
import { Check, X, Edit2, AlertTriangle, MapPin, Users, Activity, MessageSquare } from "lucide-react";
import { verifySOS, rejectSOS, editSOS } from "@/lib/api";

interface SosCardProps {
  report: SOSReport;
  onStatusChange?: (reportId: string, newStatus: string) => void;
}

export default function SosCard({ report, onStatusChange }: SosCardProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [needType, setNeedType] = useState(report.extracted?.need_type || "Rescue");
  const [peopleCount, setPeopleCount] = useState<string>(
    report.extracted?.people_count?.toString() || ""
  );
  const [locationText, setLocationText] = useState(report.extracted?.location_text || "");
  const [loading, setLoading] = useState(false);
  const [undoActive, setUndoActive] = useState(false);

  const handleVerify = async () => {
    setLoading(true);
    try {
      await verifySOS(report.id);
      onStatusChange?.(report.id, "verified");
    } catch (e) {
      alert("Error verifying SOS");
    } finally {
      setLoading(false);
    }
  };

  const handleReject = async () => {
    setLoading(true);
    try {
      await rejectSOS(report.id);
      setUndoActive(true);
      onStatusChange?.(report.id, "rejected");
    } catch (e) {
      alert("Error rejecting SOS");
    } finally {
      setLoading(false);
    }
  };

  const handleSaveEdit = async () => {
    setLoading(true);
    try {
      await editSOS(report.id, {
        need_type: needType,
        people_count: peopleCount ? parseInt(peopleCount, 10) : undefined,
        location_text: locationText,
      });
      setIsEditing(false);
      onStatusChange?.(report.id, report.status);
    } catch (e) {
      alert("Error editing SOS");
    } finally {
      setLoading(false);
    }
  };

  const isLowConfidence = report.confidence < 0.7;
  const isSpam = report.spam_score > 0.8;

  return (
    <div
      className={`rounded-card p-4 transition-all border ${
        report.status === "verified"
          ? "border-emerald-500/30 bg-white/[0.03]"
          : report.status === "rejected"
          ? "border-red-500/20 bg-white/[0.01] opacity-50"
          : "border-white/10 bg-white/[0.04] hover:border-gold/40"
      }`}
    >
      {/* Top line: status badge, source, language, timestamp */}
      <div className="flex items-center justify-between text-xs mb-2">
        <div className="flex items-center gap-2">
          {report.status === "verified" ? (
            <span className="flex items-center gap-1 text-emerald-400 font-medium bg-emerald-500/10 px-2.5 py-0.5 rounded-full border border-emerald-500/30">
              <Check className="w-3 h-3" /> Verified
            </span>
          ) : report.status === "rejected" ? (
            <span className="flex items-center gap-1 text-red-400 font-medium bg-red-500/10 px-2.5 py-0.5 rounded-full border border-red-500/30">
              <X className="w-3 h-3" /> Rejected
            </span>
          ) : (
            <span className="flex items-center gap-1 text-white/60 font-medium border border-dashed border-white/30 px-2.5 py-0.5 rounded-full">
              ○ Unverified
            </span>
          )}

          <span className="text-white/40">·</span>
          <span className="capitalize text-white/70 font-medium flex items-center gap-1">
            <MessageSquare className="w-3 h-3 text-gold" /> {report.source}
          </span>
          <span className="text-white/40">·</span>
          <span className="text-white/60">{report.language}</span>
        </div>

        <div className="flex items-center gap-2 text-white/40">
          <span>{new Date(report.received_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
          {isSpam && (
            <span className="text-[11px] font-bold text-red-400 bg-red-500/10 px-2 py-0.5 rounded border border-red-500/30">
              Spam Alert ({Math.round(report.spam_score * 100)}%)
            </span>
          )}
        </div>
      </div>

      {/* Raw message text */}
      <p className="text-[15px] font-medium text-white mb-3 selection:bg-gold/30">
        "{report.raw_text}"
      </p>

      {/* Extracted fields */}
      {!isEditing ? (
        <div className="flex flex-wrap items-center gap-2 mb-4">
          {/* Need type chip */}
          <div className="flex items-center gap-1.5 bg-white/5 border border-white/10 px-3 py-1 rounded-full text-xs">
            <Activity className="w-3 h-3 text-gold" />
            <span className="text-white/50">Need:</span>
            <span className="font-semibold text-white">{report.extracted?.need_type || "Rescue"}</span>
          </div>

          {/* People count chip */}
          <div className="flex items-center gap-1.5 bg-white/5 border border-white/10 px-3 py-1 rounded-full text-xs">
            <Users className="w-3 h-3 text-gold" />
            <span className="text-white/50">People:</span>
            <span className="font-semibold text-white">
              {report.extracted?.people_count !== null && report.extracted?.people_count !== undefined
                ? report.extracted.people_count
                : "Unknown"}
            </span>
          </div>

          {/* Location chip */}
          <div className="flex items-center gap-1.5 bg-white/5 border border-white/10 px-3 py-1 rounded-full text-xs">
            <MapPin className="w-3 h-3 text-gold" />
            <span className="text-white/50">Location:</span>
            <span className="font-semibold text-white">
              {report.extracted?.location_text || "Unresolved"}
            </span>
          </div>

          {/* Confidence pill */}
          <div
            className={`flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium border ${
              isLowConfidence
                ? "border-amber-500/40 bg-amber-500/10 text-amber-300"
                : "border-white/10 bg-white/5 text-white/70"
            }`}
          >
            {isLowConfidence && <AlertTriangle className="w-3 h-3 text-amber-400" />}
            <span>Conf. {report.confidence.toFixed(2)}</span>
            {isLowConfidence && <span className="underline ml-1">Check</span>}
          </div>
        </div>
      ) : (
        /* Edit Mode inputs */
        <div className="grid grid-cols-1 md:grid-cols-3 gap-2 mb-3 bg-black/40 p-3 rounded-input border border-gold/40">
          <div>
            <label className="text-[11px] text-white/60">Need Type</label>
            <select
              value={needType}
              onChange={(e) => setNeedType(e.target.value)}
              className="w-full bg-[#141414] border border-white/20 rounded px-2 py-1 text-xs text-white focus:border-gold outline-none"
            >
              <option value="Rescue">Rescue</option>
              <option value="Medical">Medical</option>
              <option value="Food">Food</option>
              <option value="Water">Water</option>
            </select>
          </div>

          <div>
            <label className="text-[11px] text-white/60">People Count</label>
            <input
              type="number"
              value={peopleCount}
              onChange={(e) => setPeopleCount(e.target.value)}
              placeholder="Count"
              className="w-full bg-[#141414] border border-white/20 rounded px-2 py-1 text-xs text-white focus:border-gold outline-none"
            />
          </div>

          <div>
            <label className="text-[11px] text-white/60">Location Text</label>
            <input
              type="text"
              value={locationText}
              onChange={(e) => setLocationText(e.target.value)}
              placeholder="e.g. Sector 5"
              className="w-full bg-[#141414] border border-white/20 rounded px-2 py-1 text-xs text-white focus:border-gold outline-none"
            />
          </div>
        </div>
      )}

      {/* Action buttons */}
      <div className="flex items-center justify-between pt-2 border-t border-white/5">
        <div className="flex items-center gap-2">
          {!isEditing ? (
            <button
              onClick={() => setIsEditing(true)}
              className="flex items-center gap-1.5 text-xs text-white/70 hover:text-white bg-white/5 hover:bg-white/10 px-3 py-1.5 rounded-full border border-white/15 transition-all"
            >
              <Edit2 className="w-3 h-3 text-gold" /> Edit
            </button>
          ) : (
            <div className="flex items-center gap-2">
              <button
                onClick={handleSaveEdit}
                disabled={loading}
                className="text-xs bg-gold hover:bg-gold-hover text-black font-semibold px-3 py-1 rounded-full transition-all"
              >
                Save
              </button>
              <button
                onClick={() => setIsEditing(false)}
                className="text-xs text-white/60 hover:text-white px-2 py-1 rounded-full"
              >
                Cancel
              </button>
            </div>
          )}
        </div>

        {report.status !== "verified" && report.status !== "rejected" && (
          <div className="flex items-center gap-2">
            <button
              onClick={handleReject}
              disabled={loading}
              className="flex items-center gap-1 text-xs text-red-400 hover:text-red-300 bg-red-500/10 hover:bg-red-500/20 px-3 py-1.5 rounded-full border border-red-500/30 transition-all"
            >
              <X className="w-3.5 h-3.5" /> Reject
            </button>

            {/* Primary Action Button (White fill, black text, gold hover per design doc) */}
            <button
              onClick={handleVerify}
              disabled={loading}
              className="flex items-center gap-1.5 text-xs font-semibold bg-white hover:bg-gold-hover text-black px-4 py-1.5 rounded-full transition-all shadow-md active:scale-95"
            >
              <Check className="w-3.5 h-3.5" /> Verify ▸
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

