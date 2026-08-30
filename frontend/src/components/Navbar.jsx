import React from 'react';
import { ShieldAlert, Activity, Sun, Moon } from 'lucide-react';

export default function Navbar({ activeDataset, theme = 'dark', onToggleTheme }) {
  const stateName = activeDataset?.state || 'Punjab';
  const districtName = activeDataset?.district || 'Ludhiana';
  const sanctionedCount = activeDataset?.sanctioned_count || 220;

  return (
    <header className="shrink-0 w-full bg-[#090A0B] border-b border-zinc-800/80 px-6 py-3.5 z-50 shadow-md">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-3">
        {/* Left Brand & Title */}
        <div className="flex items-center space-x-3.5">
          <div className="w-10 h-10 rounded-xl bg-[#121315] flex items-center justify-center text-white shrink-0 shadow-md shadow-black/40 button-press-effect border border-zinc-700/80">
            <ShieldAlert className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="flex items-center space-x-2.5">
              <h1 className="text-base font-bold text-white tracking-tight font-sans">
                MPLAD Intelligence
              </h1>
              <span className="text-[10px] uppercase font-mono font-bold px-2.5 py-0.5 rounded-full bg-[#121315] text-zinc-300 border border-zinc-800">
                GOI Nodal Cell
              </span>
            </div>
            <p className="text-xs text-zinc-400 font-sans mt-0.5">
              AI-Assisted Project Integrity & Risk Prioritization Platform
            </p>
          </div>
        </div>

        {/* Center Operational Context - Dynamic State & District */}
        <div className="hidden lg:flex items-center space-x-2.5 bg-[#121315] px-4 py-1.5 rounded-full border border-zinc-800/80 text-xs text-zinc-300 font-sans shadow-2xs">
          <span className="text-white font-bold text-[11px] font-mono">JURISDICTION:</span>
          <span className="font-semibold text-white uppercase">{stateName}</span>
          <span className="text-zinc-600">•</span>
          <span className="font-semibold text-white uppercase">{districtName} DISTRICT</span>
          <span className="text-zinc-600">•</span>
          <span className="text-zinc-400 font-mono text-[11px]">18TH LOK SABHA</span>
        </div>

        {/* Right Status, Theme Toggle & Profile */}
        <div className="flex items-center space-x-4 text-xs">
          {/* Global Theme Toggle Button */}
          {onToggleTheme && (
            <button
              onClick={onToggleTheme}
              title={theme === 'light' ? 'Switch to Dark Theme' : 'Switch to Light Theme'}
              className="flex items-center space-x-1.5 px-3 py-1 rounded-full font-mono text-[11px] font-bold transition-all button-press-effect cursor-pointer border bg-[#121315] text-zinc-200 border-zinc-700/80 hover:bg-[#1A1B1E] shadow-2xs"
            >
              {theme === 'light' ? (
                <>
                  <Sun className="w-3.5 h-3.5 text-amber-500" />
                  <span>Light</span>
                </>
              ) : (
                <>
                  <Moon className="w-3.5 h-3.5 text-indigo-300" />
                  <span>Dark</span>
                </>
              )}
            </button>
          )}

          <div className="flex items-center space-x-2 bg-emerald-950/60 text-emerald-300 border border-emerald-800/60 px-3.5 py-1 rounded-full font-mono text-[11px] shadow-2xs font-bold">
            <Activity className="w-3.5 h-3.5 text-emerald-400 animate-pulse" />
            <span>{sanctionedCount} WORKS INGESTED</span>
          </div>

          <div className="hidden sm:flex flex-col text-right font-sans">
            <span className="text-white font-bold text-xs">State Nodal Officer</span>
            <span className="text-zinc-400 text-[11px]">{stateName} Monitoring Cell</span>
          </div>
        </div>
      </div>
    </header>
  );
}
