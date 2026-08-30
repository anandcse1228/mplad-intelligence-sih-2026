import React from 'react';
import { PieChart, Building2 } from 'lucide-react';
import { INGESTION_METADATA } from '../data/mockData';

export default function AnalyticsWidgets() {
  const idaData = [
    { name: "DC Ludhiana IDA", count: 206, pct: 93.6, amountCr: 7.89, color: "bg-white" },
    { name: "DC Sri Muktsar Sahib IDA", count: 11, pct: 5.0, amountCr: 0.52, color: "bg-zinc-400" },
    { name: "DC Jalandhar / Ferozepur / Fazilka IDAs", count: 3, pct: 1.4, amountCr: 0.10, color: "bg-zinc-600" }
  ];

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-5 font-sans">
      {/* Real Scheme Work Status Distribution */}
      <div className="deep-black-card deep-black-card-hover rounded-2xl p-6 flex flex-col justify-between space-y-4">
        <div>
          <div className="flex items-center justify-between border-b border-zinc-800/80 pb-3 mb-4">
            <div className="flex items-center space-x-2">
              <PieChart className="w-4 h-4 text-white" />
              <h3 className="text-xs font-bold text-white uppercase tracking-wide font-sans">
                Scheme Work Status Breakdown (220 Works)
              </h3>
            </div>
            <span className="text-[10px] font-mono font-bold text-zinc-300 bg-[#17181B] px-2.5 py-0.5 rounded-full border border-zinc-800">
              CSV VALIDATED
            </span>
          </div>

          <div className="space-y-3.5">
            {INGESTION_METADATA.statusBreakdown.map((item, idx) => (
              <div key={idx} className="space-y-1.5 text-xs">
                <div className="flex justify-between items-center text-zinc-300">
                  <span className="flex items-center space-x-2">
                    <span className="w-2 h-2 rounded-full bg-white"></span>
                    <span className="font-medium text-white">{item.label}</span>
                  </span>
                  <span className="font-semibold text-white font-mono">
                    {item.count} Works ({item.percentage.toFixed(1)}%)
                  </span>
                </div>
                <div className="w-full bg-[#17181B] h-2 rounded-full overflow-hidden border border-zinc-800/80">
                  <div 
                    className="bg-white h-full transition-all duration-500 rounded-full" 
                    style={{ width: `${item.percentage}%` }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="pt-3.5 border-t border-zinc-800/80 text-[11px] text-zinc-400 font-mono flex justify-between">
          <span>Source: sanctioned_works.csv</span>
          <span>Status Records: 220</span>
        </div>
      </div>

      {/* Implementing Agency / IDA Allocation Breakdown */}
      <div className="deep-black-card deep-black-card-hover rounded-2xl p-6 flex flex-col justify-between space-y-4">
        <div>
          <div className="flex items-center justify-between border-b border-zinc-800/80 pb-3 mb-4">
            <div className="flex items-center space-x-2">
              <Building2 className="w-4 h-4 text-white" />
              <h3 className="text-xs font-bold text-white uppercase tracking-wide font-sans">
                Implementing Agency (IDA) Allocation
              </h3>
            </div>
            <span className="text-[10px] font-mono font-bold text-zinc-300 bg-[#17181B] px-2.5 py-0.5 rounded-full border border-zinc-800">
              5 IDAS TOTAL
            </span>
          </div>

          {/* Segmented Distribution Meter Bar */}
          <div className="space-y-2 mb-4">
            <div className="flex justify-between text-xs text-zinc-300">
              <span className="font-medium">IDA Allocation Ratio</span>
              <span className="font-mono text-zinc-400">Total Outlay: ₹8.52 Cr</span>
            </div>
            <div className="h-3 w-full bg-[#17181B] rounded-full overflow-hidden flex border border-zinc-800/80">
              {idaData.map((d, i) => (
                <div 
                  key={i} 
                  className={`${d.color} h-full transition-all`}
                  style={{ width: `${d.pct}%` }}
                  title={`${d.name}: ${d.count} works (${d.pct}%)`}
                ></div>
              ))}
            </div>
          </div>

          <div className="space-y-3 pt-1">
            {idaData.map((item, idx) => (
              <div key={idx} className="bg-[#17181B] border border-zinc-800/80 p-3.5 rounded-xl text-xs space-y-1">
                <div className="flex justify-between items-center">
                  <span className="flex items-center space-x-2">
                    <span className={`w-2.5 h-2.5 rounded-full ${item.color}`}></span>
                    <span className="font-semibold text-white">{item.name}</span>
                  </span>
                  <span className="font-bold text-white font-mono">
                    {item.count} Works ({item.pct}%)
                  </span>
                </div>
                <div className="flex justify-between text-[11px] text-zinc-400 font-mono pl-4">
                  <span>Sanctioned Outlay: ₹{item.amountCr.toFixed(2)} Cr</span>
                  <span>Share: {item.pct}%</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="pt-3.5 border-t border-zinc-800/80 text-[11px] text-zinc-400 font-mono flex justify-between">
          <span>Target District: Ludhiana</span>
          <span>Nodal Agencies: 5</span>
        </div>
      </div>
    </div>
  );
}
