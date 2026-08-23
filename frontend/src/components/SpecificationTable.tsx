"use client";

import React from "react";
import { Sliders, Bookmark, CheckCircle2 } from "lucide-react";

export interface SpecificationItem {
  specificationId: string;
  property: string;
  value: string;
  unit: string;
  sourceDocument: string;
  page: number;
  section: string;
  confidence: number;
}

interface SpecificationTableProps {
  entityName?: string;
  specifications?: SpecificationItem[];
}

export const SpecificationTable: React.FC<SpecificationTableProps> = ({
  entityName,
  specifications = [],
}) => {
  if (!specifications || specifications.length === 0) {
    return (
      <div className="bg-slate-900/60 border border-slate-800 rounded-lg p-8 text-center">
        <Sliders className="w-8 h-8 text-slate-600 mx-auto mb-2" />
        <p className="text-xs text-slate-400">No specifications available.</p>
        <p className="text-[10px] text-slate-500 mt-1">Create or select a project to view specifications.</p>
      </div>
    );
  }

  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-5 flex flex-col gap-4 text-zinc-100">
      <div className="flex items-center justify-between pb-2 border-b border-zinc-800">
        <div className="flex items-center gap-2">
          <Sliders className="w-5 h-5 text-indigo-400" />
          <h3 className="text-base font-bold text-zinc-100">Specifications{entityName ? ` for ${entityName}` : ""}</h3>
        </div>
        <span className="text-xs font-mono text-zinc-400">{specifications.length} Grounded Specs</span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs font-mono">
          <thead>
            <tr className="border-b border-zinc-800 text-zinc-400">
              <th className="pb-2 px-2 font-semibold">Property</th>
              <th className="pb-2 px-2 font-semibold">Value</th>
              <th className="pb-2 px-2 font-semibold">Source Document</th>
              <th className="pb-2 px-2 font-semibold">Page / Sec</th>
              <th className="pb-2 px-2 font-semibold">Confidence</th>
            </tr>
          </thead>
          <tbody>
            {specifications.map((spec) => (
              <tr key={spec.specificationId} className="border-b border-zinc-950 hover:bg-zinc-950/60">
                <td className="py-2.5 px-2 font-bold text-zinc-200">{spec.property}</td>
                <td className="py-2.5 px-2 text-emerald-400 font-semibold">{spec.value}</td>
                <td className="py-2.5 px-2 text-zinc-400">{spec.sourceDocument}</td>
                <td className="py-2.5 px-2 text-zinc-500">
                  P.{spec.page} • {spec.section}
                </td>
                <td className="py-2.5 px-2 text-emerald-400">
                  {(spec.confidence * 100).toFixed(0)}%
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
