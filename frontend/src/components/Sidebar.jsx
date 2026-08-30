import React from 'react';
import { 
  LayoutDashboard, 
  AlertTriangle, 
  BarChart3, 
  FileSearch, 
  Database, 
  History,
  ShieldCheck,
  Activity
} from 'lucide-react';

export default function Sidebar({ activeTab, setActiveTab, activeDataset, onNavigateToWorkspace }) {
  const sanctionedCount = activeDataset?.sanctioned_count ? String(activeDataset.sanctioned_count) : 'Queue';
  const idaCount = activeDataset?.ida_count ? `${activeDataset.ida_count} IDAs` : 'District';

  const navItems = [
    { key: 'COMMAND_CENTER', label: 'Command Center', icon: LayoutDashboard, enabled: true },
    { key: 'RISK_QUEUE', label: 'Risk Priority Queue', icon: AlertTriangle, enabled: true, count: sanctionedCount },
    { key: 'DISTRICT_ANALYTICS', label: 'District Analytics', icon: BarChart3, enabled: true, count: idaCount },
    { key: 'INVESTIGATION_WORKSPACE', label: 'Investigation Workspace', icon: FileSearch, enabled: true, count: 'Inspect' },
    { key: 'DATA_LINEAGE', label: 'Data Lineage & Management', icon: Database, enabled: true, count: 'Library' },
    { key: 'AUDIT_LOG', label: 'Audit Log & History', icon: History, enabled: true, count: 'Session' },
  ];

  return (
    <aside className="shrink-0 w-64 h-full bg-[#0A0B0D] text-white border-r border-zinc-800/70 p-4 flex flex-col justify-between hidden md:flex overflow-y-auto font-sans z-40 shadow-xl">
      <div className="space-y-6">
        <div>
          <div className="px-3 text-[11px] font-mono font-bold uppercase tracking-wider text-zinc-500 mb-3 flex items-center justify-between">
            <span>OPERATIONAL MODULES</span>
            <span className="w-1.5 h-1.5 rounded-full bg-zinc-400"></span>
          </div>
          <nav className="space-y-1.5">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.key;
              
              return (
                <button
                  key={item.key}
                  onClick={() => {
                    // Use the dedicated workspace handler (if provided) to clear stale selectedWorkId
                    if (item.key === 'INVESTIGATION_WORKSPACE' && onNavigateToWorkspace) {
                      onNavigateToWorkspace();
                    } else {
                      setActiveTab(item.key);
                    }
                  }}
                  className={`w-full flex items-center justify-between px-3 py-2.5 rounded-xl text-xs transition-all duration-200 text-left font-sans button-press-effect relative ${
                    isActive
                      ? 'bg-[#18191D] text-white font-bold shadow-xs border border-zinc-700/80'
                      : 'text-zinc-400 hover:text-white hover:bg-[#141518] font-medium'
                  }`}
                >
                  <div className="flex items-center space-x-3">
                    {isActive && <span className="absolute left-0 top-2.5 bottom-2.5 w-1 bg-white rounded-r-md"></span>}
                    <Icon className={`w-4 h-4 ${isActive ? 'text-white' : 'text-zinc-400'}`} />
                    <span className={isActive ? 'pl-1' : ''}>{item.label}</span>
                  </div>
                  {isActive ? (
                    <span className="w-1.5 h-1.5 rounded-full bg-white animate-pulse"></span>
                  ) : item.count ? (
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-[#141518] text-zinc-400 border border-zinc-800">
                      {item.count}
                    </span>
                  ) : null}
                </button>
              );
            })}
          </nav>
        </div>

        {/* System Architecture Meta Card */}
        <div className="p-4 bg-[#141518] border border-zinc-800/80 rounded-2xl space-y-2.5 shadow-inner">
          <div className="text-[11px] font-mono font-bold text-zinc-300 uppercase flex items-center justify-between">
            <span className="flex items-center space-x-1.5">
              <Activity className="w-3.5 h-3.5 text-emerald-400" />
              <span>SYSTEM STATE</span>
            </span>
            <span className="text-[9px] px-2 py-0.5 bg-emerald-500/15 text-emerald-300 rounded-full border border-emerald-500/30 font-bold">ONLINE</span>
          </div>
          <p className="text-[11px] text-zinc-400 leading-normal font-sans">
            FastAPI REST API connected live to SQLite database (<span className="text-zinc-200 font-mono">mplads.db</span>).
          </p>
        </div>
      </div>

      {/* Footer Branding Notice */}
      <div className="px-3 pt-4 border-t border-zinc-800/70 text-[10px] text-zinc-500 font-mono flex items-center justify-between">
        <span className="flex items-center space-x-1">
          <ShieldCheck className="w-3.5 h-3.5 text-zinc-300" />
          <span>SIH26102 • MVP</span>
        </span>
        <span>v2.0.0</span>
      </div>
    </aside>
  );
}
