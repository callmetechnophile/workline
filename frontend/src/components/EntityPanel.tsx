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
  entities = [
    {
      entityId: "ent_1",
      entityType: "COMPONENT",
      originalText: "TPS62130",
      normalizedValue: "TPS62130",
      pageNumber: 1,
      section: "Device Overview",
      confidence: 0.98,
      sourceSpan: "The TPS62130 is an easy-to-use synchronous step-down DC-DC converter.",
    },
    {
      entityId: "ent_2",
      entityType: "CURRENT",
      originalText: "3A",
      normalizedValue: "3 A",
      pageNumber: 3,
      section: "Electrical Characteristics",
      confidence: 0.95,
      sourceSpan: "Output current continuous: 3A maximum across all specified conditions.",
    },
    {
      entityId: "ent_3",
      entityType: "VOLTAGE",
      originalText: "3V3",
      normalizedValue: "3.3 V",
      pageNumber: 4,
      section: "Application Information",
      confidence: 0.96,
      sourceSpan: "Typical 3V3 power rail configuration with external inductor.",
    },
  ],
  onSelectEntity,
}) => {
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
