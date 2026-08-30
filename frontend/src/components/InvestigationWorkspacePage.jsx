import React, { useState, useMemo, useEffect, useRef, useCallback } from 'react';
import { 
  FileSearch, 
  Search, 
  Cpu, 
  AlertTriangle, 
  CheckCircle2, 
  Clock, 
  FileText, 
  Shield, 
  FileCheck,
  Send,
  UserCheck,
  ClipboardList,
  Info,
  RefreshCw,
  XCircle,
  ArrowLeft
} from 'lucide-react';
import { api } from '../api/client';

// ─────────────────────────────────────────────────────────────────────────────
// Helpers
// ─────────────────────────────────────────────────────────────────────────────
const SYSTEM_PREFIXES = ['SYSTEM', 'DATASET', 'DEMO'];

function isValidProjectWorkId(id) {
  if (!id || typeof id !== 'string') return false;
  return !SYSTEM_PREFIXES.some(prefix => id.startsWith(prefix));
}

// ─────────────────────────────────────────────────────────────────────────────
// Component
// ─────────────────────────────────────────────────────────────────────────────
export default function InvestigationWorkspacePage({
  selectedWorkId,
  onSelectWork,
  onNavigateToRiskQueue,
  activeDataset,
  scrollMainToTop,   // Issue 1: callback from App.jsx to reset the <main> scroll container
}) {
  // ── Work list state ────────────────────────────────────────────────────────
  const [allWorksList, setAllWorksList] = useState([]);
  const [queueLoading, setQueueLoading] = useState(true);
  const [queueError, setQueueError] = useState(null);

  // ── Current work being inspected ───────────────────────────────────────────
  // currentWorkId is the RESOLVED id. Set only after queue confirms the target exists.
  const [currentWorkId, setCurrentWorkId] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');

  // ── Intelligence fetch state ───────────────────────────────────────────────
  const [activeWork, setActiveWork] = useState(null);
  const [caseStatus, setCaseStatus] = useState('UNDER REVIEW');
  const [intelLoading, setIntelLoading] = useState(false);
  const [loadingStep, setLoadingStep] = useState(1);
  const [intelError, setIntelError] = useState(null);

  // ── Notes state (distinct from intelligence) ───────────────────────────────
  const [notesList, setNotesList] = useState([]);
  const [notesLoading, setNotesLoading] = useState(false);
  const [notesError, setNotesError] = useState(null);
  const [noteInput, setNoteInput] = useState('');
  const [savingNote, setSavingNote] = useState(false);

  // ── Unavailable-work notice (only shown after queue fully loaded) ───────────
  const [workNotFoundNotice, setWorkNotFoundNotice] = useState(null);

  // ── Stale-response protection: request version counters ───────────────────
  // Each new fetch increments its counter. A response is only applied if its
  // captured version still matches the current ref value at response time.
  // This covers: intel fetch, notes fetch on work change, AND save→refetch.
  const intelRequestVersion = useRef(0);
  const notesRequestVersion = useRef(0);

  // ─────────────────────────────────────────────────────────────────────────
  // PHASE 1: Load the work queue for the active dataset.
  //
  // Depends only on activeDataset.dataset_id — NOT on selectedWorkId.
  // This ensures the queue is always fetched against a confirmed, non-null
  // dataset before any work resolution happens.
  //
  // Issue 2 fix: by keeping Phase 1 decoupled from selectedWorkId, we
  // guarantee the queue is loaded for the CONFIRMED active dataset before
  // Phase 2 evaluates which work to open. selectedWorkId is read only in
  // Phase 2, which waits for queueLoading === false.
  // ─────────────────────────────────────────────────────────────────────────
  useEffect(() => {
    if (!activeDataset?.dataset_id) {
      // activeDataset not yet resolved — hold in loading state.
      return;
    }

    let cancelled = false;
    setQueueLoading(true);
    setQueueError(null);
    setWorkNotFoundNotice(null);
    setAllWorksList([]);
    setCurrentWorkId(null);
    setActiveWork(null);

    api.getRiskQueue({ page: 1, page_size: 500 })
      .then(res => {
        if (cancelled) return;
        const items = res.items || [];
        setAllWorksList(items);
        setQueueLoading(false);
      })
      .catch(err => {
        if (cancelled) return;
        console.error('Failed to load work list:', err);
        setQueueError('Could not load project queue from the active dataset.');
        setQueueLoading(false);
      });

    return () => { cancelled = true; };
  }, [activeDataset?.dataset_id]);

  // ─────────────────────────────────────────────────────────────────────────
  // PHASE 2: Resolve target work ID once queue is fully loaded.
  //
  // This effect runs ONLY when queueLoading flips to false (or selectedWorkId
  // changes after the queue is already loaded).
  //
  // Critical guarantee: "Work Unavailable" is NEVER shown until this effect
  // runs with queueLoading === false. While queueLoading is true, the loading
  // spinner is shown regardless of what selectedWorkId is.
  //
  // Issue 2 fix: No silent fallback to items[0] when selectedWorkId is set.
  // items[0] is only used when selectedWorkId is null (sidebar navigation).
  // ─────────────────────────────────────────────────────────────────────────
  useEffect(() => {
    if (queueLoading) return;    // Queue not ready — never resolve early
    if (queueError) return;

    setWorkNotFoundNotice(null);

    if (allWorksList.length === 0) {
      setIntelError('No project works found in the active dataset.');
      return;
    }

    if (selectedWorkId && isValidProjectWorkId(selectedWorkId)) {
      // Explicit navigation from Audit Log or Risk Queue: exact-match only.
      const matched = allWorksList.find(w => w.id === selectedWorkId);
      if (matched) {
        setCurrentWorkId(matched.id);
        setIntelError(null);
      } else {
        // Definitively not in this dataset — show controlled notice, never substitute.
        setCurrentWorkId(null);
        setActiveWork(null);
        setIntelLoading(false);
        setWorkNotFoundNotice({
          requestedId: selectedWorkId,
          datasetName: activeDataset?.name || 'Active Dataset',
        });
      }
    } else {
      // Sidebar navigation (selectedWorkId === null) — open top-priority work.
      const firstId = allWorksList[0].id;
      setCurrentWorkId(firstId);
      if (onSelectWork) onSelectWork(firstId);
      setIntelError(null);
    }
  }, [queueLoading, queueError, allWorksList, selectedWorkId]);

  // ─────────────────────────────────────────────────────────────────────────
  // PHASE 3: Fetch intelligence + case status when currentWorkId is resolved.
  //
  // Request version counter: cleanup increments the counter, so any in-flight
  // response from a previous work is silently discarded on work change.
  // ─────────────────────────────────────────────────────────────────────────
  useEffect(() => {
    if (!currentWorkId || !isValidProjectWorkId(currentWorkId)) return;

    const myVersion = ++intelRequestVersion.current;
    setIntelLoading(true);
    setLoadingStep(1);
    setIntelError(null);
    setWorkNotFoundNotice(null);

    const t1 = setTimeout(() => {
      if (intelRequestVersion.current === myVersion) setLoadingStep(2);
    }, 100);
    const t2 = setTimeout(() => {
      if (intelRequestVersion.current === myVersion) setLoadingStep(3);
    }, 220);

    Promise.all([
      api.getProjectIntelligence(currentWorkId),
      api.getInvestigationCase(currentWorkId).catch(() => ({ current_status: 'UNDER REVIEW' })),
    ])
      .then(([intel, caseData]) => {
        if (intelRequestVersion.current !== myVersion) return; // Stale — discard
        setLoadingStep(4);
        setActiveWork(intel);
        setCaseStatus(caseData.current_status || 'UNDER REVIEW');
        setIntelLoading(false);
      })
      .catch(err => {
        if (intelRequestVersion.current !== myVersion) return;
        console.error(`Intelligence fetch failed for '${currentWorkId}':`, err);
        setIntelError(err.message || `Unable to load intelligence record for '${currentWorkId}'.`);
        setIntelLoading(false);
      });

    return () => {
      clearTimeout(t1);
      clearTimeout(t2);
      intelRequestVersion.current++; // Invalidate — discard any late response
    };
  }, [currentWorkId]);

  // ─────────────────────────────────────────────────────────────────────────
  // PHASE 4: Fetch notes when currentWorkId changes.
  //
  // Preserves existing notesList on error — does NOT replace with [].
  // On work change, increments notesRequestVersion so old responses are discarded.
  //
  // Issue 1 fix: scrollMainToTop() is called when notes are fetched (i.e. when
  // the workspace settles on a new work), so the <main> scroll resets to top
  // reliably whenever a new work is loaded.
  // ─────────────────────────────────────────────────────────────────────────
  const fetchNotes = useCallback((workId) => {
    if (!workId || !isValidProjectWorkId(workId)) return;

    const myVersion = ++notesRequestVersion.current;
    setNotesLoading(true);
    setNotesError(null);

    api.getInvestigationNotes(workId)
      .then(data => {
        if (notesRequestVersion.current !== myVersion) return;
        setNotesList(data || []);
        setNotesLoading(false);
      })
      .catch(err => {
        if (notesRequestVersion.current !== myVersion) return;
        console.error(`Notes fetch failed for '${workId}':`, err);
        // Preserve existing notes — do NOT silently clear to [].
        setNotesError('Could not load notes. Previously loaded notes shown below.');
        setNotesLoading(false);
      });
  }, []);

  useEffect(() => {
    if (currentWorkId && isValidProjectWorkId(currentWorkId)) {
      setNotesList([]);       // Clear previous work notes before loading
      fetchNotes(currentWorkId);
      // Issue 1: scroll the actual <main> container to top when work changes.
      if (scrollMainToTop) scrollMainToTop();
    }
    return () => { notesRequestVersion.current++; };
  }, [currentWorkId, fetchNotes, scrollMainToTop]);

  // ─────────────────────────────────────────────────────────────────────────
  // Derived helpers
  // ─────────────────────────────────────────────────────────────────────────
  const selectableWorks = useMemo(() => {
    if (!allWorksList.length) return activeWork ? [activeWork] : [];
    if (!searchTerm.trim()) return allWorksList;
    const q = searchTerm.toLowerCase();
    return allWorksList.filter(w =>
      (w.id || '').toLowerCase().includes(q) ||
      (w.title || '').toLowerCase().includes(q) ||
      (w.ida || '').toLowerCase().includes(q)
    );
  }, [allWorksList, searchTerm, activeWork]);

  const topAnomalies = useMemo(() =>
    allWorksList.length ? allWorksList.slice(0, 5) : (activeWork ? [activeWork] : []),
    [allWorksList, activeWork]
  );

  // ─────────────────────────────────────────────────────────────────────────
  // User actions
  // ─────────────────────────────────────────────────────────────────────────
  const handleSelectWork = (workId) => {
    setCurrentWorkId(workId);
    if (onSelectWork) onSelectWork(workId);
    // Issue 1: scroll <main> to top when user explicitly changes the selected work.
    if (scrollMainToTop) scrollMainToTop();
  };

  // ─────────────────────────────────────────────────────────────────────────
  // Issue 3 fix: Save Note with full stale-response protection.
  //
  // Pattern:
  //   1. Capture targetWorkId and a notesRequestVersion snapshot BEFORE the async call.
  //   2. POST the note.
  //   3. Immediately after POST success, increment notesRequestVersion to invalidate
  //      any concurrent notes loads that might be in flight.
  //   4. GET fresh notes from SQLite (authoritative refetch).
  //   5. Before applying the response, verify the version still matches AND that
  //      the current activeWork is still the same work we saved to.
  //   This prevents Work A's save-refetch response from overwriting Work B's notes
  //   if the user switched works between save and refetch completing.
  // ─────────────────────────────────────────────────────────────────────────
  const handleAddNote = () => {
    if (!activeWork || !noteInput.trim() || savingNote) return;
    const textToSave = noteInput.trim();
    const targetWorkId = activeWork.id;  // Capture at click time

    setSavingNote(true);

    // Take ownership of notes versioning for this save operation.
    const mySaveVersion = ++notesRequestVersion.current;

    api.postInvestigationNote(targetWorkId, textToSave)
      .then(() => {
        setNoteInput('');
        // Authoritatively refetch from SQLite — the single source of truth.
        return api.getInvestigationNotes(targetWorkId);
      })
      .then(freshNotes => {
        // Only update UI if we are still on the same work/version request
        if (notesRequestVersion.current === mySaveVersion) {
          setNotesList(freshNotes || []);
          setNotesError(null);
        }
      })
      .catch(err => {
        if (notesRequestVersion.current === mySaveVersion) {
          alert(`Failed to save note: ${err.message}`);
        }
      })
      .finally(() => {
        setSavingNote(false);
      });
  };

  const handleStatusChange = (actionKey) => {
    if (!activeWork) return;
    api.postInvestigationAction(activeWork.id, actionKey)
      .then(res => setCaseStatus(res.current_status || res.new_status))
      .catch(err => alert(`Failed to update status: ${err.message}`));
  };

  // ─────────────────────────────────────────────────────────────────────────
  // Render states
  // ─────────────────────────────────────────────────────────────────────────

  // Loading: queue is loading OR intel is loading (but not if we already know work is unavailable).
  const isLoading = queueLoading || (!workNotFoundNotice && !queueError && intelLoading);

  if (isLoading) {
    return (
      <div className="p-8 max-w-xl mx-auto my-12 bg-[#121315] border border-zinc-800 rounded-2xl space-y-5 text-center font-sans shadow-2xl">
        <div className="w-12 h-12 rounded-2xl bg-[#1A1B1E] border border-zinc-700 flex items-center justify-center mx-auto text-white">
          <RefreshCw className="w-6 h-6 animate-spin text-white" />
        </div>
        <div>
          <h3 className="text-base font-bold text-white">Loading Intelligence Record</h3>
          <p className="text-xs text-zinc-400 font-mono mt-1">Target ID: {currentWorkId || selectedWorkId || 'Initializing...'}</p>
        </div>
        <div className="space-y-2 text-left text-xs bg-[#17181B] p-4 rounded-xl border border-zinc-800/80 font-mono">
          {[
            'Fetching project records from SQLite database...',
            'Loading Isolation Forest ML anomaly vectors (S_ml)...',
            'Evaluating statutory compliance rule signals (S_rule)...',
            'Preparing explainable risk attribution workspace...',
          ].map((step, i) => (
            <div key={i} className={`flex items-center space-x-2 ${loadingStep >= i + 1 ? 'text-emerald-400 font-semibold' : 'text-zinc-500'}`}>
              {loadingStep >= i + 1 ? <CheckCircle2 className="w-3.5 h-3.5" /> : <Clock className="w-3.5 h-3.5" />}
              <span>{step}</span>
            </div>
          ))}
        </div>
      </div>
    );
  }

  // Controlled "Work Unavailable" — shown ONLY after queue has fully loaded and definitively not found.
  if (workNotFoundNotice) {
    return (
      <div className="p-8 max-w-xl mx-auto my-12 bg-[#121315] border border-amber-900/80 rounded-2xl space-y-5 text-center font-sans shadow-2xl">
        <div className="w-12 h-12 rounded-2xl bg-amber-950/80 border border-amber-800 flex items-center justify-center mx-auto text-amber-400">
          <AlertTriangle className="w-6 h-6" />
        </div>
        <div>
          <h3 className="text-base font-bold text-white">Work Unavailable in Active Dataset</h3>
          <p className="text-xs text-zinc-300 font-mono mt-1">Requested ID: <strong className="text-white">#{workNotFoundNotice.requestedId}</strong></p>
          <p className="text-xs text-zinc-400 mt-2 leading-relaxed">
            This project does not belong to the currently active dataset (<strong className="text-zinc-200">{workNotFoundNotice.datasetName}</strong>).
            It may be recorded in another district dataset in the library.
          </p>
        </div>
        <div className="flex flex-col sm:flex-row items-center justify-center gap-3 pt-2">
          {allWorksList.length > 0 && (
            <button
              onClick={() => {
                const firstId = allWorksList[0].id;
                setCurrentWorkId(firstId);
                if (onSelectWork) onSelectWork(firstId);
                setWorkNotFoundNotice(null);
              }}
              className="px-4 py-2 bg-white hover:bg-zinc-200 text-black text-xs font-bold rounded-xl flex items-center space-x-1.5 transition-colors shadow-2xs button-press-effect w-full sm:w-auto justify-center"
            >
              <span>Inspect Top-Priority Work in Active Queue</span>
            </button>
          )}
          {onNavigateToRiskQueue && (
            <button
              onClick={onNavigateToRiskQueue}
              className="px-4 py-2 bg-[#17181B] hover:bg-zinc-800 text-white text-xs font-semibold rounded-xl border border-zinc-800 flex items-center space-x-1.5 w-full sm:w-auto justify-center"
            >
              <ArrowLeft className="w-3.5 h-3.5" />
              <span>Return to Risk Queue</span>
            </button>
          )}
        </div>
      </div>
    );
  }

  // Queue or intelligence error state.
  if (queueError || intelError || !activeWork) {
    return (
      <div className="p-8 max-w-xl mx-auto my-12 bg-[#121315] border border-rose-900/80 rounded-2xl space-y-5 text-center font-sans shadow-2xl">
        <div className="w-12 h-12 rounded-2xl bg-rose-950/80 border border-rose-800 flex items-center justify-center mx-auto text-rose-400">
          <XCircle className="w-6 h-6" />
        </div>
        <div>
          <h3 className="text-base font-bold text-white">Unable to Load Intelligence Record</h3>
          <p className="text-xs text-rose-300 font-mono mt-1">{queueError || intelError || 'The requested analysis record could not be retrieved.'}</p>
        </div>
        <div className="flex items-center justify-center space-x-3 pt-2">
          <button
            onClick={() => {
              setIntelError(null);
              setQueueError(null);
              setQueueLoading(true);
              api.getRiskQueue({ page: 1, page_size: 500 })
                .then(res => {
                  setAllWorksList(res.items || []);
                  setQueueLoading(false);
                })
                .catch(() => {
                  setQueueError('Could not load project queue from the active dataset.');
                  setQueueLoading(false);
                });
            }}
            className="px-4 py-2 bg-white hover:bg-zinc-200 text-black text-xs font-bold rounded-xl flex items-center space-x-1.5 transition-colors shadow-2xs button-press-effect"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Retry Query</span>
          </button>
          {onNavigateToRiskQueue && (
            <button
              onClick={onNavigateToRiskQueue}
              className="px-4 py-2 bg-[#17181B] hover:bg-zinc-800 text-white text-xs font-semibold rounded-xl border border-zinc-800 flex items-center space-x-1.5"
            >
              <ArrowLeft className="w-3.5 h-3.5" />
              <span>Return to Risk Queue</span>
            </button>
          )}
        </div>
      </div>
    );
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Active work resolved — render full workspace
  // ─────────────────────────────────────────────────────────────────────────
  const exp = activeWork.explanation || {};
  const scoreAttribution = exp.score_attribution || {
    ml_contribution: (0.60 * activeWork.ml_anomaly_score).toFixed(1),
    rule_contribution: (0.40 * activeWork.rule_score).toFixed(1),
    total_risk_score: activeWork.risk_priority_score,
  };
  const featureEvidenceMatrix = exp.feature_evidence_matrix || [];

  return (
    <div className="space-y-6 font-sans selection:bg-slate-900 selection:text-white pb-16">

      {/* ── Header Context Banner ─────────────────────────────────────────── */}
      <div className="deep-black-card rounded-2xl p-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2 text-xs text-zinc-400 font-semibold mb-1 font-mono">
            <FileSearch className="w-3.5 h-3.5 text-white" />
            <span>PAGE 4 • OFFICIAL HUMAN-IN-THE-LOOP INVESTIGATION WORKSPACE</span>
          </div>
          <h1 className="text-xl font-bold text-white tracking-tight">
            Work Investigation &amp; Evidence Inspection Workspace
          </h1>
          <p className="text-xs text-zinc-400 mt-1 max-w-3xl leading-relaxed">
            Detailed evidence breakdown explaining why a specific MPLADS project received its Risk Priority Score (
            <span className="text-white font-mono font-semibold">S_risk = 0.60 S_ml + 0.40 S_rule</span>).
          </p>
        </div>
        <div className="bg-[#17181B] border border-zinc-800 p-3.5 rounded-xl text-xs shrink-0 space-y-1 font-mono">
          <div className="flex items-center space-x-2 text-indigo-400 font-semibold">
            <Cpu className="w-4 h-4" />
            <span>Isolation Forest Engine</span>
          </div>
          <div className="text-[11px] text-zinc-400">
            <span>{allWorksList.length || 220} Scored Works</span> •{' '}
            <span className="text-indigo-300 font-semibold">{topAnomalies.length} Top Priorities</span>
          </div>
        </div>
      </div>

      {/* ── Work Selector & Top Priority Shortcuts ────────────────────────── */}
      <div className="deep-black-card deep-black-card-hover rounded-2xl p-5 space-y-3">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-3">
          <div className="flex items-center space-x-3 flex-1">
            <label className="text-xs text-zinc-400 uppercase font-semibold shrink-0">SELECT WORK FOR INSPECTION:</label>
            <div className="relative flex-1 max-w-xl">
              <select
                value={activeWork.id}
                onChange={e => handleSelectWork(e.target.value)}
                className="w-full bg-[#17181B] border border-zinc-800 rounded-xl px-3.5 py-2 text-xs text-white focus:outline-none focus:border-zinc-600 font-mono"
              >
                {selectableWorks.map((work, idx) => (
                  <option key={work.id} value={work.id}>
                    #{idx + 1} [{work.id}] - S_risk: {work.risk_priority_score.toFixed(1)} | {work.title.substring(0, 60)}...
                  </option>
                ))}
              </select>
            </div>
          </div>
          <div className="relative">
            <Search className="w-3.5 h-3.5 text-zinc-400 absolute left-3 top-2.5" />
            <input
              type="text"
              placeholder="Filter work dropdown..."
              value={searchTerm}
              onChange={e => setSearchTerm(e.target.value)}
              className="bg-[#17181B] border border-zinc-800 rounded-xl pl-8 pr-3 py-1.5 text-xs text-white placeholder-zinc-500 focus:outline-none focus:border-zinc-600 w-56 font-sans transition-all"
            />
          </div>
        </div>
        <div className="flex flex-wrap items-center gap-2 pt-2 border-t border-zinc-800/80 text-xs">
          <span className="text-[11px] text-zinc-400 uppercase font-semibold font-mono">Top Priority Shortcuts:</span>
          {topAnomalies.map((item, idx) => (
            <button
              key={item.id}
              onClick={() => handleSelectWork(item.id)}
              className={`px-3 py-1 rounded-xl text-[11px] font-mono border transition-all duration-200 button-press-effect ${
                activeWork.id === item.id
                  ? 'bg-white text-black border-white font-bold shadow-2xs'
                  : 'bg-[#17181B] text-zinc-300 border-zinc-800 hover:border-zinc-700'
              }`}
            >
              #{idx + 1} {item.id.split('/')[3] || item.id} (Score: {item.risk_priority_score.toFixed(1)})
            </button>
          ))}
        </div>
      </div>

      {/* ── Target Work Overview Banner — natural document flow ───────────── */}
      <div className="deep-black-card deep-black-card-hover rounded-2xl p-5 space-y-4">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 border-b border-zinc-800/80 pb-3">
          <div className="space-y-1">
            <div className="flex items-center space-x-3 font-mono flex-wrap gap-2">
              <span className="text-xs font-bold text-white px-3 py-0.5 rounded-full bg-[#17181B] border border-zinc-800">
                {activeWork.id}
              </span>
              <span className="text-xs text-zinc-300 bg-[#17181B] px-2.5 py-0.5 rounded-full border border-zinc-800">
                Category: {activeWork.category}
              </span>
              <span className={`text-xs px-3 py-0.5 rounded-full border font-bold ${
                activeWork.severity_band === 'CRITICAL RISK PRIORITY' ? 'bg-rose-950/80 text-rose-300 border-rose-800' :
                activeWork.severity_band === 'HIGH RISK PRIORITY' ? 'bg-amber-950/80 text-amber-300 border-amber-800' :
                activeWork.severity_band === 'MEDIUM RISK PRIORITY' ? 'bg-sky-950/80 text-sky-300 border-sky-800' :
                'bg-[#17181B] text-zinc-300 border-zinc-700'
              }`}>
                {activeWork.severity_band}
              </span>
            </div>
            <h2 className="text-base font-bold text-white tracking-tight mt-2 font-sans">{activeWork.title}</h2>
          </div>
          <div className="bg-[#17181B] border border-zinc-800 p-3.5 rounded-xl text-right shrink-0 font-mono">
            <span className="text-[10px] text-zinc-400 block uppercase font-semibold">INVESTIGATION STATUS</span>
            <span className="text-xs font-bold text-white uppercase block mt-0.5">{caseStatus}</span>
            <span className="text-[9px] text-zinc-500 block mt-0.5">SQLite Persisted</span>
          </div>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs">
          <div className="bg-[#17181B] p-4 rounded-xl border border-zinc-800">
            <span className="text-zinc-400 text-[10px] block uppercase font-semibold">SANCTION AMOUNT</span>
            <span className="text-base font-bold text-white font-mono">₹{(activeWork.sanctioned_amount_lakhs || 0).toFixed(2)} Lakhs</span>
            <span className="text-[10px] text-zinc-400 block mt-0.5 font-mono">Rec: ₹{(activeWork.recommended_amount_lakhs || 0).toFixed(2)} L</span>
          </div>
          <div className="bg-[#17181B] p-4 rounded-xl border border-zinc-800">
            <span className="text-zinc-400 text-[10px] block uppercase font-semibold">NODAL AGENCY (IDA)</span>
            <span className="text-xs font-bold text-white block truncate" title={activeWork.ida}>{activeWork.ida}</span>
            <span className="text-[10px] text-zinc-400 block mt-0.5">{activeWork.district} District</span>
          </div>
          <div className="bg-[#17181B] p-4 rounded-xl border border-zinc-800">
            <span className="text-zinc-400 text-[10px] block uppercase font-semibold">OFFICIAL WORK STATUS</span>
            <span className="text-xs font-bold text-white block">{activeWork.status}</span>
            <span className="text-[10px] text-zinc-400 block mt-0.5">
              {activeWork.is_completed ? 'Completed Feed Matched' : 'In Progress'}
            </span>
          </div>
          <div className="bg-[#17181B] p-4 rounded-xl border border-zinc-800">
            <span className="text-zinc-400 text-[10px] block uppercase font-semibold">SANCTION DELAY</span>
            <span className="text-base font-bold text-amber-400 font-mono">{activeWork.sanction_delay_days} Days</span>
            <span className="text-[10px] text-zinc-400 block mt-0.5 font-mono">
              {activeWork.is_recommendation_date_imputed ? '[Imputed Baseline]' : '[Observed Gap]'}
            </span>
          </div>
        </div>
      </div>

      {/* ── Explainable Risk Intelligence ──────────────────────────────────── */}
      <div className="deep-black-card deep-black-card-hover rounded-2xl p-6 space-y-5">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-zinc-800/80 pb-3 gap-2">
          <div className="flex items-center space-x-2">
            <Info className="w-4 h-4 text-white" />
            <h3 className="text-xs font-bold text-white uppercase tracking-wider">
              Explainable Risk Intelligence Breakdown &amp; Evidence Attribution
            </h3>
          </div>
          <span className="text-[10px] font-mono text-zinc-300 bg-[#17181B] border border-zinc-800 px-2.5 py-0.5 rounded-full font-bold">
            Empirical Benchmark Contextualized
          </span>
        </div>

        <div className="bg-[#17181B] border border-zinc-800 p-4 rounded-xl text-xs text-zinc-200 leading-relaxed">
          <strong className="text-white block mb-1 uppercase font-mono font-semibold text-[10px]">OFFICER RISK SUMMARY NARRATIVE:</strong>
          <p className="font-sans text-xs leading-relaxed">{exp.executive_summary || 'Work scored under hybrid risk evaluation.'}</p>
        </div>

        <div className="bg-[#17181B] border border-zinc-800 p-4 rounded-xl space-y-3">
          <div className="flex items-center justify-between text-xs">
            <span className="text-zinc-300 font-semibold uppercase font-sans">HYBRID SCORE ATTRIBUTION:</span>
            <span className="text-white font-bold font-mono">
              0.60({activeWork.ml_anomaly_score.toFixed(1)}) + 0.40({activeWork.rule_score.toFixed(1)}) = {activeWork.risk_priority_score.toFixed(1)} / 100
            </span>
          </div>
          <div className="w-full bg-[#111214] h-3 rounded-full overflow-hidden flex border border-zinc-700/60">
            <div
              style={{ width: `${Math.min(100, Math.max(0, (parseFloat(scoreAttribution.ml_contribution) / activeWork.risk_priority_score) * 100))}%` }}
              className="bg-indigo-500 h-full"
            />
            <div
              style={{ width: `${Math.min(100, Math.max(0, (parseFloat(scoreAttribution.rule_contribution) / activeWork.risk_priority_score) * 100))}%` }}
              className="bg-zinc-300 h-full"
            />
          </div>
          <div className="flex justify-between text-[11px] text-zinc-400 font-mono">
            <span>ML Component: <strong className="text-indigo-300">+{scoreAttribution.ml_contribution} pts</strong></span>
            <span>Statutory Rules: <strong className="text-zinc-200">+{scoreAttribution.rule_contribution} pts</strong></span>
          </div>
        </div>

        <div className="space-y-2.5">
          <h4 className="text-xs font-bold text-white uppercase font-mono tracking-wider">
            FEATURE EVIDENCE MATRIX (6 MULTIVARIATE INDICATORS):
          </h4>
          <div className="overflow-x-auto border border-zinc-800/80 rounded-xl">
            <table className="w-full text-left text-xs font-sans">
              <thead className="bg-[#17181B] text-zinc-400 border-b border-zinc-800 font-mono text-[10px] uppercase">
                <tr>
                  <th className="px-4 py-2.5">Feature Name</th>
                  <th className="px-4 py-2.5">Observed Value</th>
                  <th className="px-4 py-2.5">Dataset Benchmark</th>
                  <th className="px-4 py-2.5">Diagnostic Evaluation</th>
                  <th className="px-4 py-2.5 text-right">Severity</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-800 text-zinc-300 font-mono text-[11px]">
                {featureEvidenceMatrix.map((feat, idx) => (
                  <tr key={idx} className="hover:bg-[#17181B]/50 transition-colors">
                    <td className="px-4 py-3 font-semibold text-white">{feat.feature_name}</td>
                    <td className="px-4 py-3 text-white font-bold">{feat.observed_value}</td>
                    <td className="px-4 py-3 text-zinc-400 font-sans text-xs">{feat.dataset_benchmark}</td>
                    <td className="px-4 py-3 text-zinc-300 font-sans text-xs">{feat.evaluation}</td>
                    <td className="px-4 py-3 text-right">
                      <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold border ${
                        feat.severity === 'HIGH' ? 'bg-rose-950/80 text-rose-300 border-rose-800' :
                        feat.severity === 'MEDIUM' ? 'bg-amber-950/80 text-amber-300 border-amber-800' :
                        'bg-[#17181B] text-zinc-400 border-zinc-800'
                      }`}>
                        {feat.severity}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* ── Officer Actions + Investigation Notes ─────────────────────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

        {/* Officer Action Controls */}
        <div className="deep-black-card deep-black-card-hover rounded-2xl p-6 space-y-4">
          <div className="flex items-center space-x-2 border-b border-zinc-800/80 pb-3">
            <ClipboardList className="w-4 h-4 text-white" />
            <h3 className="text-xs font-bold text-white uppercase tracking-wider">OFFICER VERIFICATION &amp; AUDIT ACTIONS</h3>
          </div>
          <div className="space-y-3">
            {[
              { key: 'MARK_FOR_FIELD_VERIFICATION', label: 'Mark for Field Verification', desc: 'Assign field inspection officer to inspect physical milestone execution.', icon: <FileCheck className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" /> },
              { key: 'REQUEST_NODAL_AGENCY_AUDIT', label: 'Request Nodal Agency Audit', desc: 'Request financial sanction audit and ledger clarification from implementing agency.', icon: <Shield className="w-5 h-5 text-indigo-400 shrink-0 mt-0.5" /> },
              { key: 'CLEAR_AFTER_REVIEW', label: 'Clear Project / Close Case', desc: 'Approve justification and log statutory compliance resolution.', icon: <UserCheck className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" /> },
            ].map(action => (
              <button
                key={action.key}
                onClick={() => handleStatusChange(action.key)}
                className="w-full p-4 rounded-xl bg-[#17181B] hover:bg-zinc-800 text-left border border-zinc-800 hover:border-zinc-700 transition-all button-press-effect flex items-start space-x-3"
              >
                {action.icon}
                <div>
                  <span className="text-xs font-bold text-white block">{action.label}</span>
                  <span className="text-[11px] text-zinc-400 block mt-0.5">{action.desc}</span>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Investigation Notes */}
        <div className="deep-black-card deep-black-card-hover rounded-2xl p-6 space-y-4">
          <div className="flex items-center space-x-2 border-b border-zinc-800/80 pb-3">
            <FileText className="w-4 h-4 text-white" />
            <h3 className="text-xs font-bold text-white uppercase tracking-wider">INVESTIGATION NOTES &amp; OBSERVATIONS</h3>
          </div>

          {/* Note Input */}
          <div className="space-y-2">
            <textarea
              value={noteInput}
              onChange={e => setNoteInput(e.target.value)}
              placeholder="Enter official investigation notes, site measurements, or verification notes..."
              className="w-full bg-[#17181B] border border-zinc-800 rounded-xl p-3 text-xs text-white placeholder-zinc-500 focus:outline-none focus:border-zinc-600 h-24 resize-none font-sans"
            />
            <div className="flex justify-end">
              <button
                onClick={handleAddNote}
                disabled={!noteInput.trim() || savingNote}
                className={`px-4 py-2 rounded-xl text-xs font-bold flex items-center space-x-1.5 transition-all button-press-effect ${
                  noteInput.trim() && !savingNote
                    ? 'bg-white hover:bg-zinc-200 text-black shadow-md'
                    : 'bg-[#17181B] text-zinc-500 cursor-not-allowed border border-zinc-800'
                }`}
              >
                <Send className="w-3.5 h-3.5" />
                <span>{savingNote ? 'Saving to SQLite...' : 'Save Note to SQLite'}</span>
              </button>
            </div>
          </div>

          {/* Notes error — distinct from empty state */}
          {notesError && (
            <div className="flex items-center justify-between bg-amber-950/40 border border-amber-800/60 text-amber-300 text-[11px] font-mono px-3 py-2 rounded-xl gap-2">
              <span>{notesError}</span>
              <button
                onClick={() => fetchNotes(currentWorkId)}
                className="text-white underline underline-offset-2 text-[10px] shrink-0"
              >
                Retry
              </button>
            </div>
          )}

          {/* Notes loading */}
          {notesLoading && (
            <div className="flex items-center space-x-2 text-[11px] text-zinc-400 font-mono">
              <RefreshCw className="w-3 h-3 animate-spin" />
              <span>Loading notes from SQLite...</span>
            </div>
          )}

          {/* Saved notes list — no height restriction, natural page scroll owns flow */}
          <div className="space-y-2">
            <span className="text-[10px] text-zinc-400 uppercase font-mono font-semibold block">
              Saved Notes ({notesList.length}):
            </span>
            {!notesLoading && !notesError && notesList.length === 0 ? (
              <div className="text-xs text-zinc-500 italic p-3 bg-[#17181B] rounded-xl border border-zinc-800">
                No notes recorded yet for this project.
              </div>
            ) : (
              notesList.map(n => (
                <div key={n.id} className="p-3 bg-[#17181B] border border-zinc-800 rounded-xl space-y-1 text-xs font-sans">
                  <div className="flex items-center justify-between text-[10px] font-mono text-zinc-400">
                    <span className="text-white font-bold">{n.officer_name}</span>
                    <span>{new Date(n.timestamp).toLocaleString()}</span>
                  </div>
                  <p className="text-zinc-200">{n.note_text}</p>
                </div>
              ))
            )}
          </div>
        </div>

      </div>

    </div>
  );
}
