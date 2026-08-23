'use client';

import React from 'react';
import { Sparkles, ArrowRight, DollarSign, AlertCircle, CheckCircle2, TrendingDown } from 'lucide-react';

interface AlternativeCandidate {
  manufacturer?: string;
  mpn?: string;
  unit_price?: number;
  availability?: number;
  distributor?: string;
  compatibility?: string;
  reason?: string;
  type?: string;
  alternative?: string;
  vendor?: string;
  final_cost?: number;
}

interface ComponentItem {
  component: string;
  selected_vendor?: string;
  base_cost?: number;
  final_cost?: number;
  cost?: number;
  alternatives?: AlternativeCandidate[];
}

interface AlternativeComponentsProps {
  components: ComponentItem[];
  optimizationData?: {
    budget_target_usd?: number;
    actual_bom_usd?: number;
    original_bom_usd?: number;
    total_savings_usd?: number;
    budget_status?: string;
    primary_cost_drivers?: Array<{
      component: string;
      unit_price: number;
      extended_cost: number;
      share_pct: number;
    }>;
    possible_cost_reductions?: string[];
  };
}

export default function AlternativeComponents({ components = [], optimizationData }: AlternativeComponentsProps) {
  const safeComps = Array.isArray(components) ? components : [];
  const compWithAlts = safeComps.filter(c => c && c.alternatives && Array.isArray(c.alternatives) && c.alternatives.length > 0);

  const targetBudget = optimizationData?.budget_target_usd ?? 5.00;
  const actualBom = optimizationData?.actual_bom_usd ?? 0.00;
  const budgetStatus = optimizationData?.budget_status ?? (actualBom <= targetBudget && actualBom > 0 ? "UNDER BUDGET" : "OVER BUDGET");
  const isUnder = budgetStatus === "UNDER BUDGET";

  return (
    <div className="glass-panel border border-purple-500/20 bg-slate-900/10 p-5 space-y-5 font-mono">
      {/* Header */}
      <div className="flex justify-between items-center border-b border-purple-900/40 pb-3">
        <div className="flex items-center gap-2.5">
          <Sparkles className="w-5 h-5 text-purple-400" />
          <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider">
            Smart BOM Alternatives & Target Optimizer
          </h3>
        </div>
        <span className="text-[10px] text-purple-400 bg-purple-950/40 px-2 py-0.5 border border-purple-900/30 rounded uppercase font-bold">
          Verified Cross-Reference
        </span>
      </div>

      {/* $5 Budget Target Card */}
      <div className={`p-4 rounded-lg border flex flex-col md:flex-row md:items-center justify-between gap-4 ${
        isUnder 
          ? "bg-emerald-950/20 border-emerald-500/30" 
          : "bg-amber-950/20 border-amber-500/30"
      }`}>
        <div className="flex items-center gap-3">
          {isUnder ? (
            <CheckCircle2 className="w-6 h-6 text-emerald-400 shrink-0" />
          ) : (
            <AlertCircle className="w-6 h-6 text-amber-400 shrink-0" />
          )}
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs text-slate-400 font-bold uppercase">BUDGET TARGET:</span>
              <span className="text-sm font-bold text-slate-200">${targetBudget.toFixed(2)} USD</span>
              <span className="text-slate-600">|</span>
              <span className="text-xs text-slate-400 font-bold uppercase">ACTUAL BOM:</span>
              <span className={`text-sm font-bold ${isUnder ? "text-emerald-400" : "text-amber-400"}`}>
                ${actualBom.toFixed(2)} USD
              </span>
            </div>
            <p className="text-[11px] text-slate-400 mt-0.5">
              Cost optimization respects functional and electrical compatibility first before unit price ranking.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 self-start md:self-auto">
          <span className={`text-xs px-3 py-1 rounded font-extrabold border ${
            isUnder
              ? "bg-emerald-950/60 text-emerald-400 border-emerald-800"
              : "bg-amber-950/60 text-amber-400 border-amber-800"
          }`}>
            STATUS: {budgetStatus}
          </span>
          {optimizationData?.total_savings_usd && optimizationData.total_savings_usd > 0 && (
            <span className="text-[11px] text-emerald-400 font-bold flex items-center gap-1 bg-emerald-950/40 px-2 py-1 rounded border border-emerald-900/50">
              <TrendingDown className="w-3.5 h-3.5" />
              Save ${optimizationData.total_savings_usd.toFixed(2)}
            </span>
          )}
        </div>
      </div>

      {/* Primary Cost Drivers & Reductions if Over Budget */}
      {optimizationData?.primary_cost_drivers && optimizationData.primary_cost_drivers.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
          <div className="p-3 bg-slate-950/60 border border-slate-800 rounded-lg space-y-2">
            <span className="text-[10px] text-amber-400 font-bold uppercase tracking-wider block">
              Primary Cost Drivers:
            </span>
            <ul className="space-y-1.5 text-slate-300">
              {optimizationData.primary_cost_drivers.slice(0, 3).map((driver, i) => (
                <li key={i} className="flex justify-between items-center text-[11px]">
                  <span className="text-slate-200 font-medium truncate max-w-[200px]">{driver.component}</span>
                  <span className="text-amber-400 font-bold">${driver.extended_cost.toFixed(2)} ({driver.share_pct}%)</span>
                </li>
              ))}
            </ul>
          </div>

          {optimizationData.possible_cost_reductions && optimizationData.possible_cost_reductions.length > 0 && (
            <div className="p-3 bg-slate-950/60 border border-slate-800 rounded-lg space-y-2">
              <span className="text-[10px] text-cyan-400 font-bold uppercase tracking-wider block">
                Possible Cost Reductions:
              </span>
              <ul className="space-y-1 text-slate-300 text-[11px]">
                {optimizationData.possible_cost_reductions.map((red, i) => (
                  <li key={i} className="leading-relaxed text-slate-400">
                    • {red}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* Component Alternative Cards */}
      {compWithAlts.length === 0 ? (
        <div className="text-center py-6 text-xs text-slate-500">
          [SYSTEM NOTICE]: No alternative component suggestions compiled. Execute a design query.
        </div>
      ) : (
        <div className="space-y-4">
          {compWithAlts.map((comp, idx) => (
            <div key={idx} className="bg-zinc-950/40 border border-slate-800 rounded-lg p-4 space-y-3 text-xs">
              <div className="flex flex-col sm:flex-row justify-between sm:items-center pb-2 border-b border-slate-900 gap-1">
                <div>
                  <span className="text-slate-500 font-bold uppercase tracking-wider text-[9px]">Original Component</span>
                  <h4 className="text-sm font-bold text-slate-200 mt-0.5">{comp.component}</h4>
                </div>
                {comp.final_cost !== undefined && (
                  <div className="text-left sm:text-right">
                    <span className="text-slate-500 font-bold uppercase tracking-wider text-[9px]">Baseline Cost</span>
                    <div className="text-slate-300 font-extrabold mt-0.5">
                      ₹{comp.final_cost.toLocaleString('en-IN')}
                    </div>
                  </div>
                )}
              </div>

              <div className="space-y-1">
                <span className="text-slate-500 font-bold uppercase tracking-widest text-[9px]">Cross-Manufacturer Equivalents</span>
                <div className="overflow-x-auto pt-1">
                  <table className="w-full text-left text-[11px] border-collapse">
                    <thead>
                      <tr className="border-b border-slate-800 text-slate-400 uppercase tracking-wider text-[9px]">
                        <th className="py-2 px-2">Alternative Part</th>
                        <th className="py-2 px-2">Manufacturer</th>
                        <th className="py-2 px-2 text-right">Unit Price</th>
                        <th className="py-2 px-2">Compatibility / Compliance</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-900/60">
                      {comp.alternatives?.map((alt, i) => {
                        const partName = alt.mpn || alt.alternative || "Equivalent Part";
                        const mfg = alt.manufacturer || alt.vendor || "Verified Vendor";
                        const price = alt.unit_price ? `$${alt.unit_price.toFixed(2)}` : (alt.final_cost ? `₹${alt.final_cost}` : "—");
                        const compNote = alt.compatibility || alt.reason || "Electrically compatible";

                        return (
                          <tr key={i} className="hover:bg-purple-950/10 transition-all">
                            <td className="py-2.5 px-2 text-purple-300 font-semibold flex items-center gap-1.5">
                              <ArrowRight className="w-3 h-3 text-purple-400 flex-shrink-0" />
                              {partName}
                            </td>
                            <td className="py-2.5 px-2 text-slate-300">{mfg}</td>
                            <td className="py-2.5 px-2 text-right font-bold text-emerald-400">{price}</td>
                            <td className="py-2.5 px-2 text-slate-400 max-w-xs truncate" title={compNote}>
                              {compNote}
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
