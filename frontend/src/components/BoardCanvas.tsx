"use client";

import React from "react";
import { Layout, Maximize2 } from "lucide-react";

export interface CanvasComponent {
  ref: string;
  x: number;
  y: number;
  width: number;
  height: number;
  rotation: number;
  isHotspot?: boolean;
}

export interface BoardCanvasProps {
  widthMm?: number;
  heightMm?: number;
  components?: CanvasComponent[];
  onSelectComponent?: (ref: string) => void;
}

export const BoardCanvas: React.FC<BoardCanvasProps> = ({
  widthMm = 100,
  heightMm = 80,
  components,
  onSelectComponent,
}) => {
  if (!components || components.length === 0) {
    return (
      <div className="bg-slate-900/60 border border-slate-800 rounded-lg p-8 text-center">
        <Layout className="w-8 h-8 text-slate-600 mx-auto mb-2" />
        <p className="text-xs text-slate-400">No PCB layout data available.</p>
        <p className="text-[10px] text-slate-500 mt-1">Create or select a project to view PCB layout.</p>
      </div>
    );
  }
  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-5 flex flex-col gap-4 text-zinc-100">
      <div className="flex items-center justify-between pb-2 border-b border-zinc-800">
        <div className="flex items-center gap-2">
          <Layout className="w-5 h-5 text-indigo-400" />
          <h3 className="text-base font-bold text-zinc-100">2D Board Placement Canvas</h3>
        </div>
        <span className="text-xs font-mono text-zinc-500">
          Outline: {widthMm} × {heightMm} mm (Scale: 1:1)
        </span>
      </div>

      <div className="relative w-full h-64 bg-zinc-950 border border-zinc-800 rounded-lg flex items-center justify-center overflow-hidden">
        {/* Board Boundary */}
        <div
          className="relative bg-emerald-950/20 border-2 border-emerald-600/80 rounded"
          style={{ width: `${widthMm * 3}px`, height: `${heightMm * 3}px` }}
        >
          {/* Grid overlay */}
          <div className="absolute inset-0 opacity-10 bg-[linear-gradient(to_right,#808080_1px,transparent_1px),linear-gradient(to_bottom,#808080_1px,transparent_1px)] bg-[size:15px_15px]" />

          {/* Placed Components */}
          {components.map((comp) => (
            <div
              key={comp.ref}
              onClick={() => onSelectComponent && onSelectComponent(comp.ref)}
              className={`absolute border cursor-pointer flex items-center justify-center text-[10px] font-mono font-bold transition hover:scale-105 ${
                comp.isHotspot
                  ? "bg-rose-950/80 border-rose-500 text-rose-300 animate-pulse"
                  : "bg-indigo-950/70 border-indigo-500 text-indigo-200 hover:border-indigo-300"
              }`}
              style={{
                left: `${comp.x * 3}px`,
                top: `${comp.y * 3}px`,
                width: `${comp.width * 3}px`,
                height: `${comp.height * 3}px`,
                transform: `rotate(${comp.rotation}deg)`,
              }}
              title={`${comp.ref} (${comp.x}, ${comp.y})`}
            >
              {comp.ref}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
