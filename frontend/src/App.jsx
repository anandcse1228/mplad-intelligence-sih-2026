import React, { useState, useEffect, useRef, useCallback } from 'react';
import Navbar from './components/Navbar';
import Sidebar from './components/Sidebar';
import KpiCards from './components/KpiCards';
import DataNoticeBanner from './components/DataNoticeBanner';
import RiskQueueTable from './components/RiskQueueTable';
import AnalyticsWidgets from './components/AnalyticsWidgets';
import RiskPriorityQueuePage from './components/RiskPriorityQueuePage';
import DistrictAnalyticsPage from './components/DistrictAnalyticsPage';
import InvestigationWorkspacePage from './components/InvestigationWorkspacePage';
import DataLineagePage from './components/DataLineagePage';
import AuditLogPage from './components/AuditLogPage';
import { MapPin, RefreshCw } from 'lucide-react';
import { api } from './api/client';

export default function App() {
  const [activeTab, setActiveTab] = useState('COMMAND_CENTER');
  const [selectedWorkId, setSelectedWorkId] = useState(null);
  const [activeDataset, setActiveDataset] = useState(null);

  // Global Theme State: 'dark' (baseline) or 'light'
  const [theme, setTheme] = useState(() => {
    return localStorage.getItem('mplads_theme') || 'dark';
  });

  const handleToggleTheme = () => {
    setTheme(prev => {
      const nextTheme = prev === 'dark' ? 'light' : 'dark';
      localStorage.setItem('mplads_theme', nextTheme);
      return nextTheme;
    });
  };

  // Sync data-theme attribute on <html> element for CSS token selectors
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  // ── Ref to the actual <main> scroll container ──────────────────────────────
  // All scroll resets must target this element, NOT window.scrollTo().
  // window is NOT the scroll owner — <main> is.
  const mainScrollRef = useRef(null);

  const scrollMainToTop = useCallback(() => {
    if (mainScrollRef.current) {
      mainScrollRef.current.scrollTop = 0;
    }
  }, []);

  const fetchActiveDataset = () => {
    return api.getActiveDataset()
      .then(res => { setActiveDataset(res); return res; })
      .catch(err => { console.error("Failed to load active dataset metadata in App:", err); });
  };

  // Fetch on mount and on every tab change.
  useEffect(() => {
    fetchActiveDataset();
  }, [activeTab]);

  // Navigate from Audit Log or Risk Queue to Investigation Workspace.
  // Also resets the <main> scroll container immediately on navigation.
  const handleSelectWorkForInvestigation = (workId) => {
    setSelectedWorkId(workId);
    setActiveTab('INVESTIGATION_WORKSPACE');
    scrollMainToTop();
  };

  // Navigate from Sidebar to Investigation Workspace without a pre-selected work.
  // Clears stale selectedWorkId so workspace opens on the top-priority work.
  const handleSidebarNavigateToWorkspace = () => {
    setSelectedWorkId(null);
    setActiveTab('INVESTIGATION_WORKSPACE');
    scrollMainToTop();
  };

  const stateUpper = activeDataset?.state?.toUpperCase() || 'PUNJAB';
  const districtName = activeDataset?.district || 'Ludhiana';
  const sanctionedCount = activeDataset?.sanctioned_count || 220;

  return (
    <div
      data-theme={theme}
      className={`h-screen w-full flex flex-col overflow-hidden font-sans selection:bg-slate-900 selection:text-white ${
        theme === 'light' ? 'theme-light bg-[#F6F8FB] text-[#14213D]' : 'bg-[#080808] text-[#F5F5F5]'
      }`}
    >
      {/* Top Institutional Header - Dynamic Jurisdiction & Global Theme Toggle */}
      <Navbar activeDataset={activeDataset} theme={theme} onToggleTheme={handleToggleTheme} />

      {/* Main Shell - Fixed Flex Row Container below Header */}
      <div className="flex flex-1 overflow-hidden w-full relative">
        {/* Left Sidebar - Dynamic Counts */}
        <Sidebar
          activeTab={activeTab}
          setActiveTab={(tab) => {
            // For all non-workspace tabs, use standard setActiveTab.
            // Scroll to top on the actual <main> container.
            setActiveTab(tab);
            scrollMainToTop();
          }}
          activeDataset={activeDataset}
          onNavigateToWorkspace={handleSidebarNavigateToWorkspace}
        />

        {/* Workspace Container — THE single vertical scroll owner */}
        <main
          ref={mainScrollRef}
          className="flex-1 h-full overflow-y-auto p-4 lg:p-6 pb-20 space-y-6 max-w-[1600px] w-full mx-auto font-sans"
        >
          
          {activeTab === 'COMMAND_CENTER' ? (
            <div key="COMMAND_CENTER" className="space-y-6 animate-page-fade">
              {/* Header Context Banner */}
              <div className="dark-surface-card rounded-2xl p-6 flex flex-col md:flex-row md:items-center justify-between gap-4 shadow-md">
                <div>
                  <div className="flex items-center space-x-2 text-xs text-zinc-400 font-semibold mb-1 font-mono">
                    <MapPin className="w-3.5 h-3.5 text-white" />
                    <span>STATE MONITORING CELL • {stateUpper}</span>
                  </div>
                  <h1 className="text-xl font-bold text-white tracking-tight font-sans">
                    {districtName} District MPLADS Command Center
                  </h1>
                  <p className="text-xs text-zinc-400 mt-1 max-w-2xl leading-relaxed font-sans">
                    Real-time compliance monitoring, sanction delay analysis, and algorithmic risk prioritization across <span className="text-white font-semibold">{sanctionedCount} validated sanctioned MPLADS works</span>.
                  </p>
                </div>

                {/* Ingestion & Refresh Timestamp */}
                <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3 bg-[#1A1B1E] border border-zinc-800 p-3.5 rounded-xl text-xs font-mono">
                  <div className="space-y-0.5">
                    <span className="text-[10px] text-zinc-500 block uppercase">ACTIVE DATASET</span>
                    <span className="text-white font-semibold text-xs truncate max-w-[180px] block">{activeDataset?.name || 'Loading...'}</span>
                  </div>
                  <button 
                    onClick={() => {
                      fetchActiveDataset();
                      window.location.reload();
                    }}
                    className="px-3.5 py-2 rounded-xl bg-white hover:bg-zinc-200 text-black text-xs font-bold flex items-center space-x-1.5 transition-colors font-sans shadow-2xs button-press-effect"
                  >
                    <RefreshCw className="w-3.5 h-3.5" />
                    <span>Re-Sync</span>
                  </button>
                </div>
              </div>

              {/* Data Ingestion Status Banner */}
              <DataNoticeBanner activeDataset={activeDataset} />

              {/* Key Metric Indicators */}
              <KpiCards />

              {/* Risk Priority Queue Table Preview */}
              <div className="space-y-2.5 font-sans">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-mono font-semibold text-zinc-400 uppercase">
                    PRIORITY AUDIT QUEUE PREVIEW
                  </span>
                  <button
                    onClick={() => {
                      setActiveTab('RISK_QUEUE');
                      scrollMainToTop();
                    }}
                    className="text-xs font-sans text-white font-bold hover:underline flex items-center space-x-1"
                  >
                    <span>View Full {sanctionedCount} Risk Queue (Page 2) →</span>
                  </button>
                </div>
                <RiskQueueTable />
              </div>

              {/* Analytics Breakdown Widgets */}
              <AnalyticsWidgets />
            </div>
          ) : activeTab === 'RISK_QUEUE' ? (
            <div key="RISK_QUEUE" className="animate-page-fade">
              <RiskPriorityQueuePage onSelectWorkForInvestigation={handleSelectWorkForInvestigation} />
            </div>
          ) : activeTab === 'DISTRICT_ANALYTICS' ? (
            <div key="DISTRICT_ANALYTICS" className="animate-page-fade">
              <DistrictAnalyticsPage />
            </div>
          ) : activeTab === 'INVESTIGATION_WORKSPACE' ? (
            <div key="INVESTIGATION_WORKSPACE" className="animate-page-fade">
              <InvestigationWorkspacePage 
                selectedWorkId={selectedWorkId} 
                onSelectWork={setSelectedWorkId}
                onNavigateToRiskQueue={() => {
                  setActiveTab('RISK_QUEUE');
                  scrollMainToTop();
                }}
                activeDataset={activeDataset}
                scrollMainToTop={scrollMainToTop}
              />
            </div>
          ) : activeTab === 'DATA_LINEAGE' ? (
            <div key="DATA_LINEAGE" className="animate-page-fade">
              <DataLineagePage 
                onNavigateToCommandCenter={() => {
                  setActiveTab('COMMAND_CENTER');
                  scrollMainToTop();
                }}
                activeDataset={activeDataset}
                onDatasetSwitched={(ds) => setActiveDataset(ds)}
              />
            </div>
          ) : activeTab === 'AUDIT_LOG' ? (
            <div key="AUDIT_LOG" className="animate-page-fade">
              <AuditLogPage 
                onSelectWorkForInvestigation={handleSelectWorkForInvestigation}
              />
            </div>
          ) : null}

        </main>
      </div>
    </div>
  );
}
