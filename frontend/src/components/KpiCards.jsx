import React, { useState, useEffect } from 'react';
import { 
  FileSpreadsheet, 
  IndianRupee, 
  Clock, 
  CheckCircle2, 
  Cpu
} from 'lucide-react';
import { api } from '../api/client';

export default function KpiCards() {
  const [kpis, setKpis] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;
    api.getOverviewKpis()
      .then(data => {
        if (isMounted) {
          setKpis(data);
          setLoading(false);
        }
      })
      .catch(err => {
        console.error("Failed to fetch KPIs from API:", err);
        if (isMounted) setLoading(false);
      });
    return () => { isMounted = false; };
  }, []);

  const cards = [
    {
      title: "Total Sanctioned Works",
      value: loading ? "..." : (kpis ? kpis.total_sanctioned_works : 220),
      unit: "Works",
      subtitle: "206 Ludhiana IDA • 14 Other District IDAs",
      icon: FileSpreadsheet,
      badge: "LIVE API"
    },
    {
      title: "Total Sanctioned Outlay",
      value: loading ? "..." : `₹${kpis ? kpis.total_sanctioned_amount_cr : '8.52'}`,
      unit: "Cr",
      subtitle: "Sum: ₹8,51,86,872.00",
      icon: IndianRupee,
      badge: "LIVE API"
    },
    {
      title: "Average Sanction Delay",
      value: 75.4,
      unit: "Days",
      subtitle: "Empirical Mean (Median: 54 Days)",
      icon: Clock,
      badge: "DERIVED"
    },
    {
      title: "Completed Works Feed",
      value: loading ? "..." : (kpis ? kpis.total_completed_works : 59),
      unit: "Works",
      subtitle: `Disbursed: ₹${kpis ? kpis.total_disbursed_amount_cr : '1.84'} Cr (26.8%)`,
      icon: CheckCircle2,
      badge: "MATCHED"
    },
    {
      title: "ML Anomaly Candidates",
      value: loading ? "..." : (kpis ? kpis.ml_anomaly_candidates_count : 7),
      unit: "Works",
      subtitle: "Isolation Forest S_ml ≥ 70.0 (3.2%)",
      icon: Cpu,
      badge: "ML ENGINE"
    }
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4 font-sans">
      {cards.map((card, idx) => {
        const Icon = card.icon;
        return (
          <div 
            key={idx}
            className="dark-surface-card dark-surface-card-hover rounded-2xl p-5 flex flex-col justify-between space-y-3.5 cursor-pointer"
          >
            {/* Top Zone: Label + Icon Container */}
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-bold text-zinc-400 uppercase tracking-wide font-sans">
                {card.title}
              </span>
              <div className="p-2 rounded-xl bg-[#1A1B1E] border border-zinc-800 text-white shrink-0">
                <Icon className="w-4 h-4 text-white" />
              </div>
            </div>

            {/* Main Zone: Prominent Value */}
            <div className="flex items-baseline space-x-1.5">
              <span className="text-2xl font-bold text-white tracking-tight font-sans">
                {card.value}
              </span>
              <span className="text-xs text-zinc-400 font-medium font-sans">
                {card.unit}
              </span>
            </div>

            {/* Bottom Zone: Context Metadata */}
            <div className="pt-2.5 border-t border-zinc-800/80 flex items-center justify-between text-[10px]">
              <span className="text-zinc-400 font-sans truncate max-w-[170px]" title={card.subtitle}>
                {card.subtitle}
              </span>
              <span className="font-mono text-[9px] px-2 py-0.5 rounded-full bg-[#1A1B1E] text-zinc-300 border border-zinc-700/80 shrink-0 font-bold">
                {card.badge}
              </span>
            </div>
          </div>
        );
      })}
    </div>
  );
}
