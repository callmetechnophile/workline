"use client";

import React from "react";
import {
  CheckCircle2,
  Clock,
  Package,
  Truck,
  ExternalLink,
  ShieldCheck,
  AlertCircle,
  FileText,
} from "lucide-react";

export interface OrderStatusDetails {
  order_id: string;
  project_id: string;
  vendor: string;
  status: string;
  payment_status: string;
  approval_status: string;
  approved_by?: string;
  total: number;
  currency: string;
  external_order_id?: string;
  receipt_id?: string;
  tracking_number?: string;
  created_at: string;
  submitted_at?: string;
  confirmed_at?: string;
}

interface OrderStatusProps {
  order: OrderStatusDetails;
  onViewReceipt?: (orderId: string) => void;
  onViewAudit?: (orderId: string) => void;
}

export const OrderStatus: React.FC<OrderStatusProps> = ({
  order,
  onViewReceipt,
  onViewAudit,
}) => {
  const steps = [
    { label: "BOM Validated", done: true },
    { label: "Prices Revalidated", done: true },
    { label: "User Approved", done: order.approval_status === "APPROVED" },
    { label: "Payment Authorized", done: order.payment_status === "AUTHORIZED" || order.payment_status === "SETTLED" },
    { label: "Order Submitted", done: Boolean(order.submitted_at) || order.status === "SUBMITTED" || order.status === "CONFIRMED" },
    { label: "Vendor Confirmed", done: order.status === "CONFIRMED" || Boolean(order.confirmed_at) },
  ];

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 shadow-2xl backdrop-blur-md space-y-5">
      {/* Title Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="text-base font-bold text-slate-100">ORDER TRACKING</h3>
            <span className="font-mono text-xs px-2 py-0.5 rounded bg-slate-800 text-cyan-400 font-semibold">
              {order.order_id}
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-0.5">
            Vendor: <strong className="text-slate-200">{order.vendor}</strong> • Total: <strong className="text-emerald-400">{order.currency} {order.total.toFixed(2)}</strong>
          </p>
        </div>

        <div className="flex items-center gap-2">
          {onViewAudit && (
            <button
              onClick={() => onViewAudit(order.order_id)}
              className="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium transition-all"
            >
              Audit Trail
            </button>
          )}
          {order.receipt_id && onViewReceipt && (
            <button
              onClick={() => onViewReceipt(order.order_id)}
              className="px-2.5 py-1 rounded bg-emerald-600/20 text-emerald-400 border border-emerald-500/30 hover:bg-emerald-600/30 text-xs font-semibold flex items-center gap-1 transition-all"
            >
              <FileText className="w-3.5 h-3.5" /> View Receipt
            </button>
          )}
        </div>
      </div>

      {/* Visual Step-by-Step Progress Timeline */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2">
        {steps.map((step, idx) => (
          <div
            key={idx}
            className={`p-3 rounded-lg border flex flex-col justify-between space-y-2 transition-all ${
              step.done
                ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-300"
                : "bg-slate-950/40 border-slate-800/80 text-slate-500"
            }`}
          >
            <div className="flex items-center justify-between">
              <span className="text-[10px] font-mono text-slate-400">0{idx + 1}</span>
              {step.done ? (
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              ) : (
                <Clock className="w-4 h-4 text-slate-600" />
              )}
            </div>
            <div className="text-xs font-semibold">{step.label}</div>
          </div>
        ))}
      </div>

      {/* Detailed Meta Grid */}
      <div className="bg-slate-950/60 p-4 rounded-xl border border-slate-800 grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
        <div className="space-y-1">
          <span className="text-slate-400">Order Lifecycle State:</span>
          <div className="font-bold text-slate-200">{order.status}</div>
        </div>
        <div className="space-y-1">
          <span className="text-slate-400">Vendor Reference:</span>
          <div className="font-mono text-cyan-400 font-semibold">{order.external_order_id || "Awaiting submission"}</div>
        </div>
        <div className="space-y-1">
          <span className="text-slate-400">Approver:</span>
          <div className="text-slate-200">{order.approved_by || "Pending approval"}</div>
        </div>
      </div>
    </div>
  );
};

export default OrderStatus;
