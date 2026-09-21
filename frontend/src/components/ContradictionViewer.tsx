import React from "react";
import { AlertCircle, FileText, ChevronRight } from "lucide-react";

interface Contradiction {
  conflict_type: string;
  source_a: string;
  source_b: string;
  severity: string;
  details: string;
}

interface ContradictionViewerProps {
  contradictions?: Contradiction[];
  detectorModel?: string;
}

export default function ContradictionViewer({
  contradictions = [],
  detectorModel = "freephdlabor-v1 (Academic Discovery)",
}: ContradictionViewerProps) {
  return (
    <div className="space-y-6 p-4">
      {/* Overview Card */}
      <div className="glass-panel p-5 border border-zinc-800 bg-zinc-950/60 rounded-xl space-y-4">
        <div className="flex items-center gap-2.5 border-b border-zinc-855 pb-3">
          <div className="p-1.5 bg-red-950/30 border border-red-800/40 rounded text-red-400">
            <AlertCircle className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-lg font-mono font-bold tracking-wider text-slate-100 uppercase">Research Contradictions</h3>
            <p className="text-xs font-mono text-slate-400">Cross-referencing papers via FreePHDLabor academic synthesis engine to flag design tradeoffs.</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-zinc-900/40 border border-zinc-850 p-4 rounded-lg text-center space-y-1">
            <div className="text-[10px] font-mono font-bold text-slate-500 uppercase tracking-wider">Total Detected</div>
            <div className="text-2xl font-mono font-black text-red-500">{contradictions.length}</div>
          </div>
          <div className="bg-zinc-900/40 border border-zinc-850 p-4 rounded-lg text-center space-y-1">
            <div className="text-[10px] font-mono font-bold text-slate-500 uppercase tracking-wider">Critical/High Severity</div>
            <div className="text-2xl font-mono font-black text-amber-500">
              {contradictions.filter(c => c.severity === "critical" || c.severity === "high").length}
            </div>
          </div>
          <div className="bg-zinc-900/40 border border-zinc-850 p-4 rounded-lg text-center space-y-1 col-span-2">
            <div className="text-[10px] font-mono font-bold text-slate-500 uppercase tracking-wider">Detector Model / Engine</div>
            <div className="text-sm font-mono font-bold text-emerald-400 pt-1.5">{detectorModel}</div>
          </div>
        </div>
      </div>

      {/* Contradictions List */}
      <div className="space-y-4">
        {contradictions.length > 0 ? (
          contradictions.map((c, idx) => (
            <div key={idx} className="glass-panel p-5 border border-zinc-800 bg-zinc-950/60 rounded-xl space-y-3">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-zinc-900 pb-2.5">
                <div className="flex items-center gap-2">
                  <span className={`text-[10px] font-mono font-bold uppercase tracking-widest px-2 py-0.5 border rounded ${
                    c.severity === "critical" ? "text-red-400 bg-red-950/20 border-red-800/40" :
                    c.severity === "high" ? "text-amber-400 bg-amber-950/20 border-amber-800/40" :
                    c.severity === "medium" ? "text-yellow-400 bg-yellow-950/20 border-yellow-800/40" :
                    "text-slate-400 bg-slate-900/20 border-slate-800/40"
                  }`}>
                    {c.severity}
                  </span>
                  <span className="text-xs font-mono font-extrabold text-slate-300 uppercase tracking-wider">
                    {c.conflict_type} Conflict
                  </span>
                </div>
              </div>

              {/* Sources Comparison */}
              <div className="grid grid-cols-1 md:grid-cols-5 gap-3 items-center bg-zinc-900/30 p-3 rounded-lg border border-zinc-850">
                <div className="md:col-span-2 space-y-1">
                  <div className="text-[9px] font-mono text-slate-500 uppercase tracking-wider flex items-center gap-1">
                    <FileText className="w-3 h-3 text-cyan-400" /> Source Paper A
                  </div>
                  <div className="text-xs font-mono font-bold text-slate-300 line-clamp-1">{c.source_a}</div>
                </div>
                <div className="flex justify-center text-red-500 font-black font-mono text-xs">
                  VS
                </div>
                <div className="md:col-span-2 space-y-1">
                  <div className="text-[9px] font-mono text-slate-500 uppercase tracking-wider flex items-center gap-1">
                    <FileText className="w-3 h-3 text-cyan-400" /> Source Paper B
                  </div>
                  <div className="text-xs font-mono font-bold text-slate-300 line-clamp-1">{c.source_b}</div>
                </div>
              </div>

              {/* Description */}
              <div className="bg-zinc-900/10 border border-zinc-900 p-3.5 rounded-lg">
                <div className="text-[10px] font-mono font-bold text-slate-400 uppercase tracking-widest mb-1">Details & Rationale</div>
                <p className="text-xs font-mono text-slate-300 leading-relaxed">{c.details}</p>
              </div>
            </div>
          ))
        ) : (
          <div className="glass-panel p-8 text-center border border-zinc-800 bg-zinc-950/60 rounded-xl">
            <div className="text-sm font-mono text-slate-500 italic">No academic contradictions found across referenced papers.</div>
          </div>
        )}
      </div>
    </div>
  );
}
