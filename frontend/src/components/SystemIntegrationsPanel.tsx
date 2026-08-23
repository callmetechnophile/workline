'use client';

import React from 'react';
import { Blocks, CheckCircle2, AlertCircle, Database, Shield, GitBranch, Layers, Lock, Cpu, Sparkles, Image as ImageIcon } from 'lucide-react';

export default function SystemIntegrationsPanel() {
  const integrations = [
    {
      name: 'Amazon Bedrock AI Engine',
      category: 'Model Inference (R2)',
      status: 'Connected',
      type: 'DeepSeek V3 / Claude Haiku / Claude Sonnet / Nova Canvas',
      isSecure: true,
      desc: 'Centralized model execution across research, fast code generation, multi-physics reasoning, and engineering visuals.',
    },
    {
      name: 'Algorand Testnet x402 Engine',
      category: 'Payment Protocol (R5)',
      status: 'Active (Testnet)',
      type: 'On-Chain Algod Settlement (USDC: 10458941)',
      isSecure: true,
      desc: 'Authoritative machine-to-machine payment verification and BOM quote settlement on Algorand Testnet with Pera Wallet signing.',
    },

    {
      name: 'PaperBanana Visual Synthesis',
      category: 'Engineering Diagram Engine (R2)',
      status: 'Active',
      type: 'Bedrock Nova Canvas & SVG Synthesis',
      isSecure: true,
      desc: 'Automated architectural block diagrams, power distribution networks, and PCB schematics.',
    },
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
      name: 'DigiKey & Mouser Supplier APIs',
      category: 'Procurement (R5)',
      status: 'Active',
      type: 'Vendor Catalog & Real-time Stock',
      isSecure: true,
      desc: 'Live pricing, tiered volume discounts, and global warehouse stock feeds.',
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
        <h2 className="text-base font-bold text-slate-100">System Integrations & AI Architecture</h2>
        <p className="text-xs text-slate-400">
          Connected cloud databases, Amazon Bedrock AI inference, Algorand x402 payment facilitators, and supplier APIs.
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
              <span className="truncate max-w-[70%]">{item.type}</span>
              {item.isSecure && (
                <span className="flex items-center gap-1 text-slate-400 flex-shrink-0">
                  <Lock className="w-3 h-3 text-slate-500" />
                  <span>Isolated</span>
                </span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
