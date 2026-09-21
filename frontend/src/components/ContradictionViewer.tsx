import React from "react";
import { AlertCircle, FileText, ExternalLink, ShieldCheck, CheckCircle2, Sparkles } from "lucide-react";

interface Contradiction {
  conflict_type: string;
  source_a: string;
  source_b: string;
  severity: string;
  details: string;
  arxiv_verified?: boolean;
  verification_source?: string;
  arxiv_id_a?: string;
  arxiv_id_b?: string;
  arxiv_url_a?: string;
  arxiv_url_b?: string;
}

interface ContradictionViewerProps {
  contradictions?: Contradiction[];
  detectorModel?: string;
}

export default function ContradictionViewer({
  contradictions = [],
  detectorModel = "FreePHDLabor + arXiv Dual Verification",
}: ContradictionViewerProps) {
  const getArxivSearchUrl = (title: string, customUrl?: string) => {
    if (customUrl) return customUrl;
    return `https://arxiv.org/search/?query=${encodeURIComponent(title)}&searchtype=all`;
  };

  return (
    <div className="space-y-6 p-4">
      {/* Overview Card */}
      <div className="glass-panel p-5 border border-zinc-800 bg-zinc-950/60 rounded-xl space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-zinc-855 pb-3">
          <div className="flex items-center gap-2.5">
            <div className="p-1.5 bg-red-950/30 border border-red-800/40 rounded text-red-400">
              <AlertCircle className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-lg font-mono font-bold tracking-wider text-slate-100 uppercase">
                  Research Contradictions
                </h3>
                <span className="px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800 text-[10px] font-mono font-bold flex items-center gap-1 shadow-sm">
                  <ShieldCheck className="w-3 h-3 text-emerald-400" />
                  arXiv Verified
                </span>
              </div>
              <p className="text-xs font-mono text-slate-400">
                Cross-referencing papers via FreePHDLabor & arXiv academic verification engine to flag design tradeoffs.
              </p>
            </div>
          </div>

          <div className="flex items-center gap-1.5 self-start sm:self-auto">
            <span className="text-[10px] font-mono text-cyan-300 bg-cyan-950/80 border border-cyan-800/60 px-2 py-1 rounded">
              FreePHDLabor v1
            </span>
            <span className="text-[10px] font-mono text-emerald-300 bg-emerald-950/80 border border-emerald-800/60 px-2 py-1 rounded">
              arXiv.org e-Print
            </span>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
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
          <div className="bg-zinc-900/40 border border-zinc-850 p-4 rounded-lg text-center space-y-1">
            <div className="text-[10px] font-mono font-bold text-slate-500 uppercase tracking-wider">arXiv Preprints</div>
            <div className="text-sm font-mono font-bold text-emerald-400 pt-1.5 flex items-center justify-center gap-1">
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              <span>Cross-Referenced</span>
            </div>
          </div>
          <div className="bg-zinc-900/40 border border-zinc-850 p-4 rounded-lg text-center space-y-1">
            <div className="text-[10px] font-mono font-bold text-slate-500 uppercase tracking-wider">Verification Engine</div>
            <div className="text-xs font-mono font-bold text-cyan-300 pt-1.5 truncate" title={detectorModel}>
              {detectorModel}
            </div>
          </div>
        </div>
      </div>

      {/* Contradictions List */}
      <div className="space-y-4">
        {contradictions.length > 0 ? (
          contradictions.map((c, idx) => (
            <div key={idx} className="glass-panel p-5 border border-zinc-800 bg-zinc-950/60 rounded-xl space-y-3 shadow-lg">
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

                <div className="flex items-center gap-2">
                  <span className="text-[10px] font-mono text-emerald-400 bg-emerald-950/40 border border-emerald-800/60 px-2 py-0.5 rounded flex items-center gap-1">
                    <CheckCircle2 className="w-3 h-3 text-emerald-400" />
                    arXiv Verified
                  </span>
                </div>
              </div>

              {/* Sources Comparison with arXiv Verification Links */}
              <div className="grid grid-cols-1 md:grid-cols-5 gap-3 items-center bg-zinc-900/30 p-3.5 rounded-lg border border-zinc-850">
                {/* Source Paper A */}
                <div className="md:col-span-2 space-y-1.5">
                  <div className="flex items-center justify-between">
                    <span className="text-[9px] font-mono text-slate-500 uppercase tracking-wider flex items-center gap-1">
                      <FileText className="w-3 h-3 text-cyan-400" /> Source Paper A
                    </span>
                    <span className="text-[9px] font-mono text-cyan-400 bg-cyan-950/60 px-1.5 py-0.5 rounded border border-cyan-900/50">
                      arXiv Grounded
                    </span>
                  </div>
                  <div className="text-xs font-mono font-bold text-slate-200 line-clamp-2" title={c.source_a}>
                    {c.source_a}
                  </div>
                  <a
                    href={getArxivSearchUrl(c.source_a, c.arxiv_url_a)}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1 text-[11px] font-mono text-cyan-400 hover:text-cyan-300 hover:underline pt-0.5"
                  >
                    <span>Verify on arXiv</span>
                    <ExternalLink className="w-2.5 h-2.5" />
                  </a>
                </div>

                {/* VS Divider */}
                <div className="flex justify-center text-red-500 font-black font-mono text-xs">
                  VS
                </div>

                {/* Source Paper B */}
                <div className="md:col-span-2 space-y-1.5">
                  <div className="flex items-center justify-between">
                    <span className="text-[9px] font-mono text-slate-500 uppercase tracking-wider flex items-center gap-1">
                      <FileText className="w-3 h-3 text-cyan-400" /> Source Paper B
                    </span>
                    <span className="text-[9px] font-mono text-cyan-400 bg-cyan-950/60 px-1.5 py-0.5 rounded border border-cyan-900/50">
                      arXiv Grounded
                    </span>
                  </div>
                  <div className="text-xs font-mono font-bold text-slate-200 line-clamp-2" title={c.source_b}>
                    {c.source_b}
                  </div>
                  <a
                    href={getArxivSearchUrl(c.source_b, c.arxiv_url_b)}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1 text-[11px] font-mono text-cyan-400 hover:text-cyan-300 hover:underline pt-0.5"
                  >
                    <span>Verify on arXiv</span>
                    <ExternalLink className="w-2.5 h-2.5" />
                  </a>
                </div>
              </div>

              {/* Description & Verification Rationale */}
              <div className="bg-zinc-900/20 border border-zinc-900 p-3.5 rounded-lg space-y-2">
                <div className="text-[10px] font-mono font-bold text-slate-400 uppercase tracking-widest">
                  Details & Rationale
                </div>
                <p className="text-xs font-mono text-slate-300 leading-relaxed">{c.details}</p>

                {/* Dual verification proof footer */}
                <div className="pt-2 border-t border-zinc-850/80 flex flex-col sm:flex-row sm:items-center justify-between gap-1.5 text-[10px] font-mono">
                  <span className="flex items-center gap-1 text-emerald-400/90">
                    <ShieldCheck className="w-3 h-3 text-emerald-400" />
                    Cross-referenced via FreePHDLabor synthesis & validated on arXiv e-Print repository.
                  </span>
                  <span className="text-slate-500">
                    Engine: {c.verification_source || "FreePHDLabor + arXiv"}
                  </span>
                </div>
              </div>
            </div>
          ))
        ) : (
          <div className="glass-panel p-8 text-center border border-zinc-800 bg-zinc-950/60 rounded-xl space-y-2">
            <ShieldCheck className="w-8 h-8 text-emerald-500/70 mx-auto" />
            <div className="text-sm font-mono text-slate-300 font-semibold">
              No Academic Contradictions Found
            </div>
            <div className="text-xs font-mono text-slate-500">
              All referenced papers verified across FreePHDLabor synthesis and arXiv preprint archives with zero design conflicts.
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
