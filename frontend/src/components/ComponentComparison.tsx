"use client";

import React from "react";
import { 
  GitCompare, 
  CheckCircle2, 
  AlertTriangle, 
  XCircle, 
  HelpCircle,
  Cpu,
  Zap,
  Layers
} from "lucide-react";

interface ComponentComparisonProps {
  candidates: Array<{
    component_id: string;
    manufacturer: string;
    manufacturer_part_number: string;
    product_name: string;
    category: string;
    electrical: {
      nominal_voltage?: number;
      voltage_min?: number;
      voltage_max?: number;
      current_max?: number;
    };
    physical: {
      package?: string;
      mounting_type?: string;
    };
    interfaces: {
      i2c?: boolean;
      spi?: boolean;
      uart?: boolean;
    };
    validation_status?: string;
  }>;
}

export const ComponentComparison: React.FC<ComponentComparisonProps> = ({ candidates = [] }) => {
  const getStatusBadge = (status: string = "PASS") => {
    switch (status) {
      case "PASS":
        return <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"><CheckCircle2 className="w-3 h-3" /> PASS</span>;
      case "WARN":
        return <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/20"><AlertTriangle className="w-3 h-3" /> WARN</span>;
      case "FAIL":
        return <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-semibold bg-rose-500/10 text-rose-400 border border-rose-500/20"><XCircle className="w-3 h-3" /> FAIL</span>;
      default:
        return <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-semibold bg-slate-500/10 text-slate-400 border border-slate-500/20"><HelpCircle className="w-3 h-3" /> UNKNOWN</span>;
    }
  };

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 shadow-2xl backdrop-blur-md space-y-4">
      <div className="flex items-center gap-3 border-b border-slate-800 pb-3">
        <div className="p-2 bg-purple-500/10 border border-purple-500/20 rounded-lg text-purple-400">
          <GitCompare className="w-5 h-5" />
        </div>
        <div>
          <h3 className="text-base font-semibold text-slate-100">Component Specification Matrix</h3>
          <p className="text-xs text-slate-400">Deterministic Electrical & Interface Comparison</p>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs text-slate-300 border-collapse">
          <thead>
            <tr className="border-b border-slate-800 text-[11px] text-slate-400 uppercase tracking-wider bg-slate-950/30">
              <th className="py-2.5 px-3">Parameter</th>
              {candidates.map((c, idx) => (
                <th key={idx} className="py-2.5 px-3 font-semibold text-slate-200">
                  {c.manufacturer_part_number}
                  <span className="block font-normal text-[10px] text-slate-400">{c.manufacturer}</span>
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 font-mono">
            <tr>
              <td className="py-2.5 px-3 text-slate-400 font-sans">Nominal Voltage</td>
              {candidates.map((c, idx) => (
                <td key={idx} className="py-2.5 px-3">{c.electrical.nominal_voltage ? `${c.electrical.nominal_voltage}V` : "N/A"}</td>
              ))}
            </tr>
            <tr>
              <td className="py-2.5 px-3 text-slate-400 font-sans">Max Output Current</td>
              {candidates.map((c, idx) => (
                <td key={idx} className="py-2.5 px-3">{c.electrical.current_max ? `${c.electrical.current_max}A` : "N/A"}</td>
              ))}
            </tr>
            <tr>
              <td className="py-2.5 px-3 text-slate-400 font-sans">Package / Footprint</td>
              {candidates.map((c, idx) => (
                <td key={idx} className="py-2.5 px-3">{c.physical.package || "SMD"}</td>
              ))}
            </tr>
            <tr>
              <td className="py-2.5 px-3 text-slate-400 font-sans">Interfaces</td>
              {candidates.map((c, idx) => (
                <td key={idx} className="py-2.5 px-3">
                  {[
                    c.interfaces.i2c && "I2C",
                    c.interfaces.spi && "SPI",
                    c.interfaces.uart && "UART",
                  ].filter(Boolean).join(", ") || "Standard"}
                </td>
              ))}
            </tr>
            <tr>
              <td className="py-2.5 px-3 text-slate-400 font-sans">Deterministic Check</td>
              {candidates.map((c, idx) => (
                <td key={idx} className="py-2.5 px-3 font-sans">
                  {getStatusBadge(c.validation_status || "PASS")}
                </td>
              ))}
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default ComponentComparison;
