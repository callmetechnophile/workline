'use client';

import React, { useEffect, useState } from 'react';
import { Layers, Calculator, Info } from 'lucide-react';

interface Alternative {
  alternative: string;
  vendor: string;
  base_cost?: number;
  shipping_cost?: number;
  final_cost: number;
  reason: string;
}

interface ComponentItem {
  component: string;
  category: string;
  selected_vendor: string;
  vendor_location: string;
  base_cost: number;
  shipping_cost: number;
  distance: string;
  final_cost: number;
  stock: string;
  eta: string;
  alternatives?: Alternative[];
}

interface CostBreakdownProps {
  components: ComponentItem[];
  costSummary?: {
    totals: {
      electronics_total: number;
      mechanical_total: number;
      shipping_total: number;
      grand_total: number;
    };
  };
}

export default function CostBreakdown({ components = [], costSummary }: CostBreakdownProps) {
  // State storing active component config: mapping component name to { base_cost, shipping_cost, final_cost }
  const [activePricing, setActivePricing] = useState<Record<string, { base: number; shipping: number; final: number }>>({});

  useEffect(() => {
    const initial: Record<string, { base: number; shipping: number; final: number }> = {};
    if (Array.isArray(components)) {
      components.forEach((comp) => {
        if (comp && comp.component) {
          initial[comp.component] = {
            base: comp.base_cost ?? 0,
            shipping: comp.shipping_cost ?? 0,
            final: comp.final_cost ?? 0
          };
        }
      });
    }
    setActivePricing(initial);
  }, [components]);

  const handleSwap = (compName: string, selectedValue: string) => {
    if (!Array.isArray(components)) return;
    const original = components.find(c => c && c.component === compName);
    if (!original) return;


    if (selectedValue === "original") {
      setActivePricing(prev => ({
        ...prev,
        [compName]: {
          base: original.base_cost,
          shipping: original.shipping_cost,
          final: original.final_cost
        }
      }));
    } else {
      // Find the selected alternative
      const alt = original.alternatives?.find(a => a.alternative === selectedValue);
      if (alt) {
        setActivePricing(prev => ({
          ...prev,
          [compName]: {
            base: alt.base_cost !== undefined ? alt.base_cost : alt.final_cost,
            shipping: alt.shipping_cost !== undefined ? alt.shipping_cost : 0,
            final: alt.final_cost
          }
        }));
      }
    }
  };

  const getCategoryGroup = (category: string, name: string) => {
    const cat = (category || "").toLowerCase();
    const nm = (name || "").toLowerCase();
    if (anyMatch(cat, ["power", "energy", "solar", "battery", "esc", "charger", "supply", "voltage"]) ||
        anyMatch(nm, ["battery", "solar", "power supply", "charger", "esc"])) {
      return "Power";
    }
    if (anyMatch(cat, ["electronics", "navigation", "sensor", "controller", "board", "flight", "gps", "receiver", "mcu", "cpu", "processor", "led", "display", "screen", "wire", "module", "communication", "actuator", "indicator"]) ||
        anyMatch(nm, ["esp32", "arduino", "pico", "sensor", "led", "wire", "gps", "display", "screen", "transceiver", "mcu", "controller"])) {
      return "Electronics";
    }
    return "Mechanical";
  };

  const anyMatch = (str: string, keywords: string[]) => {
    return keywords.some(k => str.includes(k));
  };

  // Recalculate subtotals dynamically
  let rawComponentCost = 0;
  let transportCost = 0;
  
  const subtotals: Record<string, number> = {
    Electronics: 0,
    Mechanical: 0,
    Power: 0
  };

  if (Array.isArray(components)) {
    components.forEach((comp) => {
      if (comp && comp.component) {
        const pricing = activePricing[comp.component] || { base: comp.base_cost ?? 0, shipping: comp.shipping_cost ?? 0, final: comp.final_cost ?? 0 };
        const catGroup = getCategoryGroup(comp.category, comp.component);
        
        subtotals[catGroup] += pricing.base;
        rawComponentCost += pricing.base;
        transportCost += pricing.shipping;
      }
    });
  }


  const finalBOMCost = rawComponentCost + transportCost;

  return (
    <div className="glass-panel border border-emerald-500/20 bg-slate-900/10 p-5 space-y-5">
      <div className="flex justify-between items-center border-b border-emerald-900/40 pb-3">
        <div className="flex items-center gap-2.5">
          <Calculator className="w-5 h-5 text-emerald-400" />
          <h3 className="text-sm font-mono font-bold text-slate-200 uppercase tracking-wider">
            Total Build Cost Section
          </h3>
        </div>
        <span className="text-[10px] font-mono text-emerald-400 bg-emerald-950/40 px-2 py-0.5 border border-emerald-900/30 rounded uppercase font-bold">
          Procurement Totals
        </span>
      </div>

      {/* Main financial summary block */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 font-mono text-xs">
        <div className="bg-slate-950/60 p-4 border border-slate-800 rounded-lg flex flex-col justify-between space-y-1">
          <span className="text-[9px] uppercase text-slate-500 font-bold tracking-wider">Raw Component Cost</span>
          <span className="text-xl font-bold text-slate-200">₹{rawComponentCost.toLocaleString('en-IN')}</span>
        </div>
        <div className="bg-slate-950/60 p-4 border border-slate-800 rounded-lg flex flex-col justify-between space-y-1">
          <span className="text-[9px] uppercase text-slate-500 font-bold tracking-wider">Transport Cost</span>
          <span className="text-xl font-bold text-slate-400">₹{transportCost.toLocaleString('en-IN')}</span>
        </div>
        <div className="bg-slate-950/80 p-4 border border-emerald-500/20 rounded-lg flex flex-col justify-between space-y-1 shadow-lg shadow-emerald-500/5">
          <span className="text-[9px] uppercase text-emerald-500 font-bold tracking-widest">Final BOM Cost</span>
          <span className="text-xl font-extrabold text-emerald-400 glow-emerald">₹{finalBOMCost.toLocaleString('en-IN')}</span>
        </div>
      </div>

      {/* Subtotals breakdown grids */}
      <div className="space-y-2">
        <span className="text-slate-500 uppercase font-bold tracking-wider text-[9px] font-mono">Category Base Subtotals</span>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 font-mono text-xs">
          {Object.entries(subtotals).map(([category, amt]) => {
            let catText = "text-slate-400";
            if (category === "Electronics") catText = "text-blue-400";
            else if (category === "Power") catText = "text-cyan-400";
            else catText = "text-amber-400";

            return (
              <div key={category} className="bg-zinc-950/30 p-3 border border-slate-800/80 rounded flex justify-between items-center">
                <span className={`text-[10px] font-bold uppercase ${catText}`}>{category}</span>
                <span className="font-bold text-slate-200">₹{amt.toLocaleString('en-IN')}</span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Component selector for replacements */}
      {components.some(c => c.alternatives && c.alternatives.length > 0) && (
        <div className="space-y-2 font-mono text-[9px] pt-1">
          <span className="text-slate-500 uppercase font-bold tracking-wider">Dynamic Procurement Optimizations</span>
          <div className="divide-y divide-slate-800/40 max-h-[140px] overflow-y-auto pr-1">
            {components
              .filter(c => c.alternatives && c.alternatives.length > 0)
              .map((comp) => {
                const active = activePricing[comp.component] || { base: comp.base_cost, shipping: comp.shipping_cost, final: comp.final_cost };
                
                return (
                  <div key={comp.component} className="flex justify-between items-center py-2">
                    <span className="text-slate-400 font-medium max-w-[200px] truncate">{comp.component}</span>
                    <select 
                      onChange={(e) => handleSwap(comp.component, e.target.value)}
                      className="bg-slate-950 border border-slate-800 rounded p-1 text-[9px] text-slate-300 outline-none"
                    >
                      <option value="original">Original (₹{comp.final_cost})</option>
                      {comp.alternatives?.map((alt, i) => (
                        <option key={i} value={alt.alternative}>
                          {alt.alternative.split(" ")[0]} (₹{alt.final_cost})
                        </option>
                      ))}
                    </select>
                  </div>
                );
              })}
          </div>
        </div>
      )}
    </div>
  );
}
