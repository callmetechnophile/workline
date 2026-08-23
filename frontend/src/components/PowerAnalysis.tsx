'use client';

import React from 'react';
import { ShieldAlert, Zap, BatteryCharging, AlertTriangle } from 'lucide-react';

interface PowerItem {
  component: string;
  category?: string;
  voltage: number;
  nominal_current_ma?: number;
  nominal_current?: number;
  peak_current_ma?: number;
  peak_current?: number;
  standby_current?: number;
  power_w?: number;
  is_source?: boolean;
}

interface VoltageDomain {
  rail: string;
  voltage: number;
  current_ma: number;
  current_a: number;
  peak_current_a: number;
  power_w: number;
  components: string[];
}

interface ConverterReq {
  type: string;
  input_voltage: number;
  output_voltage: number;
  max_load_current_a: number;
  efficiency_pct: number;
  description: string;
}

interface PowerSummary {
  total_power_load_w: number;
  total_system_power_w?: number;
  peak_current_a?: number;
  peak_power_load_w: number;
  standby_load_ma?: number;
  required_input_v?: number;
  required_source_current_a?: number;
  recommended_supply_power_w?: number;
  safety_margin_pct?: number;
  converter_efficiency_pct?: number;
  battery_voltage_v?: number;
  battery_capacity_ah?: number;
  estimated_runtime_hours?: number;
  voltage_domains_count: number;
}

interface PowerAnalysisProps {
  data: {
    status?: string;
    power_items: PowerItem[];
    voltage_domains?: VoltageDomain[];
    converter_requirements?: ConverterReq[];
    summary: PowerSummary;
    warnings: string[];
  };
}

