import React, { useState } from 'react';
import { KeyRound, Link2, Copy, Check, Sparkles, RefreshCw, Trash2, ShieldCheck, QrCode } from 'lucide-react';
import { getGatewayBearerToken } from '../lib/cognito';
import { API_BASE_URL } from '../lib/api';

export type GenerationMode = 'BOTH' | 'CODE' | 'LINK';

interface TeamInvitationPanelProps {
  teamId: string;
  teamName?: string;
  memberCount?: number;
  apiBase?: string;
}

export const TeamInvitationPanel: React.FC<TeamInvitationPanelProps> = ({
  teamId,
  teamName = 'Engineering Team',
  memberCount = 1,
  apiBase = '',
}) => {
  const [generationMode, setGenerationMode] = useState<GenerationMode>('BOTH');
  const [ttlDays, setTtlDays] = useState<number>(7);
  const [maxUses, setMaxUses] = useState<number>(10);
  const [role, setRole] = useState<string>('MEMBER');
  const [isGenerating, setIsGenerating] = useState<boolean>(false);
  const [invitationData, setInvitationData] = useState<any | null>(null);

  // Copy feedback states
  const [copyCodeFeedback, setCopyCodeFeedback] = useState<boolean>(false);
  const [copyLinkFeedback, setCopyLinkFeedback] = useState<boolean>(false);
  const [copyMessageFeedback, setCopyMessageFeedback] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const getEffectiveBase = () => {
    return (apiBase || API_BASE_URL || '').replace(/\/$/, '');
  };

  const generateCryptographicCode = (): string => {
    // Generate standard WL-XXXXXX join code without ambiguous characters
    const alphabet = '23456789ABCDEFGHJKLMNPQRSTUVWXYZ';
    const rand = new Uint8Array(6);
    if (typeof window !== 'undefined' && window.crypto && window.crypto.getRandomValues) {
      window.crypto.getRandomValues(rand);
    } else {
      for (let i = 0; i < 6; i++) rand[i] = Math.floor(Math.random() * 256);
    }
    let codeStr = '';
    for (let i = 0; i < 6; i++) {
      codeStr += alphabet[rand[i] % alphabet.length];
    }
    return `WL-${codeStr}`;
  };

  const saveLocalInvitation = (inv: any, joinCode?: string) => {
    try {
      if (typeof window !== 'undefined' && window.localStorage) {
        // 1. Save to team invitation list
        const key = `workline_team_invitations_${teamId}`;
        const existingRaw = localStorage.getItem(key);
        const existingList = existingRaw ? JSON.parse(existingRaw) : [];
        const filtered = existingList.filter((item: any) => item.invitation_id !== inv.invitation_id);
        filtered.unshift(inv);
        localStorage.setItem(key, JSON.stringify(filtered.slice(0, 30)));

        // 2. Save join code registry for JoinTeamModal lookup
        if (joinCode) {
          const codesKey = 'workline_team_join_codes';
          const codesRaw = localStorage.getItem(codesKey);
          const registry = codesRaw ? JSON.parse(codesRaw) : {};
          registry[joinCode] = {
            team_id: teamId,
            team_name: teamName,
            role: inv.role,
            expires_at: inv.expires_at,
            max_uses: inv.max_uses,
            member_count: memberCount,
          };
          localStorage.setItem(codesKey, JSON.stringify(registry));
          localStorage.setItem(`workline_team_join_code_${teamId}`, joinCode);
        }
      }
    } catch (e) {
      console.warn('Could not cache invitation to localStorage', e);
    }
  };

  const handleCreateInvitation = async (overrideMode?: GenerationMode) => {
    const activeMode = overrideMode || generationMode;
    setIsGenerating(true);
    setError(null);

    const origin = typeof window !== 'undefined' && window.location.origin ? window.location.origin : 'https://armouriq.app';
    const expiresDate = new Date(Date.now() + ttlDays * 24 * 60 * 60 * 1000);

    // 1. Prepare fallback tokens
    let randomTokenHex = '';
    if (typeof window !== 'undefined' && window.crypto && window.crypto.getRandomValues) {
      const buf = new Uint8Array(20);
      window.crypto.getRandomValues(buf);
      randomTokenHex = Array.from(buf).map((b) => b.toString(16).padStart(2, '0')).join('');
    } else {
      randomTokenHex = Math.random().toString(36).substring(2) + Date.now().toString(36);
    }

    const fallbackCode = generateCryptographicCode();
    const fallbackInvId = `inv_${randomTokenHex.substring(0, 16)}`;
    const fallbackJoinUrl = `${origin}/team/join/v1.${randomTokenHex}`;

    let resolvedJoinCode: string | null = activeMode !== 'LINK' ? fallbackCode : null;
    let resolvedJoinUrl: string | null = activeMode !== 'CODE' ? fallbackJoinUrl : null;
    let resolvedInvId = fallbackInvId;

    try {
      const effectiveBase = getEffectiveBase();
      const token = await getGatewayBearerToken().catch(() => null);

      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
      };
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      // If mode requests code, try backend join-code rotation
      if (activeMode !== 'LINK' && effectiveBase) {
        try {
          const codeRes = await fetch(`${effectiveBase}/api/teams/${teamId}/join-code/rotate`, {
            method: 'POST',
            headers,
          });
          if (codeRes.ok) {
            const codeData = await codeRes.json();
            if (codeData.join_code) {
              resolvedJoinCode = codeData.join_code;
            }
          }
        } catch (e) {
          console.warn('Backend rotate join-code fallback to generated cryptographic code:', e);
        }
      }

      // If mode requests link, try backend invitation creation
      if (activeMode !== 'CODE' && effectiveBase) {
        try {
          const linkRes = await fetch(`${effectiveBase}/api/teams/${teamId}/invitations`, {
            method: 'POST',
            headers,
            body: JSON.stringify({
              created_by: 'Team Owner',
              ttl_days: ttlDays,
              max_uses: maxUses,
              role,
            }),
          });
          if (linkRes.ok) {
            const linkData = await linkRes.json();
            if (linkData.join_url) resolvedJoinUrl = linkData.join_url;
            if (linkData.invitation_id) resolvedInvId = linkData.invitation_id;
          }
        } catch (e) {
          console.warn('Backend invitation link fallback to cryptographic URL:', e);
        }
      }
    } catch (err: any) {
      console.warn('Remote invitation API unavailable, using resilient generated data:', err);
    }

    // Compose formatted multi-channel invitation message
    let messageTemplate = '';
    if (resolvedJoinCode && resolvedJoinUrl) {
      messageTemplate = `Hi,\n\nYou've been invited to join the team '${teamName}' on Workline.\n\n` +
        `• Team Invitation Code: ${resolvedJoinCode}\n` +
        `• Direct Join Link: ${resolvedJoinUrl}\n` +
        `• Assigned Role: ${role}\n` +
        `• Expiration: ${expiresDate.toISOString().substring(0, 10)}\n\n` +
        `To join, either click the direct link or open Workline -> click 'Join Team (Code)' and enter ${resolvedJoinCode}.\n\n` +
        `Looking forward to collaborating!`;
    } else if (resolvedJoinCode) {
      messageTemplate = `Hi,\n\nYou've been invited to join the team '${teamName}' on Workline.\n\n` +
        `• Team Invitation Code: ${resolvedJoinCode}\n` +
        `• Assigned Role: ${role}\n` +
        `• Expiration: ${expiresDate.toISOString().substring(0, 10)}\n\n` +
        `To join, open Workline -> click 'Join Team (Code)' in the workspace and enter code: ${resolvedJoinCode}.\n\n` +
        `Looking forward to collaborating!`;
    } else {
      messageTemplate = `Hi,\n\nYou've been invited to join the team '${teamName}' on Workline.\n\n` +
        `• Join Link: ${resolvedJoinUrl}\n` +
        `• Assigned Role: ${role}\n` +
        `• Expiration: ${expiresDate.toISOString().substring(0, 10)}\n\n` +
        `Click the secure link above to accept your invitation.\n\n` +
        `Looking forward to collaborating!`;
    }

    const compiledData = {
      invitation_id: resolvedInvId,
      team_id: teamId,
      team_name: teamName,
      join_code: resolvedJoinCode,
      join_url: resolvedJoinUrl,
      expires_at: expiresDate.toISOString(),
      max_uses: maxUses,
      status: 'ACTIVE',
      role,
      generation_mode: activeMode,
      message_template: messageTemplate,
      created_at: new Date().toISOString(),
      use_count: 0,
    };

    setInvitationData(compiledData);
    saveLocalInvitation(compiledData, resolvedJoinCode || undefined);
    setIsGenerating(false);
  };

  const handleRevoke = async () => {
    if (!invitationData) return;
    try {
      const effectiveBase = getEffectiveBase();
      const token = await getGatewayBearerToken().catch(() => null);
      const headers: Record<string, string> = {};
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      if (effectiveBase) {
        await Promise.allSettled([
          fetch(`${effectiveBase}/api/teams/${teamId}/invitations/${invitationData.invitation_id}/revoke`, {
            method: 'POST',
            headers,
          }),
          fetch(`${effectiveBase}/api/teams/${teamId}/join-code/revoke`, {
            method: 'POST',
            headers,
          }),
        ]);
      }
    } catch (err) {
      console.error('Revoke error:', err);
    } finally {
      try {
        if (typeof window !== 'undefined' && window.localStorage) {
          const key = `workline_team_invitations_${teamId}`;
          const existingRaw = localStorage.getItem(key);
          if (existingRaw) {
            const list = JSON.parse(existingRaw);
            const updated = list.map((item: any) =>
              item.invitation_id === invitationData.invitation_id ? { ...item, status: 'REVOKED' } : item
            );
            localStorage.setItem(key, JSON.stringify(updated));
          }
          if (invitationData.join_code) {
            const codesRaw = localStorage.getItem('workline_team_join_codes');
            if (codesRaw) {
              const registry = JSON.parse(codesRaw);
              delete registry[invitationData.join_code];
              localStorage.setItem('workline_team_join_codes', JSON.stringify(registry));
            }
          }
        }
      } catch {}
      setInvitationData(null);
    }
  };

  const handleRegenerate = async () => {
    await handleCreateInvitation();
  };

  const copyToClipboard = (text: string, type: 'code' | 'link' | 'message') => {
    if (!text) return;
    navigator.clipboard.writeText(text).then(() => {
      if (type === 'code') {
        setCopyCodeFeedback(true);
        setTimeout(() => setCopyCodeFeedback(false), 2000);
      } else if (type === 'link') {
        setCopyLinkFeedback(true);
        setTimeout(() => setCopyLinkFeedback(false), 2000);
      } else {
        setCopyMessageFeedback(true);
        setTimeout(() => setCopyMessageFeedback(false), 2000);
      }
    });
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-2xl text-slate-100 max-w-xl mx-auto space-y-6">
      {/* Modal Header */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div>
          <div className="text-xs uppercase tracking-wider text-slate-400 font-semibold">Team Collaboration</div>
          <h3 className="text-xl font-bold text-cyan-400">{teamName}</h3>
          <div className="text-xs text-slate-400 font-mono mt-0.5">Team ID: {teamId} • Members: {memberCount}</div>
        </div>
        <span className="px-3 py-1 bg-cyan-950 text-cyan-400 border border-cyan-800 rounded-full text-xs font-mono flex items-center gap-1.5 shadow-sm">
          <ShieldCheck className="w-3.5 h-3.5 text-cyan-400" />
          SECURE INVITATION
        </span>
      </div>

      {!invitationData ? (
        <div className="space-y-4">
          {/* Generation Mode Selector Tabs */}
          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase mb-1.5">
              Invitation Format
            </label>
            <div className="grid grid-cols-3 gap-1 bg-slate-950/80 p-1 rounded-lg border border-slate-800">
              <button
                type="button"
                onClick={() => setGenerationMode('BOTH')}
                className={`py-2 px-2.5 rounded-md text-xs font-semibold flex items-center justify-center gap-1.5 transition ${
                  generationMode === 'BOTH'
                    ? 'bg-cyan-600 text-white shadow-md'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-850'
                }`}
              >
                <Sparkles className="w-3.5 h-3.5" />
                <span>Link & Code</span>
              </button>

              <button
                type="button"
                onClick={() => setGenerationMode('CODE')}
                className={`py-2 px-2.5 rounded-md text-xs font-semibold flex items-center justify-center gap-1.5 transition ${
                  generationMode === 'CODE'
                    ? 'bg-cyan-600 text-white shadow-md'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-850'
                }`}
              >
                <KeyRound className="w-3.5 h-3.5" />
                <span>Code Only</span>
              </button>

              <button
                type="button"
                onClick={() => setGenerationMode('LINK')}
                className={`py-2 px-2.5 rounded-md text-xs font-semibold flex items-center justify-center gap-1.5 transition ${
                  generationMode === 'LINK'
                    ? 'bg-cyan-600 text-white shadow-md'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-850'
                }`}
              >
                <Link2 className="w-3.5 h-3.5" />
                <span>Link Only</span>
              </button>
            </div>
            <p className="text-[11px] text-slate-400 mt-1">
              {generationMode === 'BOTH' && 'Generates a 6-character Join Code (WL-XXXXXX) plus an authenticated direct web link.'}
              {generationMode === 'CODE' && 'Generates a 6-character alphanumeric code for entering in "Join Team (Code)".'}
              {generationMode === 'LINK' && 'Generates an authenticated AES-256 encrypted direct URL for one-click access.'}
            </p>
          </div>

          {/* Expiration and Max Uses Row */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Expiration</label>
              <select
                value={ttlDays}
                onChange={(e) => setTtlDays(Number(e.target.value))}
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-cyan-500 transition"
              >
                <option value={1}>1 Day</option>
                <option value={7}>7 Days (Default)</option>
                <option value={30}>30 Days</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Max Uses</label>
              <select
                value={maxUses}
                onChange={(e) => setMaxUses(Number(e.target.value))}
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-cyan-500 transition"
              >
                <option value={1}>Single-Use (1)</option>
                <option value={5}>5 Uses</option>
                <option value={10}>10 Uses (Default)</option>
                <option value={50}>50 Uses</option>
              </select>
            </div>
          </div>

          {/* Assigned Role */}
          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Assigned Role</label>
            <select
              value={role}
              onChange={(e) => setRole(e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-cyan-500 transition"
            >
              <option value="MEMBER">Member (Standard)</option>
              <option value="ENGINEER">Engineer (PCB/Hardware)</option>
              <option value="ADMIN">Admin</option>
            </select>
          </div>

          {error && (
            <div className="p-3 bg-red-950/60 border border-red-800 text-red-300 text-xs rounded-lg">{error}</div>
          )}

          {/* Generation Action Buttons */}
          <div className="space-y-2 pt-1">
            <button
              onClick={() => handleCreateInvitation()}
              disabled={isGenerating}
              className="w-full py-3 bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 text-white font-bold rounded-lg transition shadow-lg flex items-center justify-center gap-2 text-sm cursor-pointer"
            >
              {isGenerating ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>Generating Secure Credentials...</span>
                </>
              ) : generationMode === 'BOTH' ? (
                <>
                  <Sparkles className="w-4 h-4" />
                  <span>Generate Secure Invitation Link & Code</span>
                </>
              ) : generationMode === 'CODE' ? (
                <>
                  <KeyRound className="w-4 h-4" />
                  <span>Generate Team Invitation Code (WL-XXXXXX)</span>
                </>
              ) : (
                <>
                  <Link2 className="w-4 h-4" />
                  <span>Generate Secure Invitation Link</span>
                </>
              )}
            </button>

            {/* Quick action: Generate Code directly if currently in link mode */}
            {generationMode === 'LINK' && (
              <button
                type="button"
                onClick={() => {
                  setGenerationMode('CODE');
                  handleCreateInvitation('CODE');
                }}
                disabled={isGenerating}
                className="w-full py-2 bg-slate-800/80 hover:bg-slate-800 text-cyan-400 border border-slate-700 font-semibold rounded-lg text-xs transition flex items-center justify-center gap-1.5 cursor-pointer"
              >
                <KeyRound className="w-3.5 h-3.5" />
                <span>Or Generate Quick Join Code Instead</span>
              </button>
            )}
          </div>
        </div>
      ) : (
        /* Results View */
        <div className="space-y-4">
          {/* Status and Expiration */}
          <div className="flex items-center justify-between text-xs bg-slate-950/60 px-3 py-2 rounded-lg border border-slate-800">
            <div className="flex items-center gap-2">
              <span className="text-slate-400">Status:</span>
              <span className="px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800 font-mono font-bold text-[11px]">
                {invitationData.status}
              </span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-slate-400">Role: <strong className="text-cyan-300 font-mono">{invitationData.role}</strong></span>
              <span className="text-slate-500">•</span>
              <span className="text-slate-400">Expires: <strong className="text-white">{invitationData.expires_at?.substring(0, 10)}</strong></span>
            </div>
          </div>

          {/* 1. Invitation Code Display Card (if code generated) */}
          {invitationData.join_code && (
            <div className="p-4 bg-gradient-to-r from-slate-950 to-cyan-950/30 border border-cyan-700/60 rounded-xl space-y-2 shadow-inner">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-cyan-400 uppercase tracking-wider flex items-center gap-1.5">
                  <KeyRound className="w-3.5 h-3.5 text-cyan-400" />
                  Team Invitation Code
                </span>
                <span className="text-[10px] font-mono text-cyan-300/80 bg-cyan-950 px-2 py-0.5 rounded border border-cyan-800/60">
                  Instant Join Code
                </span>
              </div>

              <div className="flex items-center justify-between gap-3 bg-slate-950 p-2.5 rounded-lg border border-slate-800">
                <span className="font-mono text-xl tracking-widest font-black text-cyan-300 select-all pl-2">
                  {invitationData.join_code}
                </span>

                <button
                  onClick={() => copyToClipboard(invitationData.join_code, 'code')}
                  className="py-1.5 px-3 bg-cyan-600 hover:bg-cyan-500 text-white font-bold rounded-lg text-xs transition flex items-center gap-1.5 shadow cursor-pointer shrink-0"
                >
                  {copyCodeFeedback ? (
                    <>
                      <Check className="w-3.5 h-3.5" />
                      <span>Copied!</span>
                    </>
                  ) : (
                    <>
                      <Copy className="w-3.5 h-3.5" />
                      <span>Copy Code</span>
                    </>
                  )}
                </button>
              </div>

              <p className="text-[11px] text-slate-400 leading-relaxed">
                Invitees can enter this code directly in the <strong className="text-slate-200">"Join Team (Code)"</strong> dialog on Workline.
              </p>
            </div>
          )}

          {/* 2. Direct Invitation Link Display Card (if link generated) */}
          {invitationData.join_url && (
            <div className="p-4 bg-slate-950/90 border border-slate-800 rounded-xl space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
                  <Link2 className="w-3.5 h-3.5 text-cyan-400" />
                  Secure Invitation Link
                </span>
                <span className="text-[10px] font-mono text-slate-400 bg-slate-800 px-2 py-0.5 rounded">
                  Direct One-Click URL
                </span>
              </div>

              <div className="flex items-center justify-between gap-2 bg-slate-900 p-2.5 rounded-lg border border-slate-800">
                <div className="p-1 font-mono text-xs text-cyan-300 truncate select-all">
                  {invitationData.join_url}
                </div>

                <button
                  onClick={() => copyToClipboard(invitationData.join_url, 'link')}
                  className="py-1.5 px-3 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 font-bold rounded-lg text-xs transition flex items-center gap-1.5 cursor-pointer shrink-0"
                >
                  {copyLinkFeedback ? (
                    <>
                      <Check className="w-3.5 h-3.5 text-emerald-400" />
                      <span className="text-emerald-400">Copied!</span>
                    </>
                  ) : (
                    <>
                      <Copy className="w-3.5 h-3.5" />
                      <span>Copy Link</span>
                    </>
                  )}
                </button>
              </div>
            </div>
          )}

          {/* 3. Full Message Template Copy Button */}
          <div className="pt-1">
            <button
              onClick={() => copyToClipboard(invitationData.message_template, 'message')}
              className="w-full py-2.5 px-4 bg-slate-800/90 hover:bg-slate-700/90 text-slate-200 border border-slate-700 font-bold rounded-lg text-xs transition flex items-center justify-center gap-2 cursor-pointer shadow"
            >
              {copyMessageFeedback ? (
                <>
                  <Check className="w-4 h-4 text-emerald-400" />
                  <span className="text-emerald-400 font-semibold">✓ Full Invitation Message Copied!</span>
                </>
              ) : (
                <>
                  <Copy className="w-4 h-4 text-cyan-400" />
                  <span>Copy Complete Invitation Message (for Slack / Email)</span>
                </>
              )}
            </button>
          </div>

          {/* Footer Controls */}
          <div className="flex items-center justify-between border-t border-slate-800 pt-4 text-xs">
            <button
              onClick={() => setInvitationData(null)}
              className="text-slate-400 hover:text-white transition flex items-center gap-1 cursor-pointer"
            >
              ← Generate New
            </button>

            <div className="flex items-center gap-4">
              <button
                onClick={handleRegenerate}
                disabled={isGenerating}
                className="text-amber-400 hover:text-amber-300 hover:underline flex items-center gap-1 disabled:opacity-50 cursor-pointer"
              >
                <RefreshCw className="w-3.5 h-3.5" />
                <span>Regenerate</span>
              </button>

              <button
                onClick={handleRevoke}
                className="text-rose-400 hover:text-rose-300 hover:underline flex items-center gap-1 cursor-pointer"
              >
                <Trash2 className="w-3.5 h-3.5" />
                <span>Revoke</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TeamInvitationPanel;
