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
  citations = [
    {
      citationId: "cit_1",
      documentTitle: "TPS62130 Datasheet",
      filename: "TPS62130.pdf",
      pageNumber: 3,
      section: "Electrical Characteristics",
      quote: "Output current continuous: 3A maximum across all specified conditions.",
    },
    {
      citationId: "cit_2",
      documentTitle: "Power Architecture Spec",
      filename: "Power_Architecture.md",
      pageNumber: 1,
      section: "5V Rail Requirements",
      quote: "The primary 5V system rail requires up to 2.8A peak during telemetry transmissions.",
    },
  ],
}) => {
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
