'use client';

import React from 'react';
import { Blocks, CheckCircle2, AlertCircle, Database, Shield, GitBranch, Layers, Lock } from 'lucide-react';

export default function SystemIntegrationsPanel() {
  const integrations = [
    {
      name: 'Qdrant Cloud Vector Database',
      category: 'Knowledge Infrastructure (R3)',
      status: 'Connected',
      type: 'Managed Cloud Cluster',
      isSecure: true,
      desc: 'High-dimensional embeddings for 100k+ component datasheets and research literature.',
    },
    {
      name: 'SurrealDB Cloud Knowledge Graph',
      category: 'Knowledge Infrastructure (R3)',
      status: 'Connected',
      type: 'Graph & Relational Engine',
      isSecure: true,
      desc: 'Component taxonomy, pinout relationships, and architectural dependency links.',
    },
    {
      name: 'Clerk Authentication & Session Security',
      category: 'Identity & Access',
      status: 'Connected',
      type: 'OAuth & JWT Tokens',
      isSecure: true,
      desc: 'Cryptographic session management with multi-factor authentication.',
    },
    {
      name: 'DigiKey & Mouser Supplier APIs',
      category: 'Procurement (R5)',
      status: 'Active',
      type: 'Vendor Catalog & Real-time Stock',
      isSecure: true,
      desc: 'Live pricing, tiered volume discounts, and global warehouse stock feeds.',
    },
    {
      name: 'Base Sepolia x402 Facilitator',
      category: 'Payment Protocol (R5)',
      status: 'Active (Testnet)',
      type: 'Non-Custodial Cryptographic Escrow',
      isSecure: true,
      desc: 'Autonomous machine-to-machine payment verification and order challenge settlement.',
    },
    {
      name: 'GitHub Repository Sync',
      category: 'Version Control',
      status: 'Connected',
      type: 'callmetechnophile/workline',
      isSecure: true,
      desc: 'Continuous deployment pipelines, release tags, and automated verification.',
    },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-base font-bold text-slate-100">System Integrations & External Services</h2>
        <p className="text-xs text-slate-400">
          Connected cloud databases, supplier APIs, and authentication providers powering Workline AI.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {integrations.map((item, idx) => (
          <div
            key={idx}
            className="bg-slate-900/90 border border-slate-800 rounded-lg p-5 space-y-3"
          >
            <div className="flex items-start justify-between">
              <div>
                <span className="text-[10px] font-mono font-bold text-indigo-400 uppercase">
                  {item.category}
                </span>
                <h3 className="text-xs font-bold text-slate-200 mt-0.5">{item.name}</h3>
              </div>
              <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-mono bg-emerald-950/60 border border-emerald-800/40 text-emerald-400">
                <CheckCircle2 className="w-3 h-3" />
                <span>{item.status}</span>
              </span>
            </div>

            <p className="text-[11px] text-slate-400 leading-relaxed">
              {item.desc}
            </p>

            <div className="pt-2 border-t border-slate-850 flex items-center justify-between text-[10px] font-mono text-slate-500">
              <span>{item.type}</span>
              {item.isSecure && (
                <span className="flex items-center gap-1 text-slate-400">
                  <Lock className="w-3 h-3 text-slate-500" />
                  <span>Secrets Isolated</span>
                </span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
