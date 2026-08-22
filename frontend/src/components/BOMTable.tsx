"use client";

import React, { useState } from "react";
import { Table, Search, ArrowUpDown, Check, AlertCircle } from "lucide-react";

export interface BOMTableItem {
  ref: string;
  component: string;
  partNumber: string;
  orderingCode: string;
  qty: number;
  supplier: string;
  unitPrice: number;
  stock: number;
  status: string;
}

export interface BOMTableProps {
  items?: BOMTableItem[];
  onSelectPart?: (ref: string) => void;
}

export const BOMTable: React.FC<BOMTableProps> = ({
  items = [
    {
      ref: "U1",
      component: "TPS62130",
      partNumber: "TPS62130",
      orderingCode: "TPS62130RGTR",
      qty: 1,
      supplier: "DigiKey",
      unitPrice: 180.0,
      stock: 500,
      status: "RESOLVED",
    },
  ],
  onSelectPart,
}) => {
  const [filter, setFilter] = useState("");

  const filtered = items.filter(
    (item) =>
      item.ref.toLowerCase().includes(filter.toLowerCase()) ||
      item.partNumber.toLowerCase().includes(filter.toLowerCase()) ||
      item.orderingCode.toLowerCase().includes(filter.toLowerCase())
  );

  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-5 flex flex-col gap-4 text-zinc-100">
      <div className="flex items-center justify-between pb-2 border-b border-zinc-800">
        <div className="flex items-center gap-2">
          <Table className="w-5 h-5 text-indigo-400" />
          <h3 className="text-base font-bold text-zinc-100">BOM Line Items</h3>
        </div>
        <div className="relative">
          <Search className="w-3.5 h-3.5 absolute left-2.5 top-2 text-zinc-500" />
          <input
            type="text"
            placeholder="Filter components..."
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="pl-8 pr-3 py-1 bg-zinc-950 border border-zinc-800 rounded text-xs text-zinc-200 placeholder:text-zinc-600 focus:outline-none focus:border-indigo-500"
          />
        </div>
      </div>

      <div className="overflow-x-auto border border-zinc-800 rounded-lg">
        <table className="w-full text-left text-xs font-mono">
          <thead className="bg-zinc-950/80 text-zinc-400 border-b border-zinc-800">
            <tr>
              <th className="p-2.5">Ref</th>
              <th className="p-2.5">Component</th>
              <th className="p-2.5">Ordering Code</th>
              <th className="p-2.5">Qty</th>
              <th className="p-2.5">Supplier</th>
              <th className="p-2.5">Unit Price</th>
              <th className="p-2.5">Stock</th>
              <th className="p-2.5">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-zinc-800 bg-zinc-900">
            {filtered.map((item) => (
              <tr
                key={item.ref}
                onClick={() => onSelectPart && onSelectPart(item.ref)}
                className="hover:bg-zinc-800/40 cursor-pointer transition"
              >
                <td className="p-2.5 font-bold text-indigo-300">{item.ref}</td>
                <td className="p-2.5 font-semibold text-zinc-200">{item.component}</td>
                <td className="p-2.5 text-zinc-400">{item.orderingCode}</td>
                <td className="p-2.5">{item.qty}</td>
                <td className="p-2.5 text-zinc-300">{item.supplier}</td>
                <td className="p-2.5 font-bold text-emerald-400">₹{item.unitPrice.toFixed(2)}</td>
                <td className="p-2.5 text-zinc-300">{item.stock > 0 ? item.stock : "0"}</td>
                <td className="p-2.5">
                  <span
                    className={`px-1.5 py-0.5 rounded text-[10px] ${
                      item.status === "RESOLVED"
                        ? "text-emerald-400 bg-emerald-950/40"
                        : "text-amber-400 bg-amber-950/40"
                    }`}
                  >
                    {item.status}
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
