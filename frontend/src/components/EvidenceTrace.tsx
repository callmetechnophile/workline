"use client";

import React from "react";
import { ShieldCheck, Bookmark, FileText } from "lucide-react";

export interface EvidenceTraceItem {
  property: string;
  value: string;
  sourceDocument: string;
  page: number;
  section: string;
  sourceSpan: string;
}

interface EvidenceTraceProps {
  traces?: EvidenceTraceItem[];
}

export const EvidenceTrace: React.FC<EvidenceTraceProps> = ({
  traces = [
    {
      property: "output_current",
      value: "3 A",
      sourceDocument: "TPS62130_Datasheet.pdf",
      page: 1,
      section: "Features",
      sourceSpan: "Output current continuous: 3A maximum across all specified conditions.",
    },
  ],
}) => {
  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-5 flex flex-col gap-4 text-zinc-100">
      <div className="flex items-center justify-between pb-2 border-b border-zinc-800">
        <div className="flex items-center gap-2">
          <ShieldCheck className="w-5 h-5 text-emerald-400" />
          <h3 className="text-base font-bold text-zinc-100">Evidence Traceability</h3>
        </div>
        <span className="text-xs font-mono text-emerald-400">100% Grounded</span>
      </div>

      <div className="flex flex-col gap-3">
        {traces.map((t, idx) => (
          <div
            key={idx}
            className="p-3.5 bg-zinc-950/60 border border-zinc-800 rounded-lg flex flex-col gap-2 text-xs font-mono"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="font-bold text-zinc-200">{t.property}:</span>
                <span className="text-emerald-400 font-bold">{t.value}</span>
              </div>
              <span className="flex items-center gap-1 text-[10px] text-zinc-400 bg-zinc-900 px-2 py-0.5 rounded border border-zinc-800">
                <Bookmark className="w-3 h-3 text-indigo-400" />
                P.{t.page} • {t.section}
              </span>
            </div>

            <p className="text-[11px] text-zinc-300 italic pl-2.5 border-l-2 border-emerald-500/80">
              "{t.sourceSpan}"
            </p>

            <div className="flex items-center gap-1.5 text-[10px] text-zinc-500 pt-1 border-t border-zinc-900">
              <FileText className="w-3 h-3 text-zinc-600" />
              <span>{t.sourceDocument}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
