'use client';

import React from 'react';
import { Cpu, Download, RefreshCw } from 'lucide-react';

interface PinConnection {
  component: string;
  pin?: string;
  pin_number?: string;
  pin_name?: string;
  direction?: string;
  function?: string;
  connected_to: string;
  type?: string;
  signal_type?: string;
  voltage_domain?: string;
  status?: string;
}

interface PinMappingTableProps {
  pins?: PinConnection[];
}

export default function PinMappingTable({ pins }: PinMappingTableProps) {
  const downloadCSV = () => {
    if (!pins || pins.length === 0) return;
    const headers = ["Component", "Pin Number", "Pin Name", "Direction", "Function", "Connected To", "Signal Type", "Voltage Domain", "Status"];
    const csvContent = [
      headers.join(","),
      ...pins.map(p => `"${p.component}","${p.pin_number || ''}","${p.pin_name || p.pin || ''}","${p.direction || ''}","${p.function || ''}","${p.connected_to}","${p.signal_type || p.type || ''}","${p.voltage_domain || ''}","${p.status || 'VERIFIED'}"`)
    ].join("\n");

    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", "pin_mapping_config.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="glass-panel border border-blue-500/20 bg-slate-900/10 p-5 space-y-4">
      <div className="flex justify-between items-center border-b border-blue-900/40 pb-3">
        <div className="flex items-center gap-2.5">
          <Cpu className="w-5 h-5 text-blue-400" />
          <h3 className="text-sm font-mono font-bold text-slate-200 uppercase tracking-wider">
            Verified Pin Configuration & Interconnect Table
          </h3>
        </div>
        
        {pins && pins.length > 0 && (
          <button 
            onClick={downloadCSV}
            className="text-[10px] font-mono flex items-center gap-1.5 bg-blue-950/40 px-2.5 py-1.5 border border-blue-900/30 rounded text-cyan-400 hover:bg-blue-900/40 transition-all cursor-pointer"
          >
            <Download className="w-3.5 h-3.5" />
            Download Pin CSV
          </button>
        )}
      </div>

      {!pins || pins.length === 0 ? (
        <div className="text-center py-6 text-xs text-slate-500 font-mono">
          [SYSTEM NOTICE]: Pin connection configuration is idle. Submit a query to generate wiring boards.
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse font-mono">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 uppercase tracking-widest text-[9px]">
                <th className="py-2.5 px-3">Component / IC</th>
                <th className="py-2.5 px-3">Pin</th>
                <th className="py-2.5 px-3">Direction & Function</th>
                <th className="py-2.5 px-3">Connected Net</th>
                <th className="py-2.5 px-3 text-right">Domain</th>
                <th className="py-2.5 px-3 text-right">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/30">
              {pins.map((pin, idx) => {
                const isVerified = pin.status !== "PINOUT VERIFICATION REQUIRED";
                const pType = pin.signal_type || pin.type || "SIGNAL";
                
                let badgeColor = "bg-slate-950/60 border-slate-800 text-slate-400";
                if (pType === "I2C" || pType === "COMMUNICATION") badgeColor = "bg-blue-950/30 border-blue-900/30 text-blue-400";
                else if (pType === "POWER") badgeColor = "bg-red-950/30 border-red-900/30 text-red-400";
                else if (pType === "GROUND") badgeColor = "bg-zinc-950/60 border-zinc-800 text-zinc-400";
                else if (pType === "USB") badgeColor = "bg-emerald-950/30 border-emerald-900/30 text-emerald-400";
                else if (pType === "PWM" || pType === "GPIO") badgeColor = "bg-amber-950/30 border-amber-900/30 text-amber-400";

                return (
                  <tr key={idx} className="hover:bg-slate-900/30 transition-all">
                    <td className="py-3 px-3 text-slate-300 font-semibold">{pin.component}</td>
                    <td className="py-3 px-3 font-semibold text-cyan-300">
                      {pin.pin_number ? `Pin ${pin.pin_number} (${pin.pin_name || pin.pin})` : (pin.pin || 'Pin')}
                    </td>
                    <td className="py-3 px-3 text-slate-400 text-[11px]">
                      {pin.direction && <span className="text-slate-500 font-bold mr-1.5">[{pin.direction}]</span>}
                      {pin.function || "Signal interconnection"}
                    </td>
                    <td className="py-3 px-3 text-slate-200 font-medium">{pin.connected_to}</td>
                    <td className="py-3 px-3 text-right">
                      <span className={`inline-block text-[9px] font-extrabold px-2 py-0.5 border rounded uppercase ${badgeColor}`}>
                        {pin.voltage_domain || pType}
                      </span>
                    </td>
                    <td className="py-3 px-3 text-right">
                      <span className={`inline-block text-[9px] font-extrabold px-2 py-0.5 rounded ${
                        isVerified 
                          ? "bg-emerald-950/60 text-emerald-400 border border-emerald-800/60"
                          : "bg-amber-950/60 text-amber-400 border border-amber-800/60"
                      }`}>
                        {isVerified ? "VERIFIED" : "VERIFY"}
                      </span>
                    </td>
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
