'use client';

import React from 'react';
import { ShieldCheck, ShieldAlert, ShieldAlert as ShieldWarning, AlertTriangle } from 'lucide-react';

interface VoltageRisk {
  component_a: string;
  component_b: string;
  voltage: string;
  risk: string; // "SAFE", "WARNING", "HIGH RISK"
  details: string;
}

interface VoltageRiskTableProps {
  risks?: VoltageRisk[];
}

export default function VoltageRiskTable({ risks = [] }: VoltageRiskTableProps) {
  const safeRisks = Array.isArray(risks) ? risks : [];

  return (
    <div className="glass-panel border border-amber-500/20 bg-slate-900/10 p-5 space-y-4">
      <div className="flex justify-between items-center border-b border-amber-900/40 pb-3">
        <div className="flex items-center gap-2.5">
          <AlertTriangle className="w-5 h-5 text-amber-500" />
          <h3 className="text-sm font-mono font-bold text-slate-200 uppercase tracking-wider">
            Voltage Compatibility Checker
          </h3>
        </div>
        <span className="text-[10px] font-mono text-amber-400 bg-amber-950/40 px-2 py-0.5 border border-amber-900/30 rounded uppercase font-bold">
          Electrical Auditing
        </span>
      </div>

      {!safeRisks || safeRisks.length === 0 ? (
        <div className="text-center py-6 text-xs text-slate-500 font-mono">
          [SYSTEM NOTICE]: No electrical validation results found. Execute a design query.
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse font-mono">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 uppercase tracking-widest text-[9px]">
                <th className="py-2.5 px-3">Component A</th>
                <th className="py-2.5 px-3">Component B</th>
                <th className="py-2.5 px-3">Voltage Rail</th>
                <th className="py-2.5 px-3">Risk Assessment</th>
                <th className="py-2.5 px-3 max-w-xs">Enforcer Notes</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/30">
              {safeRisks.map((risk, idx) => {

                let badgeStyle = "bg-emerald-950/20 border-emerald-500/30 text-emerald-400";
                let statusIcon = <ShieldCheck className="w-3 h-3 text-emerald-400" />;
                
                if (risk.risk === "WARNING") {
                  badgeStyle = "bg-amber-950/20 border-amber-500/30 text-amber-400";
                  statusIcon = <AlertTriangle className="w-3 h-3 text-amber-400" />;
                } else if (risk.risk === "HIGH RISK") {
                  badgeStyle = "bg-red-950/20 border-red-500/30 text-red-400 animate-pulse";
                  statusIcon = <ShieldAlert className="w-3 h-3 text-red-400" />;
                }

                return (
                  <tr key={idx} className="hover:bg-slate-900/30 transition-all">
                    <td className="py-3.5 px-3 text-slate-300 font-medium">{risk.component_a}</td>
                    <td className="py-3.5 px-3 text-slate-300">{risk.component_b}</td>
                    <td className="py-3.5 px-3 text-slate-400">{risk.voltage}</td>
                    <td className="py-3.5 px-3">
                      <span className={`inline-flex items-center gap-1 text-[9px] font-extrabold px-2 py-0.5 rounded border uppercase ${badgeStyle}`}>
                        {statusIcon}
                        {risk.risk}
                      </span>
                    </td>
                    <td className="py-3.5 px-3 text-slate-400 leading-normal max-w-xs">{risk.details}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
