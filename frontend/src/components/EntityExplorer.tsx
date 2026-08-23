"use client";

import React, { useState } from "react";
import { Cpu, Search, CheckCircle2, AlertTriangle, Layers, Tag, Building } from "lucide-react";

export interface CanonicalEntityItem {
  entityId: string;
  entityType: string;
  canonicalName: string;
  aliases: string[];
  manufacturer?: string;
  status: "ACTIVE" | "INACTIVE" | "SUPERSEDED" | "UNRESOLVED" | "CONFLICTED";
  confidence: number;
}

interface EntityExplorerProps {
  entities?: CanonicalEntityItem[];
  selectedEntityId?: string;
  onSelectEntity?: (entityId: string) => void;
  onSearch?: (query: string) => void;
}

export const EntityExplorer: React.FC<EntityExplorerProps> = ({
  entities = [],
  selectedEntityId,
  onSelectEntity,
  onSearch,
}) => {
  const [searchTerm, setSearchTerm] = useState("");

  if (!entities || (Array.isArray(entities) && entities.length === 0)) {
    return (
      <div className="bg-slate-900/60 border border-slate-800 rounded-lg p-8 text-center">
        <Cpu className="w-8 h-8 text-slate-600 mx-auto mb-2" />
        <p className="text-xs text-slate-400">No entities extracted.</p>
        <p className="text-[10px] text-slate-500 mt-1">Create or select a project to view entities.</p>
      </div>
    );
  }

  const filtered = entities.filter(
    (e) =>
      e.canonicalName.toLowerCase().includes(searchTerm.toLowerCase()) ||
      e.aliases.some((a) => a.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-5 flex flex-col gap-4 text-zinc-100">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Cpu className="w-5 h-5 text-indigo-400" />
          <h3 className="text-base font-bold text-zinc-100">Canonical Entity Explorer</h3>
        </div>
        <span className="text-xs font-mono text-zinc-400">{entities.length} Canonical Entities</span>
      </div>

      <div className="relative">
        <Search className="w-4 h-4 text-zinc-500 absolute left-3 top-2.5" />
        <input
          type="text"
          placeholder="Search by part number, component, or alias..."
          value={searchTerm}
          onChange={(e) => {
            setSearchTerm(e.target.value);
            if (onSearch) onSearch(e.target.value);
          }}
          className="w-full pl-9 pr-3 py-2 bg-zinc-950 border border-zinc-800 rounded-lg text-xs text-zinc-200 placeholder-zinc-500 focus:outline-none focus:border-indigo-500"
        />
      </div>

      <div className="flex flex-col gap-2.5">
        {filtered.map((ent) => {
          const isSelected = ent.entityId === selectedEntityId;
          return (
            <div
              key={ent.entityId}
              onClick={() => onSelectEntity && onSelectEntity(ent.entityId)}
              className={`p-3.5 rounded-lg border transition cursor-pointer flex flex-col gap-2 ${
                isSelected
                  ? "bg-indigo-950/40 border-indigo-500/80 text-zinc-100"
                  : "bg-zinc-950/60 border-zinc-800 hover:border-zinc-700 text-zinc-300"
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-bold text-zinc-100">{ent.canonicalName}</span>
                  <span className="px-1.5 py-0.5 rounded text-[10px] font-mono bg-zinc-800 text-zinc-400 border border-zinc-700">
                    {ent.entityType}
                  </span>
                </div>

                <div className="flex items-center gap-2">
                  <span className="flex items-center gap-1 text-[10px] font-mono text-emerald-400">
                    <CheckCircle2 className="w-3 h-3" />
                    {(ent.confidence * 100).toFixed(0)}%
                  </span>
                  <span
                    className={`px-2 py-0.5 rounded text-[10px] font-mono border ${
                      ent.status === "ACTIVE"
                        ? "bg-emerald-950/60 text-emerald-300 border-emerald-800"
                        : "bg-amber-950/60 text-amber-300 border-amber-800"
                    }`}
                  >
                    {ent.status}
                  </span>
                </div>
              </div>

              {ent.manufacturer && (
                <div className="flex items-center gap-1.5 text-xs text-zinc-400">
                  <Building className="w-3.5 h-3.5 text-zinc-500" />
                  <span>{ent.manufacturer}</span>
                </div>
              )}

              {ent.aliases.length > 0 && (
                <div className="flex items-center gap-1.5 flex-wrap pt-1">
                  <Tag className="w-3 h-3 text-zinc-500" />
                  <span className="text-[10px] text-zinc-500">Aliases:</span>
                  {ent.aliases.map((a, idx) => (
                    <span
                      key={idx}
                      className="px-1.5 py-0.5 rounded text-[10px] font-mono bg-zinc-900 text-zinc-400 border border-zinc-800"
                    >
                      {a}
                    </span>
                  ))}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
