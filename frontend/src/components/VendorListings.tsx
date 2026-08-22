"use client";

import React from "react";
import { 
  Store, 
  ExternalLink, 
  CheckCircle2, 
  Clock, 
  MapPin, 
  AlertCircle 
} from "lucide-react";

interface Listing {
  listing_id: string;
  vendor_name: string;
  product_url: string;
  unit_price?: number;
  currency: string;
  stock?: number;
  in_stock: boolean;
  lead_time_days?: number;
  location?: string;
  freshness: string;
  retrieved_at: string;
}

interface VendorListingsProps {
  mpn: string;
  listings: Listing[];
}

export const VendorListings: React.FC<VendorListingsProps> = ({ mpn, listings = [] }) => {
  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 shadow-2xl backdrop-blur-md space-y-4">
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-yellow-500/10 border border-yellow-500/20 rounded-lg text-yellow-400">
            <Store className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-semibold text-slate-100">Live Vendor Sourcing</h3>
            <p className="text-xs text-slate-400 font-mono">MPN: {mpn}</p>
          </div>
        </div>
        <span className="text-xs text-slate-400 font-medium">
          {listings.length} {listings.length === 1 ? "source" : "sources"}
        </span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {listings.map((l, idx) => (
          <div key={idx} className="bg-slate-950/60 p-3.5 rounded-lg border border-slate-800 flex flex-col justify-between space-y-2">
            <div className="flex items-center justify-between">
              <span className="font-semibold text-slate-200 text-xs">{l.vendor_name}</span>
              <span className="inline-flex items-center gap-1 text-[10px] font-mono text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
                {l.freshness}
              </span>
            </div>

            <div className="flex items-baseline justify-between">
              <span className="text-base font-bold text-slate-100">
                {l.currency} {l.unit_price ? l.unit_price.toFixed(2) : "Contact Vendor"}
              </span>
              <span className="text-xs text-slate-400">
                {l.in_stock ? (
                  <span className="text-emerald-400 font-medium">{l.stock ? `${l.stock} in stock` : "In Stock"}</span>
                ) : (
                  <span className="text-rose-400">Out of Stock</span>
                )}
              </span>
            </div>

            <div className="flex items-center justify-between text-[11px] text-slate-400 pt-2 border-t border-slate-800/50">
              <span className="flex items-center gap-1">
                <MapPin className="w-3 h-3 text-slate-500" /> {l.location || "Global"}
              </span>
              <a
                href={l.product_url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-cyan-400 hover:text-cyan-300 inline-flex items-center gap-1 font-medium"
              >
                View Listing <ExternalLink className="w-3 h-3" />
              </a>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default VendorListings;
