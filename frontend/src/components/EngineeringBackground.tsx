'use client';

import React from 'react';
import { Cpu, Bot, Code2, Brain, Activity, Terminal, Layers, Sparkles } from 'lucide-react';

interface EngineeringBackgroundProps {
  variant?: 'hero' | 'subtle';
  showPills?: boolean;
}

export default function EngineeringBackground({
  variant = 'hero',
  showPills = true,
}: EngineeringBackgroundProps) {
  if (variant === 'subtle') {
    return (
      <div className="pointer-events-none fixed inset-0 z-0 overflow-hidden select-none">
        {/* Subtle background image */}
        <div 
          className="absolute inset-0 bg-cover bg-center bg-no-repeat opacity-[0.06] mix-blend-luminosity filter blur-[1px]"
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
      {/* 1. Primary Rich Engineering Wallpaper (Robotics, Electronics, Code, AI) */}
      <div
        className="absolute inset-0 bg-cover bg-center bg-no-repeat opacity-60 md:opacity-70 transform scale-[1.02] transition-transform duration-1000 ease-out"
        style={{ backgroundImage: "url('/engineering-bg.jpg')" }}
      />

      {/* 2. Technical Blueprint Overlay Gradients */}
      {/* Radial vignette spotlight to keep center text high-contrast and legible */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_rgba(3,7,18,0.55)_0%,_rgba(3,7,18,0.85)_65%,_rgba(3,7,18,0.98)_100%)]" />

      {/* Top & Bottom Bleed Gradients for seamless header/footer integration */}
      <div className="absolute inset-x-0 top-0 h-32 bg-gradient-to-b from-slate-950 via-slate-950/80 to-transparent" />
      <div className="absolute inset-x-0 bottom-0 h-44 bg-gradient-to-t from-slate-950 via-slate-950/90 to-transparent" />

      {/* 3. Subtle CAD Matrix Grid & Crosshairs */}
      <div className="absolute inset-0 cyber-grid opacity-40 mix-blend-screen" />

      {/* 4. Ambient Colored Neon Glow Accents */}
      <div className="absolute top-1/4 left-1/10 w-96 h-96 rounded-full bg-cyan-500/10 blur-[120px] pointer-events-none" />
      <div className="absolute top-1/3 right-1/10 w-96 h-96 rounded-full bg-indigo-600/15 blur-[130px] pointer-events-none" />
      <div className="absolute bottom-1/4 left-1/3 w-80 h-80 rounded-full bg-purple-600/10 blur-[110px] pointer-events-none" />

      {/* 5. Engineering Blueprint Corner Coordinates & Telemetry */}
      <div className="hidden lg:flex justify-between items-center px-10 pt-20 text-[10px] font-mono text-cyan-500/40 tracking-widest uppercase">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <span className="inline-block w-1.5 h-1.5 rounded-full bg-cyan-400/60 animate-pulse" />
            <span>SYS_GRID: [45.12° N, 122.68° W]</span>
          </div>
          <div className="text-slate-500/50">CAD_CORE: v4.8.2 // LINEAGE R5</div>
        </div>

        <div className="space-y-1 text-right">
          <div className="text-indigo-400/50">DRC_VALIDATION: 0 ERRORS</div>
          <div className="text-slate-500/50">CLK_TREE: 240MHz PLL LOCKED</div>
        </div>
      </div>

      <div className="hidden lg:flex justify-between items-center px-10 pb-8 absolute bottom-0 inset-x-0 text-[10px] font-mono text-slate-500/40 tracking-wider">
        <div>PINN_LOSS: 1.84e-05 • THERMAL_TMAX: 48.2°C</div>
        <div>IEEE-1588 PTP • I2C / SPI / QSPI / CAN BUS</div>
      </div>

      {/* 6. Floating Engineering Category Badges (Robotics, Electronics, Code, AI) */}
      {showPills && (
        <div className="hidden xl:block">
          {/* Robotics Badge (Top Left) */}
          <div className="absolute top-28 left-8 p-2.5 rounded-lg bg-slate-950/80 border border-cyan-500/30 backdrop-blur-md shadow-lg shadow-cyan-950/30 text-cyan-300 flex items-center gap-2 text-xs font-mono">
            <div className="p-1 rounded bg-cyan-500/20 text-cyan-400">
              <Bot className="w-3.5 h-3.5" />
            </div>
            <div>
              <div className="font-bold text-[11px] tracking-wider text-cyan-200 uppercase">Robotics & Kinematics</div>
              <div className="text-[9px] text-cyan-400/70">6-DOF Inverse Dynamics</div>
            </div>
          </div>

          {/* Electronics Badge (Top Right) */}
          <div className="absolute top-28 right-8 p-2.5 rounded-lg bg-slate-950/80 border border-indigo-500/30 backdrop-blur-md shadow-lg shadow-indigo-950/30 text-indigo-300 flex items-center gap-2 text-xs font-mono">
            <div className="p-1 rounded bg-indigo-500/20 text-indigo-400">
              <Cpu className="w-3.5 h-3.5" />
            </div>
            <div>
              <div className="font-bold text-[11px] tracking-wider text-indigo-200 uppercase">Electronics & PCB</div>
              <div className="text-[9px] text-indigo-400/70">High-Speed Stackup & DRC</div>
            </div>
          </div>

          {/* Programming Badge (Bottom Left) */}
          <div className="absolute bottom-28 left-8 p-2.5 rounded-lg bg-slate-950/80 border border-emerald-500/30 backdrop-blur-md shadow-lg shadow-emerald-950/30 text-emerald-300 flex items-center gap-2 text-xs font-mono">
            <div className="p-1 rounded bg-emerald-500/20 text-emerald-400">
              <Code2 className="w-3.5 h-3.5" />
            </div>
            <div>
              <div className="font-bold text-[11px] tracking-wider text-emerald-200 uppercase">Firmware & Software</div>
              <div className="text-[9px] text-emerald-400/70">RTOS / Embedded C / HAL</div>
            </div>
          </div>

          {/* AI Intelligence Badge (Bottom Right) */}
          <div className="absolute bottom-28 right-8 p-2.5 rounded-lg bg-slate-950/80 border border-purple-500/30 backdrop-blur-md shadow-lg shadow-purple-950/30 text-purple-300 flex items-center gap-2 text-xs font-mono">
            <div className="p-1 rounded bg-purple-500/20 text-purple-400">
              <Brain className="w-3.5 h-3.5" />
            </div>
            <div>
              <div className="font-bold text-[11px] tracking-wider text-purple-200 uppercase">AI & Multi-Physics</div>
              <div className="text-[9px] text-purple-400/70">PINN Solvers & Optimization</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
