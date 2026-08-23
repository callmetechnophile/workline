"use client";

import React, { useState } from "react";
import {
  ShoppingCart,
  ShieldCheck,
  Zap,
  Clock,
  ArrowRight,
  RefreshCw,
  PlusCircle,
  FileCheck,
} from "lucide-react";
import OrderPreview, { OrderPreviewData } from "./OrderPreview";
import { PaymentPanel, PaymentDetails } from "./PaymentPanel";
import OrderStatus from "./OrderStatus";
import ReceiptPanel, { ReceiptData } from "./ReceiptPanel";
import OrderAuditTimeline, { AuditEventItem } from "./OrderAuditTimeline";

export interface OrderPanelProps {
  projectId?: string;
  bomId?: string;
  initialOrders?: OrderPreviewData[];
  onCreateOrderPlan?: () => Promise<void> | void;
}

export const OrderPanel: React.FC<OrderPanelProps> = ({
  projectId,
  bomId,
  initialOrders = [],
  onCreateOrderPlan,
}) => {
  const [orders, setOrders] = useState<OrderPreviewData[]>(initialOrders);
  const [selectedOrderId, setSelectedOrderId] = useState<string | null>(
    initialOrders.length > 0 ? initialOrders[0].order_id : null
  );
  const [activePayment, setActivePayment] = useState<PaymentDetails | null>(null);
  const [activeReceipt, setActiveReceipt] = useState<ReceiptData | null>(null);
  const [auditEvents, setAuditEvents] = useState<AuditEventItem[]>([]);
  const [loading, setLoading] = useState(false);

  const selectedOrder = orders.find((o) => o.order_id === selectedOrderId);

  // 1. Create Order Plan
  const handleCreateOrderPlan = async () => {
    if (onCreateOrderPlan) {
      setLoading(true);
      try {
        await onCreateOrderPlan();
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    }
  };

  // 2. Approve Order
  const handleApprove = async (orderId: string) => {
    setLoading(true);
    try {
      setOrders((prev) =>
        prev.map((o) =>
          o.order_id === orderId
            ? { ...o, status: "APPROVED" }
            : o
        )
      );
    } finally {
      setLoading(false);
    }
  };

  // 3. Proceed to Payment
  const handleProceedToPayment = async (orderId: string) => {
    const order = orders.find((o) => o.order_id === orderId);
    if (!order) return;

    const amountVal = Number((order.total / 86.50).toFixed(2));
    setActivePayment({
      quote_id: orderId,
      payment_request_id: `req_${Math.random().toString(16).substring(2, 10)}`,
      order_id: orderId,
      project_id: projectId || order.project_id,
      amount_usd: amountVal,
      amount_usdc: amountVal,
      currency: "USD",
      network: "algorand-mainnet",
      asset: "USDC",
      asset_id: 31566704,
      recipient: "WORKLINE24EUSDCALGORANDTREASURYRECIPIENT402XXXXXXXXXXXXXX",
      expires_at: new Date(Date.now() + 30 * 60000).toISOString(),
      status: "REQUIRED",
    });
  };

  // 4. Authorize Payment & Execute
  const handleAuthorizePayment = async (quoteId: string, proof: any) => {
    if (!selectedOrder) return;

    // Transition Order to Confirmed / Manual Checkout
    const isManual = selectedOrder.execution_mode === "MANUAL";
    const resultingStatus = isManual ? "MANUAL_CHECKOUT_REQUIRED" : "CONFIRMED";

    setOrders((prev) =>
      prev.map((o) =>
        o.order_id === selectedOrder.order_id
          ? { ...o, status: resultingStatus }
          : o
      )
    );

    setActiveReceipt({
      receipt_id: `rec_${Math.random().toString(16).substring(2, 10)}`,
      order_id: selectedOrder.order_id,
      vendor: selectedOrder.vendor,
      external_order_id: `VEND-${selectedOrder.order_id}`,
      subtotal: selectedOrder.subtotal,
      shipping: selectedOrder.shipping_cost,
      tax: selectedOrder.tax,
      fees: selectedOrder.fees,
      total: selectedOrder.total,
      currency: selectedOrder.currency,
      issued_at: new Date().toISOString(),
      verification_status: "VERIFIED",
    });
  };

  return (
    <div className="space-y-6">
      {/* Top Header Card */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 shadow-2xl flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2">
            <ShoppingCart className="w-5 h-5 text-cyan-400" />
            Item Ordering & Payment Authorization
          </h2>
          <p className="text-xs text-slate-400">
            Autonomous Preparation • Human Approval • x402 Cryptographic Settlement
          </p>
        </div>

        <button
          onClick={handleCreateOrderPlan}
          disabled={loading}
          className="px-4 py-2 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-semibold shadow-lg shadow-cyan-900/30 flex items-center gap-1.5 transition-all self-start sm:self-auto disabled:opacity-50"
        >
          {loading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <PlusCircle className="w-4 h-4" />}
          Create Order Plan from BOM
        </button>
      </div>

      {/* Orders Navigation Tabs */}
      {orders.length > 0 && (
        <div className="flex gap-2 overflow-x-auto pb-1">
          {orders.map((o) => (
            <button
              key={o.order_id}
              onClick={() => {
                setSelectedOrderId(o.order_id);
                setActivePayment(null);
              }}
              className={`px-3.5 py-2 rounded-lg text-xs font-semibold border transition-all flex items-center gap-2 ${
                selectedOrderId === o.order_id
                  ? "bg-slate-800 border-cyan-500 text-cyan-300 shadow-md"
                  : "bg-slate-950/60 border-slate-800 text-slate-400 hover:text-slate-200"
              }`}
            >
              <span>{o.order_id}</span>
              <span className="text-[10px] px-1.5 py-0.2 rounded bg-slate-900 text-slate-400 border border-slate-800">
                {o.vendor}
              </span>
            </button>
          ))}
        </div>
      )}

      {/* Main Content Area */}
      {!orders || orders.length === 0 ? (
        <div className="bg-slate-900/60 border border-slate-800 rounded-lg p-8 text-center">
          <ShoppingCart className="w-8 h-8 text-slate-600 mx-auto mb-2" />
          <p className="text-xs text-slate-400">No orders placed.</p>
          <p className="text-[10px] text-slate-500 mt-1">Create or select a project to view orders.</p>
        </div>
      ) : selectedOrder ? (
        <div className="space-y-6">
          {/* 1. Order Preview & Approval */}
          <OrderPreview
            order={selectedOrder}
            onApprove={handleApprove}
            onProceedToPayment={handleProceedToPayment}
          />

          {/* 2. x402 Payment Panel */}
          {activePayment && (
            <PaymentPanel
              payment={activePayment}
              onAuthorizePayment={handleAuthorizePayment}
              onCancelPayment={() => setActivePayment(null)}
            />
          )}

          {/* 3. Tracking Status */}
          <OrderStatus
            order={{
              order_id: selectedOrder.order_id,
              project_id: selectedOrder.project_id,
              vendor: selectedOrder.vendor,
              status: selectedOrder.status,
              payment_status: selectedOrder.status === "APPROVED" ? "REQUIRED" : (selectedOrder.status === "CONFIRMED" ? "SETTLED" : "PENDING"),
              approval_status: selectedOrder.status === "READY_FOR_APPROVAL" ? "PENDING" : "APPROVED",
              total: selectedOrder.total,
              currency: selectedOrder.currency,
              created_at: new Date().toISOString(),
            }}
            onViewReceipt={() => {}}
            onViewAudit={() => {}}
          />

          {/* 4. Receipt Panel */}
          {activeReceipt && <ReceiptPanel receipt={activeReceipt} />}
        </div>
      ) : null}
    </div>
  );
};

export default OrderPanel;
