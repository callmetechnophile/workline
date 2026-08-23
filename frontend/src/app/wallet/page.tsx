'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useAuth } from '@clerk/nextjs';
import {
  Wallet,
  ShieldCheck,
  Zap,
  CheckCircle2,
  Clock,
  AlertCircle,
  ExternalLink,
  Copy,
  Check,
  RefreshCw,
  ArrowLeft,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';
import { peraWallet, WalletConnectionState, PeraSignedPaymentProof } from '@/lib/peraWallet';

export type PaymentFlowState =
  | 'DISCONNECTED'
  | 'CONNECTED'
  | 'READY'
  | 'REQUESTING_PAYMENT'
  | 'WAITING_FOR_WALLET'
  | 'PAYMENT_SIGNED'
  | 'VERIFYING'
  | 'SETTLING'
  | 'SETTLED'
  | 'FAILED'
  | 'USER_REJECTED';

interface SettledPaymentResult {
  success: boolean;
  service_id: string;
  service_name: string;
  payment: {
    status: string;
    network: string;
    asset: string;
    asset_id: number;
    amount_usdc: number;
    payer: string;
    pay_to: string;
    transaction_id: string;
    settled_at: string;
    explorer_url?: string;
  };
  result?: any;
}

interface PaymentHistoryItem {
  id: string;
  payment_request_id: string;
  service_id: string;
  amount: number;
  asset: string;
  network: string;
  transaction_id?: string;
  status: string;
  created_at: string;
  settled_at?: string;
}

export default function WalletPage() {
  const { isSignedIn, isLoaded } = useAuth();

  // Wallet Connection State
  const [walletState, setWalletState] = useState<WalletConnectionState>(peraWallet.getState());
  const [walletAddress, setWalletAddress] = useState<string | null>(peraWallet.getAddress());
  const [walletError, setWalletError] = useState<string | null>(null);

  // Payment Flow State Machine
  const [flowState, setFlowState] = useState<PaymentFlowState>('DISCONNECTED');
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [paymentResult, setPaymentResult] = useState<SettledPaymentResult | null>(null);
  const [rawChallenge, setRawChallenge] = useState<any | null>(null);
  const [signedProof, setSignedProof] = useState<PeraSignedPaymentProof | null>(null);

  // UI state
  const [detailsExpanded, setDetailsExpanded] = useState(false);
  const [copiedTx, setCopiedTx] = useState(false);
  const [copiedAddress, setCopiedAddress] = useState(false);

  // Payment history
  const [history, setHistory] = useState<PaymentHistoryItem[]>([]);
  const [historyLoading, setHistoryLoading] = useState(false);

  // Resolve API Base
  const apiBase =
    typeof window !== 'undefined'
      ? process.env.NEXT_PUBLIC_API_URL || (window.location.port === '3000' ? 'http://localhost:8000' : '')
      : '';

  // Network info
  const targetNetwork = 'Algorand Testnet';
  const targetAsset = 'USDC';
  const targetAssetId = 10458941;
  const testPriceUsdc = 0.01;

  // Subscribe to Pera Wallet client
  useEffect(() => {
    const unsub = peraWallet.subscribe((state, address) => {
      setWalletState(state);
      setWalletAddress(address);
      if (state === 'CONNECTED' && address) {
        setFlowState((prev) => (prev === 'SETTLED' ? 'SETTLED' : 'READY'));
      } else if (state === 'DISCONNECTED') {
        setFlowState('DISCONNECTED');
      }
    });
    return () => unsub();
  }, []);

  // Fetch payment history
  const loadPaymentHistory = async () => {
    setHistoryLoading(true);
    try {
      const res = await fetch(`${apiBase}/api/x402/payments`);
      if (res.ok) {
        const data = await res.json();
        setHistory(data.payments || []);
      }
    } catch {
      // Ignore background history failure
    } finally {
      setHistoryLoading(false);
    }
  };

  useEffect(() => {
    loadPaymentHistory();
  }, [apiBase]);

  // Connect Pera Wallet
  const handleConnect = async () => {
    setWalletError(null);
    setErrorMessage(null);
    try {
      await peraWallet.connect();
    } catch (err: any) {
      setWalletError(err?.message || 'Failed to connect Pera Wallet.');
    }
  };

  // Disconnect Pera Wallet
  const handleDisconnect = async () => {
    await peraWallet.disconnect();
    setFlowState('DISCONNECTED');
    setPaymentResult(null);
    setSignedProof(null);
  };

  // Copy helper
  const copyToClipboard = (text: string, type: 'tx' | 'address') => {
    if (typeof navigator !== 'undefined') {
      navigator.clipboard.writeText(text);
      if (type === 'tx') {
        setCopiedTx(true);
        setTimeout(() => setCopiedTx(false), 2500);
      } else {
        setCopiedAddress(true);
        setTimeout(() => setCopiedAddress(false), 2500);
      }
    }
  };

  const handlePayTestService = async () => {
    if (!walletAddress || walletState !== 'CONNECTED') {
      setErrorMessage('Please connect your Pera Wallet first.');
      return;
    }

    setErrorMessage(null);
    setPaymentResult(null);
    setFlowState('REQUESTING_PAYMENT');

    try {
      // Step 1: Initial Request (Expects REAL HTTP 402)
      const initialRes = await fetch(`${apiBase}/api/x402/demo`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (initialRes.status !== 402) {
        throw new Error(`Expected HTTP 402 challenge from server, but received HTTP ${initialRes.status}`);
      }

      const challengeJson = await initialRes.json();
      const challenge = challengeJson.challenge;
      if (!challenge) {
        throw new Error('Malformed 402 challenge: Missing challenge metadata.');
      }
      setRawChallenge(challenge);

      // Step 2: Prompt Pera Wallet for Signature
      setFlowState('WAITING_FOR_WALLET');

      const proof = await peraWallet.signPaymentTransaction({
        quote_id: challenge.payment_request_id,
        payment_request_id: challenge.payment_request_id,
        amount_usdc: challenge.amount || testPriceUsdc,
        asset_id: challenge.asset_id || targetAssetId,
        network: challenge.network || 'algorand-testnet',
        pay_to: challenge.pay_to,
      });

      setSignedProof(proof);
      setFlowState('PAYMENT_SIGNED');

      // Step 3: Automatic Retry with Payment Proof
      setFlowState('VERIFYING');

      const retryRes = await fetch(`${apiBase}/api/x402/demo`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'X-PAYMENT': JSON.stringify({
            payment_request_id: challenge.payment_request_id,
            tx_hash: proof.tx_hash,
            signature: proof.signature,
            payer_address: proof.payer,
          }),
        },
      });

      if (!retryRes.ok) {
        const errData = await retryRes.json().catch(() => null);
        throw new Error(errData?.detail || `Payment verification failed (HTTP ${retryRes.status})`);
      }

      // Step 4: Settle & Deliver Paid Result
      setFlowState('SETTLING');
      const settledData = await retryRes.json();

      setPaymentResult({
        success: true,
        service_id: settledData.service_id || 'workline.test.verified',
        service_name: 'Workline Verified Engineering Service',
        payment: {
          status: settledData.payment?.status || 'SETTLED',
          network: settledData.payment?.network || 'algorand-testnet',
          asset: settledData.payment?.asset || 'USDC',
          asset_id: targetAssetId,
          amount_usdc: settledData.payment?.amount_usdc || testPriceUsdc,
          payer: proof.payer,
          pay_to: challenge.pay_to,
          transaction_id: settledData.payment?.tx_hash || proof.tx_hash,
          settled_at: settledData.payment?.settled_at || new Date().toISOString(),
          explorer_url: `https://lora.algokit.io/testnet/transaction/${settledData.payment?.tx_hash || proof.tx_hash}`,
        },
        result: settledData.result,
      });

      setFlowState('SETTLED');
      loadPaymentHistory();
    } catch (err: any) {
      if (err?.message?.includes('rejected') || err?.message?.includes('cancelled')) {
        setFlowState('USER_REJECTED');
        setErrorMessage('Payment signature was cancelled in Pera Wallet.');
      } else {
        setFlowState('FAILED');
        setErrorMessage(err?.message || 'Payment settlement failed.');
      }
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-mono flex flex-col justify-between">
      {/* Top Header */}
      <header className="h-14 border-b border-slate-800 bg-slate-950/80 backdrop-blur-md px-6 flex items-center justify-between sticky top-0 z-20">
        <div className="flex items-center gap-3">
          <Link
            href="/"
            className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-white transition-colors cursor-pointer"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Workbench</span>
          </Link>
          <span className="text-slate-700">|</span>
          <div className="flex items-center gap-2">
            <Wallet className="w-4 h-4 text-cyan-400" />
            <span className="font-bold text-xs uppercase tracking-wider text-slate-200">
              Workline Wallet & Payments
            </span>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <span className="px-2 py-0.5 rounded bg-emerald-950/60 border border-emerald-800/40 text-[10px] text-emerald-400 font-bold">
            Algorand Testnet
          </span>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 max-w-4xl w-full mx-auto p-6 space-y-6">
        {/* Title / Description */}
        <div className="space-y-1">
          <h1 className="text-xl font-bold tracking-tight text-white uppercase flex items-center gap-2">
            <span>Workline Wallet</span>
            <span className="text-xs px-2 py-0.5 rounded bg-cyan-950/60 border border-cyan-800/40 text-cyan-400 font-normal">
              x402 Protocol
            </span>
          </h1>
          <p className="text-xs text-slate-400">
            Connect Pera Wallet to make verified x402 payments on Algorand.
          </p>
        </div>

        {/* Global Error Banner */}
        {(walletError || errorMessage) && (
          <div className="bg-rose-950/40 border border-rose-800/60 rounded-xl p-4 text-xs text-rose-300 flex items-start gap-3">
            <AlertCircle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
            <div className="space-y-1 flex-1">
              <span className="font-bold uppercase tracking-wide block">
                {flowState === 'USER_REJECTED' ? 'Payment Cancelled' : 'Payment Notification'}
              </span>
              <p className="text-rose-200/90">{walletError || errorMessage}</p>
            </div>
            <button
              onClick={() => {
                setWalletError(null);
                setErrorMessage(null);
              }}
              className="text-rose-400 hover:text-white text-xs cursor-pointer"
            >
              Dismiss
            </button>
          </div>
        )}

        {/* Connection Card */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 shadow-xl space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div className="flex items-center gap-2.5">
              <div className="p-2 bg-cyan-500/10 border border-cyan-500/20 rounded-lg text-cyan-400">
                <Wallet className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200">
                  {walletState === 'CONNECTED' ? 'Wallet Connected' : 'Connect Your Wallet'}
                </h3>
                <span className="text-[10px] text-slate-400">Network: {targetNetwork}</span>
              </div>
            </div>

            {walletState === 'CONNECTED' ? (
              <span className="flex items-center gap-1.5 text-[11px] font-bold text-emerald-400 bg-emerald-950/60 border border-emerald-800/60 px-2.5 py-1 rounded">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                CONNECTED
              </span>
            ) : (
              <span className="text-[11px] text-slate-500 font-bold uppercase">DISCONNECTED</span>
            )}
          </div>

          {walletState === 'CONNECTED' && walletAddress ? (
            <div className="space-y-3">
              <div className="bg-slate-950/80 p-3 rounded-lg border border-slate-800 flex items-center justify-between">
                <div className="space-y-0.5 truncate pr-3">
                  <span className="text-[10px] text-slate-500 uppercase">Pera Wallet Address</span>
                  <div className="text-xs text-slate-200 font-bold truncate select-all">{walletAddress}</div>
                </div>
                <button
                  onClick={() => copyToClipboard(walletAddress, 'address')}
                  className="px-2.5 py-1.5 bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-300 rounded text-[11px] flex items-center gap-1 cursor-pointer transition shrink-0"
                >
                  {copiedAddress ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                  <span>{copiedAddress ? 'Copied' : 'Copy'}</span>
                </button>
              </div>

              <div className="flex justify-end">
                <button
                  onClick={handleDisconnect}
                  className="text-xs px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded border border-slate-700 transition cursor-pointer font-bold"
                >
                  Disconnect Wallet
                </button>
              </div>
            </div>
          ) : (
            <div className="space-y-3">
              <p className="text-xs text-slate-400 leading-relaxed">
                Connect your Pera Wallet on Algorand Testnet to test micro-payments and verify autonomous agent settlements.
              </p>
              <button
                onClick={handleConnect}
                disabled={walletState === 'CONNECTING'}
                className="w-full py-2.5 px-4 bg-cyan-600 hover:bg-cyan-500 text-white font-bold text-xs rounded-lg transition flex items-center justify-center gap-2 cursor-pointer shadow-lg"
              >
                {walletState === 'CONNECTING' ? (
                  <>
                    <RefreshCw className="w-4 h-4 animate-spin" />
                    <span>Connecting Pera Wallet...</span>
                  </>
                ) : (
                  <>
                    <Wallet className="w-4 h-4" />
                    <span>Connect Pera Wallet</span>
                  </>
                )}
              </button>
            </div>
          )}
        </div>

        {/* x402 Test Execution Card */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 shadow-xl space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div className="flex items-center gap-2.5">
              <div className="p-2 bg-yellow-500/10 border border-yellow-500/20 rounded-lg text-yellow-400">
                <Zap className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200">
                  x402 Payment Test
                </h3>
                <span className="text-[10px] text-slate-400">
                  Workline Verified Engineering Service
                </span>
              </div>
            </div>
            <span className="text-xs font-bold text-cyan-400 bg-cyan-950/40 border border-cyan-800/40 px-2.5 py-1 rounded">
              0.01 USDC
            </span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div className="bg-slate-950/80 p-3 rounded-lg border border-slate-800 space-y-0.5">
              <span className="text-[10px] text-slate-500 uppercase">Service</span>
              <div className="text-xs font-bold text-slate-200 truncate">Verified Service</div>
            </div>
            <div className="bg-slate-950/80 p-3 rounded-lg border border-slate-800 space-y-0.5">
              <span className="text-[10px] text-slate-500 uppercase">Price</span>
              <div className="text-xs font-bold text-cyan-400">0.01 USDC</div>
            </div>
            <div className="bg-slate-950/80 p-3 rounded-lg border border-slate-800 space-y-0.5">
              <span className="text-[10px] text-slate-500 uppercase">Network</span>
              <div className="text-xs font-bold text-slate-200">Testnet</div>
            </div>
            <div className="bg-slate-950/80 p-3 rounded-lg border border-slate-800 space-y-0.5">
              <span className="text-[10px] text-slate-500 uppercase">Asset ID</span>
              <div className="text-xs font-bold text-slate-400">{targetAssetId}</div>
            </div>
          </div>

          {/* Payment Action Button */}
          {flowState !== 'SETTLED' ? (
            <div className="space-y-3 pt-2">
              <button
                onClick={handlePayTestService}
                disabled={
                  walletState !== 'CONNECTED' ||
                  flowState === 'REQUESTING_PAYMENT' ||
                  flowState === 'WAITING_FOR_WALLET' ||
                  flowState === 'VERIFYING' ||
                  flowState === 'SETTLING'
                }
                className={`w-full py-3 px-4 font-bold text-xs rounded-lg transition flex items-center justify-center gap-2 ${
                  walletState === 'CONNECTED' &&
                  flowState !== 'REQUESTING_PAYMENT' &&
                  flowState !== 'WAITING_FOR_WALLET' &&
                  flowState !== 'VERIFYING' &&
                  flowState !== 'SETTLING'
                    ? 'bg-gradient-to-r from-cyan-600 to-emerald-600 hover:from-cyan-500 hover:to-emerald-500 text-white shadow-lg cursor-pointer'
                    : 'bg-slate-800 text-slate-500 cursor-not-allowed border border-slate-700'
                }`}
              >
                {flowState === 'REQUESTING_PAYMENT' ? (
                  <>
                    <RefreshCw className="w-4 h-4 animate-spin" />
                    <span>Requesting HTTP 402 Challenge...</span>
                  </>
                ) : flowState === 'WAITING_FOR_WALLET' ? (
                  <>
                    <Clock className="w-4 h-4 animate-pulse text-amber-400" />
                    <span>Approve 0.01 USDC in Pera Wallet...</span>
                  </>
                ) : flowState === 'PAYMENT_SIGNED' || flowState === 'VERIFYING' ? (
                  <>
                    <RefreshCw className="w-4 h-4 animate-spin text-cyan-400" />
                    <span>Verifying with GoPlausible Facilitator...</span>
                  </>
                ) : flowState === 'SETTLING' ? (
                  <>
                    <RefreshCw className="w-4 h-4 animate-spin text-emerald-400" />
                    <span>Waiting for Algorand Testnet Settlement...</span>
                  </>
                ) : walletState !== 'CONNECTED' ? (
                  <>
                    <Wallet className="w-4 h-4" />
                    <span>Connect Pera Wallet to Pay</span>
                  </>
                ) : (
                  <>
                    <ShieldCheck className="w-4 h-4" />
                    <span>Pay 0.01 USDC via x402</span>
                  </>
                )}
              </button>
            </div>
          ) : (
            /* Settlement Success Banner */
            paymentResult && (
              <div className="space-y-4 pt-2">
                <div className="p-4 bg-emerald-950/40 border border-emerald-700/60 rounded-xl space-y-3">
                  <div className="flex items-center justify-between border-b border-emerald-800/40 pb-2">
                    <div className="flex items-center gap-2 text-emerald-400 font-bold text-sm">
                      <CheckCircle2 className="w-5 h-5" />
                      <span>✓ PAYMENT SETTLED</span>
                    </div>
                    <span className="text-[10px] text-emerald-300 font-mono">
                      Algorand Testnet USDC
                    </span>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
                    <div>
                      <span className="text-[10px] text-slate-500 uppercase block">Service</span>
                      <span className="text-slate-200 font-bold">{paymentResult.service_name}</span>
                    </div>
                    <div>
                      <span className="text-[10px] text-slate-500 uppercase block">Amount</span>
                      <span className="text-emerald-400 font-bold">
                        {paymentResult.payment.amount_usdc.toFixed(2)} USDC
                      </span>
                    </div>
                    <div>
                      <span className="text-[10px] text-slate-500 uppercase block">Payer</span>
                      <span className="text-slate-300 font-bold truncate block select-all">
                        {paymentResult.payment.payer}
                      </span>
                    </div>
                    <div>
                      <span className="text-[10px] text-slate-500 uppercase block">Recipient</span>
                      <span className="text-slate-300 font-bold truncate block select-all">
                        {paymentResult.payment.pay_to}
                      </span>
                    </div>
                  </div>

                  <div className="bg-slate-950/90 p-3 rounded-lg border border-emerald-900/60 space-y-1">
                    <span className="text-[10px] text-slate-500 uppercase block">
                      Real Algorand Transaction ID
                    </span>
                    <div className="flex items-center justify-between gap-2">
                      <span className="text-xs text-cyan-400 font-bold truncate select-all">
                        {paymentResult.payment.transaction_id}
                      </span>
                      <button
                        onClick={() => copyToClipboard(paymentResult.payment.transaction_id, 'tx')}
                        className="px-2 py-1 bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-300 rounded text-[10px] flex items-center gap-1 cursor-pointer transition shrink-0"
                      >
                        {copiedTx ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                        <span>{copiedTx ? 'Copied' : 'Copy'}</span>
                      </button>
                    </div>
                  </div>

                  <div className="text-[10px] text-slate-500">
                    Settled At: {new Date(paymentResult.payment.settled_at).toLocaleString()}
                  </div>

                  <div className="flex flex-wrap gap-2 pt-1">
                    {paymentResult.payment.explorer_url && (
                      <a
                        href={paymentResult.payment.explorer_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="px-3 py-1.5 bg-cyan-600 hover:bg-cyan-500 text-white rounded text-xs font-bold flex items-center gap-1.5 transition shadow"
                      >
                        <ExternalLink className="w-3.5 h-3.5" />
                        <span>View on Algorand Explorer</span>
                      </a>
                    )}
                    <button
                      onClick={() => setFlowState('READY')}
                      className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded text-xs font-bold transition border border-slate-700 cursor-pointer"
                    >
                      Back to Wallet
                    </button>
                  </div>
                </div>
              </div>
            )
          )}
        </div>

        {/* Collapsible Payment Details Section */}
        <div className="bg-slate-900/60 border border-slate-800 rounded-xl overflow-hidden shadow-xl">
          <button
            onClick={() => setDetailsExpanded(!detailsExpanded)}
            className="w-full px-5 py-3.5 bg-slate-950/60 hover:bg-slate-950 flex items-center justify-between text-xs font-bold uppercase tracking-wider text-slate-300 transition cursor-pointer"
          >
            <div className="flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-indigo-400" />
              <span>Payment Details & Protocol Audit</span>
            </div>
            {detailsExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </button>

          {detailsExpanded && (
            <div className="p-5 border-t border-slate-800 bg-slate-950/40 text-xs space-y-3">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-slate-300">
                <div>
                  <span className="text-[10px] text-slate-500 uppercase block">Protocol Scheme</span>
                  <span className="font-bold">x402 / Algorand AVM</span>
                </div>
                <div>
                  <span className="text-[10px] text-slate-500 uppercase block">Facilitator</span>
                  <span className="font-bold">GoPlausible (https://facilitator.goplausible.xyz)</span>
                </div>
                <div>
                  <span className="text-[10px] text-slate-500 uppercase block">Network</span>
                  <span className="font-bold">{targetNetwork}</span>
                </div>
                <div>
                  <span className="text-[10px] text-slate-500 uppercase block">USDC ASA ID</span>
                  <span className="font-bold">{targetAssetId}</span>
                </div>
                <div>
                  <span className="text-[10px] text-slate-500 uppercase block">Replay Protection</span>
                  <span className="text-emerald-400 font-bold">Enabled (tx_hash uniqueness check)</span>
                </div>
                <div>
                  <span className="text-[10px] text-slate-500 uppercase block">Pricing Authority</span>
                  <span className="text-emerald-400 font-bold">Server-Authoritative (0.01 USDC)</span>
                </div>
              </div>

              {rawChallenge && (
                <div className="space-y-1 pt-2">
                  <span className="text-[10px] text-slate-500 uppercase block">Active Challenge Nonce</span>
                  <div className="bg-slate-950 p-2.5 rounded border border-slate-800 text-[11px] font-mono text-cyan-300 break-all select-all">
                    {rawChallenge.nonce || rawChallenge.payment_request_id}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Payment History Audit Table */}
        <div className="bg-slate-900/60 border border-slate-800 rounded-xl overflow-hidden shadow-xl space-y-0">
          <div className="px-5 py-4 border-b border-slate-800 bg-slate-950/60 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Clock className="w-4 h-4 text-slate-400" />
              <span className="text-xs font-bold text-slate-200 uppercase">
                Payment History ({history.length})
              </span>
            </div>
            <button
              onClick={loadPaymentHistory}
              disabled={historyLoading}
              className="text-[11px] text-slate-400 hover:text-white flex items-center gap-1 cursor-pointer"
            >
              <RefreshCw className={`w-3 h-3 ${historyLoading ? 'animate-spin' : ''}`} />
              <span>Refresh</span>
            </button>
          </div>

          {historyLoading ? (
            <div className="p-10 text-center text-xs text-slate-500">Loading payment history...</div>
          ) : history.length === 0 ? (
            <div className="p-10 text-center text-xs text-slate-500">
              No payments yet. Complete the x402 payment test above to see settled transactions.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs font-mono">
                <thead className="bg-slate-950 text-slate-400 border-b border-slate-800 text-[10px] uppercase">
                  <tr>
                    <th className="p-3">Date</th>
                    <th className="p-3">Service</th>
                    <th className="p-3">Amount</th>
                    <th className="p-3">Network</th>
                    <th className="p-3">Status</th>
                    <th className="p-3">Transaction ID</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 text-slate-300 text-[11px]">
                  {history.map((item) => (
                    <tr key={item.id} className="hover:bg-slate-850/40">
                      <td className="p-3 text-slate-500">{new Date(item.created_at).toLocaleDateString()}</td>
                      <td className="p-3 font-bold text-indigo-300">{item.service_id}</td>
                      <td className="p-3 font-bold text-emerald-400">${item.amount.toFixed(2)} USDC</td>
                      <td className="p-3 text-slate-400">{item.network}</td>
                      <td className="p-3">
                        <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-950/80 text-emerald-400 border border-emerald-800/40">
                          {item.status}
                        </span>
                      </td>
                      <td className="p-3 font-mono text-cyan-400 truncate max-w-xs select-all">
                        {item.transaction_id ? (
                          <a
                            href={`https://lora.algokit.io/testnet/transaction/${item.transaction_id}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="hover:underline flex items-center gap-1"
                          >
                            {item.transaction_id.slice(0, 12)}...
                            <ExternalLink className="w-3 h-3 shrink-0" />
                          </a>
                        ) : (
                          '—'
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800 py-4 text-center text-[10px] text-slate-600">
        Workline AI • Algorand x402 Micro-Monetization Engine • GoPlausible Facilitator
      </footer>
    </div>
  );
}
