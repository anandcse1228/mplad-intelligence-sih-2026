import React, { useState, useEffect, useMemo } from 'react';
import { 
  BarChart3, 
  Building, 
  MapPin, 
  PieChart, 
  AlertTriangle, 
  CheckCircle2, 
  Clock, 
  FileText,
  Info,
  Shield,
  Layers,
  TrendingUp,
  Award
} from 'lucide-react';
import { api } from '../api/client';

export default function DistrictAnalyticsPage() {
  const [allWorks, setAllWorks] = useState([]);
  const [loading, setLoading] = useState(true);

  // Selected Filter State
  const [selectedIda, setSelectedIda] = useState('ALL');
  const [selectedCategory, setSelectedCategory] = useState('ALL');

  useEffect(() => {
    let isMounted = true;
    api.getRiskQueue({ page: 1, page_size: 500 })
      .then(res => {
        if (isMounted) {
          setAllWorks(res.items || []);
          setLoading(false);
        }
      })
      .catch(err => {
        console.error("Failed to fetch works for analytics:", err);
        if (isMounted) setLoading(false);
      });
    return () => { isMounted = false; };
  }, []);

  // Compute District Metadata Dynamically
  const districtMetadata = useMemo(() => {
    if (!allWorks || allWorks.length === 0) {
      return { state: 'Punjab', district: 'Ludhiana', constituency: 'LUDHIANA', mpName: 'Nodal Representative' };
    }
    const first = allWorks[0];
    return {
      state: first.state || 'State',
      district: first.district || 'District',
      constituency: first.constituency || 'Constituency',
      mpName: first.mp_name || 'Nodal Representative'
    };
  }, [allWorks]);

  // Compute Unique IDAs & Categories
  const idas = useMemo(() => {
    if (!allWorks) return ['ALL'];
    const set = new Set(allWorks.map(w => w.ida).filter(Boolean));
    return ['ALL', ...Array.from(set).sort()];
  }, [allWorks]);

  const categories = useMemo(() => {
    if (!allWorks) return ['ALL'];
    const set = new Set(allWorks.map(w => w.category).filter(Boolean));
    return ['ALL', ...Array.from(set).sort()];
  }, [allWorks]);

  // Filtered dataset for analytics
  const filteredWorks = useMemo(() => {
    if (!allWorks) return [];
    return allWorks.filter(w => {
      if (selectedIda !== 'ALL' && w.ida !== selectedIda) return false;
      if (selectedCategory !== 'ALL' && w.category !== selectedCategory) return false;
      return true;
    });
  }, [allWorks, selectedIda, selectedCategory]);

  // Total Summary Metrics for Filtered Works
  const summaryMetrics = useMemo(() => {
    const count = filteredWorks.length;
    const totalSanctionedCr = filteredWorks.reduce((acc, w) => acc + (w.sanctioned_amount_lakhs || 0), 0) / 100.0;
    const totalRecommendedCr = filteredWorks.reduce((acc, w) => acc + (w.recommended_amount_lakhs || 0), 0) / 100.0;
    const totalDisbursedCr = filteredWorks.reduce((acc, w) => acc + (w.disbursed_amount_lakhs || 0), 0) / 100.0;
    
    const delays = filteredWorks.map(w => w.sanction_delay_days || 0);
    const avgDelay = delays.length > 0 ? (delays.reduce((a, b) => a + b, 0) / delays.length) : 0;
    
    const sortedDelays = [...delays].sort((a, b) => a - b);
    const medianDelay = sortedDelays.length > 0 ? sortedDelays[Math.floor(sortedDelays.length / 2)] : 0;

    const criticalRiskCount = filteredWorks.filter(w => w.severity_band === 'CRITICAL RISK PRIORITY').length;
    const highRiskCount = filteredWorks.filter(w => w.severity_band === 'HIGH RISK PRIORITY').length;
    const mediumRiskCount = filteredWorks.filter(w => w.severity_band === 'MEDIUM RISK PRIORITY').length;
    const normalRiskCount = filteredWorks.filter(w => w.severity_band === 'NORMAL RISK').length;
    const mlAnomaliesCount = filteredWorks.filter(w => w.is_ml_anomaly).length;

    return {
      count,
      totalSanctionedCr: totalSanctionedCr.toFixed(2),
      totalRecommendedCr: totalRecommendedCr.toFixed(2),
      totalDisbursedCr: totalDisbursedCr.toFixed(2),
      avgDelay: avgDelay.toFixed(1),
      medianDelay,
      criticalRiskCount,
      highRiskCount,
      mediumRiskCount,
      normalRiskCount,
      mlAnomaliesCount
    };
  }, [filteredWorks]);

  // IDA Allocation Breakdown Data
  const idaBreakdown = useMemo(() => {
    const map = {};
    allWorks.forEach(w => {
      if (!map[w.ida]) {
        map[w.ida] = {
          ida: w.ida,
          worksCount: 0,
          totalSanctionedLakhs: 0,
          highRiskCount: 0,
          mlAnomaliesCount: 0,
          delays: []
        };
      }
      map[w.ida].worksCount += 1;
      map[w.ida].totalSanctionedLakhs += (w.sanctioned_amount_lakhs || 0);
      if (w.severity_band === 'HIGH RISK PRIORITY' || w.severity_band === 'CRITICAL RISK PRIORITY') {
        map[w.ida].highRiskCount += 1;
      }
      if (w.is_ml_anomaly) {
        map[w.ida].mlAnomaliesCount += 1;
      }
      map[w.ida].delays.push(w.sanction_delay_days || 0);
    });

    return Object.values(map).map(item => ({
      ...item,
      avgDelay: item.delays.length > 0 ? (item.delays.reduce((a, b) => a + b, 0) / item.delays.length).toFixed(1) : 0
    })).sort((a, b) => b.totalSanctionedLakhs - a.totalSanctionedLakhs);
  }, [allWorks]);

  // Category Allocation Breakdown Data
  const categoryBreakdown = useMemo(() => {
    const map = {};
    allWorks.forEach(w => {
      if (!map[w.category]) {
        map[w.category] = {
          category: w.category,
          worksCount: 0,
          totalSanctionedLakhs: 0,
          highRiskCount: 0,
          mlAnomaliesCount: 0
        };
      }
      map[w.category].worksCount += 1;
      map[w.category].totalSanctionedLakhs += (w.sanctioned_amount_lakhs || 0);
      if (w.severity_band === 'HIGH RISK PRIORITY' || w.severity_band === 'CRITICAL RISK PRIORITY') {
        map[w.category].highRiskCount += 1;
      }
      if (w.is_ml_anomaly) map[w.category].mlAnomaliesCount += 1;
    });

    return Object.values(map).sort((a, b) => b.totalSanctionedLakhs - a.totalSanctionedLakhs);
  }, [allWorks]);

  if (loading) {
    return (
      <div className="p-8 font-mono text-center text-zinc-500 deep-black-card rounded-2xl">
        Loading API district analytics...
      </div>
    );
  }

  const maxCategoryLakhs = Math.max(...categoryBreakdown.map(c => c.totalSanctionedLakhs), 1);
  const actualIdaCount = idas.filter(i => i !== 'ALL').length;
  const actualCatCount = categories.filter(c => c !== 'ALL').length;

  return (
    <div className="space-y-6 font-sans selection:bg-slate-900 selection:text-white pb-6">
      
      {/* Header Context Banner */}
      <div className="deep-black-card rounded-2xl p-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2 text-xs text-zinc-400 font-semibold mb-1 font-mono">
            <BarChart3 className="w-3.5 h-3.5 text-white" />
            <span className="uppercase">PAGE 3 • {districtMetadata.district} DISTRICT ANALYTICS ({districtMetadata.state})</span>
          </div>
          <h1 className="text-xl font-bold text-white tracking-tight">
            Constituency Risk Analytics & IDA Allocation Breakdown
          </h1>
          <p className="text-xs text-zinc-400 mt-1 max-w-3xl leading-relaxed">
            Analytical distribution of <span className="text-white font-semibold">{allWorks.length} validated sanctioned MPLADS works</span> across {actualIdaCount} Nodal Implementing Agencies (IDAs) and {actualCatCount} scheme work categories in {districtMetadata.constituency} Constituency.
          </p>
        </div>

        {/* Dynamic Filters Toolbar */}
        <div className="flex flex-wrap items-center gap-3 bg-[#17181B] border border-zinc-800 p-3.5 rounded-xl text-xs font-sans shrink-0">
          <div className="space-y-1">
            <label className="text-[10px] text-zinc-400 uppercase font-mono block">FILTER BY IDA AGENCY:</label>
            <select
              value={selectedIda}
              onChange={(e) => setSelectedIda(e.target.value)}
              className="bg-[#121315] border border-zinc-700/80 rounded-lg px-2.5 py-1 text-xs text-white focus:outline-none focus:border-zinc-500 font-sans"
            >
              {idas.map((ida, idx) => (
                <option key={idx} value={ida}>
                  {ida === 'ALL' ? `All IDAs (${actualIdaCount} Agencies)` : ida.substring(0, 35)}
                </option>
              ))}
            </select>
          </div>

          <div className="space-y-1">
            <label className="text-[10px] text-zinc-400 uppercase font-mono block">FILTER BY CATEGORY:</label>
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="bg-[#121315] border border-zinc-700/80 rounded-lg px-2.5 py-1 text-xs text-white focus:outline-none focus:border-zinc-500 font-sans"
            >
              {categories.map((cat, idx) => (
                <option key={idx} value={cat}>
                  {cat === 'ALL' ? `All Categories (${actualCatCount})` : cat}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Overview Analytics Summary Strip */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs font-sans">
        <div className="deep-black-card deep-black-card-hover rounded-2xl p-5 space-y-1">
          <span className="text-zinc-400 text-[10px] uppercase font-semibold font-mono">SANCTIONED OUTLAY</span>
          <div className="text-xl font-bold text-white font-mono">₹{summaryMetrics.totalSanctionedCr} Cr</div>
          <span className="text-[10px] text-zinc-400 font-mono">Filter Count: {summaryMetrics.count} Works</span>
        </div>

        <div className="deep-black-card deep-black-card-hover rounded-2xl p-5 space-y-1">
          <span className="text-zinc-400 text-[10px] uppercase font-semibold font-mono">AVERAGE DELAY</span>
          <div className="text-xl font-bold text-amber-400 font-mono">{summaryMetrics.avgDelay} Days</div>
          <span className="text-[10px] text-zinc-400 font-mono">Median: {summaryMetrics.medianDelay} Days</span>
        </div>

        <div className="deep-black-card deep-black-card-hover rounded-2xl p-5 space-y-1">
          <span className="text-zinc-400 text-[10px] uppercase font-semibold font-mono">HIGH / CRITICAL RISK</span>
          <div className="text-xl font-bold text-rose-400 font-mono">{summaryMetrics.highRiskCount + summaryMetrics.criticalRiskCount}</div>
          <span className="text-[10px] text-zinc-400 font-mono">Require Priority Audit</span>
        </div>

        <div className="deep-black-card deep-black-card-hover rounded-2xl p-5 space-y-1">
          <span className="text-zinc-400 text-[10px] uppercase font-semibold font-mono">ML ANOMALY OUTLIERS</span>
          <div className="text-xl font-bold text-indigo-400 font-mono">{summaryMetrics.mlAnomaliesCount}</div>
          <span className="text-[10px] text-zinc-400 font-mono">Isolation Forest Upper 30%</span>
        </div>
      </div>

      {/* SECTION 1: IDA IMPLEMENTING AGENCY CONCENTRATION TABLE */}
      <div className="deep-black-card deep-black-card-hover rounded-2xl p-6 space-y-4">
        <div className="flex items-center justify-between border-b border-zinc-800/80 pb-3">
          <div className="flex items-center space-x-2">
            <Building className="w-4 h-4 text-white" />
            <h3 className="text-xs font-bold text-white uppercase tracking-wider">
              Nodal Implementing Agency (IDA) Work & Outlay Distribution
            </h3>
          </div>
          <span className="text-[10px] font-mono text-zinc-400 bg-[#17181B] border border-zinc-800 px-2.5 py-0.5 rounded-full">
            {idaBreakdown.length} Active IDAs
          </span>
        </div>

        <div className="overflow-x-auto border border-zinc-800/80 rounded-xl">
          <table className="w-full text-left text-xs font-sans">
            <thead className="bg-[#17181B] text-zinc-400 border-b border-zinc-800 font-mono text-[10px] uppercase">
              <tr>
                <th className="px-4 py-2.5">Implementing Agency (IDA)</th>
                <th className="px-4 py-2.5 text-center">Total Works</th>
                <th className="px-4 py-2.5">Total Outlay (₹ Lakhs)</th>
                <th className="px-4 py-2.5 text-center">Avg Delay</th>
                <th className="px-4 py-2.5 text-center">ML Anomalies</th>
                <th className="px-4 py-2.5 text-center">High / Critical</th>
                <th className="px-4 py-2.5 text-right">Agency Concentration</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-800 text-zinc-300 font-mono text-[11px]">
              {idaBreakdown.map((item, idx) => {
                const pct = allWorks.length > 0 ? ((item.worksCount / allWorks.length) * 100).toFixed(1) : 0;
                return (
                  <tr key={idx} className="hover:bg-[#17181B]/50 transition-colors">
                    <td className="px-4 py-3 font-semibold text-white font-sans">{item.ida}</td>
                    <td className="px-4 py-3 text-center text-white font-bold">{item.worksCount}</td>
                    <td className="px-4 py-3 text-white font-bold font-mono">₹{item.totalSanctionedLakhs.toFixed(2)} L</td>
                    <td className="px-4 py-3 text-center text-amber-400">{item.avgDelay}d</td>
                    <td className="px-4 py-3 text-center text-indigo-400 font-bold">{item.mlAnomaliesCount}</td>
                    <td className="px-4 py-3 text-center text-rose-400 font-bold">{item.highRiskCount}</td>
                    <td className="px-4 py-3 text-right">
                      <div className="flex items-center justify-end space-x-2">
                        <span className="text-zinc-400 font-mono text-[10px]">{pct}%</span>
                        <div className="w-16 bg-zinc-800 h-1.5 rounded-full overflow-hidden">
                          <div style={{ width: `${pct}%` }} className="bg-indigo-500 h-full"></div>
                        </div>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* SECTION 2: CATEGORY ALLOCATION BREAKDOWN */}
      <div className="deep-black-card deep-black-card-hover rounded-2xl p-6 space-y-4">
        <div className="flex items-center justify-between border-b border-zinc-800/80 pb-3">
          <div className="flex items-center space-x-2">
            <PieChart className="w-4 h-4 text-white" />
            <h3 className="text-xs font-bold text-white uppercase tracking-wider">
              Category Cost Distribution & Risk Concentration
            </h3>
          </div>
          <span className="text-[10px] font-mono text-zinc-400 bg-[#17181B] border border-zinc-800 px-2.5 py-0.5 rounded-full">
            {categoryBreakdown.length} Scheme Categories
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {categoryBreakdown.map((cat, idx) => {
            const barPct = ((cat.totalSanctionedLakhs / maxCategoryLakhs) * 100).toFixed(1);
            return (
              <div key={idx} className="bg-[#17181B] p-4 rounded-xl border border-zinc-800 space-y-2">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-bold text-white font-sans">{cat.category}</span>
                  <span className="font-mono text-white font-bold">₹{cat.totalSanctionedLakhs.toFixed(2)} Lakhs</span>
                </div>

                <div className="w-full bg-[#111214] h-2 rounded-full overflow-hidden border border-zinc-700/60">
                  <div style={{ width: `${barPct}%` }} className="bg-emerald-500 h-full"></div>
                </div>

                <div className="flex items-center justify-between text-[11px] text-zinc-400 font-mono pt-1">
                  <span>Works: <strong className="text-white">{cat.worksCount}</strong></span>
                  <span>ML Anomalies: <strong className="text-indigo-400">{cat.mlAnomaliesCount}</strong></span>
                  <span>High/Critical Risk: <strong className="text-rose-400">{cat.highRiskCount}</strong></span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

    </div>
  );
}
