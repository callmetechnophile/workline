'use client';

import React, { useState, useRef, useEffect } from 'react';
import { useCognitoAuth } from '@/lib/CognitoAuthContext';
import CognitoAuthModal from './CognitoAuthModal';
import { ShieldCheck, LogOut, ChevronDown, UserCheck } from 'lucide-react';

export default function CognitoUserButton() {
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

  const initials = (userEmail || 'U').slice(0, 2).toUpperCase();

  return (
    <div className="relative" ref={menuRef}>
      <button
        onClick={() => setDropdownOpen(!dropdownOpen)}
        className="flex items-center gap-2 py-1 px-2 rounded-lg border border-slate-800 bg-slate-900/80 hover:bg-slate-800/80 transition-all cursor-pointer"
      >
        <div className="w-6 h-6 rounded-full bg-gradient-to-tr from-indigo-600 to-violet-500 flex items-center justify-center text-[10px] font-bold text-white uppercase">
          {initials}
        </div>
        <span className="text-xs font-mono text-slate-200 hidden md:inline max-w-[130px] truncate">
          {userEmail}
        </span>
        <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
      </button>

      {dropdownOpen && (
        <div className="absolute right-0 mt-2 w-56 rounded-xl border border-slate-800 bg-slate-900/95 p-2 shadow-2xl backdrop-blur-xl z-50 animate-fade-in">
          <div className="px-3 py-2 border-b border-slate-800">
            <p className="text-[10px] font-mono uppercase text-slate-500">Signed in as</p>
            <p className="text-xs font-semibold text-slate-200 truncate">{userEmail}</p>
            <div className="mt-1 flex items-center gap-1 text-[10px] text-emerald-400 font-mono">
              <UserCheck className="w-3 h-3 text-emerald-500" />
              <span>AWS Cognito Verified</span>
            </div>
          </div>
          <button
            onClick={() => {
              setDropdownOpen(false);
              signOut();
            }}
            className="w-full mt-1.5 flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs text-rose-400 hover:bg-rose-950/40 hover:text-rose-300 transition-colors cursor-pointer"
          >
            <LogOut className="w-3.5 h-3.5" />
            <span>Sign Out</span>
          </button>
        </div>
      )}
    </div>
  );
}
