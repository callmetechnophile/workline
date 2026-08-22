"use client";

import React, { useState } from "react";
import { Layers, Eye, Zap, Flame, Shield, Crosshair } from "lucide-react";

export interface ComponentItem {
  id: string;
  reference_designator: string;
  value: string;
  footprint_id: string;
  x: float;
  y: float;
  rotation: float;
  layer: string;
  locked: boolean;
}

export interface BoardDetails {
  width: number;
  height: number;
  thickness: number;
  layer_count: number;
}

interface PCBBoardViewProps {
  board: BoardDetails;
  components: ComponentItem[];
  hotspots?: Array<{ component: string; x: number; y: number; predicted_temp: number }>;
  temperatureGrid?: number[][];
  onSelectComponent?: (comp: ComponentItem) => void;
  selectedComponentId?: string | null;
}

export const PCBBoardView: React.FC<PCBBoardViewProps> = ({
  board,
  components,
  hotspots = [],
  temperatureGrid,
  onSelectComponent,
  selectedComponentId,
}) => {
  const [showThermalOverlay, setShowThermalOverlay] = useState(false);
  const [showNets, setShowNets] = useState(true);

  // SVG dimensions
  const scale = 6.0; // pixels per mm
  const svgWidth = board.width * scale;
  const svgHeight = board.height * scale;

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 shadow-2xl backdrop-blur-md space-y-4">
      {/* Top Toolbar */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 border-b border-slate-800 pb-3">
        <div>
          <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
            <Layers className="w-5 h-5 text-cyan-400" />
            2D PCB BOARD VIEW
            <span className="text-xs font-mono px-2 py-0.5 rounded bg-slate-800 text-cyan-400">
              {board.width} x {board.height} mm ({board.layer_count} Layers)
            </span>
          </h3>
          <p className="text-xs text-slate-400">Normalized physical land patterns and layout placement</p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowThermalOverlay(!showThermalOverlay)}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-all border ${
              showThermalOverlay
                ? "bg-rose-500/20 text-rose-300 border-rose-500/40 shadow-lg shadow-rose-950/40"
                : "bg-slate-800 text-slate-400 border-slate-700 hover:text-slate-200"
            }`}
          >
            <Flame className="w-3.5 h-3.5" /> Thermal Heatmap
          </button>
          <button
            onClick={() => setShowNets(!showNets)}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-all border ${
              showNets
                ? "bg-cyan-500/20 text-cyan-300 border-cyan-500/40"
                : "bg-slate-800 text-slate-400 border-slate-700 hover:text-slate-200"
            }`}
          >
            <Zap className="w-3.5 h-3.5" /> Ratsnest Nets
          </button>
        </div>
      </div>

      {/* SVG Canvas Board Representation */}
      <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 flex justify-center overflow-auto">
        <svg
          width={svgWidth}
          height={svgHeight}
          className="bg-emerald-950/40 border-2 border-emerald-500/60 rounded shadow-inner"
          viewBox={`0 0 ${board.width} ${board.height}`}
        >
          {/* Board Grid Pattern */}
          <defs>
            <pattern id="pcb_grid" width="5" height="5" patternUnits="userSpaceOnUse">
              <path d="M 5 0 L 0 0 0 5" fill="none" stroke="rgba(16, 185, 129, 0.08)" strokeWidth="0.2" />
            </pattern>
          </defs>
          <rect width={board.width} height={board.height} fill="url(#pcb_grid)" />

          {/* Mounting Holes */}
          <circle cx="4" cy="4" r="1.6" fill="#0f172a" stroke="#fbbf24" strokeWidth="0.6" />
          <circle cx={board.width - 4} cy="4" r="1.6" fill="#0f172a" stroke="#fbbf24" strokeWidth="0.6" />
          <circle cx="4" cy={board.height - 4} r="1.6" fill="#0f172a" stroke="#fbbf24" strokeWidth="0.6" />
          <circle cx={board.width - 4} cy={board.height - 4} r="1.6" fill="#0f172a" stroke="#fbbf24" strokeWidth="0.6" />

          {/* Thermal Overlay Gradients */}
          {showThermalOverlay && hotspots.map((h, i) => (
            <circle
              key={i}
              cx={h.x}
              cy={h.y}
              r="12"
              fill="rgba(244, 63, 94, 0.35)"
              className="animate-pulse"
            />
          ))}

          {/* Ratsnest Connections */}
          {showNets && components.slice(0, -1).map((comp, idx) => {
            const nextComp = components[idx + 1];
            return (
              <line
                key={`net_${idx}`}
                x1={comp.x}
                y1={comp.y}
                x2={nextComp.x}
                y2={nextComp.y}
                stroke="rgba(6, 182, 212, 0.4)"
                strokeWidth="0.3"
                strokeDasharray="1,1"
              />
            );
          })}

          {/* Components & Land Patterns */}
          {components.map((comp) => {
            const isSelected = comp.id === selectedComponentId;
            const w = comp.footprint_id.includes("ESP32") ? 18.0 : (comp.footprint_id.includes("SOT223") ? 6.5 : (comp.footprint_id.includes("HDR") ? 10.16 : 4.9));
            const h = comp.footprint_id.includes("ESP32") ? 25.5 : (comp.footprint_id.includes("SOT223") ? 3.5 : (comp.footprint_id.includes("HDR") ? 2.54 : 3.9));

            return (
              <g
                key={comp.id}
                onClick={() => onSelectComponent && onSelectComponent(comp)}
                className="cursor-pointer transition-transform hover:scale-105"
              >
                {/* Courtyard box */}
                <rect
                  x={comp.x - w / 2}
                  y={comp.y - h / 2}
                  width={w}
                  height={h}
                  fill={isSelected ? "rgba(6, 182, 212, 0.25)" : "rgba(30, 41, 59, 0.85)"}
                  stroke={isSelected ? "#22d3ee" : (comp.locked ? "#f43f5e" : "#e2e8f0")}
                  strokeWidth={isSelected ? 0.6 : 0.3}
                  rx="0.4"
                />

                {/* Solder Pads */}
                <circle cx={comp.x - w / 2 + 0.8} cy={comp.y - h / 2 + 0.8} r="0.4" fill="#fbbf24" />
                <circle cx={comp.x + w / 2 - 0.8} cy={comp.y + h / 2 - 0.8} r="0.4" fill="#fbbf24" />

                {/* RefDes Label */}
                <text
                  x={comp.x}
                  y={comp.y + 0.5}
                  fontSize="1.6"
                  fill="#f8fafc"
                  textAnchor="middle"
                  fontFamily="monospace"
                  fontWeight="bold"
                >
                  {comp.reference_designator}
                </text>
              </g>
            );
          })}
        </svg>
      </div>

      {/* Legend & Stats */}
      <div className="flex flex-wrap items-center justify-between gap-3 text-xs text-slate-400 pt-1">
        <div className="flex items-center gap-4">
          <span className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded bg-slate-700 border border-slate-300"></span> SMD Component
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded bg-rose-500"></span> Locked Component
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-amber-400"></span> Pad / Via
          </span>
        </div>
        <span className="text-[11px] text-slate-500 font-mono">
          Origin (0,0): Top-Left Corner
        </span>
      </div>
    </div>
  );
};

export default PCBBoardView;
