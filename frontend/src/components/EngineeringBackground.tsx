'use client';

import React from 'react';

interface EngineeringBackgroundProps {
  variant?: 'hero' | 'subtle';
}

export default function EngineeringBackground({
  variant = 'hero',
}: EngineeringBackgroundProps) {
  if (variant === 'subtle') {
    return (
      <div className="pointer-events-none fixed inset-0 z-0 overflow-hidden select-none">
        {/* Subtle background image */}
        <div 
          className="absolute inset-0 bg-cover bg-center bg-no-repeat opacity-[0.06] mix-blend-luminosity filter blur-[4px]"
          style={{ backgroundImage: "url('/engineering-bg.jpg')" }}
        />
        {/* Subtle CAD Blueprint Grid */}
        <div className="absolute inset-0 cyber-grid opacity-30" />
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-slate-950/50 to-slate-950/90" />
      </div>
    );
  }

  return (
    <div className="pointer-events-none absolute inset-0 overflow-hidden select-none z-0">
      {/* 1. Primary Engineering Wallpaper with ~30% Blur (4px blur with scale to prevent edge bleed) */}
      <div
        className="absolute inset-0 bg-cover bg-center bg-no-repeat opacity-65 md:opacity-75 filter blur-[4px] transform scale-105 transition-transform duration-700 ease-out"
        style={{ backgroundImage: "url('/engineering-bg.jpg')" }}
      />

      {/* 2. Seamless Technical Vignette & Spotlight Gradients */}
      {/* Central radial gradient to keep foreground typography ultra-sharp and legible */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_rgba(3,7,18,0.52)_0%,_rgba(3,7,18,0.78)_60%,_rgba(3,7,18,0.95)_100%)]" />

      {/* Top & Bottom Bleed Gradients for seamless header/footer integration */}
      <div className="absolute inset-x-0 top-0 h-24 bg-gradient-to-b from-slate-950 via-slate-950/70 to-transparent" />
      <div className="absolute inset-x-0 bottom-0 h-28 bg-gradient-to-t from-slate-950 via-slate-950/80 to-transparent" />

      {/* 3. Subtle CAD Matrix Grid */}
      <div className="absolute inset-0 cyber-grid opacity-30 mix-blend-screen" />

      {/* 4. Soft Ambient Neon Lighting Accent Orbs */}
      <div className="absolute top-1/4 left-1/12 w-80 h-80 rounded-full bg-cyan-500/10 blur-[100px] pointer-events-none" />
      <div className="absolute top-1/3 right-1/12 w-80 h-80 rounded-full bg-indigo-600/15 blur-[110px] pointer-events-none" />
    </div>
  );
}
