"use client";

import React from "react";
import { Store, Tag, Clock, PackageCheck } from "lucide-react";

export interface SupplierOfferItem {
  supplier: string;
  sku: string;
  unitPrice: number;
  breaks: Array<{ qty: number; price: number }>;
  stock: number;
  leadTimeDays?: number;
  moq: number;
  isPreferred?: boolean;
}

export interface SupplierOffersProps {
  partNumber?: string;
  offers?: SupplierOfferItem[];
  onSelectOffer?: (supplier: string) => void;
}

export const SupplierOffers: React.FC<SupplierOffersProps> = ({
  partNumber,
  offers = [],
  onSelectOffer,
}) => {
  if (!offers || (Array.isArray(offers) && offers.length === 0)) {
    return (
      <div className="bg-slate-900/60 border border-slate-800 rounded-lg p-8 text-center">
        <Store className="w-8 h-8 text-slate-600 mx-auto mb-2" />
        <p className="text-xs text-slate-400">No supplier offers available.</p>
        <p className="text-[10px] text-slate-500 mt-1">Create or select a project to view supplier offers.</p>
      </div>
    );
  }

  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-5 flex flex-col gap-4 text-zinc-100">
      <div className="flex items-center gap-2 pb-2 border-b border-zinc-800">
        <Store className="w-5 h-5 text-indigo-400" />
        <h3 className="text-base font-bold text-zinc-100">
          Supplier Offers{partNumber ? `: ${partNumber}` : ""}
        </h3>
      </div>

      <div className="grid grid-cols-2 gap-4">
        {offers.map((offer) => (
          <div
            key={offer.supplier}
            onClick={() => onSelectOffer && onSelectOffer(offer.supplier)}
            className={`p-4 rounded-lg border flex flex-col gap-3 cursor-pointer transition ${
              offer.isPreferred
                ? "bg-indigo-950/20 border-indigo-800/80"
                : "bg-zinc-950/60 border-zinc-800 hover:border-zinc-700"
            }`}
          >
            <div className="flex items-center justify-between">
              <span className="font-bold text-zinc-100">{offer.supplier}</span>
              <span className="text-xs font-mono text-emerald-400 font-bold">₹{offer.unitPrice.toFixed(2)} / unit</span>
            </div>

            <div className="flex flex-col gap-1 text-xs font-mono text-zinc-400">
              <div className="flex justify-between">
                <span>SKU:</span>
                <span className="text-zinc-200">{offer.sku}</span>
              </div>
              <div className="flex justify-between">
                <span>Stock:</span>
                <span className="text-emerald-400 font-bold">{offer.stock} pcs</span>
              </div>
              <div className="flex justify-between">
                <span>Lead Time:</span>
                <span className="text-zinc-200">~{offer.leadTimeDays || 3} days</span>
              </div>
              <div className="flex justify-between">
                <span>MOQ:</span>
                <span className="text-zinc-200">{offer.moq} pcs</span>
              </div>
            </div>

            <div className="p-2 bg-zinc-900/90 rounded border border-zinc-800/60 text-[11px] font-mono">
              <span className="text-zinc-500 block mb-1">Volume Pricing Breaks:</span>
              <div className="flex items-center gap-2">
                {offer.breaks.map((b) => (
                  <span key={b.qty} className="text-zinc-300">
                    {b.qty}+: <strong className="text-emerald-400">₹{b.price}</strong>
                  </span>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