export default function PowerAnalysis({ data }: PowerAnalysisProps) {
  if (!data || !data.summary) {
    return (
      <div className="flex flex-col items-center justify-center p-8 text-slate-400">
        <Zap className="w-12 h-12 mb-2 stroke-1 text-slate-600 animate-pulse" />
        <p>No power analysis data compiled yet.</p>
      </div>
    );
  }

  const { power_items = [], voltage_domains = [], converter_requirements = [], summary, warnings = [] } = data;

  return (
    <div className="space-y-6">
      {/* Warnings Banner */}
      {warnings && warnings.length > 0 && (
        <div className="border border-red-500/20 bg-red-950/20 p-4 rounded-lg flex items-start gap-3 shadow-lg shadow-red-950/20">
          <ShieldAlert className="w-5 h-5 text-red-500 shrink-0 mt-0.5" />
          <div className="space-y-1">
            <h4 className="text-xs font-bold text-red-400 uppercase tracking-wider font-mono">Electrical Audit Alerts</h4>
            <ul className="list-disc pl-4 text-xs text-red-200/80 font-mono space-y-1">
              {warnings.map((warn, i) => (
                <li key={i}>{warn}</li>
              ))}
            </ul>
          </div>
        </div>
      )}

      {/* Summary KPI Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="glass-panel p-4 border border-blue-500/20 bg-zinc-950/30 font-mono">
          <div className="text-[10px] text-slate-400 uppercase tracking-wider mb-1">Total System Power</div>
          <div className="text-2xl font-bold text-cyan-400">{summary.total_system_power_w || summary.total_power_load_w} W</div>
          <div className="text-[9px] text-slate-500 mt-1">Active load: {summary.total_power_load_w}W (@ {summary.converter_efficiency_pct || 88}% η)</div>
        </div>
        <div className="glass-panel p-4 border border-blue-500/20 bg-zinc-950/30 font-mono">
          <div className="text-[10px] text-slate-400 uppercase tracking-wider mb-1">Required Input</div>
          <div className="text-2xl font-bold text-amber-400">{summary.required_input_v || 5.0} V</div>
          <div className="text-[9px] text-slate-500 mt-1">Source draw: {summary.required_source_current_a || (summary.total_power_load_w / 5.0).toFixed(2)} A</div>
        </div>
        <div className="glass-panel p-4 border border-blue-500/20 bg-zinc-950/30 font-mono">
          <div className="text-[10px] text-slate-400 uppercase tracking-wider mb-1">Recommended Supply</div>
          <div className="text-2xl font-bold text-emerald-400">
            {summary.recommended_supply_power_w || (summary.total_power_load_w * 1.25).toFixed(2)} W
          </div>
          <div className="text-[9px] text-slate-500 mt-1">
            Safety Headroom: {summary.safety_margin_pct || 25}%
          </div>
        </div>
        <div className="glass-panel p-4 border border-blue-500/20 bg-zinc-950/30 font-mono">
          <div className="text-[10px] text-slate-400 uppercase tracking-wider mb-1">Voltage Domains</div>
          <div className="text-2xl font-bold text-indigo-400">{voltage_domains.length || summary.voltage_domains_count} Rails</div>
          <div className="text-[9px] text-slate-500 mt-1">Independent power planes</div>
        </div>
      </div>

      {/* System Voltage Domains Table */}
      {voltage_domains.length > 0 && (
        <div className="glass-panel p-6 border border-blue-500/20 bg-zinc-950/40">
          <h3 className="text-sm font-semibold text-cyan-400 glow-cyan mb-4 flex items-center gap-2 font-mono">
            <Zap className="w-4 h-4 text-cyan-400" />
            System Voltage Domains (Multi-Rail Power Analysis)
          </h3>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse font-mono">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400 uppercase tracking-wider text-[10px]">
                  <th className="py-2.5 px-3">Voltage Rail</th>
                  <th className="py-2.5 px-3 text-right">Rail Voltage</th>
                  <th className="py-2.5 px-3 text-right">Rail Current</th>
                  <th className="py-2.5 px-3 text-right">Rail Power</th>
                  <th className="py-2.5 px-3">Attached Components</th>
                </tr>
              </thead>
              <tbody>
                {voltage_domains.map((vd, idx) => (
                  <tr key={idx} className="border-b border-slate-900/60 hover:bg-slate-900/20 transition-all">
                    <td className="py-3 px-3 text-cyan-300 font-bold">{vd.rail}</td>
                    <td className="py-3 px-3 text-right text-slate-200">{vd.voltage} V</td>
                    <td className="py-3 px-3 text-right text-amber-400">{vd.current_a} A ({vd.current_ma} mA)</td>
                    <td className="py-3 px-3 text-right text-emerald-400 font-bold">{vd.power_w} W</td>
                    <td className="py-3 px-3 text-slate-400 text-[11px]">{vd.components.join(", ")}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Converter Requirements */}
      {converter_requirements.length > 0 && (
        <div className="glass-panel p-6 border border-blue-500/20 bg-zinc-950/40">
          <h3 className="text-sm font-semibold text-cyan-400 glow-cyan mb-4 flex items-center gap-2 font-mono">
            <BatteryCharging className="w-4 h-4 text-cyan-400" />
            DC-DC Converter & Regulator Requirements
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 font-mono text-xs">
            {converter_requirements.map((req, idx) => (
              <div key={idx} className="p-4 bg-slate-950/60 border border-slate-800/80 rounded-lg space-y-1.5">
                <div className="flex justify-between items-center text-cyan-300 font-bold">
                  <span>{req.type}</span>
                  <span className="text-[10px] bg-cyan-950/60 border border-cyan-800 text-cyan-400 px-2 py-0.5 rounded">
                    {req.efficiency_pct}% Efficiency
                  </span>
                </div>
                <div className="text-slate-300">
                  <span className="text-slate-500">Step-down:</span> {req.input_voltage}V → <span className="font-bold text-amber-300">{req.output_voltage}V</span> (Rated {req.max_load_current_a}A)
                </div>
                <p className="text-slate-400 text-[11px] leading-relaxed pt-1">
                  {req.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Component Power Ratings list */}
      <div className="glass-panel p-6 border border-blue-500/20 bg-zinc-950/40 space-y-4">
        <h3 className="text-sm font-semibold text-cyan-400 glow-cyan flex items-center gap-2 font-mono">
          <Zap className="w-4 h-4 text-cyan-400" />
          Component Power Ratings list
        </h3>
        
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse font-mono">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 uppercase tracking-wider text-[10px]">
                <th className="py-2.5 px-3">Component name</th>
                <th className="py-2.5 px-3 text-right">voltage rating</th>
                <th className="py-2.5 px-3 text-right">current rating</th>
                <th className="py-2.5 px-3 text-right">power rating</th>
              </tr>
            </thead>
            <tbody>
              {power_items.map((item, idx) => {
                const nominal = item.nominal_current_ma ?? item.nominal_current ?? 0;
                const currentRating = item.is_source ? "—" : `${nominal} mA`;
                const powerRating = item.is_source 
                  ? "—" 
                  : `${(item.power_w ?? (item.voltage * nominal / 1000)).toFixed(3)} W`;
                
                return (
                  <tr key={idx} className="border-b border-slate-900/60 hover:bg-slate-900/20 transition-all">
                    <td className="py-3 px-3 text-slate-200 font-semibold">{item.component}</td>
                    <td className="py-3 px-3 text-right text-slate-300">{item.voltage} V</td>
                    <td className="py-3 px-3 text-right text-cyan-400">{currentRating}</td>
                    <td className="py-3 px-3 text-right text-emerald-400 font-bold">{powerRating}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        {/* Copyable Markdown Format Area */}
        <div className="space-y-2 pt-2">
          <span className="text-[10px] text-slate-500 font-mono tracking-widest uppercase block">Copyable Markdown Format</span>
          <pre className="p-3 bg-slate-950 border border-slate-900 rounded text-[11px] text-slate-400 font-mono overflow-x-auto select-all max-h-[160px]">
{`Component name | voltage rating | current rating | power rating |\n` +
`---|---|---|---|\n` +
power_items.map(item => {
  const nominal = item.nominal_current_ma ?? item.nominal_current ?? 0;
  const currentRating = item.is_source ? "—" : `${nominal} mA`;
  const powerRating = item.is_source 
    ? "—" 
    : `${(item.power_w ?? (item.voltage * nominal / 1000)).toFixed(3)} W`;
  return `${item.component} | ${item.voltage} V | ${currentRating} | ${powerRating} |`;
}).join('\n')}
          </pre>
        </div>
      </div>
    </div>
  );
}
