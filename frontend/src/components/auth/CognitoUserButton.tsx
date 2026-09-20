'use client';

import React, { useState, useRef, useEffect } from 'react';
import { useCognitoAuth } from '@/lib/CognitoAuthContext';
import CognitoAuthModal from './CognitoAuthModal';
import { ShieldCheck, LogOut, ChevronUp, UserCheck } from 'lucide-react';

interface CognitoUserButtonProps {
  direction?: 'up' | 'down';
  className?: string;
}

export default function CognitoUserButton({
  direction = 'up',
  className = '',
}: CognitoUserButtonProps) {
  const { isSignedIn, userEmail, signOut } = useCognitoAuth();
  const [modalOpen, setModalOpen] = useState(false);
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

  if (!isSignedIn) {
    return (
      <>
        <button
          onClick={() => setModalOpen(true)}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold font-mono transition-all shadow-md shadow-indigo-600/20 cursor-pointer"
        >
          <ShieldCheck className="w-3.5 h-3.5" />
          <span>Cognito Auth</span>
        </button>
        <CognitoAuthModal isOpen={modalOpen} onClose={() => setModalOpen(false)} />
      </>
    );
  }

  const initials = (userEmail || 'TE').slice(0, 2).toUpperCase();

  return (
    <div className={`relative ${className}`} ref={menuRef}>
      <button
        onClick={() => setDropdownOpen(!dropdownOpen)}
        className="group flex items-center justify-between gap-2 py-1.5 px-2.5 rounded-lg border border-slate-700/90 bg-slate-900 hover:bg-slate-850 hover:border-slate-500 transition-all cursor-pointer shadow-sm w-full"
        title={userEmail || 'User Account'}
      >
        <div className="flex items-center gap-2 min-w-0">
          <div className="w-6 h-6 rounded-full bg-gradient-to-tr from-indigo-500 to-violet-500 flex items-center justify-center text-[10px] font-bold text-white uppercase shrink-0 shadow-inner">
            {initials}
          </div>
          <span className="text-xs font-mono font-medium text-slate-100 group-hover:text-white truncate max-w-[145px]">
            {userEmail}
          </span>
        </div>

        {/* Clearly visible up arrow sign */}
        <div className="p-1 rounded bg-slate-800 border border-slate-650 group-hover:bg-slate-700 group-hover:border-slate-500 transition-colors shrink-0 flex items-center justify-center">
          <ChevronUp className="w-3.5 h-3.5 text-white stroke-[2.5]" />
        </div>
      </button>

      {dropdownOpen && (
        <div
          className={`absolute ${
            direction === 'up' ? 'bottom-full mb-2' : 'top-full mt-2'
          } right-0 w-60 rounded-xl border border-slate-700 bg-slate-900/98 p-2 shadow-2xl backdrop-blur-xl z-50 animate-fade-in`}
        >
          <div className="px-3 py-2 border-b border-slate-800">
            <p className="text-[10px] font-mono uppercase text-slate-400">Signed in as</p>
            <p className="text-xs font-semibold text-white truncate">{userEmail}</p>
            <div className="mt-1 flex items-center gap-1.5 text-[10px] text-emerald-400 font-mono">
              <UserCheck className="w-3.5 h-3.5 text-emerald-400" />
              <span>AWS Cognito Verified</span>
            </div>
          </div>
          <button
            onClick={() => {
              setDropdownOpen(false);
              signOut();
            }}
            className="w-full mt-1.5 flex items-center gap-2 px-3 py-2 rounded-lg text-xs font-medium text-rose-400 hover:bg-rose-950/50 hover:text-rose-300 transition-colors cursor-pointer"
          >
            <LogOut className="w-3.5 h-3.5" />
            <span>Sign Out</span>
          </button>
        </div>
      )}
    </div>
  );
}
