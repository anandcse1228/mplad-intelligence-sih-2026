import React from 'react';
import { Cpu, CheckCircle2, ShieldAlert } from 'lucide-react';

export default function DataNoticeBanner({ activeDataset }) {
  const sanctionedCount = activeDataset?.sanctioned_count || 220;
  const anomalyCount = activeDataset?.ml_anomaly_count || 7;
  const datasetName = activeDataset?.name || 'Active MPLADS Dataset';

  return (
    <div className="bg-[#141518] border border-zinc-800/80 text-white rounded-2xl p-6 shadow-md font-sans">
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
        {/* Primary ML Engine Status Narrative & Formula */}
        <div className="space-y-2.5 max-w-3xl">
          <div className="flex items-center space-x-3 font-mono">
            <span className="flex items-center space-x-1.5 text-xs font-bold text-emerald-400 bg-emerald-950/80 px-3 py-1 rounded-full border border-emerald-800/80">
              <Cpu className="w-3.5 h-3.5" />
              <span>ISOLATION FOREST ENGINE ACTIVE</span>
            </span>
            <span className="text-xs text-zinc-400">
              Scored: <strong className="text-white">{sanctionedCount} Sanctioned Works</strong>
            </span>
            <span className="text-xs text-zinc-400">
              Features: <strong className="text-white">6 Engineered Metrics</strong>
            </span>
          </div>

          <h3 className="text-sm font-bold text-white tracking-tight font-sans">
            Hybrid Risk Scoring Formula: <span className="font-mono text-emerald-400 font-bold">S_risk = 0.60 × S_ml + 0.40 × S_rule</span>
          </h3>

          <p className="text-xs text-zinc-300 leading-relaxed font-sans">
            Unsupervised ML Isolation Forest evaluates statistical anomaly distance (<span className="font-mono text-indigo-300">S_ml</span>), combined deterministically with statutory compliance rule violations (<span className="font-mono text-zinc-200">S_rule</span>) across active dataset <strong className="text-white">'{datasetName}'</strong>. Identifies {anomalyCount} statistical anomaly candidates (<span className="font-mono text-emerald-400 font-bold">S_ml ≥ 70.0</span>) requiring officer audit.
          </p>
        </div>

        {/* Supporting Model Status Indicators */}
        <div className="flex flex-col sm:flex-row lg:flex-col items-start lg:items-end gap-2 text-xs font-mono shrink-0">
          <div className="bg-[#1A1B1E] border border-zinc-800/80 px-3.5 py-1.5 rounded-xl flex items-center space-x-2 text-zinc-300">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
            <span>Multi-Dataset Isolation Active</span>
          </div>
          <div className="bg-[#1A1B1E] border border-zinc-800/80 px-3.5 py-1.5 rounded-xl flex items-center space-x-2 text-zinc-300">
            <ShieldAlert className="w-3.5 h-3.5 text-indigo-400" />
            <span>{anomalyCount} ML Anomalies Scored</span>
          </div>
        </div>
      </div>
    </div>
  );
}
