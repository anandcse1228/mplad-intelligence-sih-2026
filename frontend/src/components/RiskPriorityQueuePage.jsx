import React, { useState, useMemo, useEffect } from 'react';
import { 
  AlertTriangle, 
  Search, 
  ChevronLeft, 
  ChevronRight, 
  Layers, 
  FileText, 
  Cpu, 
  Shield, 
  CheckCircle2, 
  Clock, 
  MapPin, 
  Building,
  Info,
  CheckCheck
} from 'lucide-react';
import { api } from '../api/client';

export default function RiskPriorityQueuePage({ onSelectWorkForInvestigation }) {
  const [works, setWorks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [kpis, setKpis] = useState(null);

  // Pagination & Filtering state
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(15);
  const [totalRecords, setTotalRecords] = useState(0);
  const [totalPages, setTotalPages] = useState(1);

  // Active filters
  const [activeFilter, setActiveFilter] = useState('ALL'); // ALL, CRITICAL, HIGH, MEDIUM, NORMAL, ML_ANOMALY
  const [categoryFilter, setCategoryFilter] = useState('ALL');
  const [searchQuery, setSearchQuery] = useState('');

  // Modal State for Review
  const [activeModalWork, setActiveModalWork] = useState(null);

  // Load KPI metrics for the severity count badges
  useEffect(() => {
    api.getOverviewKpis()
      .then(res => setKpis(res))
      .catch(err => console.error("Failed to load KPI metrics:", err));
  }, []);

  // Fetch paginated risk queue from backend API
  useEffect(() => {
    let isMounted = true;
    setLoading(true);

    const params = {
      page: currentPage,
      page_size: pageSize,
      severity: activeFilter !== 'ALL' ? activeFilter : undefined,
      category: categoryFilter !== 'ALL' ? categoryFilter : undefined,
      search: searchQuery.trim() || undefined
    };

    api.getRiskQueue(params)
      .then(res => {
        if (isMounted) {
          setWorks(res.items || []);
          setTotalRecords(res.total || 0);
          setTotalPages(res.total_pages || 1);
          setLoading(false);
        }
      })
      .catch(err => {
        console.error("Failed to load risk queue from API:", err);
        if (isMounted) setLoading(false);
      });

    return () => { isMounted = false; };
  }, [currentPage, pageSize, activeFilter, categoryFilter, searchQuery]);

  // Reset to page 1 when filters change
  const handleFilterChange = (filterType) => {
    setActiveFilter(filterType);
    setCurrentPage(1);
  };

  const handleCategoryChange = (cat) => {
    setCategoryFilter(cat);
    setCurrentPage(1);
  };

  const handleSearchChange = (val) => {
    setSearchQuery(val);
    setCurrentPage(1);
  };

  const handlePageSizeChange = (size) => {
    setPageSize(Number(size));
    setCurrentPage(1);
  };

  const handleReviewClick = (work) => {
    setActiveModalWork(work);
  };

  return (
    <div className="space-y-6 font-sans selection:bg-slate-900 selection:text-white pb-6">
      
      {/* Header Context Banner */}
      <div className="deep-black-card rounded-2xl p-6 flex flex-col md:flex-row md:items-center justify-between gap-4 shadow-xs">
        <div>
          <div className="flex items-center space-x-2 text-xs text-zinc-400 font-semibold mb-1 font-mono">
            <Shield className="w-3.5 h-3.5 text-white" />
            <span>PAGE 2 • FULL CONSTITUENCY RISK PRIORITY QUEUE</span>
          </div>
          <h1 className="text-xl font-bold text-white tracking-tight font-sans">
            Risk Priority Audit Queue & Algorithmic Triage
          </h1>
          <p className="text-xs text-zinc-400 mt-1 max-w-3xl leading-relaxed font-sans">
            Complete ranking of all 220 validated sanctioned MPLADS works in Ludhiana District based on the hybrid score <span className="text-white font-semibold font-mono">S_risk = 0.60 S_ml + 0.40 S_rule</span>. Connected live to SQLite backend API.
          </p>
        </div>

        <div className="bg-[#17181B] border border-zinc-800 p-3.5 rounded-xl text-xs shrink-0 space-y-1 font-mono">
          <div className="flex items-center space-x-2 text-white font-semibold">
            <Layers className="w-4 h-4 text-white" />
            <span>220 Validated Works</span>
          </div>
          <div className="text-[11px] text-zinc-400">
            <span>FastAPI Paginated Queue</span>
          </div>
        </div>
      </div>

      {/* Severity Filter KPI Cards Bar */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 text-xs">
        <button
          onClick={() => handleFilterChange('ALL')}
          className={`p-4 rounded-2xl border text-left transition-all duration-200 font-sans button-press-effect ${
            activeFilter === 'ALL' 
              ? 'bg-white border-white text-black font-bold shadow-md' 
              : 'deep-black-card hover:border-zinc-700 text-zinc-300'
          }`}
        >
          <div className={`text-[10px] uppercase font-mono font-bold ${activeFilter === 'ALL' ? 'text-zinc-700' : 'text-zinc-400'}`}>ALL SCORED WORKS</div>
          <div className="text-xl font-bold mt-1 font-sans">{kpis ? kpis.total_sanctioned_works : 220}</div>
          <div className={`text-[10px] mt-0.5 font-mono ${activeFilter === 'ALL' ? 'text-zinc-700' : 'text-zinc-500'}`}>100% Validated</div>
        </button>

        <button
          onClick={() => handleFilterChange('CRITICAL')}
          className={`p-4 rounded-2xl border text-left transition-all duration-200 font-sans button-press-effect ${
            activeFilter === 'CRITICAL' 
              ? 'bg-rose-700 border-rose-700 text-white shadow-md' 
              : 'deep-black-card hover:border-zinc-700 text-zinc-300'
          }`}
        >
          <div className={`text-[10px] uppercase font-mono font-bold ${activeFilter === 'CRITICAL' ? 'text-rose-100' : 'text-rose-400'}`}>CRITICAL RISK</div>
          <div className={`text-xl font-bold mt-1 font-sans ${activeFilter === 'CRITICAL' ? 'text-white' : 'text-rose-400'}`}>{kpis ? kpis.critical_risk_count : 0}</div>
          <div className={`text-[10px] mt-0.5 font-mono ${activeFilter === 'CRITICAL' ? 'text-rose-100' : 'text-zinc-500'}`}>S_risk ≥ 75.0</div>
        </button>

        <button
          onClick={() => handleFilterChange('HIGH')}
          className={`p-4 rounded-2xl border text-left transition-all duration-200 font-sans button-press-effect ${
            activeFilter === 'HIGH' 
              ? 'bg-amber-600 border-amber-600 text-white shadow-md' 
              : 'deep-black-card hover:border-zinc-700 text-zinc-300'
          }`}
        >
          <div className={`text-[10px] uppercase font-mono font-bold ${activeFilter === 'HIGH' ? 'text-amber-100' : 'text-amber-400'}`}>HIGH RISK</div>
          <div className={`text-xl font-bold mt-1 font-sans ${activeFilter === 'HIGH' ? 'text-white' : 'text-amber-400'}`}>{kpis ? kpis.high_risk_count : 5}</div>
          <div className={`text-[10px] mt-0.5 font-mono ${activeFilter === 'HIGH' ? 'text-amber-100' : 'text-zinc-500'}`}>60.0 ≤ S_risk &lt; 75.0</div>
        </button>

        <button
          onClick={() => handleFilterChange('MEDIUM')}
          className={`p-4 rounded-2xl border text-left transition-all duration-200 font-sans button-press-effect ${
            activeFilter === 'MEDIUM' 
              ? 'bg-sky-700 border-sky-700 text-white shadow-md' 
              : 'deep-black-card hover:border-zinc-700 text-zinc-300'
          }`}
        >
          <div className={`text-[10px] uppercase font-mono font-bold ${activeFilter === 'MEDIUM' ? 'text-sky-100' : 'text-sky-400'}`}>MEDIUM RISK</div>
          <div className={`text-xl font-bold mt-1 font-sans ${activeFilter === 'MEDIUM' ? 'text-white' : 'text-sky-400'}`}>{kpis ? kpis.medium_risk_count : 11}</div>
          <div className={`text-[10px] mt-0.5 font-mono ${activeFilter === 'MEDIUM' ? 'text-sky-100' : 'text-zinc-500'}`}>40.0 ≤ S_risk &lt; 60.0</div>
        </button>

        <button
          onClick={() => handleFilterChange('NORMAL')}
          className={`p-4 rounded-2xl border text-left transition-all duration-200 font-sans button-press-effect ${
            activeFilter === 'NORMAL' 
              ? 'bg-zinc-800 border-zinc-800 text-white shadow-md' 
              : 'deep-black-card hover:border-zinc-700 text-zinc-300'
          }`}
        >
          <div className={`text-[10px] uppercase font-mono font-bold ${activeFilter === 'NORMAL' ? 'text-zinc-300' : 'text-zinc-400'}`}>NORMAL RISK</div>
          <div className={`text-xl font-bold mt-1 font-sans ${activeFilter === 'NORMAL' ? 'text-white' : 'text-white'}`}>{kpis ? kpis.normal_risk_count : 204}</div>
          <div className={`text-[10px] mt-0.5 font-mono ${activeFilter === 'NORMAL' ? 'text-zinc-300' : 'text-zinc-500'}`}>S_risk &lt; 40.0</div>
        </button>

        <button
          onClick={() => handleFilterChange('ML_ANOMALY')}
          className={`p-4 rounded-2xl border text-left transition-all duration-200 font-sans button-press-effect ${
            activeFilter === 'ML_ANOMALY' 
              ? 'bg-indigo-700 border-indigo-700 text-white shadow-md' 
              : 'deep-black-card hover:border-zinc-700 text-zinc-300'
          }`}
        >
          <div className={`text-[10px] uppercase font-mono font-bold ${activeFilter === 'ML_ANOMALY' ? 'text-indigo-100' : 'text-indigo-400'}`}>ML ANOMALIES</div>
          <div className={`text-xl font-bold mt-1 font-sans ${activeFilter === 'ML_ANOMALY' ? 'text-white' : 'text-indigo-400'}`}>{kpis ? kpis.ml_anomaly_candidates_count : 7}</div>
          <div className={`text-[10px] mt-0.5 font-mono ${activeFilter === 'ML_ANOMALY' ? 'text-indigo-100' : 'text-zinc-500'}`}>S_ml ≥ 70.0</div>
        </button>
      </div>

      {/* Main Table Container */}
      <div className="deep-black-card rounded-2xl p-6 space-y-4 shadow-xs">
        
        {/* Controls Toolbar */}
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 border-b border-zinc-800/80 pb-4">
          <div className="flex items-center space-x-3 flex-1">
            {/* Search Input */}
            <div className="relative flex-1 max-w-md">
              <Search className="w-3.5 h-3.5 text-zinc-400 absolute left-3 top-2.5" />
              <input
                type="text"
                placeholder="Search Work ID, title, or IDA agency..."
                value={searchQuery}
                onChange={(e) => handleSearchChange(e.target.value)}
                className="w-full bg-[#17181B] border border-zinc-800 rounded-xl pl-8 pr-3 py-1.5 text-xs text-white placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-zinc-700 focus:border-zinc-700 transition-all"
              />
            </div>

            {/* Category Filter Dropdown */}
            <select
              value={categoryFilter}
              onChange={(e) => handleCategoryChange(e.target.value)}
              className="bg-[#17181B] border border-zinc-800 rounded-xl px-3 py-1.5 text-xs text-white focus:outline-none focus:border-zinc-700 font-sans"
            >
              <option value="ALL">All Categories (4)</option>
              <option value="Roads/Infrastructure">Roads/Infrastructure (120)</option>
              <option value="Community Infrastructure">Community Infrastructure (53)</option>
              <option value="Public Amenities">Public Amenities (26)</option>
              <option value="Normal/Others">Normal/Others (21)</option>
            </select>
          </div>

          {/* Page Size Selector */}
          <div className="flex items-center space-x-2 text-xs text-zinc-400">
            <span>Show entries:</span>
            <select
              value={pageSize}
              onChange={(e) => handlePageSizeChange(e.target.value)}
              className="bg-[#17181B] border border-zinc-800 rounded-xl px-2.5 py-1 text-xs text-white focus:outline-none focus:border-zinc-700 font-mono"
            >
              <option value={15}>15 entries</option>
              <option value={25}>25 entries</option>
              <option value={50}>50 entries</option>
            </select>
          </div>
        </div>

        {/* Priority Queue Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse font-sans">
            <thead>
              <tr className="border-b border-zinc-800 text-zinc-300 uppercase text-[10px] font-mono bg-[#090A0B]">
                <th className="py-3.5 px-3">RANK & WORK ID</th>
                <th className="py-3.5 px-3 max-w-md">WORK DESCRIPTION</th>
                <th className="py-3.5 px-3">CATEGORY & IDA</th>
                <th className="py-3.5 px-3 text-right">AMOUNT</th>
                <th className="py-3.5 px-3 text-center">DELAY</th>
                <th className="py-3.5 px-3 text-center">S_ML</th>
                <th className="py-3.5 px-3 text-center">S_RULE</th>
                <th className="py-3.5 px-3 text-center">S_RISK</th>
                <th className="py-3.5 px-3 text-center">SEVERITY</th>
                <th className="py-3.5 px-3 text-center">ACTION</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-800/80 bg-[#121315]">
              {loading ? (
                <tr>
                  <td colSpan="10" className="py-8 text-center text-zinc-500 font-mono">
                    Loading paginated risk queue from backend REST API...
                  </td>
                </tr>
              ) : works.length > 0 ? (
                works.map((work, idx) => {
                  const globalRank = (currentPage - 1) * pageSize + idx + 1;
                  return (
                    <tr key={work.id} className="hover:bg-[#1C1D20] transition-colors duration-150">
                      <td className="py-3.5 px-3 font-mono">
                        <div className="flex items-center space-x-2">
                          <span className="text-zinc-500 font-bold text-[10px] w-6">#{globalRank}</span>
                          <span className="text-white font-bold text-[11px] truncate max-w-[130px]" title={work.id}>
                            {work.id}
                          </span>
                        </div>
                      </td>

                      <td className="py-3.5 px-3 max-w-md">
                        <div className="text-zinc-200 line-clamp-2 leading-relaxed font-medium" title={work.title}>
                          {work.title}
                        </div>
                      </td>

                      <td className="py-3.5 px-3 space-y-0.5">
                        <div className="text-white font-semibold">{work.category}</div>
                        <div className="text-[10px] text-zinc-400 font-mono truncate max-w-[150px]" title={work.ida}>
                          {work.ida}
                        </div>
                      </td>

                      <td className="py-3.5 px-3 text-right font-bold text-white font-mono">
                        ₹{(work.sanctioned_amount_lakhs || 0).toFixed(2)} L
                      </td>

                      <td className="py-3.5 px-3 text-center font-mono">
                        <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                          work.sanction_delay_days > 120 ? 'bg-amber-950/80 text-amber-300 border border-amber-800' : 'text-zinc-400'
                        }`}>
                          {work.sanction_delay_days}d
                        </span>
                      </td>

                      <td className="py-3.5 px-3 text-center font-mono">
                        <span className={`font-bold ${work.is_ml_anomaly ? 'text-indigo-400' : 'text-zinc-400'}`}>
                          {(work.ml_anomaly_score || 0).toFixed(1)}
                        </span>
                      </td>

                      <td className="py-3.5 px-3 text-center text-white font-bold font-mono">
                        {(work.rule_score || 0).toFixed(1)}
                      </td>

                      <td className="py-3.5 px-3 text-center font-mono">
                        <span className={`text-sm font-bold ${
                          work.risk_priority_score >= 75 ? 'text-rose-400' :
                          work.risk_priority_score >= 60 ? 'text-amber-400' :
                          work.risk_priority_score >= 40 ? 'text-sky-400' : 'text-white'
                        }`}>
                          {(work.risk_priority_score || 0).toFixed(1)}
                        </span>
                      </td>

                      <td className="py-3.5 px-3 text-center font-mono">
                        <span className={`text-[9px] px-2.5 py-0.5 rounded-full border font-bold ${
                          work.severity_band === 'CRITICAL RISK PRIORITY' ? 'bg-rose-950/80 text-rose-300 border-rose-800' :
                          work.severity_band === 'HIGH RISK PRIORITY' ? 'bg-amber-950/80 text-amber-300 border-amber-800' :
                          work.severity_band === 'MEDIUM RISK PRIORITY' ? 'bg-sky-950/80 text-sky-300 border-sky-800' :
                          'bg-[#17181B] text-zinc-300 border-zinc-700'
                        }`}>
                          {work.severity_band === 'HIGH RISK PRIORITY' ? 'HIGH' :
                           work.severity_band === 'MEDIUM RISK PRIORITY' ? 'MEDIUM' :
                           work.severity_band === 'CRITICAL RISK PRIORITY' ? 'CRITICAL' : 'NORMAL'}
                        </span>
                      </td>

                      <td className="py-3.5 px-3 text-center font-sans">
                        <button
                          onClick={() => handleReviewClick(work)}
                          className="px-3 py-1 rounded-xl bg-white hover:bg-zinc-200 text-black text-[11px] font-bold transition-all duration-150 shadow-2xs button-press-effect"
                        >
                          Review
                        </button>
                      </td>
                    </tr>
                  );
                })
              ) : (
                <tr>
                  <td colSpan="10" className="py-12 text-center text-zinc-400 font-sans">
                    {activeFilter === 'CRITICAL' ? (
                      <div className="max-w-md mx-auto space-y-2 p-5 bg-[#17181B] border border-zinc-800 rounded-2xl shadow-2xs">
                        <CheckCheck className="w-8 h-8 text-emerald-400 mx-auto" />
                        <h3 className="text-sm font-bold text-white">No Critical Risk Works Found</h3>
                        <p className="text-xs text-zinc-400 leading-relaxed font-sans">
                          No validated project currently meets the Critical Risk threshold (<span className="font-mono font-semibold text-white">S_risk ≥ 75.0</span>). Max score in dataset is <span className="font-mono font-semibold text-white">S_risk = 69.4</span> (High Risk Priority).
                        </p>
                      </div>
                    ) : (
                      <span>No matching works found in database for current filters.</span>
                    )}
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Controls */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-3 pt-3 border-t border-zinc-800/80 text-xs font-sans">
          <div className="text-zinc-400">
            Showing records <span className="text-white font-semibold font-mono">{totalRecords > 0 ? (currentPage - 1) * pageSize + 1 : 0}</span> to <span className="text-white font-semibold font-mono">{Math.min(currentPage * pageSize, totalRecords)}</span> of <span className="text-white font-semibold font-mono">{totalRecords}</span> matching works
          </div>

          <div className="flex items-center space-x-2 font-mono">
            <button
              disabled={currentPage <= 1 || loading}
              onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
              className="px-3 py-1.5 rounded-xl bg-[#17181B] hover:bg-zinc-800 text-white border border-zinc-800 disabled:opacity-40 disabled:cursor-not-allowed flex items-center space-x-1 font-sans button-press-effect"
            >
              <ChevronLeft className="w-3.5 h-3.5" />
              <span>Previous</span>
            </button>
            <span className="text-zinc-400 px-2 text-xs">
              Page {currentPage} of {totalPages}
            </span>
            <button
              disabled={currentPage >= totalPages || loading}
              onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
              className="px-3 py-1.5 rounded-xl bg-[#17181B] hover:bg-zinc-800 text-white border border-zinc-800 disabled:opacity-40 disabled:cursor-not-allowed flex items-center space-x-1 font-sans button-press-effect"
            >
              <span>Next</span>
              <ChevronRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>

      </div>

      {/* Review Evidence Modal */}
      {activeModalWork && (
        <div className="fixed inset-0 z-50 bg-black/75 backdrop-blur-xs flex items-center justify-center p-4 overflow-y-auto">
          <div className="bg-[#121315] border border-zinc-800 rounded-2xl max-w-2xl w-full p-6 space-y-4 shadow-2xl font-sans text-white max-h-[90vh] overflow-y-auto my-auto">
            <div className="flex items-center justify-between border-b border-zinc-800 pb-3">
              <div className="flex items-center space-x-2">
                <AlertTriangle className="w-5 h-5 text-amber-400" />
                <h3 className="text-sm font-bold text-white uppercase tracking-wider font-sans">
                  Risk Attribution Evidence Summary
                </h3>
              </div>
              <button 
                onClick={() => setActiveModalWork(null)}
                className="text-zinc-400 hover:text-white text-xs font-bold px-2.5 py-1 bg-[#17181B] rounded-xl border border-zinc-800"
              >
                ✕ Close
              </button>
            </div>

            <div className="space-y-3 text-xs">
              <div className="flex justify-between items-start bg-[#17181B] p-4 rounded-xl border border-zinc-800">
                <div>
                  <div className="text-white font-bold font-mono text-xs">{activeModalWork.id}</div>
                  <div className="text-zinc-200 font-semibold mt-1 text-xs">{activeModalWork.title}</div>
                </div>
                <div className="text-right shrink-0 pl-4 font-mono">
                  <div className="text-lg font-bold text-white">{activeModalWork.risk_priority_score.toFixed(1)}</div>
                  <div className="text-[10px] text-zinc-400 uppercase font-sans">Risk Priority Score</div>
                </div>
              </div>

              {/* Explainable Risk Executive Summary Narrative */}
              {activeModalWork.explanation?.executive_summary && (
                <div className="bg-[#17181B] border border-zinc-800 p-4 rounded-xl text-zinc-300 leading-relaxed text-[11px]">
                  <strong className="text-white block uppercase font-mono font-semibold text-[10px] mb-0.5">Explainability Summary:</strong>
                  <p className="font-sans">{activeModalWork.explanation.executive_summary}</p>
                </div>
              )}

              <div className="grid grid-cols-2 gap-3">
                <div className="bg-[#17181B] p-4 rounded-xl border border-zinc-800">
                  <span className="text-zinc-400 text-[10px] uppercase font-mono">ML Isolation Forest Anomaly</span>
                  <div className="text-base font-bold text-indigo-400 mt-1 font-mono">
                    {activeModalWork.ml_anomaly_score.toFixed(1)} / 100
                  </div>
                  <p className="text-[11px] text-zinc-400 mt-1">
                    {activeModalWork.is_ml_anomaly ? 'Statistically significant anomaly candidate.' : 'Normal feature distribution.'}
                  </p>
                </div>

                <div className="bg-[#17181B] p-4 rounded-xl border border-zinc-800">
                  <span className="text-zinc-400 text-[10px] uppercase font-mono">Statutory Compliance Rules</span>
                  <div className="text-base font-bold text-white mt-1 font-mono">
                    {activeModalWork.rule_score.toFixed(1)} / 100
                  </div>
                  <p className="text-[11px] text-zinc-400 mt-1">
                    {(activeModalWork.rule_signals || []).length} compliance rule signals triggered.
                  </p>
                </div>
              </div>
            </div>

            <div className="flex items-center justify-between pt-3 border-t border-zinc-800">
              {onSelectWorkForInvestigation ? (
                <button
                  onClick={() => {
                    const targetId = activeModalWork.id;
                    setActiveModalWork(null);
                    onSelectWorkForInvestigation(targetId);
                  }}
                  className="px-4 py-2 bg-white hover:bg-zinc-200 text-black rounded-xl text-xs font-bold flex items-center space-x-1.5 transition-colors shadow-2xs button-press-effect"
                >
                  <span>Open in Investigation Workspace (Page 4) →</span>
                </button>
              ) : <div></div>}

              <button
                onClick={() => setActiveModalWork(null)}
                className="px-4 py-2 bg-[#17181B] hover:bg-zinc-800 text-white rounded-xl text-xs font-semibold border border-zinc-800"
              >
                Close Summary
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
