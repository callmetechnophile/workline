"use client";

import React, { useState } from "react";
import { Table, Search, ArrowUpDown, Check, AlertCircle } from "lucide-react";

import { EngineeringStatusBadge } from "./EngineeringStatusBadge";

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
    <div className="bg-surface border border-border rounded-lg p-5 flex flex-col gap-4 text-foreground">
      <div className="flex items-center justify-between pb-2 border-b border-border">
        <div className="flex items-center gap-2">
          <Table className="w-5 h-5 text-primary" />
          <h3 className="text-base font-bold text-foreground">BOM Line Items</h3>
        </div>
        <div className="relative">
          <Search className="w-3.5 h-3.5 absolute left-2.5 top-2 text-muted-foreground" />
          <input
            type="text"
            placeholder="Filter components..."
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="pl-8 pr-3 py-1 bg-surface-secondary border border-border rounded text-xs text-foreground placeholder:text-muted focus:outline-none focus:border-primary"
          />
        </div>
      </div>

      <div className="overflow-x-auto border border-border rounded-lg">
        <table className="w-full text-left text-xs font-mono font-tabular">
          <thead className="bg-surface-secondary/80 text-muted-foreground border-b border-border">
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
          <tbody className="divide-y divide-border bg-surface">
            {filtered.map((item) => (
              <tr
                key={item.ref}
                onClick={() => onSelectPart && onSelectPart(item.ref)}
                className="hover:bg-surface-secondary/50 cursor-pointer transition"
              >
                <td className="p-2.5 font-bold text-primary">{item.ref}</td>
                <td className="p-2.5 font-semibold text-foreground">{item.component}</td>
                <td className="p-2.5 text-muted-foreground">{item.orderingCode}</td>
                <td className="p-2.5 text-foreground">{item.qty}</td>
                <td className="p-2.5 text-foreground-secondary">{item.supplier}</td>
                <td className="p-2.5 font-bold text-emerald-400">₹{item.unitPrice.toFixed(2)}</td>
                <td className="p-2.5 text-foreground-secondary">{item.stock > 0 ? item.stock : "0"}</td>
                <td className="p-2.5">
                  <EngineeringStatusBadge status={item.status} size="sm" />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
