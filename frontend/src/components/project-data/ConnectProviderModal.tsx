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
  Mail,
  Lock,
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
  // Input fields for ID and credentials
  const [userIdInput, setUserIdInput] = useState(
    providerId === 'google_drive'
      ? clerkAccount?.email || ''
      : clerkAccount?.username || ''
  );
  const [token, setToken] = useState('');
  const [target, setTarget] = useState(
    providerId === 'google_drive'
      ? `WORKLINE/Projects/${defaultProjectName.replace(/\s+/g, '-')}`
      : `workline-${defaultProjectName.toLowerCase().replace(/[^a-z0-9]+/g, '-')}`
  );
  const [branch, setBranch] = useState('main');
  const [host, setHost] = useState('https://gitlab.com');

  // Verification states
  const [isVerifying, setIsVerifying] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [verifiedInfo, setVerifiedInfo] = useState<{
    account: string;
    name?: string;
    email?: string;
    avatarUrl?: string;
    authType?: string;
  } | null>(null);

  if (!isOpen) return null;

  // 1. Verify via Clerk Google/GitHub active session
  const handleVerifyWithClerkSession = () => {
    setErrorMsg(null);
    if (!clerkAccount) {
      setErrorMsg(`No active ${providerName} session found. Please enter credentials below.`);
      return;
    }

    if (providerId === 'google_drive') {
      const enteredEmail = userIdInput.trim().toLowerCase();
      const sessionEmail = (clerkAccount.email || '').trim().toLowerCase();
      if (!enteredEmail) {
        setErrorMsg('Please enter your Gmail ID or Google Workspace email.');
        return;
      }
      if (enteredEmail !== sessionEmail) {
        setErrorMsg(`Gmail ID mismatch: You entered '${enteredEmail}', but your logged-in session is '${sessionEmail}'.`);
        return;
      }
      setVerifiedInfo({
        account: enteredEmail,
        name: clerkAccount.username || enteredEmail.split('@')[0],
        email: enteredEmail,
        avatarUrl: clerkAccount.avatarUrl || undefined,
        authType: 'Active Google Session (Verified)',
      });
    } else if (providerId === 'github') {
      const enteredUsername = userIdInput.trim().replace(/^@+/, '').toLowerCase();
      const sessionUsername = (clerkAccount.username || '').trim().replace(/^@+/, '').toLowerCase();
      if (!enteredUsername) {
        setErrorMsg('Please enter your GitHub ID / username.');
        return;
      }
      if (enteredUsername !== sessionUsername) {
        setErrorMsg(`GitHub ID mismatch: You entered '@${enteredUsername}', but your linked session is '@${sessionUsername}'.`);
        return;
      }
      setVerifiedInfo({
        account: clerkAccount.username || enteredUsername,
        name: clerkAccount.username || enteredUsername,
        email: clerkAccount.email,
        avatarUrl: clerkAccount.avatarUrl || undefined,
        authType: 'Linked GitHub Session (Verified)',
      });
    }
  };

  // 2. Real API Verification against provider API
  const handleVerifyLiveApi = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg(null);
    setVerifiedInfo(null);

    const enteredId = userIdInput.trim();
    if (!enteredId) {
      setErrorMsg(`Please enter your ${providerId === 'google_drive' ? 'Gmail ID' : `${providerName} ID`}.`);
      return;
    }

    if (!token.trim()) {
      setErrorMsg(
        providerId === 'bitbucket'
          ? 'Please enter your Bitbucket App Password.'
          : `Please enter your ${providerName} Personal Access Token or OAuth credential.`
      );
      return;
    }

    setIsVerifying(true);

    try {
      const payload: any = {
        provider: providerId,
        token: token.trim(),
        username: enteredId,
      };
      if (providerId === 'gitlab') payload.host = host.trim();

      const res = await fetch(`${apiBase}/api/project/data/verify-auth`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      const data = await res.json();
      if (!res.ok || !data.success) {
        setErrorMsg(data.error || data.detail || 'Authentication verification failed. Please check your credentials.');
        return;
      }

      setVerifiedInfo({
        account: data.account || enteredId,
        name: data.name,
        email: data.email,
        avatarUrl: data.avatar_url,
        authType: data.auth_type || 'Verified via Live API',
      });
    } catch (err: any) {
      setErrorMsg(`Verification network request failed: ${err.message}`);
    } finally {
      setIsVerifying(false);
    }
  };

  // 3. Final step: Connect and enable upload once verified
  const handleConfirmConnection = () => {
    if (!verifiedInfo) return;

    const newState: CloudProviderState = {
      id: providerId,
      name: providerName,
      connected: true,
      account: verifiedInfo.account,
      target: target,
      branch: branch,
      lastSync: new Date().toISOString(),
      syncDirection: 'LOCAL_TO_REMOTE',
      lastCommitHash: 'verified_id',
      localVersion: '1.0',
      remoteVersion: '1.0',
    };

    onSaveConnection(newState);
    onClose();
  };

  const idLabel =
    providerId === 'google_drive'
      ? 'Gmail ID / Google Account'
      : providerId === 'github'
      ? 'GitHub Username / ID'
      : providerId === 'gitlab'
      ? 'GitLab Username / ID'
      : 'Bitbucket Username / ID';

  const idPlaceholder =
    providerId === 'google_drive'
      ? 'e.g. yourname@gmail.com'
      : providerId === 'github'
      ? 'e.g. octocat'
      : providerId === 'gitlab'
      ? 'e.g. gitlab-user'
      : 'e.g. bitbucket-user';

  const credentialLabel =
    providerId === 'google_drive'
      ? 'Google OAuth Bearer Token / API Token'
      : providerId === 'github'
      ? 'GitHub Personal Access Token (PAT with repo scope)'
      : providerId === 'gitlab'
      ? 'GitLab Personal Access Token (api or write_repository scope)'
      : 'Bitbucket App Password (Repositories: Write scope)';

  const credentialPlaceholder =
    providerId === 'google_drive'
      ? 'ya29.xxxxxxxxxxxxxxxxxxxx'
      : providerId === 'github'
      ? 'ghp_xxxxxxxxxxxxxxxxxxxx'
      : providerId === 'gitlab'
      ? 'glpat-xxxxxxxxxxxxxxxxxxxx'
      : 'App Password from Bitbucket Settings';

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4 animate-in fade-in duration-200">
      <div className="w-full max-w-lg bg-slate-900 border border-slate-800 rounded-xl shadow-2xl overflow-hidden flex flex-col">
        {/* Modal Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800 bg-slate-950/80">
          <div className="flex items-center gap-2.5">
            <div className="p-2 bg-indigo-950/80 border border-indigo-700/50 rounded-lg text-indigo-400">
              <ShieldCheck className="w-5 h-5 text-emerald-400" />
            </div>
            <div>
              <h3 className="text-base font-bold text-slate-100">
                Verify & Connect {providerName}
              </h3>
              <p className="text-xs text-slate-400 font-mono">
                Mandatory ID Verification before Upload & Sync Permissions
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

        {/* Modal Body */}
        <div className="p-6 space-y-5 overflow-y-auto max-h-[75vh]">
          {/* Error Banner */}
          {errorMsg && (
            <div className="p-3 bg-rose-950/50 border border-rose-700/60 rounded-lg flex items-start gap-2.5 text-xs font-mono text-rose-300">
              <AlertCircle className="w-4 h-4 text-rose-400 flex-shrink-0 mt-0.5" />
              <div className="leading-snug">{errorMsg}</div>
            </div>
          )}

          {/* Verification Success Banner */}
          {verifiedInfo && (
            <div className="p-4 bg-emerald-950/60 border border-emerald-600/70 rounded-lg space-y-2.5 animate-in fade-in duration-200">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-xs font-mono text-emerald-300 font-bold">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                  <span>IDENTITY VERIFIED</span>
                </div>
                <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-emerald-900 text-emerald-200">
                  READY TO UPLOAD
                </span>
              </div>
              <div className="flex items-center gap-3 text-xs font-mono">
                {verifiedInfo.avatarUrl ? (
                  <img
                    src={verifiedInfo.avatarUrl}
                    alt="Avatar"
                    className="w-9 h-9 rounded-full border border-emerald-500/50 object-cover"
                  />
                ) : (
                  <div className="w-9 h-9 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-xs font-bold text-slate-200">
                    {verifiedInfo.account.slice(0, 2).toUpperCase()}
                  </div>
                )}
                <div>
                  <div className="font-bold text-slate-100">{verifiedInfo.account}</div>
                  <div className="text-[11px] text-slate-400">
                    {verifiedInfo.name || verifiedInfo.email || verifiedInfo.authType}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Form to enter User ID and Credentials */}
          <form onSubmit={handleVerifyLiveApi} className="space-y-4">
            {/* Step 1: User ID */}
            <div className="space-y-1">
              <label className="text-xs font-mono text-slate-200 font-semibold flex items-center justify-between">
                <span>{idLabel}</span>
                <span className="text-[10px] text-rose-400 font-normal">Required</span>
              </label>
              <input
                type="text"
                value={userIdInput}
                onChange={(e) => {
                  setUserIdInput(e.target.value);
                  setVerifiedInfo(null);
                }}
                placeholder={idPlaceholder}
                required
                className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs font-mono text-slate-200 focus:outline-none focus:border-indigo-500"
              />
              <p className="text-[10px] text-slate-500 font-mono">
                {providerId === 'google_drive'
                  ? 'Your Gmail or Google account ID used for storing project archives.'
                  : `Your official ${providerName} user handle.`}
              </p>
            </div>

            {/* Quick Session Option for Google or GitHub if available */}
            {clerkAccount && (providerId === 'google_drive' || providerId === 'github') && (
              <div className="p-3 bg-indigo-950/30 border border-indigo-800/50 rounded-lg space-y-2">
                <div className="flex items-center justify-between text-xs font-mono text-indigo-300">
                  <div className="flex items-center gap-1.5 font-semibold">
                    <UserCheck className="w-3.5 h-3.5 text-emerald-400" />
                    <span>Logged-in {providerName} Session Detected</span>
                  </div>
                  <span className="text-[10px] text-slate-400">
                    {providerId === 'google_drive' ? clerkAccount.email : `@${clerkAccount.username}`}
                  </span>
                </div>
                <button
                  type="button"
                  onClick={handleVerifyWithClerkSession}
                  className="w-full py-1.5 px-3 bg-indigo-600/30 hover:bg-indigo-600/50 text-indigo-200 border border-indigo-500/40 rounded text-xs font-mono cursor-pointer transition-all flex items-center justify-center gap-1.5"
                >
                  <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                  <span>Verify with Active Session</span>
                </button>
              </div>
            )}

            {/* GitLab Host if applicable */}
            {providerId === 'gitlab' && (
              <div className="space-y-1">
                <label className="text-xs font-mono text-slate-300">GitLab Host URL</label>
                <input
                  type="text"
                  value={host}
                  onChange={(e) => setHost(e.target.value)}
                  placeholder="https://gitlab.com"
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs font-mono text-slate-200 focus:outline-none focus:border-indigo-500"
                />
              </div>
            )}

            {/* Step 2: Credentials / Token */}
            <div className="space-y-1">
              <label className="text-xs font-mono text-slate-200 font-semibold flex items-center justify-between">
                <span>{credentialLabel}</span>
                <span className="text-[10px] text-slate-500">Live API Check</span>
              </label>
              <input
                type="password"
                value={token}
                onChange={(e) => {
                  setToken(e.target.value);
                  setVerifiedInfo(null);
                }}
                placeholder={credentialPlaceholder}
                className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs font-mono text-slate-200 focus:outline-none focus:border-indigo-500"
              />
              <p className="text-[10px] text-slate-500 font-mono">
                Credentials are authenticated against official {providerName} APIs. Zero secrets exported to repo.
              </p>
            </div>

            {/* Step 3: Target Folder or Repository */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
              <div className="space-y-1">
                <label className="text-xs font-mono text-slate-300">
                  {providerId === 'google_drive' ? 'Drive Target Folder' : 'Target Repository'}
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

            {/* Verify Button */}
            {!verifiedInfo && (
              <button
                type="submit"
                disabled={isVerifying || !userIdInput.trim()}
                className="w-full py-2.5 px-4 bg-slate-800 hover:bg-slate-700 disabled:opacity-50 text-slate-100 border border-slate-700 rounded-lg text-xs font-semibold cursor-pointer transition-all flex items-center justify-center gap-2"
              >
                {isVerifying ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin text-indigo-400" />
                    <span>Verifying {userIdInput} with {providerName} API...</span>
                  </>
                ) : (
                  <>
                    <ShieldCheck className="w-4 h-4 text-emerald-400" />
                    <span>Verify {providerName} ID & Credentials</span>
                  </>
                )}
              </button>
            )}
          </form>

          {/* Confirm & Enable Uploads Button (Active only when verified) */}
          {verifiedInfo && (
            <div className="pt-2">
              <button
                type="button"
                onClick={handleConfirmConnection}
                className="w-full py-3 px-4 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-bold shadow-lg shadow-emerald-600/20 cursor-pointer transition-all flex items-center justify-center gap-2"
              >
                <CheckCircle2 className="w-4 h-4 text-white" />
                <span>Authorize & Enable Uploads for {verifiedInfo.account}</span>
              </button>
            </div>
          )}
        </div>

        {/* Modal Footer */}
        <div className="flex items-center justify-between px-6 py-3 border-t border-slate-800 bg-slate-950/80 text-[11px] font-mono text-slate-500">
          <span>Verification is required before syncing or uploading project data.</span>
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
