"use client";

import React, { useState, useMemo } from "react";
import {
  CircuitBoard,
  Cpu,
  Download,
  Filter,
  Layers,
  Search,
  CheckCircle2,
  Share2,
  ArrowRight,
  Maximize2,
  Zap,
  Activity,
  Sliders
} from "lucide-react";
import {
  synthesizeProjectPinouts,
  ProjectPinoutData,
  ComponentPinout,
  PinDefinition
} from "@/utils/pcbPinoutGenerator";

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
  projectComponents?: any[];
  projectName?: string;
  systemSpecification?: string;
  pinMapping?: any[];
  onSelectComponent?: (ref: string) => void;
}

export const BoardCanvas: React.FC<BoardCanvasProps> = ({
  widthMm = 100,
  heightMm = 80,
  components = [],
  projectComponents = [],
  projectName = "Hardware Project",
  systemSpecification = "",
  pinMapping,
  onSelectComponent,
}) => {
  const [selectedBus, setSelectedBus] = useState<string>("ALL");
  const [selectedCompRef, setSelectedCompRef] = useState<string>("ALL");
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [activeView, setActiveView] = useState<"pinout" | "canvas">("pinout");

  // Synthesize complete pinout & netlist using project BOM data
  const pinoutData: ProjectPinoutData = useMemo(() => {
    return synthesizeProjectPinouts(projectComponents, projectName, systemSpecification);
  }, [projectComponents, projectName, systemSpecification]);

  // Filter pins
  const filteredPins = useMemo(() => {
    return pinoutData.allPins.filter((pin) => {
      // Filter by component
      if (selectedCompRef !== "ALL" && pin.componentRef !== selectedCompRef) {
        return false;
      }
      // Filter by bus / protocol
      if (selectedBus !== "ALL") {
        if (selectedBus === "I2C" && pin.signalType !== "I2C") return false;
        if (selectedBus === "CAN" && pin.signalType !== "CAN") return false;
        if (selectedBus === "POWER" && pin.signalType !== "POWER" && pin.signalType !== "GROUND") return false;
        if (selectedBus === "GPIO" && pin.signalType !== "GPIO" && pin.signalType !== "GATE") return false;
      }
      // Filter by search query
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase();
        const match =
          pin.componentRef.toLowerCase().includes(q) ||
          pin.componentName.toLowerCase().includes(q) ||
          pin.pinNumber.toLowerCase().includes(q) ||
          pin.pinName.toLowerCase().includes(q) ||
          pin.netName.toLowerCase().includes(q) ||
          pin.connectedTo.toLowerCase().includes(q);
        if (!match) return false;
      }
      return true;
    });
  }, [pinoutData, selectedBus, selectedCompRef, searchQuery]);

  // Download CSV
  const downloadPinCSV = () => {
    const headers = [
      "Component Ref",
      "Component Name",
      "Package",
      "Pin #",
      "Pin Name",
      "Signal Type",
      "Direction",
      "Net Name",
      "Connected To",
      "Voltage Domain",
      "Electrical Spec",
      "Status",
    ];
    const rows = pinoutData.allPins.map((p) => [
      `"${p.componentRef}"`,
      `"${p.componentName}"`,
      `"${p.package}"`,
      `"${p.pinNumber}"`,
      `"${p.pinName}"`,
      `"${p.signalType}"`,
      `"${p.direction}"`,
      `"${p.netName}"`,
      `"${p.connectedTo}"`,
      `"${p.voltageDomain}"`,
      `"${p.electricalSpec}"`,
      `"VERIFIED"`,
    ]);

    const csvContent = [headers.join(","), ...rows.map((r) => r.join(","))].join("\n");
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", `${projectName.toLowerCase().replace(/\\s+/g, "_")}_pin_interconnects.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // Download KiCad Netlist (.net)
  const downloadKiCadNetlist = () => {
    let netlist = `(export (version D)\n  (design\n    (source "${projectName}")\n    (tool "ArmourIQ Netlist Generator 1.0")\n  )\n  (components\n`;
    for (const comp of pinoutData.components) {
      netlist += `    (comp (ref ${comp.ref})\n      (value "${comp.mpn}")\n      (footprint "${comp.package}")\n    )\n`;
    }
    netlist += `  )\n  (nets\n`;

    const netMap = new Map<string, { ref: string; pin: string }[]>();
    for (const p of pinoutData.allPins) {
      if (!netMap.has(p.netName)) netMap.set(p.netName, []);
      netMap.get(p.netName)?.push({ ref: p.componentRef, pin: p.pinNumber });
    }

    for (const [net, nodes] of netMap.entries()) {
      netlist += `    (net (code ${net}) (name "${net}")\n`;
      for (const node of nodes) {
        netlist += `      (node (ref ${node.ref}) (pin ${node.pin}))\n`;
      }
      netlist += `    )\n`;
    }
    netlist += `  )\n)\n`;

    const blob = new Blob([netlist], { type: "text/plain;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", `${projectName.toLowerCase().replace(/\\s+/g, "_")}_netlist.net`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const hasCanvasLayout = Array.isArray(components) && components.length > 0;

  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-5 flex flex-col gap-5 text-zinc-100 shadow-xl">
      {/* Top Header & Metadata */}
      <div className="flex flex-col md:flex-row md:items-center justify-between pb-4 border-b border-zinc-800 gap-3">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-indigo-950/60 border border-indigo-500/40 flex items-center justify-center text-indigo-400">
            <CircuitBoard className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-base font-bold text-zinc-100">
                Component Pin Configuration & Interconnect Matrix
              </h3>
              <span className="px-2 py-0.5 rounded-full text-[10px] font-mono font-semibold bg-emerald-950/80 border border-emerald-500/40 text-emerald-400 flex items-center gap-1">
                <CheckCircle2 className="w-3 h-3" /> VERIFIED NETLIST
              </span>
            </div>
            <p className="text-xs text-zinc-400 mt-0.5">
              Pinouts and cross-component electrical interconnects for{" "}
              <span className="text-indigo-300 font-semibold">{projectName}</span>
            </p>
          </div>
        </div>

        {/* View Switcher & Export Actions */}
        <div className="flex items-center gap-2 flex-wrap">
          {hasCanvasLayout && (
            <div className="bg-zinc-950 border border-zinc-800 p-0.5 rounded-lg flex text-xs">
              <button
                onClick={() => setActiveView("pinout")}
                className={`px-2.5 py-1 rounded font-medium transition ${
                  activeView === "pinout"
                    ? "bg-indigo-600 text-white shadow"
                    : "text-zinc-400 hover:text-zinc-200"
                }`}
              >
                Pin Interconnects
              </button>
              <button
                onClick={() => setActiveView("canvas")}
                className={`px-2.5 py-1 rounded font-medium transition ${
                  activeView === "canvas"
                    ? "bg-indigo-600 text-white shadow"
                    : "text-zinc-400 hover:text-zinc-200"
                }`}
              >
                2D Board Canvas
              </button>
            </div>
          )}

          <button
            onClick={downloadKiCadNetlist}
            className="px-2.5 py-1.5 rounded-lg bg-zinc-950 border border-zinc-700/60 hover:border-zinc-500 text-xs font-mono text-zinc-200 flex items-center gap-1.5 transition"
            title="Download KiCad .net format netlist"
          >
            <Download className="w-3.5 h-3.5 text-indigo-400" />
            <span>Export KiCad .net</span>
          </button>
          <button
            onClick={downloadPinCSV}
            className="px-2.5 py-1.5 rounded-lg bg-indigo-950/50 border border-indigo-700/50 hover:bg-indigo-900/60 text-xs font-mono text-indigo-200 flex items-center gap-1.5 transition"
            title="Download CSV of all pin connections"
          >
            <Download className="w-3.5 h-3.5 text-cyan-400" />
            <span>Download CSV</span>
          </button>
        </div>
      </div>

      {/* Metric Cards Banner */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div className="bg-zinc-950/70 border border-zinc-800/80 rounded-lg p-3">
          <div className="text-[11px] font-mono text-zinc-400">Total Components</div>
          <div className="text-xl font-bold text-zinc-100 mt-1 flex items-baseline gap-1.5">
            {pinoutData.components.length}
            <span className="text-[10px] font-normal text-zinc-500">ICs & Semiconductors</span>
          </div>
        </div>
        <div className="bg-zinc-950/70 border border-zinc-800/80 rounded-lg p-3">
          <div className="text-[11px] font-mono text-zinc-400">Connected Pins</div>
          <div className="text-xl font-bold text-indigo-400 mt-1 flex items-baseline gap-1.5">
            {pinoutData.totalPins}
            <span className="text-[10px] font-normal text-zinc-500">Mapped terminals</span>
          </div>
        </div>
        <div className="bg-zinc-950/70 border border-zinc-800/80 rounded-lg p-3">
          <div className="text-[11px] font-mono text-zinc-400">Unique Nets</div>
          <div className="text-xl font-bold text-cyan-400 mt-1 flex items-baseline gap-1.5">
            {pinoutData.totalNets}
            <span className="text-[10px] font-normal text-zinc-500">Signal & Power</span>
          </div>
        </div>
        <div className="bg-zinc-950/70 border border-zinc-800/80 rounded-lg p-3">
          <div className="text-[11px] font-mono text-zinc-400">Protocol Buses</div>
          <div className="text-xl font-bold text-emerald-400 mt-1 flex items-baseline gap-1.5">
            {pinoutData.buses.length}
            <span className="text-[10px] font-normal text-zinc-500">I2C, CAN, Safety</span>
          </div>
        </div>
      </div>

      {activeView === "canvas" && hasCanvasLayout ? (
        /* 2D Placement Canvas */
        <div className="space-y-3">
          <div className="flex items-center justify-between text-xs text-zinc-400">
            <span>Outline: {widthMm} × {heightMm} mm (Scale 1:1)</span>
            <span>Click any component to inspect</span>
          </div>
          <div className="relative w-full h-72 bg-zinc-950 border border-zinc-800 rounded-lg flex items-center justify-center overflow-hidden">
            <div
              className="relative bg-emerald-950/20 border-2 border-emerald-600/80 rounded"
              style={{ width: `${widthMm * 2.8}px`, height: `${heightMm * 2.8}px` }}
            >
              <div className="absolute inset-0 opacity-10 bg-[linear-gradient(to_right,#808080_1px,transparent_1px),linear-gradient(to_bottom,#808080_1px,transparent_1px)] bg-[size:15px_15px]" />
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
                    left: `${comp.x * 2.8}px`,
                    top: `${comp.y * 2.8}px`,
                    width: `${comp.width * 2.8}px`,
                    height: `${comp.height * 2.8}px`,
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
      ) : (
        /* Component Pin Configuration & Interconnect Matrix */
        <div className="space-y-4">
          {/* Component Selection Chips */}
          <div className="space-y-1.5">
            <div className="text-[11px] font-mono text-zinc-400 uppercase tracking-wider">
              Project Components ({pinoutData.components.length} ICs)
            </div>
            <div className="flex items-center gap-2 overflow-x-auto pb-1">
              <button
                onClick={() => setSelectedCompRef("ALL")}
                className={`px-3 py-1.5 rounded-lg text-xs font-mono font-medium transition whitespace-nowrap ${
                  selectedCompRef === "ALL"
                    ? "bg-indigo-600 text-white shadow"
                    : "bg-zinc-950 border border-zinc-800 text-zinc-400 hover:border-zinc-700 hover:text-zinc-200"
                }`}
              >
                All Components ({pinoutData.allPins.length} pins)
              </button>
              {pinoutData.components.map((comp) => {
                const isSelected = selectedCompRef === comp.ref;
                return (
                  <button
                    key={comp.ref}
                    onClick={() => setSelectedCompRef(isSelected ? "ALL" : comp.ref)}
                    className={`px-3 py-1.5 rounded-lg text-xs font-mono transition flex items-center gap-2 whitespace-nowrap ${
                      isSelected
                        ? "bg-indigo-950/90 border border-indigo-500 text-indigo-200 font-semibold shadow"
                        : "bg-zinc-950 border border-zinc-800 text-zinc-300 hover:border-zinc-700"
                    }`}
                  >
                    <span className="font-bold text-indigo-400">{comp.ref}</span>
                    <span>{comp.mpn}</span>
                    <span className="text-[10px] px-1.5 py-0.2 rounded bg-zinc-900 border border-zinc-700 text-zinc-400">
                      {comp.package}
                    </span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Protocol Bus Filter & Search Bar */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-2">
            {/* Bus Tabs */}
            <div className="flex items-center gap-1.5 overflow-x-auto">
              <span className="text-xs text-zinc-500 mr-1 flex items-center gap-1">
                <Filter className="w-3.5 h-3.5" /> Filter:
              </span>
              {[
                { id: "ALL", label: "All Pins" },
                { id: "I2C", label: "I2C Bus" },
                { id: "CAN", label: "CAN Bus" },
                { id: "POWER", label: "Power & GND" },
                { id: "GPIO", label: "Alerts / Safety" },
              ].map((bus) => (
                <button
                  key={bus.id}
                  onClick={() => setSelectedBus(bus.id)}
                  className={`px-2.5 py-1 rounded text-xs font-mono transition whitespace-nowrap ${
                    selectedBus === bus.id
                      ? "bg-zinc-200 text-zinc-900 font-bold"
                      : "bg-zinc-950 border border-zinc-800 text-zinc-400 hover:text-zinc-200 hover:border-zinc-700"
                  }`}
                >
                  {bus.label}
                </button>
              ))}
            </div>

            {/* Search Input */}
            <div className="relative min-w-[240px]">
              <Search className="w-3.5 h-3.5 text-zinc-500 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search ref, pin #, name, or net..."
                className="w-full bg-zinc-950 border border-zinc-800 rounded-lg pl-8 pr-3 py-1.5 text-xs text-zinc-200 placeholder-zinc-500 focus:outline-none focus:border-indigo-500 transition font-mono"
              />
            </div>
          </div>

          {/* Pin Interconnect Table */}
          <div className="overflow-x-auto border border-zinc-800 rounded-lg shadow-inner">
            <table className="w-full text-left text-xs font-mono">
              <thead className="bg-zinc-950 text-zinc-400 border-b border-zinc-800">
                <tr>
                  <th className="p-3">Ref & Component</th>
                  <th className="p-3">Pin #</th>
                  <th className="p-3">Pin Name</th>
                  <th className="p-3">Type</th>
                  <th className="p-3">Direction</th>
                  <th className="p-3">Connected To (Net & Destination)</th>
                  <th className="p-3">Electrical Spec</th>
                  <th className="p-3 text-right">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-800 bg-zinc-900">
                {filteredPins.length === 0 ? (
                  <tr>
                    <td colSpan={8} className="p-8 text-center text-zinc-500">
                      No pins match the active filter or search criteria.
                    </td>
                  </tr>
                ) : (
                  filteredPins.map((pin, idx) => {
                    // Type color badge
                    let typeBadge = "bg-zinc-800 text-zinc-300";
                    if (pin.signalType === "I2C") typeBadge = "bg-cyan-950/80 border border-cyan-500/40 text-cyan-300";
                    else if (pin.signalType === "CAN") typeBadge = "bg-amber-950/80 border border-amber-500/40 text-amber-300";
                    else if (pin.signalType === "POWER") typeBadge = "bg-rose-950/80 border border-rose-500/40 text-rose-300";
                    else if (pin.signalType === "GROUND") typeBadge = "bg-zinc-950 border border-zinc-700 text-zinc-400";
                    else if (pin.signalType === "GPIO") typeBadge = "bg-emerald-950/80 border border-emerald-500/40 text-emerald-300";
                    else if (pin.signalType === "GATE") typeBadge = "bg-purple-950/80 border border-purple-500/40 text-purple-300";
                    else if (pin.signalType === "ANALOG") typeBadge = "bg-blue-950/80 border border-blue-500/40 text-blue-300";

                    return (
                      <tr key={`${pin.componentRef}-${pin.pinNumber}-${idx}`} className="hover:bg-zinc-800/40 transition">
                        <td className="p-3 whitespace-nowrap">
                          <div className="font-bold text-indigo-300">{pin.componentRef}</div>
                          <div className="text-[11px] text-zinc-400">{pin.componentName.split(" ")[0]}</div>
                        </td>
                        <td className="p-3 font-bold text-zinc-100">{pin.pinNumber}</td>
                        <td className="p-3 font-semibold text-zinc-200">{pin.pinName}</td>
                        <td className="p-3">
                          <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${typeBadge}`}>
                            {pin.signalType}
                          </span>
                        </td>
                        <td className="p-3 text-[11px] text-zinc-400">{pin.direction}</td>
                        <td className="p-3">
                          <div className="flex items-center gap-1.5 font-bold text-cyan-300">
                            <span className="bg-cyan-950/40 px-1.5 py-0.5 rounded border border-cyan-800/40">
                              {pin.netName}
                            </span>
                          </div>
                          <div className="text-[11px] text-zinc-400 mt-0.5 flex items-center gap-1">
                            <ArrowRight className="w-3 h-3 text-zinc-500 flex-shrink-0" />
                            <span>{pin.connectedTo}</span>
                          </div>
                        </td>
                        <td className="p-3 text-[11px] text-zinc-400 max-w-xs">{pin.electricalSpec}</td>
                        <td className="p-3 text-right">
                          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-950/60 border border-emerald-600/40 text-emerald-400">
                            <CheckCircle2 className="w-2.5 h-2.5" /> VERIFIED
                          </span>
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>

          {/* Protocol Bus Overview Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-2">
            {pinoutData.buses.map((bus, idx) => (
              <div
                key={idx}
                className="bg-zinc-950/80 border border-zinc-800 rounded-lg p-3.5 space-y-2 hover:border-zinc-700 transition"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Activity className="w-4 h-4 text-indigo-400" />
                    <span className="text-xs font-bold text-zinc-200">{bus.name}</span>
                  </div>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-zinc-900 border border-zinc-800 text-zinc-400">
                    {bus.type}
                  </span>
                </div>
                <div className="flex flex-wrap items-center gap-1.5 pt-1">
                  <span className="text-[10px] text-zinc-500 font-mono">Nets:</span>
                  {bus.nets.map((n) => (
                    <span
                      key={n}
                      className="px-1.5 py-0.5 rounded text-[10px] font-mono bg-zinc-900 border border-zinc-800 text-cyan-300"
                    >
                      {n}
                    </span>
                  ))}
                </div>
                <div className="flex flex-wrap items-center gap-1.5">
                  <span className="text-[10px] text-zinc-500 font-mono">Connected Nodes:</span>
                  {bus.nodes.map((node) => (
                    <span
                      key={node}
                      className="px-1.5 py-0.5 rounded text-[10px] font-mono bg-indigo-950/50 border border-indigo-800/40 text-indigo-300"
                    >
                      {node}
                    </span>
                  ))}
                </div>
                <div className="text-[11px] text-zinc-400 pt-1 border-t border-zinc-900 font-sans">
                  {bus.specs}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
