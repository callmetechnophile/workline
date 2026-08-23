"use client";

import React, { useState } from "react";
import { Cpu, CheckCircle, HelpCircle, ArrowRight } from "lucide-react";

export interface PartVariantItem {
  orderingCode: string;
  package: string;
  packaging: string;
  manufacturer: string;
}

export interface PartResolutionPanelProps {
  canonicalPart?: string;
  variants?: PartVariantItem[];
  selectedCode?: string;
  onSelectVariant?: (code: string) => void;
}

export const PartResolutionPanel: React.FC<PartResolutionPanelProps> = ({
  canonicalPart,
  variants = [],
  selectedCode,
  onSelectVariant,
}) => {
  if (!variants || (Array.isArray(variants) && variants.length === 0)) {
    return (
      <div className="bg-slate-900/60 border border-slate-800 rounded-lg p-8 text-center">
        <Cpu className="w-8 h-8 text-slate-600 mx-auto mb-2" />
        <p className="text-xs text-slate-400">No part resolution data.</p>
        <p className="text-[10px] text-slate-500 mt-1">Create or select a project to view part resolution data.</p>
      </div>
    );
  }
  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-5 flex flex-col gap-4 text-zinc-100">
      <div className="flex items-center gap-2 pb-2 border-b border-zinc-800">
        <Cpu className="w-5 h-5 text-indigo-400" />
        <h3 className="text-base font-bold text-zinc-100">Part & Ordering Code Resolution</h3>
      </div>

      <div className="text-xs text-zinc-400">
        Canonical Engineering Component: <strong className="text-zinc-100">{canonicalPart}</strong>
      </div>

      <div className="flex flex-col gap-2">
        {variants.map((v) => (
          <div
            key={v.orderingCode}
            onClick={() => onSelectVariant && onSelectVariant(v.orderingCode)}
            className={`p-3 rounded-lg border flex items-center justify-between text-xs cursor-pointer transition ${
              v.orderingCode === selectedCode
                ? "bg-indigo-950/30 border-indigo-700/80 text-zinc-100"
                : "bg-zinc-950/50 border-zinc-800 text-zinc-400 hover:border-zinc-700"
            }`}
          >
            <div className="flex flex-col gap-0.5">
              <span className="font-mono font-bold text-indigo-300">{v.orderingCode}</span>
              <span className="text-[11px] text-zinc-500">
                {v.manufacturer} • {v.package} • {v.packaging}
              </span>
            </div>
            {v.orderingCode === selectedCode ? (
              <span className="flex items-center gap-1 text-[11px] font-bold text-emerald-400">
                <CheckCircle className="w-3.5 h-3.5" /> Selected
              </span>
            ) : (
              <span className="text-[11px] text-zinc-600">Select</span>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};
