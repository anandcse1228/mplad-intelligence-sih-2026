import React, { useState, useEffect } from 'react';
import { 
  Search, 
  ChevronRight, 
  Cpu,
  Layers,
  AlertTriangle,
  FileCheck
} from 'lucide-react';
import { api } from '../api/client';

export default function RiskQueueTable() {
  const [searchTerm, setSearchTerm] = useState('');
  const [activeModalWork, setActiveModalWork] = useState(null);
  const [queueItems, setQueueItems] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;
    api.getRiskQueue({ page: 1, page_size: 10, search: searchTerm })
      .then(res => {
        if (isMounted) {
          setQueueItems(res.items || []);
          setLoading(false);
        }
      })
      .catch(err => {
        console.error("Failed to fetch risk queue preview:", err);
        if (isMounted) setLoading(false);
      });
    return () => { isMounted = false; };
  }, [searchTerm]);

  const handleReviewClick = (work) => {
    setActiveModalWork(work);
  };

  return (
    <div className="deep-black-card rounded-2xl overflow-hidden font-sans shadow-xs">
      {/* Table Header Controls */}
      <div className="p-5 border-b border-zinc-800/80 flex flex-col md:flex-row md:items-center justify-between gap-3 bg-[#121315]">
        <div>
          <div className="flex items-center space-x-2">
            <Layers className="w-4 h-4 text-white" />
            <h2 className="text-sm font-bold text-white uppercase tracking-wider font-sans">
              ML Isolation Forest Priority Audit Queue (S_risk = 0.60 S_ml + 0.40 S_rule)
            </h2>
          </div>
          <p className="text-xs text-zinc-400 mt-0.5 font-sans">
            Ranked risk priority queue combining unsupervised ML Isolation Forest anomaly evidence with statutory compliance rule signals.
          </p>
        </div>

        {/* Search Input */}
        <div className="flex items-center space-x-3">
          <div className="relative">
            <Search className="w-3.5 h-3.5 text-zinc-400 absolute left-3 top-2.5" />
            <input 
              type="text"
              placeholder="Search work title, ID, agency..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="bg-[#17181B] border border-zinc-800 rounded-xl pl-8 pr-3 py-1.5 text-xs text-white placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-zinc-700 focus:border-zinc-700 w-48 lg:w-64 transition-all"
            />
          </div>
        </div>
      </div>

      {/* Table Content */}
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs border-collapse font-sans">
          <thead>
            <tr className="border-b border-zinc-800 text-zinc-300 uppercase text-[10px] font-mono bg-[#090A0B]">
              <th className="py-3.5 px-4">RANK & WORK ID</th>
              <th className="py-3.5 px-4">WORK DESCRIPTION</th>
              <th className="py-3.5 px-4">CATEGORY & IDA</th>
              <th className="py-3.5 px-4 text-right">SANCTION AMOUNT</th>
              <th className="py-3.5 px-4 text-center">DELAY</th>
              <th className="py-3.5 px-4 text-center">S_ML</th>
              <th className="py-3.5 px-4 text-center">S_RULE</th>
              <th className="py-3.5 px-4 text-center">S_RISK</th>
              <th className="py-3.5 px-4 text-center">SEVERITY BAND</th>
              <th className="py-3.5 px-4 text-center font-sans">ACTION</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-zinc-800/80 bg-[#121315]">
            {loading ? (
              <tr>
                <td colSpan="10" className="py-8 text-center text-zinc-500 font-mono">
                  Loading live API risk queue preview...
                </td>
              </tr>
            ) : queueItems.length > 0 ? (
              queueItems.map((work, idx) => (
                <tr key={work.id} className="hover:bg-[#1C1D20] transition-colors duration-150">
                  <td className="py-3.5 px-4 font-mono">
                    <div className="flex items-center space-x-2">
                      <span className="text-zinc-500 font-bold text-[10px]">#{idx + 1}</span>
                      <span className="text-white font-bold text-[11px] truncate max-w-[130px]" title={work.id}>
                        {work.id}
                      </span>
                    </div>
                  </td>

                  <td className="py-3.5 px-4 max-w-xs">
                    <div className="text-zinc-200 line-clamp-2 leading-relaxed font-medium" title={work.title}>
                      {work.title}
                    </div>
                  </td>

                  <td className="py-3.5 px-4 space-y-0.5">
                    <div className="text-white font-semibold">{work.category}</div>
                    <div className="text-[10px] text-zinc-400 font-mono truncate max-w-[140px]" title={work.ida}>
                      {work.ida}
                    </div>
                  </td>

                  <td className="py-3.5 px-4 text-right font-bold text-white font-mono">
                    ₹{(work.sanctioned_amount_lakhs || 0).toFixed(2)} Lakhs
                  </td>

                  <td className="py-3.5 px-4 text-center font-mono">
                    <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                      work.sanction_delay_days > 120 ? 'bg-amber-950/80 text-amber-300 border border-amber-800/80' : 'text-zinc-400'
                    }`}>
                      {work.sanction_delay_days}d
                    </span>
                  </td>

                  <td className="py-3.5 px-4 text-center font-mono">
                    <span className={`font-bold ${work.is_ml_anomaly ? 'text-indigo-400' : 'text-zinc-400'}`}>
                      {(work.ml_anomaly_score || 0).toFixed(1)}
                    </span>
                  </td>

                  <td className="py-3.5 px-4 text-center text-white font-bold font-mono">
                    {(work.rule_score || 0).toFixed(1)}
                  </td>

                  <td className="py-3.5 px-4 text-center font-mono">
                    <span className={`text-sm font-bold ${
                      work.risk_priority_score >= 75 ? 'text-rose-400' :
                      work.risk_priority_score >= 60 ? 'text-amber-400' :
                      work.risk_priority_score >= 40 ? 'text-sky-400' : 'text-white'
                    }`}>
                      {(work.risk_priority_score || 0).toFixed(1)}
                    </span>
                  </td>

                  <td className="py-3.5 px-4 text-center font-mono">
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

                  <td className="py-3.5 px-4 text-center font-sans">
                    <button
                      onClick={() => handleReviewClick(work)}
                      className="px-3 py-1 rounded-xl bg-white hover:bg-zinc-200 text-black text-[10px] font-bold transition-all duration-150 shadow-2xs button-press-effect"
                    >
                      Review
                    </button>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="10" className="py-8 text-center text-zinc-500 font-mono">
                  No matching works found.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Review Modal */}
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
                  <div className="text-zinc-200 font-semibold mt-1">{activeModalWork.title}</div>
                </div>
                <div className="text-right font-mono shrink-0 pl-4">
                  <div className="text-lg font-bold text-white">{activeModalWork.risk_priority_score.toFixed(1)}</div>
                  <div className="text-[10px] text-zinc-400 uppercase font-sans">Risk Priority Score</div>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3 font-mono">
                <div className="bg-[#17181B] p-4 rounded-xl border border-zinc-800">
                  <span className="text-zinc-400 text-[10px] uppercase font-sans">ML Isolation Forest Anomaly</span>
                  <div className="text-base font-bold text-indigo-400 mt-1">
                    {activeModalWork.ml_anomaly_score.toFixed(1)} / 100
                  </div>
                  <p className="text-[10px] text-zinc-400 mt-1 font-sans">
                    {activeModalWork.is_ml_anomaly ? 'Statistically significant anomaly candidate.' : 'Normal feature distribution.'}
                  </p>
                </div>

                <div className="bg-[#17181B] p-4 rounded-xl border border-zinc-800">
                  <span className="text-zinc-400 text-[10px] uppercase font-sans">Statutory Compliance Rules</span>
                  <div className="text-base font-bold text-white mt-1">
                    {activeModalWork.rule_score.toFixed(1)} / 100
                  </div>
                  <p className="text-[10px] text-zinc-400 mt-1 font-sans">
                    {(activeModalWork.rule_signals || []).length} compliance rule signals triggered.
                  </p>
                </div>
              </div>
            </div>

            <div className="flex items-center justify-end pt-3 border-t border-zinc-800">
              <button
                onClick={() => setActiveModalWork(null)}
                className="px-4 py-2 bg-white hover:bg-zinc-200 text-black rounded-xl text-xs font-bold button-press-effect"
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
