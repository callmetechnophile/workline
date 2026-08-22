"use client";

import React, { useState } from "react";
import { 
  FileSpreadsheet, 
  CheckCircle2, 
  Clock, 
  ExternalLink, 
  ShieldCheck, 
  AlertTriangle,
  Truck,
  IndianRupee,
  Layers
} from "lucide-react";

export interface BOMItem {
  bom_item_id: string;
  component_id: string;
  manufacturer: string;
  mpn: string;
  description?: string;
  quantity: number;
  selected_vendor: string;
  vendor_product_url?: string;
  unit_price: number;
  extended_price: number;
  currency: string;
  stock?: number;
  lead_time_days?: number;
  datasheet_url?: string;
  validation_status: string;
}

export interface BOMData {
  bom_id: string;
  project_id: string;
  version: number;
  status: string;
  total_component_cost: number;
  estimated_shipping: number;
  estimated_total: number;
  currency: string;
  items: BOMItem[];
}

interface BOMTableProps {
  bom: BOMData;
  onApprove?: (bomId: string) => void;
}

export const BOMTable: React.FC<BOMTableProps> = ({ bom, onApprove }) => {
  const [approving, setApproving] = useState(false);
  const [status, setStatus] = useState(bom.status);

  const handleApprove = async () => {
    setApproving(true);
    try {
      const res = await fetch(`/api/bom/${bom.bom_id}/approve`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ approved_by: "Lead Engineer" }),
      });
      if (res.ok) {
        setStatus("APPROVED");
        if (onApprove) onApprove(bom.bom_id);
      }
    } catch (err) {
      console.error("BOM approval failed:", err);
    } finally {
      setApproving(false);
    }
  };

  const isApproved = status === "APPROVED";

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 shadow-2xl backdrop-blur-md space-y-5">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-emerald-500/10 border border-emerald-500/20 rounded-lg text-emerald-400">
            <FileSpreadsheet className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-semibold text-slate-100">Engineering Bill of Materials</h3>
            <p className="text-xs text-slate-400 font-mono">ID: {bom.bom_id} • v{bom.version}</p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold ${
            isApproved 
              ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20" 
              : "bg-amber-500/10 text-amber-400 border border-amber-500/20"
          }`}>
            {isApproved ? <CheckCircle2 className="w-3.5 h-3.5" /> : <Clock className="w-3.5 h-3.5" />}
            {status.replace(/_/g, " ")}
          </span>

          {!isApproved && (
            <button
              disabled={approving}
              onClick={handleApprove}
              className="px-4 py-1.5 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white text-xs font-semibold rounded-lg shadow-lg transition-all flex items-center gap-1.5"
            >
              <CheckCircle2 className="w-3.5 h-3.5" /> Approve BOM
            </button>
          )}
        </div>
      </div>

      {/* Financial Summary Card */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        <div className="bg-slate-950/60 p-3.5 rounded-lg border border-slate-800/80">
          <span className="text-[11px] text-slate-400 uppercase tracking-wider block mb-1">Component Total</span>
          <span className="text-lg font-bold text-slate-100 flex items-center gap-1">
            <IndianRupee className="w-4 h-4 text-slate-400" /> {bom.total_component_cost.toLocaleString()}
          </span>
        </div>
        <div className="bg-slate-950/60 p-3.5 rounded-lg border border-slate-800/80">
          <span className="text-[11px] text-slate-400 uppercase tracking-wider block mb-1 flex items-center gap-1">
            <Truck className="w-3.5 h-3.5 text-yellow-400" /> Est. Freight (Landed)
          </span>
          <span className="text-lg font-bold text-yellow-400 flex items-center gap-1">
            <IndianRupee className="w-4 h-4 text-yellow-400/80" /> {bom.estimated_shipping.toLocaleString()}
            <span className="text-[10px] font-normal text-slate-400 ml-1">ESTIMATED</span>
          </span>
        </div>
        <div className="bg-slate-950/60 p-3.5 rounded-lg border border-emerald-500/30">
          <span className="text-[11px] text-emerald-400 uppercase tracking-wider block mb-1">Total Landed Cost</span>
          <span className="text-lg font-bold text-emerald-400 flex items-center gap-1">
            <IndianRupee className="w-4 h-4 text-emerald-400" /> {bom.estimated_total.toLocaleString()}
          </span>
        </div>
      </div>

      {/* Line Items Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs text-slate-300 border-collapse">
          <thead>
            <tr className="border-b border-slate-800 text-[11px] text-slate-400 uppercase tracking-wider bg-slate-950/30">
              <th className="py-2.5 px-3">Component / MPN</th>
              <th className="py-2.5 px-3">Manufacturer</th>
              <th className="py-2.5 px-3 text-center">Qty</th>
              <th className="py-2.5 px-3">Vendor</th>
              <th className="py-2.5 px-3 text-right">Unit Cost</th>
              <th className="py-2.5 px-3 text-right">Ext. Cost</th>
              <th className="py-2.5 px-3 text-center">Datasheet</th>
              <th className="py-2.5 px-3 text-center">Validation</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 font-mono">
            {bom.items.map((item, idx) => (
              <tr key={idx} className="hover:bg-slate-800/30 transition-colors">
                <td className="py-3 px-3">
                  <div className="font-semibold text-slate-100 font-sans">{item.mpn}</div>
                  <div className="text-[11px] text-slate-400 font-sans truncate max-w-xs">{item.description}</div>
                </td>
                <td className="py-3 px-3 text-slate-400 font-sans">{item.manufacturer}</td>
                <td className="py-3 px-3 text-center text-slate-200">{item.quantity}</td>
                <td className="py-3 px-3 font-sans">
                  {item.vendor_product_url ? (
                    <a 
                      href={item.vendor_product_url} 
                      target="_blank" 
                      rel="noopener noreferrer" 
                      className="text-cyan-400 hover:underline inline-flex items-center gap-1"
                    >
                      {item.selected_vendor} <ExternalLink className="w-3 h-3" />
                    </a>
                  ) : (
                    <span className="text-slate-300">{item.selected_vendor}</span>
                  )}
                </td>
                <td className="py-3 px-3 text-right text-slate-300">₹{item.unit_price}</td>
                <td className="py-3 px-3 text-right font-bold text-slate-100">₹{item.extended_price}</td>
                <td className="py-3 px-3 text-center font-sans">
                  {item.datasheet_url ? (
                    <a
                      href={item.datasheet_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1 text-[11px] text-indigo-400 hover:text-indigo-300"
                    >
                      <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" /> PDF
                    </a>
                  ) : (
                    <span className="text-slate-500 text-[11px]">N/A</span>
                  )}
                </td>
                <td className="py-3 px-3 text-center font-sans">
                  <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                    <CheckCircle2 className="w-3 h-3" /> PASS
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default BOMTable;
