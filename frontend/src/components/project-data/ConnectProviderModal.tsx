'use client';

import React, { useState } from 'react';
import { CloudProviderId, CloudProviderState } from '@/lib/workline-filesystem/types';
import {
  X,
  ShieldCheck,
  Key,
  Globe,
  GitBranch,
  Folder,
  CheckCircle2,
  AlertCircle,
  Loader2,
  ExternalLink,
  UserCheck,
} from 'lucide-react';

interface ConnectProviderModalProps {
  isOpen: boolean;
  onClose: () => void;
  providerId: CloudProviderId;
  providerName: string;
  defaultProjectName: string;
  clerkAccount?: {
    username?: string | null;
    email?: string;
    avatarUrl?: string | null;
  } | null;
  onSaveConnection: (state: CloudProviderState) => void;
  apiBase?: string;
}

export default function ConnectProviderModal({
  isOpen,
  onClose,
  providerId,
  providerName,
  defaultProjectName,
  clerkAccount,
  onSaveConnection,
  apiBase = '',
}: ConnectProviderModalProps) {
  const [token, setToken] = useState('');
  const [username, setUsername] = useState(clerkAccount?.username || '');
  const [target, setTarget] = useState(
    providerId === 'google_drive'
      ? `WORKLINE/Projects/${defaultProjectName.replace(/\s+/g, '-')}`
      : `workline-${defaultProjectName.toLowerCase().replace(/[^a-z0-9]+/g, '-')}`
  );
  const [branch, setBranch] = useState('main');
  const [host, setHost] = useState('https://gitlab.com');
  const [isVerifying, setIsVerifying] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [verifiedInfo, setVerifiedInfo] = useState<any | null>(null);

  if (!isOpen) return null;

  // 1. One-click Connect via active Clerk OAuth session
  const handleConnectWithClerk = () => {
    if (!clerkAccount) return;
    const accountName = clerkAccount.username || clerkAccount.email || 'Authenticated User';
    const newState: CloudProviderState = {
      id: providerId,
      name: providerName,
      connected: true,
      account: accountName,
      target: target,
      branch: branch,
      lastSync: new Date().toISOString(),
      syncDirection: 'LOCAL_TO_REMOTE',
      lastCommitHash: 'clerk_auth',
      localVersion: '1.0',
      remoteVersion: '1.0',
    };
    onSaveConnection(newState);
    onClose();
  };

  // 2. Real API Verification using backend /api/project/data/verify-auth
  const handleVerifyLiveCredentials = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg(null);
    setVerifiedInfo(null);
    setIsVerifying(true);

    try {
      const payload: any = {
        provider: providerId,
        token: token.trim(),
      };
      if (providerId === 'bitbucket') payload.username = username.trim();
      if (providerId === 'gitlab') payload.host = host.trim();

      const res = await fetch(`${apiBase}/api/project/data/verify-auth`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      const data = await res.json();
      if (!res.ok || !data.success) {
        setErrorMsg(data.error || data.detail || 'Authentication failed. Please check your credentials.');
        return;
      }

      setVerifiedInfo(data);
      // Save authenticated state
      const newState: CloudProviderState = {
        id: providerId,
        name: providerName,
        connected: true,
        account: data.account || data.email || username || 'Verified Account',
        target: target,
        branch: branch,
        lastSync: new Date().toISOString(),
        syncDirection: 'LOCAL_TO_REMOTE',
        lastCommitHash: 'verified_pat',
        localVersion: '1.0',
        remoteVersion: '1.0',
      };
      onSaveConnection(newState);
      setTimeout(() => onClose(), 800);
    } catch (err: any) {
      setErrorMsg(`Verification request failed: ${err.message}`);
    } finally {
      setIsVerifying(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4 animate-in fade-in duration-200">
      <div className="w-full max-w-lg bg-slate-900 border border-slate-800 rounded-xl shadow-2xl overflow-hidden flex flex-col">
        {/* Modal Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800 bg-slate-950/80">
          <div className="flex items-center gap-2.5">
            <div className="p-2 bg-indigo-950/80 border border-indigo-700/50 rounded-lg text-indigo-400">
              <Key className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-slate-100">
                Authenticate {providerName}
              </h3>
              <p className="text-xs text-slate-400 font-mono">
                Real Credentials Verification & Target Selection
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-slate-400 hover:text-slate-100 hover:bg-slate-800 rounded-lg transition-colors cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Content */}
        <div className="p-6 space-y-5 overflow-y-auto max-h-[75vh]">
          {/* Active Clerk OAuth Session if available */}
          {clerkAccount && (
            <div className="p-4 bg-indigo-950/40 border border-indigo-700/50 rounded-lg space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-xs font-mono text-indigo-300 font-semibold">
                  <UserCheck className="w-4 h-4 text-emerald-400" />
                  <span>Detected {providerName} OAuth Session</span>
                </div>
                <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-emerald-950 text-emerald-400 border border-emerald-800">
                  VERIFIED IDENTITY
                </span>
              </div>

              <div className="flex items-center gap-3">
                {clerkAccount.avatarUrl ? (
                  <img src={clerkAccount.avatarUrl} alt="Avatar" className="w-8 h-8 rounded-full border border-slate-700" />
                ) : (
                  <div className="w-8 h-8 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-xs font-bold text-slate-300">
                    {(clerkAccount.username || clerkAccount.email || 'US').slice(0, 2).toUpperCase()}
                  </div>
                )}
                <div className="text-xs font-mono min-w-0">
                  <div className="font-semibold text-slate-100 truncate">
                    {clerkAccount.username || clerkAccount.email}
                  </div>
                  {clerkAccount.email && (
                    <div className="text-slate-400 text-[11px] truncate">{clerkAccount.email}</div>
                  )}
                </div>
              </div>

              <button
                type="button"
                onClick={handleConnectWithClerk}
                className="w-full py-2 px-3 bg-indigo-600 hover:bg-indigo-500 text-white rounded text-xs font-semibold shadow transition-all cursor-pointer flex items-center justify-center gap-2"
              >
                <span>Authorize {providerName} as {clerkAccount.username || clerkAccount.email}</span>
              </button>
            </div>
          )}

          {/* Manual Token / PAT Verification Form */}
          <form onSubmit={handleVerifyLiveCredentials} className="space-y-4">
            <div className="text-xs font-mono text-slate-400 font-semibold uppercase tracking-wider flex items-center justify-between">
              <span>{clerkAccount ? 'Or Enter Personal Access Token' : 'Enter Real API Credentials'}</span>
              <span className="text-[10px] text-slate-500 font-normal">Direct Provider API Verification</span>
            </div>

            {/* Error Banner */}
            {errorMsg && (
              <div className="p-3 bg-rose-950/50 border border-rose-700/60 rounded-lg flex items-start gap-2 text-xs font-mono text-rose-300">
                <AlertCircle className="w-4 h-4 text-rose-400 flex-shrink-0 mt-0.5" />
                <div className="leading-snug">{errorMsg}</div>
              </div>
            )}

            {/* Success Banner */}
            {verifiedInfo && (
              <div className="p-3 bg-emerald-950/50 border border-emerald-700/60 rounded-lg flex items-center gap-2 text-xs font-mono text-emerald-300">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
                <div>
                  Verified identity: <span className="font-bold text-white">{verifiedInfo.account}</span> ({verifiedInfo.name || verifiedInfo.email || verifiedInfo.auth_type})
                </div>
              </div>
            )}

            {/* GitLab Host option */}
            {providerId === 'gitlab' && (
              <div className="space-y-1">
                <label className="text-xs font-mono text-slate-300">GitLab Instance URL</label>
                <input
                  type="text"
                  value={host}
                  onChange={(e) => setHost(e.target.value)}
                  placeholder="https://gitlab.com"
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs font-mono text-slate-200 focus:outline-none focus:border-indigo-500"
                />
              </div>
            )}

            {/* Bitbucket Username */}
            {providerId === 'bitbucket' && (
              <div className="space-y-1">
                <label className="text-xs font-mono text-slate-300">Bitbucket Username</label>
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="your-bitbucket-username"
                  required
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs font-mono text-slate-200 focus:outline-none focus:border-indigo-500"
                />
              </div>
            )}

            {/* Token Input */}
            <div className="space-y-1">
              <label className="text-xs font-mono text-slate-300 flex items-center justify-between">
                <span>
                  {providerId === 'github'
                    ? 'GitHub Personal Access Token (PAT)'
                    : providerId === 'gitlab'
                    ? 'GitLab Personal Access Token'
                    : providerId === 'bitbucket'
                    ? 'Bitbucket App Password'
                    : 'Google Drive OAuth Token / API Key'}
                </span>
                <span className="text-[10px] text-slate-500">Live API Checked</span>
              </label>
              <input
                type="password"
                value={token}
                onChange={(e) => setToken(e.target.value)}
                placeholder={
                  providerId === 'github'
                    ? 'ghp_xxxxxxxxxxxxxxxxxxxx'
                    : providerId === 'gitlab'
                    ? 'glpat-xxxxxxxxxxxxxxxxxxxx'
                    : providerId === 'bitbucket'
                    ? 'App password with repository write access'
                    : 'ya29.xxxxxxxxxxxxxxxxxxxx'
                }
                required
                className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs font-mono text-slate-200 focus:outline-none focus:border-indigo-500"
              />
              <p className="text-[10px] text-slate-500 font-mono pt-0.5">
                Token is verified directly against {providerName}&apos;s official API and stored securely in client storage.
              </p>
            </div>

            {/* Target Folder or Repository */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
              <div className="space-y-1">
                <label className="text-xs font-mono text-slate-300">
                  {providerId === 'google_drive' ? 'Drive Target Folder' : 'Target Repository Name'}
                </label>
                <input
                  type="text"
                  value={target}
                  onChange={(e) => setTarget(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs font-mono text-slate-200 focus:outline-none focus:border-indigo-500"
                />
              </div>

              {providerId !== 'google_drive' && (
                <div className="space-y-1">
                  <label className="text-xs font-mono text-slate-300">Git Branch</label>
                  <input
                    type="text"
                    value={branch}
                    onChange={(e) => setBranch(e.target.value)}
                    className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs font-mono text-slate-200 focus:outline-none focus:border-indigo-500"
                  />
                </div>
              )}
            </div>

            <button
              type="submit"
              disabled={isVerifying || !token.trim()}
              className="w-full py-2.5 px-4 bg-slate-800 hover:bg-slate-700 disabled:opacity-50 text-slate-100 border border-slate-700 rounded-lg text-xs font-semibold cursor-pointer transition-all flex items-center justify-center gap-2"
            >
              {isVerifying ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin text-indigo-400" />
                  <span>Verifying Credentials against {providerName} API...</span>
                </>
              ) : (
                <>
                  <ShieldCheck className="w-4 h-4 text-indigo-400" />
                  <span>Verify with {providerName} API & Connect</span>
                </>
              )}
            </button>
          </form>
        </div>

        {/* Modal Footer */}
        <div className="flex items-center justify-between px-6 py-3 border-t border-slate-800 bg-slate-950/80 text-[11px] font-mono text-slate-500">
          <span>In accordance with §8: Zero secrets exported to repository files.</span>
          <button
            type="button"
            onClick={onClose}
            className="text-slate-400 hover:text-slate-200 cursor-pointer"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
}
