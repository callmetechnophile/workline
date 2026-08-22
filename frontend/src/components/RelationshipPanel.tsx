"use client";

import React from "react";
import { GitCommit, ArrowRight, ShieldCheck, Layers, FileText } from "lucide-react";

export interface RelationshipItem {
  relationshipId: string;
  fromEntity: string;
  relationshipType: string;
  toEntity: string;
  sourceType: string;
  confidence: number;
}

interface RelationshipPanelProps {
  entityId?: string;
  relationships?: RelationshipItem[];
}

export const RelationshipPanel: React.FC<RelationshipPanelProps> = ({
  entityId = "ENT-TPS62130",
  relationships = [
    {
      relationshipId: "REL-1",
      fromEntity: "ENT-TPS62130",
      relationshipType: "MANUFACTURED_BY",
      toEntity: "ENT-TEXAS-INSTRUMENTS",
      sourceType: "DOCUMENT_EVIDENCE",
      confidence: 1.0,
    },
    {
      relationshipId: "REL-2",
      fromEntity: "ENT-TPS62130",
      relationshipType: "HAS_DATASHEET",
      toEntity: "DOC-TPS62130",
      sourceType: "DOCUMENT_EVIDENCE",
      confidence: 1.0,
    },
    {
      relationshipId: "REL-3",
      fromEntity: "REQ-3V3-RAIL",
      relationshipType: "SATISFIED_BY",
      toEntity: "ENT-TPS62130",
      sourceType: "DETERMINISTIC_RULE",
      confidence: 0.98,
    },
  ],
}) => {
  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-5 flex flex-col gap-4 text-zinc-100">
      <div className="flex items-center justify-between pb-2 border-b border-zinc-800">
        <div className="flex items-center gap-2">
          <Layers className="w-5 h-5 text-indigo-400" />
          <h3 className="text-base font-bold text-zinc-100">Knowledge Graph Relationships</h3>
        </div>
        <span className="text-xs font-mono text-zinc-400">{relationships.length} Active Edges</span>
      </div>

      <div className="flex flex-col gap-2.5">
        {relationships.map((rel) => (
          <div
            key={rel.relationshipId}
            className="p-3 bg-zinc-950/60 border border-zinc-800 rounded-lg flex items-center justify-between"
          >
            <div className="flex items-center gap-2 text-xs font-mono">
              <span className="font-bold text-zinc-200">{rel.fromEntity}</span>
              <div className="flex items-center gap-1 px-2 py-0.5 rounded bg-indigo-950/60 text-indigo-300 border border-indigo-800 text-[10px]">
                <ArrowRight className="w-3 h-3" />
                <span>{rel.relationshipType}</span>
              </div>
              <span className="font-bold text-indigo-300">{rel.toEntity}</span>
            </div>

            <div className="flex items-center gap-2">
              <span className="text-[10px] font-mono text-zinc-500 bg-zinc-900 px-1.5 py-0.5 rounded border border-zinc-800">
                {rel.sourceType}
              </span>
              <span className="text-[10px] font-mono text-emerald-400">
                {(rel.confidence * 100).toFixed(0)}%
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
