'use client';

import React, { use } from 'react';
import { SignIn } from '@clerk/nextjs';
import { Key } from 'lucide-react';

export const dynamic = 'force-dynamic';

interface LoginPageProps {
  searchParams: Promise<{ redirect?: string }>;
}

export default function LoginPage({ searchParams }: LoginPageProps) {
  // Unwrap searchParams using React.use()
  const params = use(searchParams);
  const forceRedirectUrl = params.redirect || '/';

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-zinc-950 text-slate-100 p-4 font-mono">
      <div className="glass-panel p-8 border border-zinc-800 bg-zinc-950/80 rounded-xl max-w-md w-full flex flex-col items-center shadow-2xl relative overflow-hidden">
        {/* Subtle diagonal hover sweeping gradient */}
        <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/0 via-cyan-500/5 to-cyan-500/0 -translate-x-full hover:translate-x-full transition-all duration-1000 pointer-events-none" />

        <div className="flex items-center gap-2 mb-6">
          <Key className="w-5 h-5 text-cyan-400 animate-pulse" />
          <h2 className="text-sm font-extrabold uppercase tracking-[0.2em] bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">
            WORKLINE LOGIN
          </h2>
        </div>

        <SignIn 
          forceRedirectUrl={forceRedirectUrl} 
          signUpForceRedirectUrl={forceRedirectUrl}
        />
      </div>
    </div>
  );
}
