'use client';

import React, { useState, useRef } from 'react';
import { Cpu, HelpCircle, Eye, EyeOff } from 'lucide-react';

interface Connection {
  source: string;
  source_pin: string;
  target: string;
  target_pin: string;
  color: string;
  protocol: string;
  description: string;
}

interface WiringDiagramProps {
  data?: {
    connections: Connection[];
  };
}

export default function WiringDiagram({ data }: WiringDiagramProps) {
  const [selectedProtocol, setSelectedProtocol] = useState<string>("all");
  const [zoomLevel, setZoomLevel] = useState<number>(1);
  const [panOffset, setPanOffset] = useState({ x: 0, y: 0 });
  const [activeConnection, setActiveConnection] = useState<Connection | null>(null);

  const containerRef = useRef<SVGSVGElement | null>(null);
  const isPanningRef = useRef<boolean>(false);
  const startPanRef = useRef({ x: 0, y: 0 });

  if (!data || !Array.isArray(data.connections) || data.connections.length === 0) {
    return (
      <div className="bg-slate-900/60 border border-slate-800 rounded-lg p-8 text-center">
        <Cpu className="w-8 h-8 text-slate-600 mx-auto mb-2" />
        <p className="text-xs text-slate-400">No wiring data available.</p>
        <p className="text-[10px] text-slate-500 mt-1">Create or select a project to view wiring diagram.</p>
      </div>
    );
  }

  const { connections } = data;

  // Layout Coordinates for Chip Packages
  const chips: { [key: string]: { x: number; y: number; w: number; h: number; pins: string[]; color: string } } = {};

  // Helper: calculate physical position coordinates for a pin
  const getPinCoords = (chipName: string, pinName: string) => {
    const chip = chips[chipName];
    if (!chip) return { x: 0, y: 0 };
    
    // Find index of pin
    const pinIdx = chip.pins.indexOf(pinName);
    if (pinIdx === -1) return { x: chip.x + chip.w / 2, y: chip.y + chip.h / 2 };
    
    // Distribute pins along left or right side
    const spacing = chip.h / (chip.pins.length + 1);
    const pinY = chip.y + (pinIdx + 1) * spacing;
    
    // Battery and Flex sensors connect from right side. ESP32 left side for battery input, right for SDA/SCL.
    // Let's customize side based on targets
    let pinX = chip.x;
    if (chipName === "LiPo Battery" || chipName === "Flex Sensor Array") {
      pinX = chip.x + chip.w; // Right side
    } else if (chipName === "ESP32 Board") {
      pinX = pinName.includes("ADC") || pinName.includes("SDA") || pinName.includes("SCL") 
        ? chip.x + chip.w  // Right side
        : chip.x;          // Left side
    } else if (chipName === "PCA9685 Driver") {
      pinX = pinName.includes("Channel") 
        ? chip.x + chip.w  // Right side (output)
        : chip.x;          // Left side (input)
    } else if (chipName === "SG90 Servo Array" || chipName === "MG996R Servo" || chipName === "RGB LED indicators") {
      pinX = chip.x;       // Left side
    }
    
    return { x: pinX, y: pinY };
  };

  // Zoom / Pan Handlers
  const handleZoom = (factor: number) => {
    setZoomLevel(prev => Math.max(0.6, Math.min(2.0, prev + factor)));
  };

  const handleReset = () => {
    setZoomLevel(1);
    setPanOffset({ x: 0, y: 0 });
  };

  const handleMouseDown = (e: React.MouseEvent<SVGSVGElement>) => {
    // Only pan if clicking on empty background
    if (e.target === containerRef.current) {
      isPanningRef.current = true;
      startPanRef.current = {
        x: e.clientX - panOffset.x,
        y: e.clientY - panOffset.y
      };
    }
  };

  const handleMouseMove = (e: React.MouseEvent<SVGSVGElement>) => {
    if (isPanningRef.current) {
      setPanOffset({
        x: e.clientX - startPanRef.current.x,
        y: e.clientY - startPanRef.current.y
      });
    }
  };

  const handleMouseUp = () => {
    isPanningRef.current = false;
  };

  // Filter connections by protocol
  const filteredConnections = connections.filter(conn => {
    if (selectedProtocol === "all") return true;
    return conn.protocol.toLowerCase() === selectedProtocol.toLowerCase();
  });

  const protocols = Array.from(new Set(connections.map(c => c.protocol)));

  return (
    <div className="space-y-4">
      {/* Schematics Toolbar */}
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-800 pb-3">
        <div className="flex items-center gap-1.5 bg-slate-900/50 border border-slate-800 p-1 rounded-md">
          <button
            onClick={() => setSelectedProtocol("all")}
            className={`text-[10px] font-mono uppercase tracking-wider px-3 py-1 rounded transition-all cursor-pointer ${
              selectedProtocol === "all"
                ? "bg-cyan-950/50 border border-cyan-800 text-cyan-400 font-bold"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            All Buses
          </button>
          {protocols.map((proto) => (
            <button
              key={proto}
              onClick={() => setSelectedProtocol(proto)}
              className={`text-[10px] font-mono uppercase tracking-wider px-3 py-1 rounded transition-all cursor-pointer ${
                selectedProtocol === proto
                  ? "bg-cyan-950/50 border border-cyan-800 text-cyan-400 font-bold"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              {proto}
            </button>
          ))}
        </div>

        <div className="flex items-center gap-2">
          <button onClick={() => handleZoom(0.1)} className="px-2.5 py-1 text-xs border border-slate-800 bg-slate-900 rounded font-mono hover:text-slate-100 cursor-pointer">+</button>
          <button onClick={() => handleZoom(-0.1)} className="px-2.5 py-1 text-xs border border-slate-800 bg-slate-900 rounded font-mono hover:text-slate-100 cursor-pointer">-</button>
          <button onClick={handleReset} className="px-3 py-1 text-[10px] border border-slate-800 bg-slate-900 rounded font-mono hover:text-slate-100 cursor-pointer">RESET</button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* SVG schematics board */}
        <div className="lg:col-span-3 border border-slate-800/80 bg-zinc-950/60 rounded-xl relative overflow-hidden h-[480px]">
          <svg
            ref={containerRef}
            className="w-full h-full cursor-move"
            onMouseDown={handleMouseDown}
            onMouseMove={handleMouseMove}
            onMouseUp={handleMouseUp}
            onMouseLeave={handleMouseUp}
          >
            <g transform={`translate(${panOffset.x}, ${panOffset.y}) scale(${zoomLevel})`}>
              {/* Draw Chip Modules */}
              {Object.entries(chips).map(([name, chip]) => {
                // Only render chips that are referenced in active connections to avoid empty boxes
                const referenced = connections.some(c => c.source === name || c.target === name);
                if (!referenced) return null;

                return (
                  <g key={name} transform={`translate(${chip.x}, ${chip.y})`}>
                    {/* Package Outline */}
                    <rect
                      x="0"
                      y="0"
                      width={chip.w}
                      height={chip.h}
                      rx="4"
                      fill="#09090b"
                      stroke={chip.color}
                      strokeWidth="1.5"
                      fillOpacity="0.8"
                      className="shadow-lg"
                    />
                    
                    {/* Header bar */}
                    <rect
                      x="0"
                      y="0"
                      width={chip.w}
                      height="20"
                      rx="3"
                      fill={chip.color}
                      fillOpacity="0.15"
                    />
                    
                    {/* Label */}
                    <text
                      x={chip.w / 2}
                      y="14"
                      textAnchor="middle"
                      fill="#f8fafc"
                      fontSize="9"
                      fontFamily="monospace"
                      fontWeight="bold"
                    >
                      {name}
                    </text>

                    {/* Draw Pins indicators */}
                    {chip.pins.map((pin, pinIdx) => {
                      const spacing = chip.h / (chip.pins.length + 1);
                      const pinY = (pinIdx + 1) * spacing;
                      const isRight = pin.includes("ADC") || pin.includes("SDA") || pin.includes("SCL") || name === "LiPo Battery" || name === "Flex Sensor Array" || pin.includes("Channel");
                      const pinX = isRight ? chip.w : 0;

                      return (
                        <g key={pin} transform={`translate(${pinX}, ${pinY})`}>
                          <circle r="3" fill="#64748b" />
                          <text
                            x={isRight ? -8 : 8}
                            y="3"
                            textAnchor={isRight ? "end" : "start"}
                            fill="#94a3b8"
                            fontSize="7"
                            fontFamily="monospace"
                          >
                            {pin.length > 15 ? `${pin.split(" ")[0]}` : pin}
                          </text>
                        </g>
                      );
                    })}
                  </g>
                );
              })}

              {/* Draw Wire Connections */}
              {filteredConnections.map((conn, idx) => {
                const start = getPinCoords(conn.source, conn.source_pin);
                const end = getPinCoords(conn.target, conn.target_pin);
                
                // Curve wires slightly
                const dx = end.x - start.x;
                const dy = end.y - start.y;
                // Add horizontal control offset to make clean orthogonal-like routings
                const c1 = start.x + dx * 0.4;
                const c2 = end.x - dx * 0.4;
                const pathData = `M ${start.x} ${start.y} C ${c1} ${start.y}, ${c2} ${end.y}, ${end.x} ${end.y}`;

                const isActive = activeConnection === conn;

                return (
                  <g key={idx} className="group cursor-pointer" onClick={() => setActiveConnection(conn)}>
                    <path
                      d={pathData}
                      fill="none"
                      stroke={conn.color}
                      strokeWidth={isActive ? 2.5 : 1.5}
                      strokeOpacity={isActive ? 1.0 : 0.6}
                      className="transition-all duration-200 group-hover:stroke-opacity-100 group-hover:stroke-[2px]"
                    />
                    {/* Glow outline */}
                    <path
                      d={pathData}
                      fill="none"
                      stroke={conn.color}
                      strokeWidth="5"
                      strokeOpacity={isActive ? 0.35 : 0.1}
                      className="blur-xs pointer-events-none"
                    />
                    {/* Small arrow marker at end */}
                    <circle cx={end.x} cy={end.y} r="2" fill={conn.color} />
                  </g>
                );
              })}
            </g>
          </svg>
        </div>

        {/* Selected Connection Assistant Sidebar */}
        <div className="lg:col-span-1">
          <div className="glass-panel p-4 border border-blue-500/20 bg-zinc-950/40 font-mono h-full flex flex-col justify-between">
            <div>
              <h4 className="text-xs font-bold text-cyan-400 uppercase tracking-wider mb-3 flex items-center gap-1.5">
                <Cpu className="w-4 h-4 text-cyan-400" />
                Wire Properties
              </h4>
              {activeConnection ? (
                <div className="space-y-4">
                  <div>
                    <span className="text-[10px] text-slate-500 block">From Source Pin</span>
                    <span className="text-xs text-slate-200 font-bold block">{activeConnection.source} ➔ {activeConnection.source_pin}</span>
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-500 block">To Destination Pin</span>
                    <span className="text-xs text-slate-200 font-bold block">{activeConnection.target} ➔ {activeConnection.target_pin}</span>
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-500 block">Signal Protocol</span>
                    <span className="text-xs bg-slate-900 border border-slate-800 text-cyan-400 px-2 py-0.5 rounded inline-block font-bold">
                      {activeConnection.protocol}
                    </span>
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-500 block">Functional Specs</span>
                    <span className="text-xs text-slate-300 block leading-relaxed">{activeConnection.description}</span>
                  </div>
                </div>
              ) : (
                <div className="text-xs text-slate-500 italic p-2 border border-slate-900 border-dashed rounded text-center">
                  Click on any colored connection wire path to inspect pin routing details.
                </div>
              )}
            </div>

            <div className="border-t border-slate-800 pt-4 mt-4 text-[10px] text-slate-400 space-y-1">
              <span className="font-bold block text-slate-300">Wiring Prototyping Checklist:</span>
              <span>1. Match logic domain voltages.</span>
              <span>2. Share common grounds.</span>
              <span>3. Ensure robust power supply current.</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
