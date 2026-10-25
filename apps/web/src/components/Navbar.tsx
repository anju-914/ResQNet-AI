"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { Radio, AlertCircle, CheckCircle2, Shield, User } from "lucide-react";
import { fetchSOSReports, fetchResources } from "@/lib/api";

export default function Navbar() {
  const [pendingCount, setPendingCount] = useState(0);
  const [verifiedCount, setVerifiedCount] = useState(0);
  const [teamsCount, setTeamsCount] = useState(0);
  const [isLive, setIsLive] = useState(true);

  const loadCounters = async () => {
    try {
      const [sosData, resources] = await Promise.all([
        fetchSOSReports(),
        fetchResources(),
      ]);
      setPendingCount(sosData.pending_count);
      setVerifiedCount(sosData.verified_count);
      setTeamsCount(resources.length);
      setIsLive(true);
    } catch {
      setIsLive(false);
    }
  };

  useEffect(() => {
    loadCounters();
    const interval = setInterval(loadCounters, 4000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header className="h-14 border-b border-white/10 bg-[#0a0a0a] px-6 flex items-center justify-between z-30 select-none">
      {/* Brand & Live status */}
      <div className="flex items-center gap-6">
        <Link href="/" className="flex items-center gap-2 group">
          <span className="font-serif italic text-2xl tracking-wide text-white group-hover:text-gold-hover transition-colors">
            ResQNet AI
          </span>
          <span className="text-[11px] font-medium tracking-widest uppercase bg-white/5 border border-white/10 text-white/60 px-2 py-0.5 rounded-full ml-1">
            Coordinator
          </span>
        </Link>

        {/* Live indicator (Design doc: slow 3s opacity pulse on green dot) */}
        <div className="flex items-center gap-2 bg-white/5 border border-white/10 px-3 py-1 rounded-full text-xs">
          <span
            className={`w-2 h-2 rounded-full ${
              isLive ? "bg-emerald-500 animate-pulse" : "bg-zinc-500"
            }`}
          />
          <span className="text-white/80 font-medium">
            {isLive ? "Live" : "Offline"}
          </span>
        </div>
      </div>

      {/* Real-time Triage Counters */}
      <div className="flex items-center gap-4 text-xs font-medium">
        <Link
          href="/queue"
          className="flex items-center gap-2 bg-white/5 hover:bg-white/10 border border-white/10 hover:border-gold/40 px-3 py-1.5 rounded-full transition-all"
        >
          <AlertCircle className="w-3.5 h-3.5 text-amber-400" />
          <span className="text-white/60">Pending</span>
          <span className="tabular-nums font-semibold text-white bg-amber-500/20 px-2 py-0.2 rounded-full">
            {pendingCount}
          </span>
        </Link>

        <Link
          href="/"
          className="flex items-center gap-2 bg-white/5 hover:bg-white/10 border border-white/10 hover:border-gold/40 px-3 py-1.5 rounded-full transition-all"
        >
          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
          <span className="text-white/60">Verified</span>
          <span className="tabular-nums font-semibold text-white bg-emerald-500/20 px-2 py-0.2 rounded-full">
            {verifiedCount}
          </span>
        </Link>

        <Link
          href="/incidents"
          className="flex items-center gap-2 bg-white/5 hover:bg-white/10 border border-white/10 hover:border-gold/40 px-3 py-1.5 rounded-full transition-all"
        >
          <Shield className="w-3.5 h-3.5 text-gold-light" />
          <span className="text-white/60">Teams</span>
          <span className="tabular-nums font-semibold text-white bg-gold/20 px-2 py-0.2 rounded-full">
            {teamsCount}
          </span>
        </Link>

        {/* Coordinator Profile Pill */}
        <div className="flex items-center gap-2 bg-white/5 border border-white/10 px-3 py-1.5 rounded-full text-white/80">
          <User className="w-3.5 h-3.5 text-gold" />
          <span className="text-xs">NDRF Control</span>
        </div>
      </div>
    </header>
  );
}

