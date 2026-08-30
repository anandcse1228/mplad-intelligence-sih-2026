import React, { useState, useEffect, useMemo } from 'react';
import { 
  History, 
  Search, 
  CheckCircle2, 
  Clock, 
  Shield, 
  FileCheck, 
  UserCheck, 
  AlertTriangle,
  Info,
  Layers,
  Send,
  Trash2
} from 'lucide-react';
import { api } from '../api/client';

export default function AuditLogPage({ onSelectWorkForInvestigation }) {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterAction, setFilterAction] = useState('ALL');
  const [logsList, setLogsList] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchLogs = () => {
    setLoading(true);
    api.getAuditLogs({ page: 1, page_size: 100 })
      .then(res => {
        setLogsList(res.items || []);
        setLoading(false);
      })
      .catch(err => {
        console.error("Failed to fetch audit logs:", err);
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchLogs();
  }, []);

  const handleClearLogs = () => {
    if (window.confirm("Are you sure you want to clear the active audit trail in SQLite?")) {
      api.clearAuditLogs()
        .then(() => fetchLogs())
        .catch(err => alert(`Failed to clear logs: ${err.message}`));
    }
  };

  // Filtered audit logs
  const filteredLogs = useMemo(() => {
    return logsList.filter(log => {
      // Action Type Filter
      if (filterAction === 'VERIFICATION' && !(log.action_type || '').includes('VERIFICATION')) return false;
      if (filterAction === 'AUDIT' && !(log.action_type || '').includes('AUDIT')) return false;
      if (filterAction === 'NOTE' && !(log.action_type || '').includes('NOTE')) return false;
      if (filterAction === 'CLEARED' && !(log.action_type || '').includes('CLEARED')) return false;

      // Search Query
      if (searchTerm.trim() !== '') {
        const q = searchTerm.toLowerCase();
        const matchesWorkId = (log.work_id || '').toLowerCase().includes(q);
        const matchesAction = (log.action_type || '').toLowerCase().includes(q);
        const matchesDetails = (log.details || '').toLowerCase().includes(q);
        const matchesActor = (log.actor || '').toLowerCase().includes(q);
        return matchesWorkId || matchesAction || matchesDetails || matchesActor;
      }

      return true;
    });
  }, [logsList, filterAction, searchTerm]);

  return (
    <div className="space-y-6 font-sans selection:bg-slate-900 selection:text-white pb-6">
      
      {/* Header Context Banner */}
      <div className="deep-black-card rounded-2xl p-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2 text-xs text-zinc-400 font-semibold mb-1 font-mono">
            <History className="w-3.5 h-3.5 text-white" />
            <span>PAGE 6 • OFFICIAL SESSION AUDIT TRAIL & HISTORY</span>
          </div>
          <h1 className="text-xl font-bold text-white tracking-tight">
            Institutional Audit Log & Official Action History
          </h1>
          <p className="text-xs text-zinc-400 mt-1 max-w-3xl leading-relaxed">
            Real-time compliance audit log recording all officer review decisions, field verification dispatches, nodal audit requests, and notes persisted in SQLite database (<span className="font-mono text-zinc-200">audit_logs</span>).
          </p>
        </div>

        {/* Audit Status Badge & Clear Control */}
        <div className="flex items-center space-x-3 shrink-0">
          <div className="bg-[#17181B] border border-zinc-800 p-3.5 rounded-xl text-xs space-y-1 font-mono">
            <div className="flex items-center space-x-2 text-white font-semibold">
              <Shield className="w-4 h-4 text-white" />
              <span>{logsList.length} Audit Events</span>
            </div>
            <div className="text-[11px] text-zinc-400">
              <span>SQLite Database Persisted</span>
            </div>
          </div>

          <button
            onClick={handleClearLogs}
            className="px-4 py-2.5 rounded-xl bg-rose-950/80 hover:bg-rose-900 text-rose-300 border border-rose-800 text-xs font-semibold flex items-center space-x-1.5 transition-colors duration-150 font-sans shadow-2xs button-press-effect"
          >
            <Trash2 className="w-3.5 h-3.5" />
            <span>Reset Audit Trail</span>
          </button>
        </div>
      </div>

      {/* Main Container */}
      <div className="deep-black-card rounded-2xl p-6 space-y-4">
        
        {/* Controls Toolbar */}
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 border-b border-zinc-800/80 pb-4">
          <div className="flex flex-wrap items-center gap-3 flex-1">
            {/* Search Input */}
            <div className="relative flex-1 max-w-md">
              <Search className="w-3.5 h-3.5 text-zinc-400 absolute left-3 top-2.5" />
              <input
                type="text"
                placeholder="Search audit trail by Work ID, action, or officer..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full bg-[#17181B] border border-zinc-800 rounded-xl pl-8 pr-3 py-1.5 text-xs text-white placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-zinc-700 focus:border-zinc-700 transition-all"
              />
            </div>

            {/* Action Filter Pills */}
            <div className="flex items-center space-x-1.5 text-xs font-mono">
              <button
                onClick={() => setFilterAction('ALL')}
                className={`px-3 py-1.5 rounded-xl border text-xs font-semibold transition-all duration-150 button-press-effect ${
                  filterAction === 'ALL'
                    ? 'bg-white text-black border-white'
                    : 'bg-[#17181B] text-zinc-300 border-zinc-800 hover:bg-zinc-800'
                }`}
              >
                All Events ({logsList.length})
              </button>

              <button
                onClick={() => setFilterAction('VERIFICATION')}
                className={`px-3 py-1.5 rounded-xl border text-xs font-semibold transition-all duration-150 button-press-effect ${
                  filterAction === 'VERIFICATION'
                    ? 'bg-white text-black border-white'
                    : 'bg-[#17181B] text-zinc-300 border-zinc-800 hover:bg-zinc-800'
                }`}
              >
                Field Verification
              </button>

              <button
                onClick={() => setFilterAction('AUDIT')}
                className={`px-3 py-1.5 rounded-xl border text-xs font-semibold transition-all duration-150 button-press-effect ${
                  filterAction === 'AUDIT'
                    ? 'bg-amber-600 text-white border-amber-600'
                    : 'bg-[#17181B] text-zinc-300 border-zinc-800 hover:bg-zinc-800'
                }`}
              >
                Nodal Audit
              </button>

              <button
                onClick={() => setFilterAction('NOTE')}
                className={`px-3 py-1.5 rounded-xl border text-xs font-semibold transition-all duration-150 button-press-effect ${
                  filterAction === 'NOTE'
                    ? 'bg-sky-700 text-white border-sky-700'
                    : 'bg-[#17181B] text-zinc-300 border-zinc-800 hover:bg-zinc-800'
                }`}
              >
                Officer Notes
              </button>
            </div>
          </div>
        </div>

        {/* Audit Log Events List */}
        <div className="space-y-3">
          {loading ? (
            <div className="py-8 text-center text-zinc-500 font-mono text-xs">
              Loading audit event history from SQLite database...
            </div>
          ) : filteredLogs.length > 0 ? (
            filteredLogs.map((log, idx) => {
              const isVerification = (log.action_type || '').includes('FIELD VERIFICATION');
              const isAudit = (log.action_type || '').includes('AUDIT');
              const isNote = (log.action_type || '').includes('NOTE');
              const isCleared = (log.action_type || '').includes('CLEARED');

              return (
                <div 
                  key={log.id || idx}
                  className="bg-[#17181B] border border-zinc-800 hover:border-zinc-700 transition-all duration-150 p-4 rounded-xl space-y-2 text-xs"
                >
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-zinc-800/80 pb-2">
                    <div className="flex items-center space-x-3 font-mono">
                      <span className="font-bold text-white text-xs px-2.5 py-0.5 rounded-full bg-[#121315] border border-zinc-700">
                        {log.work_id}
                      </span>
                      <span className={`px-2.5 py-0.5 rounded-full font-bold text-[10px] ${
                        isVerification ? 'bg-white text-black border border-white' :
                        isAudit ? 'bg-amber-950/80 text-amber-300 border border-amber-800' :
                        isNote ? 'bg-sky-950/80 text-sky-300 border border-sky-800' :
                        isCleared ? 'bg-emerald-950/80 text-emerald-300 border border-emerald-800' :
                        'bg-[#121315] text-zinc-300 border border-zinc-700'
                      }`}>
                        {log.action_type}
                      </span>
                    </div>

                    <div className="flex items-center space-x-3 text-[11px] text-zinc-400 font-mono">
                      <span>Actor: <strong className="text-white">{log.actor || "State Nodal Officer"}</strong></span>
                      <span>•</span>
                      <span>{log.timestamp ? new Date(log.timestamp).toLocaleString() : 'Just now'}</span>
                    </div>
                  </div>

                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pt-1 font-sans">
                    <p className="text-zinc-200 text-xs leading-normal">
                      {log.details || "Official action recorded."}
                    </p>

                    {onSelectWorkForInvestigation && log.work_id && !log.work_id.startsWith('SYSTEM') && !log.work_id.startsWith('DATASET') && !log.work_id.startsWith('DEMO') && (
                      <button
                        onClick={() => {
                          onSelectWorkForInvestigation(log.work_id);
                        }}
                        className="px-3 py-1 rounded-xl bg-white hover:bg-zinc-200 text-black border border-white text-[10px] font-mono font-bold shrink-0 self-start sm:self-auto transition-colors duration-150 shadow-2xs button-press-effect"
                      >
                        Inspect Work (Page 4) →
                      </button>
                    )}
                  </div>
                </div>
              );
            })
          ) : (
            <div className="p-8 text-center bg-[#17181B] border border-zinc-800 rounded-2xl text-zinc-400 font-mono text-xs space-y-1">
              <p className="font-semibold text-white">No session audit events found matching filters.</p>
              <p className="text-[11px] text-zinc-500">Perform an official action or save a note on Page 4 to record live compliance events in SQLite.</p>
            </div>
          )}
        </div>

      </div>

    </div>
  );
}
