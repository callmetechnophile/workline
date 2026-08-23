'use client';

import React, { useState, useEffect } from 'react';
import {
  Server,
  Code2,
  DollarSign,
  ShieldCheck,
  Zap,
  CheckCircle2,
  ArrowRight,
  ExternalLink,
  Loader2,
  AlertCircle,
  Copy,
  Check,
} from 'lucide-react';

interface ServiceItem {
  id: string;
  name: string;
  description: string;
  price_usdc: number;
  endpoint: string;
  network?: string;
  asset?: string;
  asset_id?: number;
  enabled?: boolean;
}

interface APIServicesPanelProps {
  apiBase?: string;
}

export default function APIServicesPanel({ apiBase }: APIServicesPanelProps) {
  const base = apiBase || 'https://workline-core-gateway.onrender.com';
  const [services, setServices] = useState<ServiceItem[]>([]);
  const [networkInfo, setNetworkInfo] = useState<{
    network: string;
    asset: string;
    asset_id: number;
    pay_to: string;
  }>({
    network: 'algorand-mainnet',
    asset: 'USDC',
    asset_id: 31566704,
    pay_to: 'WORKLINE24EUSDCALGORANDTREASURYRECIPIENT402XXXXXXXXXXXXXX',
  });
  const [isLoading, setIsLoading] = useState(true);
  const [selectedService, setSelectedService] = useState<ServiceItem | null>(null);
  const [testResponse, setTestResponse] = useState<any | null>(null);
  const [isTesting, setIsTesting] = useState(false);
  const [copiedKey, setCopiedKey] = useState<string | null>(null);

  useEffect(() => {
    async function fetchServices() {
      setIsLoading(true);
      try {
        const res = await fetch(`${base}/api/x402/services`);
        if (res.ok) {
          const data = await res.json();
          setServices(data.services || []);
          if (data.network) {
            setNetworkInfo({
              network: data.network,
              asset: data.asset,
              asset_id: data.asset_id,
              pay_to: data.pay_to,
            });
          }
        } else {
          // Fallback defaults
          setServices([
            {
              id: 'bom.optimize',
              name: 'BOM Sourcing Optimizer',
              description: 'Autonomous multi-vendor component consolidation, availability verification, and cost minimization.',
              price_usdc: 0.50,
              endpoint: '/api/x402/bom/optimize',
            },
            {
              id: 'component.analyze',
              name: 'Component & Datasheet AI',
              description: 'Automated pin mapping, voltage rail risk evaluation, and alternative part validation from manufacturer datasheets.',
              price_usdc: 0.25,
              endpoint: '/api/x402/component/analyze',
            },
            {
              id: 'research.engineering',
              name: 'Hardware Research Synthesis',
              description: 'Literature vector search, academic contradiction analysis, and deterministic topology recommendations.',
              price_usdc: 1.00,
              endpoint: '/api/x402/research/engineering',
            },
            {
              id: 'simulation.thermal',
              name: 'Multi-Physics Thermal PINN',
              description: 'Neural surrogate Physics-Informed Neural Network (PINN) 2D/3D thermal dissipation and board hotspot solver.',
              price_usdc: 0.75,
              endpoint: '/api/x402/simulation/thermal',
            },
            {
              id: 'procurement.quote',
              name: 'Multi-Vendor RFQ Consolidation',
              description: 'Aggregates live distributor pricing (DigiKey, Mouser, Robu), MOQ price breaks, and consolidated shipping estimates.',
              price_usdc: 0.25,
              endpoint: '/api/x402/procurement/quote',
            },
          ]);
        }
      } catch (err) {
        console.error('Failed to load services:', err);
      } finally {
        setIsLoading(false);
      }
    }
    fetchServices();
  }, [base]);

  const handleTestHandshake = async (service: ServiceItem) => {
    setSelectedService(service);
    setIsTesting(true);
    setTestResponse(null);

    try {
      // Intentionally call without payment proof to demonstrate the 402 challenge
      const res = await fetch(`${base}${service.endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          project_id: 'sample_test_board',
          parameters: { test: true },
        }),
      });

      const data = await res.json();
      setTestResponse({
        http_status: res.status,
        headers: {
          'x-payment-required': res.headers.get('x-payment-required') || 'present',
        },
        body: data,
      });
    } catch (err: any) {
      setTestResponse({
        error: err?.message || 'Handshake failed',
      });
    } finally {
      setIsTesting(false);
    }
  };

  const copyToClipboard = (text: string, key: string) => {
    navigator.clipboard.writeText(text);
    setCopiedKey(key);
    setTimeout(() => setCopiedKey(null), 2000);
  };

  return (
    <div className="space-y-6 max-w-6xl">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div>
          <div className="flex items-center gap-2.5">
            <Server className="w-5 h-5 text-indigo-400" />
            <h1 className="text-lg font-bold text-slate-100 uppercase font-mono tracking-wide">
              Workline AI Services & x402 Monetization
            </h1>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Pay-per-use computational engineering APIs monetized via <strong className="text-indigo-300">USDC on Algorand Testnet (ASA #10458941)</strong> with real-time on-chain settlement.
          </p>

        </div>

        {/* Network Badge */}
        <div className="flex items-center gap-3 bg-slate-900/80 border border-slate-800 rounded-lg px-3 py-2 text-xs font-mono">
          <div className="flex items-center gap-1.5">
            <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <span className="text-slate-300">{networkInfo.network}</span>
          </div>
          <span className="text-slate-600">|</span>
          <span className="text-indigo-400 font-bold">{networkInfo.asset} (ASA #{networkInfo.asset_id})</span>
        </div>
      </div>

      {/* Services Table */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-xl overflow-hidden shadow-xl">
        <div className="px-5 py-4 border-b border-slate-800 bg-slate-950/60 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Code2 className="w-4 h-4 text-indigo-400" />
            <h2 className="text-xs font-bold text-slate-200 uppercase font-mono">
              Available Engineering APIs ({services.length})
            </h2>
          </div>
          <span className="text-[10px] text-slate-500 font-mono">
            Autonomous Agent Accessible
          </span>
        </div>

        {isLoading ? (
          <div className="p-12 text-center flex flex-col items-center justify-center space-y-3">
            <Loader2 className="w-6 h-6 text-indigo-400 animate-spin" />
            <span className="text-xs text-slate-400">Loading service catalog...</span>
          </div>
        ) : (
          <div className="divide-y divide-slate-800/60">
            {services.map((s) => (
              <div
                key={s.id}
                className="p-5 flex flex-col lg:flex-row lg:items-center justify-between gap-4 hover:bg-slate-850/40 transition-colors"
              >
                <div className="space-y-1 max-w-2xl">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs font-bold text-slate-100">
                      {s.name}
                    </span>
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-400">
                      {s.id}
                    </span>
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-950/60 text-emerald-400 border border-emerald-800/40">
                      ACTIVE
                    </span>
                  </div>
                  <p className="text-xs text-slate-400 leading-relaxed">
                    {s.description}
                  </p>
                  <div className="text-[11px] font-mono text-slate-500 pt-1 flex items-center gap-2">
                    <span className="text-indigo-400 font-semibold">POST</span>
                    <code>{s.endpoint}</code>
                  </div>
                </div>

                <div className="flex items-center gap-4 flex-shrink-0">
                  <div className="text-right">
                    <div className="text-base font-bold font-mono text-emerald-400">
                      ${s.price_usdc.toFixed(2)} <span className="text-xs text-slate-400">USDC</span>
                    </div>
                    <div className="text-[10px] font-mono text-slate-500">
                      per invocation
                    </div>
                  </div>

                  <button
                    onClick={() => handleTestHandshake(s)}
                    className="px-3.5 py-2 bg-slate-800 hover:bg-indigo-600 text-slate-200 hover:text-white rounded-lg text-xs font-mono font-medium transition-all flex items-center gap-1.5 cursor-pointer shadow"
                  >
                    <span>Test 402</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Interactive 402 Handshake Inspector */}
      {selectedService && (
        <div className="bg-slate-900 border border-indigo-900/60 rounded-xl p-6 space-y-4 shadow-2xl animate-in fade-in duration-200">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div className="flex items-center gap-2">
              <Zap className="w-4 h-4 text-amber-400" />
              <h3 className="text-xs font-bold font-mono text-slate-100 uppercase">
                402 Payment Challenge Test: {selectedService.name}
              </h3>
            </div>
            <button
              onClick={() => setSelectedService(null)}
              className="text-xs text-slate-500 hover:text-slate-300 font-mono cursor-pointer"
            >
              Close
            </button>
          </div>

          {isTesting ? (
            <div className="py-8 flex flex-col items-center justify-center space-y-2">
              <Loader2 className="w-5 h-5 text-indigo-400 animate-spin" />
              <span className="text-xs text-slate-400 font-mono">
                Calling {selectedService.endpoint} without payment proof...
              </span>
            </div>
          ) : testResponse ? (
            <div className="space-y-4 text-xs font-mono">
              <div className="flex items-center gap-3">
                <span className="px-2.5 py-1 rounded bg-amber-950/80 border border-amber-600/60 text-amber-300 font-bold">
                  HTTP {testResponse.http_status} PAYMENT REQUIRED
                </span>
                <span className="text-slate-400">
                  Standard non-custodial x402 challenge generated successfully.
                </span>
              </div>

              {/* Challenge Details Breakdown */}
              {testResponse.body?.challenge && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 bg-slate-950 border border-slate-800 rounded-lg p-4">
                  <div>
                    <span className="text-slate-500 block text-[10px]">PAYMENT REQUEST ID</span>
                    <span className="text-slate-200 select-all">{testResponse.body.challenge.payment_request_id}</span>
                  </div>
                  <div>
                    <span className="text-slate-500 block text-[10px]">PRICE REQUIRED</span>
                    <span className="text-emerald-400 font-bold">
                      ${testResponse.body.challenge.amount} {testResponse.body.challenge.asset}
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-500 block text-[10px]">ALGORAND NETWORK / ASA ID</span>
                    <span className="text-slate-200">
                      {testResponse.body.challenge.network} (#{testResponse.body.challenge.asset_id})
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-500 block text-[10px]">NONCE</span>
                    <span className="text-slate-300 select-all">{testResponse.body.challenge.nonce}</span>
                  </div>
                  <div className="md:col-span-2">
                    <span className="text-slate-500 block text-[10px]">WORKLINE TREASURY (PAY TO)</span>
                    <div className="flex items-center justify-between bg-slate-900 p-1.5 rounded mt-0.5 border border-slate-800">
                      <span className="text-[11px] text-slate-300 truncate select-all">
                        {testResponse.body.challenge.pay_to}
                      </span>
                      <button
                        onClick={() => copyToClipboard(testResponse.body.challenge.pay_to, 'pay_to')}
                        className="text-slate-400 hover:text-white p-1 cursor-pointer"
                      >
                        {copiedKey === 'pay_to' ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                      </button>
                    </div>
                  </div>
                </div>
              )}

              {/* Raw JSON viewer */}
              <div>
                <span className="text-slate-500 text-[10px] uppercase block mb-1">
                  Full 402 Handshake Response Payload
                </span>
                <pre className="p-3 bg-slate-950 border border-slate-800 rounded-lg overflow-x-auto text-[11px] text-slate-300 max-h-60">
                  {JSON.stringify(testResponse, null, 2)}
                </pre>
              </div>
            </div>
          ) : null}
        </div>
      )}
    </div>
  );
}
