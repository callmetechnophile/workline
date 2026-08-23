"use client";

import React from "react";
import { ShieldCheck, Bookmark, FileText, ExternalLink } from "lucide-react";

export interface EvidenceItem {
  property: string;
  value: string;
  document: string;
  page: number;
  section: string;
  confidence: number;
}

interface EvidencePanelProps {
  entityName?: string;
  evidence?: EvidenceItem[];
}

export const EvidencePanel: React.FC<EvidencePanelProps> = ({
  entityName,
  evidence = [],
}) => {
  if (!evidence || (Array.isArray(evidence) && evidence.length === 0)) {
    return (
      <div className="bg-slate-900/60 border border-slate-800 rounded-lg p-8 text-center">
        <ShieldCheck className="w-8 h-8 text-slate-600 mx-auto mb-2" />
        <p className="text-xs text-slate-400">No evidence available.</p>
        <p className="text-[10px] text-slate-500 mt-1">Create or select a project to view evidence.</p>
      </div>
    );
  }
  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-5 flex flex-col gap-4 text-zinc-100">
      <div className="flex items-center justify-between pb-2 border-b border-zinc-800">
        <div className="flex items-center gap-2">
          <ShieldCheck className="w-5 h-5 text-emerald-400" />
          <h3 className="text-base font-bold text-zinc-100">Evidence Chain for {entityName}</h3>
        </div>
        <span className="text-xs font-mono text-emerald-400">100% Provenance Backed</span>
      </div>

      <div className="flex flex-col gap-3">
        {evidence.map((ev, idx) => (
          <div
            key={idx}
            className="p-3.5 bg-zinc-950/60 border border-zinc-800 rounded-lg flex flex-col gap-2"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-xs font-semibold text-zinc-200">
                <span className="text-zinc-400">{ev.property}:</span>
                <span className="text-emerald-400 font-bold">{ev.value}</span>
              </div>
              <span className="flex items-center gap-1 text-[10px] font-mono text-zinc-400 bg-zinc-900 px-2 py-0.5 rounded border border-zinc-800">
                <Bookmark className="w-3 h-3 text-indigo-400" />
                Page {ev.page} • {ev.section}
              </span>
            </div>

            <div className="flex items-center gap-2 text-[11px] font-mono text-zinc-500 pt-1 border-t border-zinc-900">
              <FileText className="w-3 h-3 text-zinc-600" />
              <span>Source Document: {ev.document}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
