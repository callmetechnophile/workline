"use client";

import React, { useState } from "react";
import {
  FileCheck,
  ShieldCheck,
  AlertTriangle,
  Clock,
  ArrowRight,
  DollarSign,
  PackageCheck,
  Building,
  CheckCircle2,
  RefreshCw,
} from "lucide-react";

export interface OrderItemPreview {
  order_item_id: string;
  manufacturer: string;
  mpn: string;
  description?: string;
  quantity: number;
  unit_price: number;
  extended_price: number;
  currency: string;
  vendor_name: string;
  stock_at_validation?: number;
}

export interface OrderPreviewData {
  order_id: string;
  project_id: string;
  vendor: string;
  currency: string;
  subtotal: number;
  shipping_cost: number;
  tax: number;
  fees: number;
  total: number;
  status: string;
  execution_mode: "AUTOMATED" | "MANUAL" | "UNAVAILABLE";
  items: OrderItemPreview[];
  price_changes_count?: number;
  stock_changes_count?: number;
}

interface OrderPreviewProps {
  order: OrderPreviewData;
  onApprove?: (orderId: string) => Promise<void>;
  onCancel?: (orderId: string) => Promise<void>;
  onProceedToPayment?: (orderId: string) => Promise<void>;
  isApproving?: boolean;
}

