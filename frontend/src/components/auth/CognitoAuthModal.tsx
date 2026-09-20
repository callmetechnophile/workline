'use client';

import React, { useState } from 'react';
import { useCognitoAuth } from '@/lib/CognitoAuthContext';
import { ShieldCheck, Lock, Mail, Key, Sparkles, X, CheckCircle2, AlertCircle } from 'lucide-react';

interface CognitoAuthModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function CognitoAuthModal({ isOpen, onClose }: CognitoAuthModalProps) {
  const { signIn, signUp, confirmSignUp, signInDemo, error, clearError } = useCognitoAuth();

  const [mode, setMode] = useState<'signin' | 'signup' | 'confirm'>('signin');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmCode, setConfirmCode] = useState('');
  const [loading, setLoading] = useState(false);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleDemoSignIn = async () => {
    setLoading(true);
    setStatusMessage(null);
    clearError();
    try {
      await signInDemo();
      onClose();
    } catch {
      // Error handled by context
    } finally {
      setLoading(false);
    }
  };

  const handleSignIn = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setStatusMessage(null);
    clearError();
    try {
      await signIn(email, password);
      onClose();
    } catch {
      // Error handled by context
    } finally {
      setLoading(false);
    }
  };

  const handleSignUp = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setStatusMessage(null);
    clearError();
    try {
      const res = await signUp(email, password);
      if (res.userConfirmed) {
        await signIn(email, password);
        onClose();
      } else {
        setMode('confirm');
        setStatusMessage(`Verification code sent to ${email}. Please check your inbox.`);
      }
    } catch {
      // Error handled by context
    } finally {
      setLoading(false);
    }
  };

  const handleConfirm = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setStatusMessage(null);
    clearError();
    try {
      await confirmSignUp(email, confirmCode);
      await signIn(email, password);
      onClose();
    } catch {
      // Error handled by context
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-fade-in">
      <div className="relative w-full max-w-md rounded-2xl border border-slate-800 bg-slate-900/95 p-6 shadow-2xl backdrop-blur-xl">
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute right-4 top-4 p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Header */}
        <div className="flex items-center gap-3 mb-6">
          <div className="p-2.5 rounded-xl bg-indigo-950/60 border border-indigo-700/50 text-indigo-400">
            <ShieldCheck className="w-6 h-6" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-white tracking-tight">AWS Cognito Access</h3>
            <p className="text-xs text-slate-400">Hardware Engineering Cloud Authentication</p>
          </div>
        </div>

        {/* 1-Click Quick Demo Login Card */}
        <div className="mb-6 p-4 rounded-xl border border-indigo-900/50 bg-indigo-950/30">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-mono font-semibold text-indigo-300 flex items-center gap-1.5">
              <Sparkles className="w-3.5 h-3.5 text-indigo-400 animate-pulse" />
              QUICK EVALUATION ACCESS
            </span>
            <span className="text-[10px] px-2 py-0.5 rounded-full bg-indigo-900/60 text-indigo-200 border border-indigo-700/40">
              Verified Role
            </span>
          </div>
          <p className="text-xs text-slate-300 mb-3">
            Instant 1-click access with the pre-configured test account (<code className="text-indigo-300">testuser@workline.ai</code>).
          </p>
          <button
            onClick={handleDemoSignIn}
            disabled={loading}
            className="w-full py-2 px-4 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold flex items-center justify-center gap-2 transition-all shadow-lg shadow-indigo-600/20 disabled:opacity-50 cursor-pointer"
          >
            {loading ? 'Authenticating with AWS...' : 'Sign In as Test Engineer'}
          </button>
        </div>

        {/* Divider */}
        <div className="relative my-4">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-slate-800" />
          </div>
          <div className="relative flex justify-center text-xs uppercase">
            <span className="bg-slate-900 px-2 text-slate-500 font-mono">Or Use Credentials</span>
          </div>
        </div>

        {/* Mode Tabs */}
        <div className="flex rounded-lg bg-slate-950 p-1 mb-4 border border-slate-800 text-xs font-medium">
          <button
            type="button"
            onClick={() => {
              setMode('signin');
              clearError();
            }}
            className={`flex-1 py-1.5 rounded-md transition-all ${
              mode === 'signin'
                ? 'bg-slate-800 text-white shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Sign In
          </button>
          <button
            type="button"
            onClick={() => {
              setMode('signup');
              clearError();
            }}
            className={`flex-1 py-1.5 rounded-md transition-all ${
              mode === 'signup'
                ? 'bg-slate-800 text-white shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Create Account
          </button>
        </div>

        {/* Error / Status Alerts */}
        {error && (
          <div className="mb-4 p-3 rounded-lg bg-rose-950/50 border border-rose-800/60 text-xs text-rose-300 flex items-start gap-2">
            <AlertCircle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
            <span>{error}</span>
          </div>
        )}
        {statusMessage && (
          <div className="mb-4 p-3 rounded-lg bg-emerald-950/50 border border-emerald-800/60 text-xs text-emerald-300 flex items-start gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
            <span>{statusMessage}</span>
          </div>
        )}

        {/* Forms */}
        {mode === 'signin' && (
          <form onSubmit={handleSignIn} className="space-y-3">
            <div>
              <label className="block text-xs font-mono text-slate-400 mb-1">Email Address</label>
              <div className="relative">
                <Mail className="absolute left-3 top-2.5 w-4 h-4 text-slate-500" />
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="engineer@company.com"
                  className="w-full pl-9 pr-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-white text-xs placeholder:text-slate-600 focus:outline-none focus:border-indigo-500 transition-colors"
                />
              </div>
            </div>
            <div>
              <label className="block text-xs font-mono text-slate-400 mb-1">Password</label>
              <div className="relative">
                <Lock className="absolute left-3 top-2.5 w-4 h-4 text-slate-500" />
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full pl-9 pr-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-white text-xs placeholder:text-slate-600 focus:outline-none focus:border-indigo-500 transition-colors"
                />
              </div>
            </div>
            <button
              type="submit"
              disabled={loading}
              className="w-full mt-2 py-2 px-4 rounded-lg bg-slate-800 hover:bg-slate-700 text-white text-xs font-semibold transition-all border border-slate-700 disabled:opacity-50 cursor-pointer"
            >
              {loading ? 'Authenticating...' : 'Sign In with AWS Cognito'}
            </button>
          </form>
        )}

        {mode === 'signup' && (
          <form onSubmit={handleSignUp} className="space-y-3">
            <div>
              <label className="block text-xs font-mono text-slate-400 mb-1">Email Address</label>
              <div className="relative">
                <Mail className="absolute left-3 top-2.5 w-4 h-4 text-slate-500" />
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="engineer@company.com"
                  className="w-full pl-9 pr-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-white text-xs placeholder:text-slate-600 focus:outline-none focus:border-indigo-500 transition-colors"
                />
              </div>
            </div>
            <div>
              <label className="block text-xs font-mono text-slate-400 mb-1">Password (Min 8 chars, 1 uppercase)</label>
              <div className="relative">
                <Lock className="absolute left-3 top-2.5 w-4 h-4 text-slate-500" />
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Min 8 characters"
                  className="w-full pl-9 pr-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-white text-xs placeholder:text-slate-600 focus:outline-none focus:border-indigo-500 transition-colors"
                />
              </div>
            </div>
            <button
              type="submit"
              disabled={loading}
              className="w-full mt-2 py-2 px-4 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold transition-all shadow-md shadow-indigo-600/20 disabled:opacity-50 cursor-pointer"
            >
              {loading ? 'Registering...' : 'Register User'}
            </button>
          </form>
        )}

        {mode === 'confirm' && (
          <form onSubmit={handleConfirm} className="space-y-3">
            <div>
              <label className="block text-xs font-mono text-slate-400 mb-1">Confirmation Code</label>
              <div className="relative">
                <Key className="absolute left-3 top-2.5 w-4 h-4 text-slate-500" />
                <input
                  type="text"
                  required
                  value={confirmCode}
                  onChange={(e) => setConfirmCode(e.target.value)}
                  placeholder="Enter 6-digit code"
                  className="w-full pl-9 pr-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-white text-xs placeholder:text-slate-600 focus:outline-none focus:border-indigo-500 transition-colors"
                />
              </div>
            </div>
            <button
              type="submit"
              disabled={loading}
              className="w-full mt-2 py-2 px-4 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold transition-all shadow-md shadow-emerald-600/20 disabled:opacity-50 cursor-pointer"
            >
              {loading ? 'Verifying...' : 'Confirm Account & Sign In'}
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
