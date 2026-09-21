'use client';

import React, { useState, useRef, useEffect } from 'react';
import { useUser, useClerk, SignInButton } from '@clerk/nextjs';
import { useCognitoAuth } from '@/lib/CognitoAuthContext';
import { LogOut, ChevronUp, ChevronDown, UserCheck, Settings, ShieldCheck, User } from 'lucide-react';

interface UnifiedUserButtonProps {
  direction?: 'up' | 'down';
  className?: string;
}

export default function UnifiedUserButton({
  direction = 'up',
  className = '',
}: UnifiedUserButtonProps) {
  const { user: clerkUser, isSignedIn: isClerkSignedIn } = useUser();
  const { signOut: clerkSignOut, openUserProfile } = useClerk();
  const { isSignedIn: isCognitoSignedIn, userEmail: cognitoEmail, signOut: cognitoSignOut } = useCognitoAuth();

  const [dropdownOpen, setDropdownOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  // Close dropdown on outside click
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setDropdownOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const isSignedIn = isClerkSignedIn || isCognitoSignedIn;

  if (!isSignedIn) {
    return (
      <SignInButton mode="modal">
        <button
          className={`flex items-center justify-center gap-2 py-2 px-3 rounded-lg border border-slate-700 bg-slate-900 hover:bg-slate-800 hover:border-slate-600 text-slate-200 text-xs font-mono font-semibold transition-all cursor-pointer shadow-sm ${className}`}
        >
          <User className="w-3.5 h-3.5 text-indigo-400" />
          <span>Sign In / Register</span>
        </button>
      </SignInButton>
    );
  }

  // Determine user identity details
  let displayName = 'Engineer';
  let displayEmail = '';
  let avatarUrl: string | null = null;
  let providerLabel = 'Clerk Verified';

  if (isClerkSignedIn && clerkUser) {
    displayEmail = clerkUser.primaryEmailAddress?.emailAddress || '';
    displayName = clerkUser.fullName || clerkUser.username || displayEmail.split('@')[0] || 'Engineer';
    avatarUrl = clerkUser.imageUrl || null;

    // Detect OAuth provider
    const externalAccounts = clerkUser.externalAccounts || [];
    const isGoogle = externalAccounts.some((acc: any) => acc.provider?.includes('google'));
    const isGithub = externalAccounts.some((acc: any) => acc.provider?.includes('github'));
    if (isGoogle) providerLabel = 'Google Verified';
    else if (isGithub) providerLabel = 'GitHub Verified';
    else providerLabel = 'Clerk Verified';
  } else if (isCognitoSignedIn) {
    displayEmail = cognitoEmail || '';
    displayName = cognitoEmail?.split('@')[0] || 'Cognito User';
    providerLabel = 'AWS Cognito Verified';
  }

  const initials = (displayName || displayEmail || 'US')
    .slice(0, 2)
    .toUpperCase();

  const handleSignOut = async () => {
    setDropdownOpen(false);
    if (isClerkSignedIn) {
      await clerkSignOut();
    }
    if (isCognitoSignedIn) {
      cognitoSignOut();
    }
    // Also clear session storage
    if (typeof window !== 'undefined') {
      localStorage.removeItem('workline_cognito_session');
    }
  };

  return (
    <div className={`relative ${className}`} ref={menuRef}>
      <button
        onClick={() => setDropdownOpen(!dropdownOpen)}
        className="group flex items-center justify-between gap-2 py-1.5 px-2.5 rounded-lg border border-slate-700/90 bg-slate-900 hover:bg-slate-850 hover:border-slate-500 transition-all cursor-pointer shadow-sm w-full"
        title={displayEmail || displayName}
      >
        <div className="flex items-center gap-2 min-w-0">
          {avatarUrl ? (
            <img
              src={avatarUrl}
              alt={displayName}
              className="w-6 h-6 rounded-full object-cover shrink-0 border border-indigo-500/40"
            />
          ) : (
            <div className="w-6 h-6 rounded-full bg-gradient-to-tr from-indigo-500 to-violet-500 flex items-center justify-center text-[10px] font-bold text-white uppercase shrink-0 shadow-inner">
              {initials}
            </div>
          )}
          <div className="flex flex-col text-left overflow-hidden min-w-0">
            <span className="text-xs font-mono font-medium text-slate-100 group-hover:text-white truncate max-w-[140px]">
              {displayName}
            </span>
            <span className="text-[10px] text-slate-400 font-mono truncate max-w-[140px]">
              {displayEmail}
            </span>
          </div>
        </div>

        {/* Direction-aware chevron arrow: ChevronUp at bottom of screen, ChevronDown at top */}
        <div className="p-1 rounded bg-slate-800 border border-slate-650 group-hover:bg-slate-700 group-hover:border-slate-500 transition-colors shrink-0 flex items-center justify-center">
          {direction === 'up' ? (
            <ChevronUp className="w-3.5 h-3.5 text-white stroke-[2.5]" />
          ) : (
            <ChevronDown className="w-3.5 h-3.5 text-white stroke-[2.5]" />
          )}
        </div>
      </button>

      {/* Upward popping dropdown when direction === 'up' */}
      {dropdownOpen && (
        <div
          className={`absolute ${
            direction === 'up' ? 'bottom-full mb-2' : 'top-full mt-2'
          } left-0 right-0 w-full min-w-[240px] rounded-xl border border-slate-700 bg-slate-900/98 p-2 shadow-2xl backdrop-blur-xl z-50 animate-fade-in`}
        >
          <div className="px-3 py-2 border-b border-slate-800">
            <p className="text-[10px] font-mono uppercase text-slate-400">Signed In As</p>
            <p className="text-xs font-semibold text-white truncate">{displayName}</p>
            <p className="text-[11px] text-slate-300 font-mono truncate">{displayEmail}</p>
            <div className="mt-1 flex items-center gap-1.5 text-[10px] text-emerald-400 font-mono">
              <UserCheck className="w-3.5 h-3.5 text-emerald-400" />
              <span>{providerLabel}</span>
            </div>
          </div>

          <div className="py-1 space-y-0.5">
            {isClerkSignedIn && (
              <button
                onClick={() => {
                  setDropdownOpen(false);
                  openUserProfile?.();
                }}
                className="w-full flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium text-slate-300 hover:bg-slate-800 hover:text-white transition-colors cursor-pointer"
              >
                <Settings className="w-3.5 h-3.5 text-slate-400" />
                <span>Manage Profile & Security</span>
              </button>
            )}

            <button
              onClick={handleSignOut}
              className="w-full flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium text-rose-400 hover:bg-rose-950/50 hover:text-rose-300 transition-colors cursor-pointer"
            >
              <LogOut className="w-3.5 h-3.5" />
              <span>Sign Out</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
