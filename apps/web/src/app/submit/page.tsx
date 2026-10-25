"use client";

import React, { useState } from "react";
import { submitSOS } from "@/lib/api";
import { SOSReport } from "@/lib/types";
import { Send, CheckCircle2, MessageSquare, Sparkles, ArrowRight } from "lucide-react";
import Link from "next/link";

export default function SubmitSOSPage() {
  const [rawText, setRawText] = useState("");
  const [source, setSource] = useState<string>("whatsapp");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<SOSReport | null>(null);

  const sampleMessages = [
    {
      title: "Hinglish (Sector 5 Flood)",
      text: "paani bhar gaya hai near sector 5, 5 log chhat par hain please madad karo",
      source: "whatsapp",
    },
    {
      title: "Hindi (Yamuna Khadar Submerged)",
      text: "यमुना खादर में पानी भर चुका है, 12 लोग फंसे हैं, नाव भेजो",
      source: "mesh",
    },
    {
      title: "English (Kashmere Gate Medical)",
      text: "Urgent medical assistance required at Kashmere Gate ISBT, an elderly woman is bleeding",
      source: "app",
    },
    {
      title: "Hinglish (Mayur Vihar Food Shortage)",
      text: "chhat par paani aa raha hai, bache bhookhe hain ration chahiye at Mayur Vihar",
      source: "whatsapp",
    },
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!rawText.trim()) return;

    setLoading(true);
    try {
      const res = await submitSOS(rawText, source);
      setResult(res);
      setRawText("");
    } catch (err: any) {
      alert(`Submission error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-full bg-dot-grid p-8 max-w-3xl mx-auto space-y-6">
      <div className="pb-4 border-b border-white/10">
        <h1 className="font-serif italic text-3xl text-white">
          Forwarded SOS Ingestion Simulator
        </h1>
        <p className="text-xs text-white/50 mt-1">
          Paste any forwarded WhatsApp SOS message, citizen text, or simulated BLE mesh packet to run entity extraction.
        </p>
      </div>

      {/* Preset sample message pills */}
      <div className="space-y-2">
        <span className="text-[11px] font-semibold uppercase tracking-wider text-white/40 flex items-center gap-1.5">
          <Sparkles className="w-3 h-3 text-gold" /> Test with Preset Disaster Reports:
        </span>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
          {sampleMessages.map((sample, idx) => (
            <button
              key={idx}
              onClick={() => {
                setRawText(sample.text);
                setSource(sample.source);
              }}
              className="text-left p-3 rounded-card bg-white/[0.03] hover:bg-white/[0.07] border border-white/10 hover:border-gold/40 transition-all text-xs group"
            >
              <div className="font-semibold text-white/90 group-hover:text-gold-hover mb-1 flex items-center justify-between">
                <span>{sample.title}</span>
                <span className="text-[10px] text-white/40 uppercase bg-white/5 px-1.5 py-0.5 rounded">
                  {sample.source}
                </span>
              </div>
              <p className="text-white/60 line-clamp-1 italic">"{sample.text}"</p>
            </button>
          ))}
        </div>
      </div>

      {/* Main Submission Form */}
      <form onSubmit={handleSubmit} className="space-y-4 bg-white/[0.04] p-6 rounded-panel border border-white/10">
        <div className="flex items-center gap-4">
          <label className="text-xs text-white/70 font-medium">Channel Source:</label>
          <div className="flex items-center gap-2">
            {["whatsapp", "app", "mesh"].map((ch) => (
              <button
                key={ch}
                type="button"
                onClick={() => setSource(ch)}
                className={`px-3 py-1 rounded-full text-xs font-medium capitalize transition-all border ${
                  source === ch
                    ? "bg-gold text-black border-gold font-semibold"
                    : "bg-white/5 border-white/10 text-white/60 hover:text-white"
                }`}
              >
                {ch}
              </button>
            ))}
          </div>
        </div>

        <div>
          <label className="text-xs text-white/70 font-medium block mb-1.5">
            Raw Message Content (Hindi, Hinglish, English):
          </label>
          <textarea
            rows={4}
            value={rawText}
            onChange={(e) => setRawText(e.target.value)}
            placeholder="e.g. paani bhar gaya hai near sector 5, 5 log chhat par hain please madad karo..."
            className="w-full bg-[#121212] border border-white/20 focus:border-gold rounded-card p-3 text-sm text-white placeholder-white/30 outline-none resize-none"
            required
          />
        </div>

        <button
          type="submit"
          disabled={loading || !rawText.trim()}
          className="w-full py-3 bg-white hover:bg-gold-hover text-black font-semibold rounded-full flex items-center justify-center gap-2 transition-all shadow-lg active:scale-98 disabled:opacity-50"
        >
          <Send className="w-4 h-4" />
          {loading ? "Extracting Entities..." : "Submit SOS Signal ▸"}
        </button>
      </form>

      {/* Result feedback card */}
      {result && (
        <div className="p-5 rounded-panel bg-emerald-500/10 border border-emerald-500/30 space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-emerald-400 font-semibold text-sm">
              <CheckCircle2 className="w-4 h-4" />
              <span>SOS Processed & Enqueued</span>
            </div>
            <Link
              href="/queue"
              className="flex items-center gap-1 text-xs text-gold-hover hover:underline font-semibold"
            >
              Inspect in Queue <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          <div className="text-xs space-y-1 bg-black/40 p-3 rounded-card">
            <div className="text-white/50">Language: <span className="text-white font-medium">{result.language}</span></div>
            <div className="text-white/50">Extracted Need: <span className="text-white font-medium">{result.extracted?.need_type}</span></div>
            <div className="text-white/50">People Count: <span className="text-white font-medium">{result.extracted?.people_count ?? "Unknown"}</span></div>
            <div className="text-white/50">Location: <span className="text-white font-medium">{result.extracted?.location_text ?? "Unresolved"}</span></div>
            <div className="text-white/50">Confidence: <span className="text-emerald-400 font-medium">{(result.confidence * 100).toFixed(0)}%</span></div>
          </div>
        </div>
      )}
    </div>
  );
}

