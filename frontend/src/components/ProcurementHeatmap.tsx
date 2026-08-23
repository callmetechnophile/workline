import React, { useState } from "react";
import { MapPin, Plane, Truck, Calendar, ShoppingBag, ShieldAlert } from "lucide-react";

export interface Component {
  component: string;
  selected_vendor: string;
  final_cost: number;
  stock?: string;
}

export interface VendorLocation {
  name: string;
  city: string;
  coords: { x: number; y: number }; // SVG Map Coordinates
  distance: string;
  shippingCost: string;
  eta: string;
  regionType: "local" | "regional" | "long-distance";
  status: "In Stock" | "Low Stock" | "Out of Stock";
}

export interface ProcurementHeatmapProps {
  components?: Component[];
  vendorLocations?: Record<string, VendorLocation>;
}

export default function ProcurementHeatmap({
  components = [],
  vendorLocations = {},
}: ProcurementHeatmapProps) {
  const [selectedVendor, setSelectedVendor] = useState<string | null>(null);

  if ((!components || components.length === 0) && (!vendorLocations || Object.keys(vendorLocations).length === 0)) {
    return (
      <div className="bg-slate-900/60 border border-slate-800 rounded-lg p-8 text-center">
        <MapPin className="w-8 h-8 text-slate-600 mx-auto mb-2" />
        <p className="text-xs text-slate-400">No procurement activity.</p>
        <p className="text-[10px] text-slate-500 mt-1">Create or select a project to view procurement heatmap.</p>
      </div>
    );
  }

  const getRegionColor = (type: string) => {
    switch (type) {
      case "local":
        return "text-emerald-400 border-emerald-800/40 bg-emerald-950/20";
      case "regional":
        return "text-amber-400 border-amber-800/40 bg-amber-950/20";
      default:
        return "text-red-400 border-red-800/40 bg-red-950/20";
    }
  };

  // Assign components to vendor keys
  const getVendorKey = (vendorName: string): string => {
    if (!vendorName) return "";
    const name = vendorName.toLowerCase();
    const match = Object.keys(vendorLocations).find(
      (k) => k.toLowerCase().includes(name) || name.includes(k.toLowerCase())
    );
    return match || vendorName;
  };

  const activeVendor = selectedVendor ? vendorLocations[selectedVendor] : null;

  return (
    <div className="grid grid-cols-1 xl:grid-cols-3 gap-6 p-4">
      {/* Interactive Cyberpunk Map */}
      <div className="xl:col-span-2 glass-panel p-5 border border-zinc-800 bg-zinc-950/60 rounded-xl space-y-4 flex flex-col justify-between">
        <div className="border-b border-zinc-850 pb-3">
          <h3 className="text-lg font-mono font-bold tracking-wider text-slate-100 uppercase">Geographical Procurement Map</h3>
          <p className="text-xs font-mono text-slate-500">Visualizing global to regional logistics channels for BOM optimization.</p>
        </div>

        {/* Vector SVG Map Container */}
        <div className="relative w-full h-[360px] bg-zinc-950 rounded-lg border border-zinc-900 overflow-hidden flex items-center justify-center">
          <svg className="w-full h-full" viewBox="0 0 500 400">
            {/* Ambient grid lines */}
            <defs>
              <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
                <path d="M 20 0 L 0 0 0 20" fill="none" stroke="#222" strokeWidth="0.5" />
              </pattern>
            </defs>
            <rect width="100%" height="100%" fill="url(#grid)" />

            {/* Simulated Landmass Outline */}
            <path
              d="M50,80 Q90,50 150,90 T250,70 T350,110 T400,200 T300,320 T200,380 T150,300 Z"
              fill="none"
              stroke="#333"
              strokeWidth="1.5"
              strokeDasharray="4 4"
            />
            {/* Local India Sourcing Region boundaries */}
            <circle cx="230" cy="270" r="100" fill="none" stroke="rgba(34, 197, 94, 0.1)" strokeWidth="1" />
            <circle cx="230" cy="270" r="160" fill="none" stroke="rgba(245, 158, 11, 0.05)" strokeWidth="1" />

            {/* Sourcing Routes (Connecting vendor to Design Lab at coords 230, 270 - Bangalore/Chennai region) */}
            {Object.values(vendorLocations).map((loc) => {
              const isActive = selectedVendor === loc.name;
              let strokeColor = "rgba(100, 116, 139, 0.3)"; // default gray
              if (isActive) {
                strokeColor = loc.regionType === "local" ? "#10b981" : loc.regionType === "regional" ? "#f59e0b" : "#ef4444";
              }
              return (
                <g key={loc.name}>
                  <path
                    d={`M ${loc.coords.x} ${loc.coords.y} Q ${(loc.coords.x + 230)/2 + 20} ${(loc.coords.y + 270)/2 - 20} 230 270`}
                    fill="none"
                    stroke={strokeColor}
                    strokeWidth={isActive ? 2 : 1}
                    strokeDasharray={isActive ? "none" : "3 3"}
                  />
                  {isActive && (
                    <circle cx="230" cy="270" r="4" fill="#22d3ee">
                      <animate attributeName="r" values="3;9;3" dur="2s" repeatCount="indefinite" />
                    </circle>
                  )}
                </g>
              );
            })}

            {/* Central Design Hub / Project Location Node */}
            <g transform="translate(230, 270)">
              <circle r="8" fill="#0891b2" className="animate-ping opacity-25" />
              <circle r="5" fill="#22d3ee" />
              <text x="10" y="4" fill="#22d3ee" className="text-[10px] font-mono font-bold uppercase">Design Lab</text>
            </g>

            {/* Vendor Nodes */}
            {Object.values(vendorLocations).map((loc) => {
              const isSelected = selectedVendor === loc.name;
              const nodeColor = loc.regionType === "local" ? "#10b981" : loc.regionType === "regional" ? "#f59e0b" : "#ef4444";
              
              return (
                <g 
                  key={loc.name} 
                  transform={`translate(${loc.coords.x}, ${loc.coords.y})`}
                  onClick={() => setSelectedVendor(loc.name)}
                  className="cursor-pointer group"
                >
                  <circle r={isSelected ? 7 : 5} fill={nodeColor} className="transition-all" />
                  <circle r={isSelected ? 12 : 8} fill="none" stroke={nodeColor} strokeWidth="1" className="animate-ping opacity-20" />
                  <text 
                    y="-10" 
                    textAnchor="middle" 
                    fill={isSelected ? "#fff" : "#888"} 
                    className="text-[9px] font-mono font-extrabold select-none opacity-80 group-hover:opacity-100 transition-opacity"
                  >
                    {loc.city}
                  </text>
                </g>
              );
            })}
          </svg>

          {/* Region Legend */}
          <div className="absolute bottom-3 left-3 bg-zinc-950/80 border border-zinc-800 p-2.5 rounded text-[9px] font-mono space-y-1.5 backdrop-blur-sm">
            <div className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-emerald-500" /> Local (Green)</div>
            <div className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-amber-500" /> Regional (Yellow)</div>
            <div className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-red-500" /> Long-Distance (Red)</div>
          </div>
        </div>
      </div>

      {/* Logistics & Sourcing Details Panel */}
      <div className="glass-panel p-5 border border-zinc-800 bg-zinc-950/60 rounded-xl space-y-6">
        <div className="border-b border-zinc-850 pb-3 flex items-center gap-2">
          <ShoppingBag className="w-5 h-5 text-cyan-400" />
          <h3 className="text-lg font-mono font-bold tracking-wider text-slate-100 uppercase">Vendor Logistics</h3>
        </div>

        {activeVendor ? (
          <div className="space-y-5">
            {/* Vendor Profile */}
            <div className="p-4 bg-zinc-900/60 border border-zinc-850 rounded-lg space-y-3">
              <div className="flex items-center justify-between border-b border-zinc-800 pb-2">
                <span className="text-xs font-mono font-bold text-slate-200">{activeVendor.name}</span>
                <span className={`text-[9px] font-mono font-bold uppercase tracking-widest px-2 py-0.5 border rounded ${getRegionColor(activeVendor.regionType)}`}>
                  {activeVendor.regionType}
                </span>
              </div>

              {/* Delivery Stats */}
              <div className="grid grid-cols-2 gap-3 text-xs font-mono">
                <div className="space-y-1">
                  <span className="text-slate-500 block">Distance</span>
                  <span className="text-slate-300 font-bold flex items-center gap-1"><MapPin className="w-3.5 h-3.5 text-cyan-400" />{activeVendor.distance}</span>
                </div>
                <div className="space-y-1">
                  <span className="text-slate-500 block">Shipping Cost</span>
                  <span className="text-slate-300 font-bold">{activeVendor.shippingCost}</span>
                </div>
                <div className="space-y-1">
                  <span className="text-slate-500 block">ETA</span>
                  <span className="text-slate-300 font-bold flex items-center gap-1"><Calendar className="w-3.5 h-3.5 text-cyan-400" />{activeVendor.eta}</span>
                </div>
                <div className="space-y-1">
                  <span className="text-slate-500 block">Status</span>
                  <span className={`font-bold ${activeVendor.status === "In Stock" ? "text-emerald-400" : "text-amber-400"}`}>{activeVendor.status}</span>
                </div>
              </div>
            </div>

            {/* Components Sourced from this Vendor */}
            <div className="space-y-2">
              <div className="text-[10px] font-mono font-bold text-slate-400 uppercase tracking-widest">Sourced Components</div>
              <div className="space-y-2 max-h-[160px] overflow-y-auto pr-1">
                {components.filter(c => getVendorKey(c.selected_vendor) === activeVendor.name).map((c, idx) => (
                  <div key={idx} className="flex justify-between items-center p-2.5 bg-zinc-900/20 border border-zinc-850 rounded">
                    <span className="text-xs font-mono text-slate-300 truncate mr-2">{c.component}</span>
                    <span className="text-xs font-mono font-bold text-slate-100 flex-shrink-0">₹{c.final_cost}</span>
                  </div>
                ))}
                {components.filter(c => getVendorKey(c.selected_vendor) === activeVendor.name).length === 0 && (
                  <div className="text-xs font-mono text-slate-500 italic">No parts allocated to this vendor on current run.</div>
                )}
              </div>
            </div>
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center p-8 bg-zinc-900/10 border border-dashed border-zinc-800 rounded-lg text-center space-y-2">
            <ShieldAlert className="w-8 h-8 text-zinc-600" />
            <div className="text-xs font-mono text-slate-400">Click on any map node to load logistic profiles and ETAs.</div>
          </div>
        )}
      </div>
    </div>
  );
}
