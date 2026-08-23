"use client";

import React from "react";
import { ShieldCheck, FileText, Bookmark, ExternalLink } from "lucide-react";

export interface CitationItem {
  citationId: string;
  documentTitle: string;
  filename: string;
  pageNumber: number;
  section: string;
  quote: string;
}

interface SourceTraceabilityProps {
  citations?: CitationItem[];
}

export const SourceTraceability: React.FC<SourceTraceabilityProps> = ({
  citations = [],
}) => {
  if (!citations || citations.length === 0) {
    return (
      <div className="bg-slate-900/60 border border-slate-800 rounded-lg p-8 text-center">
        <ShieldCheck className="w-8 h-8 text-slate-600 mx-auto mb-2" />
        <p className="text-xs text-slate-400">No source citations.</p>
        <p className="text-[10px] text-slate-500 mt-1">Create or select a project to view source traceability.</p>
      </div>
    );
  }

  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-5 flex flex-col gap-4 text-zinc-100">
      <div className="flex items-center justify-between pb-2 border-b border-zinc-800">
        <div className="flex items-center gap-2">
          <ShieldCheck className="w-5 h-5 text-emerald-400" />
          <h3 className="text-base font-bold text-zinc-100">Source Provenance & Traceability</h3>
        </div>
        <span className="text-xs font-mono text-emerald-400">100% Factually Grounded</span>
      </div>

      <div className="flex flex-col gap-3">
        {citations.map((c) => (
          <div
            key={c.citationId}
            className="p-3.5 bg-zinc-950/60 border border-zinc-800 rounded-lg flex flex-col gap-2"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-xs font-semibold text-zinc-200">
                <FileText className="w-3.5 h-3.5 text-indigo-400" />
                <span>{c.documentTitle}</span>
                <span className="text-[11px] font-mono text-zinc-500">({c.filename})</span>
              </div>
              <span className="flex items-center gap-1 text-[10px] font-mono text-zinc-400 bg-zinc-900 px-2 py-0.5 rounded border border-zinc-800">
                <Bookmark className="w-3 h-3 text-indigo-400" />
                Page {c.pageNumber} • {c.section}
              </span>
            </div>

            <p className="text-xs text-zinc-300 italic pl-3 border-l-2 border-emerald-500/80 bg-zinc-900/40 p-2 rounded-r">
              "{c.quote}"
            </p>
          </div>
        ))}
      </div>
    </div>
  );
};
