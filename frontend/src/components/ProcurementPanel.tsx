"use client";

import React, { useState } from "react";
import { 
  ShoppingBag, 
  Layers, 
  Truck, 
  Clock, 
  Sparkles, 
  Check, 
  ArrowRight,
  TrendingDown
} from "lucide-react";

interface OptimizationOption {
  option_id: string;
  name: string;
  strategy: string;
  vendor_count: number;
  selected_vendors: string[];
  total_component_cost: number;
  estimated_shipping: number;
  estimated_landed_total: number;
  currency: string;
  max_lead_time_days: number;
  tradeoffs: string[];
}

interface ProcurementPanelProps {
  recommendedOption?: OptimizationOption;
  alternativeOptions?: OptimizationOption[];
  onSelectOption?: (optionId: string) => void;
}

export const ProcurementPanel: React.FC<ProcurementPanelProps> = ({
  recommendedOption,
  alternativeOptions = [],
  onSelectOption,
}) => {
  const [selected, setSelected] = useState<string>(
    recommendedOption?.option_id || "opt_consolidated"
  );

  const allOptions = recommendedOption 
    ? [recommendedOption, ...alternativeOptions.filter(o => o.option_id !== recommendedOption.option_id)]
    : alternativeOptions;

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 shadow-2xl backdrop-blur-md space-y-5">
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-cyan-500/10 border border-cyan-500/20 rounded-lg text-cyan-400">
            <ShoppingBag className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-semibold text-slate-100">Multi-Vendor Procurement Optimizer</h3>
            <p className="text-xs text-slate-400">Landed Cost & Vendor Consolidation Analysis</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {allOptions.map((opt) => {
          const isSelected = selected === opt.option_id;
          const isRec = recommendedOption?.option_id === opt.option_id;

          return (
            <div
              key={opt.option_id}
              onClick={() => {
                setSelected(opt.option_id);
                if (onSelectOption) onSelectOption(opt.option_id);
              }}
              className={`cursor-pointer rounded-xl p-4 border transition-all duration-200 flex flex-col justify-between space-y-3 ${
                isSelected
                  ? "bg-slate-950/80 border-cyan-500 shadow-lg shadow-cyan-500/10 ring-1 ring-cyan-500"
                  : "bg-slate-950/40 border-slate-800 hover:border-slate-700"
              }`}
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-semibold text-slate-200">{opt.name}</span>
                  {isRec && (
                    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                      <Sparkles className="w-3 h-3" /> Recommended
                    </span>
                  )}
                </div>

                <div className="grid grid-cols-3 gap-2 text-xs py-2 bg-slate-900/50 rounded-lg px-3 border border-slate-800/50">
                  <div>
                    <span className="text-[10px] text-slate-400 block">Components</span>
                    <span className="font-semibold text-slate-200">₹{opt.total_component_cost}</span>
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-400 block">Freight</span>
                    <span className="font-semibold text-yellow-400">₹{opt.estimated_shipping}</span>
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-400 block">Landed Total</span>
                    <span className="font-bold text-emerald-400">₹{opt.estimated_landed_total}</span>
                  </div>
                </div>

                <div className="mt-3 space-y-1">
                  <span className="text-[10px] text-slate-400 uppercase tracking-wider block">Strategy Tradeoffs</span>
                  {opt.tradeoffs.map((t, idx) => (
                    <div key={idx} className="flex items-center gap-1.5 text-[11px] text-slate-300">
                      <Check className="w-3 h-3 text-cyan-400 shrink-0" />
                      <span>{t}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="pt-2 border-t border-slate-800/60 flex items-center justify-between text-[11px] text-slate-400">
                <span className="flex items-center gap-1">
                  <Truck className="w-3.5 h-3.5 text-slate-400" /> {opt.selected_vendors.join(", ")}
                </span>
                <span className="flex items-center gap-1">
                  <Clock className="w-3.5 h-3.5 text-slate-400" /> ~{opt.max_lead_time_days} days
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default ProcurementPanel;
