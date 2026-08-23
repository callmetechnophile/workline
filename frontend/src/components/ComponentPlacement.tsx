"use client";

import React, { useState } from "react";
import { Crosshair, Move, RotateCw, MapPin } from "lucide-react";

export interface ComponentPlacementItem {
  ref: string;
  part: string;
  package: string;
  x: number;
  y: number;
  rotation: number;
  layer: string;
  status: "PLACED" | "UNPLACED" | "LOCKED";
}

export interface ComponentPlacementProps {
  components?: ComponentPlacementItem[];
  onMoveComponent?: (ref: string, x: number, y: number) => void;
}

export const ComponentPlacement: React.FC<ComponentPlacementProps> = ({
  components,
  onMoveComponent,
}) => {
  if (!components || components.length === 0) {
    return (
      <div className="bg-slate-900/60 border border-slate-800 rounded-lg p-8 text-center">
        <Crosshair className="w-8 h-8 text-slate-600 mx-auto mb-2" />
        <p className="text-xs text-slate-400">No placement data available.</p>
        <p className="text-[10px] text-slate-500 mt-1">Create or select a project to view placement data.</p>
      </div>
    );
  }
  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-5 flex flex-col gap-4 text-zinc-100">
      <div className="flex items-center gap-2 pb-2 border-b border-zinc-800">
        <Crosshair className="w-5 h-5 text-indigo-400" />
        <h3 className="text-base font-bold text-zinc-100">Component Placement Table</h3>
      </div>

      <div className="overflow-x-auto border border-zinc-800 rounded-lg">
        <table className="w-full text-left text-xs font-mono">
          <thead className="bg-zinc-950 text-zinc-400 border-b border-zinc-800">
            <tr>
              <th className="p-2.5">Designator</th>
              <th className="p-2.5">Part Name</th>
              <th className="p-2.5">Package</th>
              <th className="p-2.5">Position (X, Y)</th>
              <th className="p-2.5">Rotation</th>
              <th className="p-2.5">Layer</th>
              <th className="p-2.5">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-zinc-800 bg-zinc-900">
            {components.map((c) => (
              <tr key={c.ref} className="hover:bg-zinc-800/40 transition">
                <td className="p-2.5 font-bold text-indigo-300">{c.ref}</td>
                <td className="p-2.5 text-zinc-200">{c.part}</td>
                <td className="p-2.5 text-zinc-400">{c.package}</td>
                <td className="p-2.5 text-zinc-300">({c.x.toFixed(1)}, {c.y.toFixed(1)}) mm</td>
                <td className="p-2.5 text-zinc-400">{c.rotation}°</td>
                <td className="p-2.5 text-zinc-300">{c.layer}</td>
                <td className="p-2.5">
                  <span className="px-1.5 py-0.5 rounded text-[10px] bg-emerald-950/50 text-emerald-400">
                    {c.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
