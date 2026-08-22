"use client";

import React from "react";
import { History, Shield, CheckCircle2, User, Bot, Clock } from "lucide-react";

export interface AuditEventItem {
  event_id: string;
  order_id: string;
  event_type: string;
  timestamp: string;
  actor_type: string;
  actor_id: string;
  previous_status?: string;
  new_status?: string;
  metadata?: Record<string, any>;
}

interface OrderAuditTimelineProps {
  events: AuditEventItem[];
  orderId: string;
}

export const OrderAuditTimeline: React.FC<OrderAuditTimelineProps> = ({ events, orderId }) => {
  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 shadow-2xl backdrop-blur-md space-y-4">
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-indigo-500/10 border border-indigo-500/20 rounded-lg text-indigo-400">
            <History className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-semibold text-slate-100">Order Audit Trail</h3>
            <p className="text-xs text-slate-400">Append-Only Event Provenance for {orderId}</p>
          </div>
        </div>

        <span className="text-xs text-slate-500 font-mono">
          {events.length} event(s)
        </span>
      </div>

      <div className="space-y-3 relative before:absolute before:inset-0 before:left-3.5 before:w-0.5 before:bg-slate-800">
        {events.map((evt) => (
          <div key={evt.event_id} className="relative flex items-start gap-3 pl-1">
            <div className="w-6 h-6 rounded-full bg-slate-900 border border-slate-700 flex items-center justify-center text-cyan-400 shrink-0 z-10">
              {evt.actor_type === "AGENT" ? <Bot className="w-3.5 h-3.5" /> : <User className="w-3.5 h-3.5" />}
            </div>

            <div className="flex-1 bg-slate-950/60 p-3 rounded-lg border border-slate-800 text-xs space-y-1">
              <div className="flex items-center justify-between">
                <span className="font-bold text-slate-200 font-mono">{evt.event_type}</span>
                <span className="text-[10px] text-slate-500">{new Date(evt.timestamp).toLocaleTimeString()}</span>
              </div>

              <div className="text-slate-400 text-[11px]">
                Actor: <strong className="text-slate-300">{evt.actor_id}</strong> ({evt.actor_type})
                {evt.previous_status && evt.new_status && (
                  <span className="ml-2 font-mono text-cyan-400">
                    {evt.previous_status} → {evt.new_status}
                  </span>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default OrderAuditTimeline;
