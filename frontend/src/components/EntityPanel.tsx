"use client";

import React from "react";
import { Cpu, Zap, Activity, CheckCircle2, Bookmark, ArrowUpRight } from "lucide-react";

export interface EntityItem {
  entityId: string;
  entityType: string;
  originalText: string;
  normalizedValue: string;
  pageNumber: number;
  section: string;
  confidence: number;
  sourceSpan: string;
}

interface EntityPanelProps {
  entities?: EntityItem[];
  onSelectEntity?: (entity: EntityItem) => void;
}

export const EntityPanel: React.FC<EntityPanelProps> = ({
  entities = [],
  onSelectEntity,
}) => {
  if (!entities || (Array.isArray(entities) && entities.length === 0)) {
    return (
      <div className="bg-slate-900/60 border border-slate-800 rounded-lg p-8 text-center">
        <Cpu className="w-8 h-8 text-slate-600 mx-auto mb-2" />
        <p className="text-xs text-slate-400">No entities available.</p>
        <p className="text-[10px] text-slate-500 mt-1">Create or select a project to view entities.</p>
      </div>
    );
  }
  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-5 flex flex-col gap-4 text-zinc-100">
      <div className="flex items-center justify-between pb-2 border-b border-zinc-800">
        <div className="flex items-center gap-2">
          <Cpu className="w-5 h-5 text-indigo-400" />
          <h3 className="text-base font-bold text-zinc-100">Extracted Engineering Entities</h3>
        </div>
        <span className="text-xs font-mono text-zinc-400">{entities.length} Detected Entities</span>
      </div>

      <div className="flex flex-col gap-2.5">
        {entities.map((ent) => (
          <div
            key={ent.entityId}
            onClick={() => onSelectEntity && onSelectEntity(ent)}
            className="p-3 bg-zinc-950/60 border border-zinc-800 rounded-lg flex flex-col gap-2 hover:border-zinc-700 transition cursor-pointer"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-indigo-950 text-indigo-300 border border-indigo-800">
                  {ent.entityType}
                </span>
                <span className="text-xs font-bold text-zinc-100">{ent.normalizedValue}</span>
                {ent.originalText !== ent.normalizedValue && (
                  <span className="text-[11px] text-zinc-500 font-mono">({ent.originalText})</span>
                )}
              </div>

              <div className="flex items-center gap-2">
                <span className="text-[10px] font-mono text-emerald-400 flex items-center gap-1">
                  <CheckCircle2 className="w-3 h-3" />
                  {(ent.confidence * 100).toFixed(0)}%
                </span>
                <span className="text-[10px] font-mono text-zinc-500 bg-zinc-900 px-1.5 py-0.5 rounded border border-zinc-800 flex items-center gap-1">
                  <Bookmark className="w-2.5 h-2.5" />
                  P.{ent.pageNumber}
                </span>
              </div>
            </div>

            <p className="text-[11px] text-zinc-400 italic pl-2 border-l-2 border-zinc-800 line-clamp-2">
              "{ent.sourceSpan}"
            </p>
          </div>
        ))}
      </div>
    </div>
  );
};