export const OrderPreview: React.FC<OrderPreviewProps> = ({
  order,
  onApprove,
  onCancel,
  onProceedToPayment,
  isApproving = false,
}) => {
  const isApproved = order.status === "APPROVED" || order.status === "PAYMENT_REQUIRED" || order.status === "PAYMENT_PENDING" || order.status === "PAYMENT_AUTHORIZED" || order.status === "CONFIRMED";
  const isManual = order.execution_mode === "MANUAL";

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 shadow-2xl backdrop-blur-md space-y-5">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 border-b border-slate-800 pb-4">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-cyan-500/10 border border-cyan-500/20 rounded-lg text-cyan-400">
            <FileCheck className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-base font-bold text-slate-100">ORDER PREVIEW</h3>
              <span className="font-mono text-xs px-2 py-0.5 rounded bg-slate-800 text-cyan-400 font-semibold">
                {order.order_id}
              </span>
            </div>
            <p className="text-xs text-slate-400 flex items-center gap-2 mt-0.5">
              <span>Vendor: <strong className="text-slate-200">{order.vendor}</strong></span>
              <span>•</span>
              <span className={`px-1.5 py-0.2 rounded text-[10px] font-semibold ${
                isManual ? "bg-amber-500/10 text-amber-400 border border-amber-500/20" : "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
              }`}>
                {order.execution_mode}
              </span>
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <span className={`px-2.5 py-1 rounded-full text-xs font-semibold uppercase tracking-wider ${
            isApproved ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/30" : "bg-amber-500/10 text-amber-400 border border-amber-500/30"
          }`}>
            {order.status}
          </span>
        </div>
      </div>

      {/* Line Items Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs border-collapse">
          <thead>
            <tr className="border-b border-slate-800 text-slate-400 uppercase text-[10px] tracking-wider">
              <th className="pb-2">Component</th>
              <th className="pb-2">MPN</th>
              <th className="pb-2 text-right">Qty</th>
              <th className="pb-2 text-right">Unit Price</th>
              <th className="pb-2 text-right">Ext. Price</th>
              <th className="pb-2 text-center">Stock</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60">
            {order.items.map((item) => (
              <tr key={item.order_item_id} className="hover:bg-slate-800/30 transition-colors">
                <td className="py-2.5 font-medium text-slate-200">
                  {item.description || item.mpn}
                  <div className="text-[10px] text-slate-500">{item.manufacturer}</div>
                </td>
                <td className="py-2.5 font-mono text-cyan-400">{item.mpn}</td>
                <td className="py-2.5 text-right font-semibold text-slate-200">{item.quantity}</td>
                <td className="py-2.5 text-right text-slate-300">{item.currency} {item.unit_price.toFixed(2)}</td>
                <td className="py-2.5 text-right font-semibold text-slate-100">{item.currency} {item.extended_price.toFixed(2)}</td>
                <td className="py-2.5 text-center">
                  <span className="inline-flex items-center gap-1 text-[10px] font-semibold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full border border-emerald-500/20">
                    <CheckCircle2 className="w-3 h-3" /> In Stock
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Financial Summary Breakdown */}
      <div className="bg-slate-950/60 p-4 rounded-xl border border-slate-800 grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div className="space-y-1.5 text-xs">
          <div className="text-slate-400 font-semibold uppercase text-[10px] tracking-wider mb-2">Revalidation Status</div>
          <div className="flex items-center gap-2 text-slate-300">
            <ShieldCheck className="w-4 h-4 text-emerald-400 shrink-0" />
            <span>Price changes: <strong>{order.price_changes_count || 0}</strong></span>
          </div>
          <div className="flex items-center gap-2 text-slate-300">
            <PackageCheck className="w-4 h-4 text-emerald-400 shrink-0" />
            <span>Stock changes: <strong>{order.stock_changes_count || 0}</strong></span>
          </div>
          <div className="flex items-center gap-2 text-slate-400 text-[11px]">
            <Clock className="w-3.5 h-3.5" />
            <span>Live revalidated before authorization</span>
          </div>
        </div>

        <div className="space-y-1.5 text-xs text-right sm:border-l sm:border-slate-800/80 sm:pl-4">
          <div className="flex justify-between text-slate-400">
            <span>Subtotal:</span>
            <span className="font-mono text-slate-200">{order.currency} {order.subtotal.toFixed(2)}</span>
          </div>
          <div className="flex justify-between text-slate-400">
            <span className="flex items-center gap-1">
              Shipping:
              <span className="text-[9px] bg-slate-800 text-slate-400 px-1 rounded">ESTIMATED</span>
            </span>
            <span className="font-mono text-slate-200">{order.currency} {order.shipping_cost.toFixed(2)}</span>
          </div>
          <div className="flex justify-between text-slate-400">
            <span>Tax (GST 18%):</span>
            <span className="font-mono text-slate-200">{order.currency} {order.tax.toFixed(2)}</span>
          </div>
          {order.fees > 0 && (
            <div className="flex justify-between text-slate-400">
              <span>Handling Fees:</span>
              <span className="font-mono text-slate-200">{order.currency} {order.fees.toFixed(2)}</span>
            </div>
          )}
          <div className="flex justify-between text-sm font-bold text-slate-100 pt-2 border-t border-slate-800">
            <span className="text-cyan-400">TOTAL:</span>
            <span className="font-mono text-emerald-400 text-base">{order.currency} {order.total.toFixed(2)}</span>
          </div>
        </div>
      </div>

      {/* Action Checkpoints */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-3 pt-2">
        <div className="text-[11px] text-slate-500">
          Payment method: <strong className="text-slate-300">x402 (Non-Custodial USDC)</strong>
        </div>

        <div className="flex items-center gap-2 w-full sm:w-auto">
          {onCancel && !isApproved && (
            <button
              onClick={() => onCancel(order.order_id)}
              className="px-3 py-1.5 rounded-lg border border-slate-700 hover:bg-slate-800 text-slate-400 hover:text-slate-200 text-xs font-semibold transition-all w-full sm:w-auto"
            >
              Cancel
            </button>
          )}

          {!isApproved && onApprove && (
            <button
              onClick={() => onApprove(order.order_id)}
              disabled={isApproving}
              className="px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold shadow-lg shadow-emerald-900/30 transition-all flex items-center justify-center gap-1.5 w-full sm:w-auto disabled:opacity-50"
            >
              {isApproving ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <ShieldCheck className="w-3.5 h-3.5" />}
              Approve Order
            </button>
          )}

          {isApproved && onProceedToPayment && (
            <button
              onClick={() => onProceedToPayment(order.order_id)}
              className="px-4 py-2 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-semibold shadow-lg shadow-cyan-900/30 transition-all flex items-center justify-center gap-1.5 w-full sm:w-auto"
            >
              Proceed to x402 Payment <ArrowRight className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default OrderPreview;
