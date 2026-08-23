'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { Search, Moon, Sun, ShieldCheck, Sparkles, Terminal, Wallet } from 'lucide-react';
import { SignInButton, SignUpButton, UserButton, useAuth } from '@clerk/nextjs';
import { peraWallet, WalletConnectionState } from '@/lib/peraWallet';

interface TopbarProps {
  isLightMode: boolean;
  onToggleTheme: () => void;
  projectName?: string;
  onOpenNewProject: () => void;
  onOpenCopilot: () => void;
}

export default function Topbar({
  isLightMode,
  onToggleTheme,
  projectName,
  onOpenNewProject,
  onOpenCopilot,
}: TopbarProps) {
  const { isSignedIn } = useAuth();
  const [walletState, setWalletState] = useState<WalletConnectionState>(peraWallet.getState());
  const [walletAddress, setWalletAddress] = useState<string | null>(peraWallet.getAddress());

  useEffect(() => {
    const unsub = peraWallet.subscribe((state, address) => {
      setWalletState(state);
      setWalletAddress(address);
    });
    return () => unsub();
  }, []);

  return (
    <header className="h-14 border-b border-slate-800 bg-slate-950/80 backdrop-blur-md px-6 flex items-center justify-between z-20 sticky top-0">
      {/* Left: Project Context & Breadcrumb */}
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2 text-xs font-mono">
          <span className="text-slate-500">Project:</span>
          {projectName ? (
            <span className="px-2.5 py-1 rounded bg-slate-900 border border-slate-700 text-slate-200 font-semibold">
              {projectName}
            </span>
          ) : (
            <button
              onClick={onOpenNewProject}
              className="text-xs text-slate-400 hover:text-indigo-400 underline decoration-dotted cursor-pointer"
            >
              No project selected (Create +)
            </button>
          )}
        </div>

        {/* Multi-Microservice Cluster Status */}
        <div className="hidden lg:flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-emerald-950/40 border border-emerald-800/40 text-[10px] font-mono text-emerald-400">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
          <span>R1-R5 CLUSTER ACTIVE</span>
        </div>
      </div>

      {/* Center: Global Command / Search Trigger */}
      <div className="hidden md:flex items-center w-80 max-w-md">
        <button
          onClick={onOpenNewProject}
          className="w-full flex items-center justify-between px-3 py-1.5 bg-slate-900/90 border border-slate-800 rounded-md text-xs text-slate-400 hover:border-slate-700 hover:text-slate-200 transition-all cursor-pointer"
        >
          <div className="flex items-center gap-2">
            <Search className="w-3.5 h-3.5 text-slate-500" />
            <span>Search components, specs, requirements...</span>
          </div>
          <kbd className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-800 border border-slate-700 text-slate-400">
            ⌘K
          </kbd>
        </button>
      </div>

      {/* Right: Actions, AI Copilot, Theme & Auth */}
      <div className="flex items-center gap-3">
        {/* Dedicated Wallet Icon & Payments Button */}
        <Link
          href="/wallet"
          title="Wallet & Payments"
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md border text-xs font-mono transition-all cursor-pointer ${
            walletState === 'CONNECTED' && walletAddress
              ? 'bg-cyan-950/60 border-cyan-700/60 text-cyan-300 hover:bg-cyan-900/60'
              : 'bg-slate-900/70 border-slate-800 text-slate-400 hover:text-slate-200 hover:border-slate-700'
          }`}
        >
          <Wallet className={`w-3.5 h-3.5 ${walletState === 'CONNECTED' ? 'text-cyan-400' : 'text-slate-400'}`} />
          {walletState === 'CONNECTED' && walletAddress ? (
            <span className="font-bold text-[11px] truncate max-w-[90px]">
              {walletAddress.slice(0, 4)}...{walletAddress.slice(-4)}
            </span>
          ) : (
            <span className="hidden sm:inline text-[11px]">Wallet</span>
          )}
        </Link>

        {/* Contextual AI Assistant Drawer Trigger */}
        <button
          onClick={onOpenCopilot}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-indigo-950/60 border border-indigo-700/50 text-indigo-300 hover:bg-indigo-900/60 hover:text-white text-xs font-medium transition-all cursor-pointer"
          title="Open Engineering Copilot"
        >
          <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
          <span className="hidden sm:inline">AI Copilot</span>
        </button>

        {/* Theme Toggle */}
        <button
          onClick={onToggleTheme}
          className="p-2 rounded-md border border-slate-800 bg-slate-900/60 text-slate-400 hover:text-slate-200 hover:border-slate-700 transition-all cursor-pointer"
          title={isLightMode ? "Switch to Dark Mode" : "Switch to Light Mode"}
        >
          {isLightMode ? <Sun className="w-4 h-4 text-amber-400" /> : <Moon className="w-4 h-4" />}
        </button>

        {/* Auth Buttons */}
        {!isSignedIn ? (
          <div className="flex items-center gap-2">
            <SignInButton mode="modal">
              <button className="text-xs font-mono font-semibold px-3 py-1.5 rounded border border-slate-800 bg-slate-900 hover:bg-slate-800 text-slate-300 transition-all cursor-pointer">
                Sign In
              </button>
            </SignInButton>
            <SignUpButton mode="modal">
              <button className="text-xs font-mono font-semibold px-3 py-1.5 rounded bg-indigo-600 hover:bg-indigo-500 text-white transition-all cursor-pointer">
                Sign Up
              </button>
            </SignUpButton>
          </div>
        ) : (
          <UserButton />
        )}
      </div>
    </header>
  );
}
