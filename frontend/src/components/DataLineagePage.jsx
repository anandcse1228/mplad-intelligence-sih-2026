import React, { useState, useEffect } from 'react';
import { 
  Database, 
  CheckCircle2, 
  ArrowRight, 
  GitBranch,
  Table,
  FileCheck,
  Info,
  Shield,
  Upload,
  RefreshCw,
  Cpu,
  AlertTriangle,
  FileSpreadsheet,
  Layers,
  CheckCircle,
  XCircle,
  Play,
  RotateCcw,
  Clock,
  Building,
  Download,
  Trash2,
  ExternalLink,
  BookOpen
} from 'lucide-react';
import { api } from '../api/client';

export default function DataLineagePage({ onNavigateToCommandCenter, activeDataset: parentActiveDataset, onDatasetSwitched }) {
  const [activeDataset, setActiveDataset] = useState(parentActiveDataset || null);
  const [loadingActive, setLoadingActive] = useState(false);
  const [datasetLibrary, setDatasetLibrary] = useState([]);
  const [loadingLibrary, setLoadingLibrary] = useState(false);

  // File Upload State
  const [sanctFile, setSanctFile] = useState(null);
  const [recFile, setRecFile] = useState(null);
  const [compFile, setCompFile] = useState(null);
  const [datasetName, setDatasetName] = useState('');

  // Validation State
  const [validating, setValidating] = useState(false);
  const [validationResult, setValidationResult] = useState(null);
  const [validationError, setValidationError] = useState('');

  // Analysis State
  const [analyzing, setAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [analysisError, setAnalysisError] = useState('');

  // Restore Modal State
  const [showRestoreModal, setShowRestoreModal] = useState(false);
  const [restoring, setRestoring] = useState(false);

  // Load Active Dataset info and Dataset Library
  const loadData = () => {
    setLoadingActive(true);
    setLoadingLibrary(true);

    api.getActiveDataset()
      .then(res => {
        setActiveDataset(res);
        setLoadingActive(false);
        if (onDatasetSwitched) onDatasetSwitched(res);
      })
      .catch(err => {
        console.error("Failed to fetch active dataset:", err);
        setLoadingActive(false);
      });

    api.listDatasets()
      .then(res => {
        setDatasetLibrary(res.items || []);
        setLoadingLibrary(false);
      })
      .catch(err => {
        console.error("Failed to fetch dataset library:", err);
        setLoadingLibrary(false);
      });
  };

  useEffect(() => {
    loadData();
  }, []);

  // Handle Upload & Real Validation
  const handleUploadAndValidate = async () => {
    if (!sanctFile || !recFile || !compFile) {
      alert("Please select all three required CSV files (Sanctioned, Recommended, and Completed works) before validating.");
      return;
    }

    setValidating(true);
    setValidationError('');
    setValidationResult(null);
    setAnalysisResult(null);

    const formData = new FormData();
    formData.append('sanctioned_file', sanctFile);
    formData.append('recommended_file', recFile);
    formData.append('completed_file', compFile);

    try {
      await api.uploadDatasetFiles(formData);
      const valRes = await api.validateDataset();
      setValidationResult(valRes);
      setValidating(false);
    } catch (err) {
      console.error("Validation error:", err);
      setValidationError(err.message || "Failed to validate uploaded files.");
      setValidating(false);
    }
  };

  // Handle Run Real ML Analysis
  const handleRunAnalysis = async () => {
    if (!validationResult || !validationResult.valid) {
      alert("Dataset must pass validation before intelligence analysis can be executed.");
      return;
    }

    setAnalyzing(true);
    setAnalysisError('');
    setAnalysisResult(null);

    try {
      const res = await api.runIntelligenceAnalysis(datasetName);
      setAnalysisResult(res);
      setAnalyzing(false);
      loadData();
    } catch (err) {
      console.error("ML analysis error:", err);
      setAnalysisError(err.message || "ML pipeline execution failed.");
      setAnalyzing(false);
    }
  };

  // Handle Switch Active Dataset
  const handleSwitchDataset = async (datasetId) => {
    try {
      const switched = await api.switchDataset(datasetId);
      loadData();
      alert(`Switched active dataset to: '${switched.name}'. All application pages are now reflecting this dataset.`);
    } catch (err) {
      console.error("Switch dataset error:", err);
      alert(`Failed to switch dataset: ${err.message}`);
    }
  };

  // Handle Delete Dataset from Library
  const handleDeleteDataset = async (datasetId) => {
    if (!window.confirm("Are you sure you want to delete this dataset from the library?")) return;
    try {
      await api.deleteDataset(datasetId);
      loadData();
    } catch (err) {
      alert(`Failed to delete dataset: ${err.message}`);
    }
  };

  // Handle Restore Demo Dataset
  const handleRestoreDemo = async () => {
    setRestoring(true);
    try {
      const res = await api.restoreDemoDataset();
      setRestoring(false);
      setShowRestoreModal(false);
      setValidationResult(null);
      setAnalysisResult(null);
      setSanctFile(null);
      setRecFile(null);
      setCompFile(null);
      loadData();
      alert(`Demo Dataset Restored: ${res.dataset_name} (${res.total_scored_works} Sanctioned Works, ${res.ml_anomaly_candidates} ML Anomalies).`);
    } catch (err) {
      console.error("Restore demo error:", err);
      alert(`Failed to restore demo dataset: ${err.message}`);
      setRestoring(false);
    }
  };

  return (
    <div className="space-y-6 font-sans selection:bg-slate-900 selection:text-white pb-8">
      
      {/* Header Context Banner */}
      <div className="dark-surface-card rounded-2xl p-6 flex flex-col md:flex-row md:items-center justify-between gap-4 shadow-md">
        <div>
          <div className="flex items-center space-x-2 text-xs text-zinc-400 font-semibold mb-1 font-mono">
            <Database className="w-3.5 h-3.5 text-white" />
            <span>PAGE 5 • DATA LINEAGE & DATASET MANAGEMENT</span>
          </div>
          <h1 className="text-xl font-bold text-white tracking-tight">
            Data Ingestion, Multi-Dataset Library & ML Re-Analysis
          </h1>
          <p className="text-xs text-zinc-400 mt-1 max-w-3xl leading-relaxed font-sans">
            End-to-end dataset management: upload custom MPLADS CSV datasets, perform schema validation, execute the real pure Python Isolation Forest ML pipeline, manage persistent datasets in the library, and export official PDF intelligence reports.
          </p>
        </div>

        {/* Active Dataset Status Pill */}
        <div className="bg-[#1A1B1E] border border-zinc-800 p-3.5 rounded-xl text-xs shrink-0 space-y-1 font-mono">
          <div className="flex items-center space-x-2 text-white font-semibold">
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            <span>{activeDataset ? activeDataset.status : 'ACTIVE'} DATASET</span>
          </div>
          <div className="text-[11px] text-zinc-400">
            <span>{activeDataset ? activeDataset.sanctioned_count : 220} Scored Records</span> • <span className="text-emerald-400 font-semibold">100% Validated</span>
          </div>
        </div>
      </div>

      {/* SECTION 1: CURRENT ACTIVE DATASET SNAPSHOT */}
      <div className="dark-surface-card dark-surface-card-hover rounded-2xl p-6 space-y-5 shadow-md">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-zinc-800/80 pb-3 gap-3">
          <div className="flex items-center space-x-2.5">
            <Building className="w-4 h-4 text-white" />
            <h3 className="text-xs font-bold text-white uppercase tracking-wide">
              Current Active Dataset Snapshot
            </h3>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            {activeDataset && (
              <a
                href={api.getDownloadReportUrl(activeDataset.dataset_id)}
                target="_blank"
                rel="noreferrer"
                className="px-3.5 py-1.5 rounded-xl bg-emerald-950/80 hover:bg-emerald-900 text-emerald-300 border border-emerald-800 text-xs font-mono font-semibold flex items-center space-x-1.5 transition-colors button-press-effect"
              >
                <Download className="w-3.5 h-3.5" />
                <span>Download Report (PDF)</span>
              </a>
            )}

            <button
              onClick={() => setShowRestoreModal(true)}
              className="px-3.5 py-1.5 rounded-xl bg-[#1A1B1E] hover:bg-zinc-800 text-zinc-200 border border-zinc-700/80 text-xs font-mono font-semibold flex items-center space-x-1.5 transition-colors button-press-effect"
            >
              <RotateCcw className="w-3.5 h-3.5 text-zinc-400" />
              <span>Restore Demo Dataset</span>
            </button>
            
            <button
              onClick={loadData}
              className="p-1.5 rounded-xl bg-[#1A1B1E] hover:bg-zinc-800 text-zinc-300 border border-zinc-700/80 transition-colors"
              title="Refresh Metadata"
            >
              <RefreshCw className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>

        {loadingActive ? (
          <div className="py-6 text-center text-xs font-mono text-zinc-500">Loading active dataset metadata...</div>
        ) : activeDataset ? (
          <div className="space-y-4 text-xs font-sans">
            <div className="flex flex-col md:flex-row md:items-center justify-between bg-[#1A1B1E] p-4 rounded-xl border border-zinc-800 gap-3">
              <div className="space-y-1">
                <span className="text-[10px] text-zinc-400 uppercase font-mono block font-semibold">ACTIVE DATASET IDENTIFIER:</span>
                <span className="text-base font-bold text-white font-sans">{activeDataset.name}</span>
                <span className="text-[11px] text-zinc-400 font-mono block">
                  Jurisdiction: <strong className="text-white">{activeDataset.state}</strong> • <strong className="text-white">{activeDataset.district} District</strong> ({activeDataset.constituency})
                </span>
              </div>

              <div className="flex items-center space-x-2 font-mono">
                <span className="px-3 py-1 rounded-full bg-emerald-950/80 text-emerald-300 border border-emerald-800 font-bold text-xs">
                  ✓ {activeDataset.validation_status}
                </span>
                <span className="px-3 py-1 rounded-full bg-indigo-950/80 text-indigo-300 border border-indigo-800 font-bold text-xs">
                  ✓ ML {activeDataset.analysis_status}
                </span>
              </div>
            </div>

            {/* Metrics Breakdown Grid */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
              <div className="bg-[#1A1B1E] p-3.5 rounded-xl border border-zinc-800 space-y-1">
                <span className="text-zinc-400 text-[10px] uppercase font-semibold font-mono">SANCTIONED WORKS</span>
                <div className="text-lg font-bold text-white font-sans">{activeDataset.sanctioned_count}</div>
                <span className="text-[10px] text-zinc-500 font-mono">Primary Works Feed</span>
              </div>

              <div className="bg-[#1A1B1E] p-3.5 rounded-xl border border-zinc-800 space-y-1">
                <span className="text-zinc-400 text-[10px] uppercase font-semibold font-mono">RECOMMENDED WORKS</span>
                <div className="text-lg font-bold text-white font-sans">{activeDataset.recommended_count}</div>
                <span className="text-[10px] text-zinc-500 font-mono">Recommendation Dates</span>
              </div>

              <div className="bg-[#1A1B1E] p-3.5 rounded-xl border border-zinc-800 space-y-1">
                <span className="text-zinc-400 text-[10px] uppercase font-semibold font-mono">COMPLETED WORKS</span>
                <div className="text-lg font-bold text-white font-sans">{activeDataset.completed_count}</div>
                <span className="text-[10px] text-zinc-500 font-mono">Disbursement Feeds</span>
              </div>

              <div className="bg-[#1A1B1E] p-3.5 rounded-xl border border-zinc-800 space-y-1">
                <span className="text-zinc-400 text-[10px] uppercase font-semibold font-mono">ML ANOMALIES (S_ml ≥ 70)</span>
                <div className="text-lg font-bold text-indigo-400 font-sans">{activeDataset.ml_anomaly_count}</div>
                <span className="text-[10px] text-zinc-500 font-mono">Isolation Forest Upper 30%</span>
              </div>
            </div>

            {/* Severity Distribution Strip */}
            <div className="flex flex-wrap items-center justify-between bg-[#1A1B1E] p-3.5 rounded-xl border border-zinc-800 text-[11px] font-mono">
              <span className="text-zinc-400 font-semibold">Active Risk Distribution:</span>
              <span className="text-rose-400 font-bold">Critical: {activeDataset.critical_risk_count}</span>
              <span className="text-amber-400 font-bold">High Risk: {activeDataset.high_risk_count}</span>
              <span className="text-sky-400 font-bold">Medium Risk: {activeDataset.medium_risk_count}</span>
              <span className="text-zinc-300 font-bold">Normal: {activeDataset.normal_risk_count}</span>
            </div>
          </div>
        ) : null}
      </div>

      {/* SECTION 2: DATASET LIBRARY / STORED DATASETS */}
      <div className="dark-surface-card dark-surface-card-hover rounded-2xl p-6 space-y-4 shadow-md">
        <div className="flex items-center justify-between border-b border-zinc-800/80 pb-3">
          <div className="flex items-center space-x-2.5">
            <BookOpen className="w-4 h-4 text-indigo-400" />
            <h3 className="text-xs font-bold text-white uppercase tracking-wide font-sans">
              Persistent Dataset Library ({datasetLibrary.length} Stored Datasets)
            </h3>
          </div>
          <span className="text-[10px] font-mono text-zinc-400 bg-[#1A1B1E] px-2.5 py-0.5 rounded-full border border-zinc-800">
            Multi-Dataset Isolated Storage
          </span>
        </div>

        <p className="text-xs text-zinc-400 leading-relaxed font-sans">
          All analyzed datasets are preserved independently in SQLite. Switching the active dataset updates the entire platform (Command Center, Risk Queue, District Analytics, Investigation Workspace) without deleting previously analyzed state data.
        </p>

        <div className="overflow-x-auto border border-zinc-800/80 rounded-xl">
          <table className="w-full text-left text-xs font-sans">
            <thead className="bg-[#17181B] text-zinc-400 border-b border-zinc-800 font-mono text-[10px] uppercase">
              <tr>
                <th className="px-4 py-2.5">Status</th>
                <th className="px-4 py-2.5">Dataset Name</th>
                <th className="px-4 py-2.5">Jurisdiction</th>
                <th className="px-4 py-2.5">Sanctioned Works</th>
                <th className="px-4 py-2.5">ML Anomalies</th>
                <th className="px-4 py-2.5">High / Critical</th>
                <th className="px-4 py-2.5 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-800 text-zinc-300 font-mono text-[11px]">
              {datasetLibrary.map((d) => (
                <tr key={d.dataset_id} className={`hover:bg-[#17181B]/50 transition-colors ${d.is_active ? 'bg-indigo-950/20' : ''}`}>
                  <td className="px-4 py-3">
                    {d.is_active ? (
                      <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-emerald-950/80 text-emerald-300 border border-emerald-800">
                        ● ACTIVE
                      </span>
                    ) : (
                      <span className="px-2.5 py-0.5 rounded-full text-[10px] font-medium bg-[#1A1B1E] text-zinc-400 border border-zinc-800">
                        STORED
                      </span>
                    )}
                  </td>
                  <td className="px-4 py-3 font-semibold text-white font-sans">{d.name}</td>
                  <td className="px-4 py-3 text-zinc-300">{d.district}, {d.state}</td>
                  <td className="px-4 py-3 font-bold text-white">{d.sanctioned_count}</td>
                  <td className="px-4 py-3 text-indigo-400 font-bold">{d.ml_anomaly_count}</td>
                  <td className="px-4 py-3 text-amber-400 font-bold">{d.high_risk_count + d.critical_risk_count}</td>
                  <td className="px-4 py-3 text-right">
                    <div className="flex items-center justify-end space-x-2">
                      {!d.is_active && (
                        <button
                          onClick={() => handleSwitchDataset(d.dataset_id)}
                          className="px-3 py-1 bg-white hover:bg-zinc-200 text-black rounded-lg text-[11px] font-bold transition-all button-press-effect"
                        >
                          Make Active
                        </button>
                      )}

                      <a
                        href={api.getDownloadReportUrl(d.dataset_id)}
                        target="_blank"
                        rel="noreferrer"
                        className="p-1.5 bg-[#1A1B1E] hover:bg-zinc-800 text-zinc-300 rounded-lg border border-zinc-700 transition-colors"
                        title="Download PDF Report"
                      >
                        <Download className="w-3.5 h-3.5" />
                      </a>

                      {!d.is_active && d.dataset_id !== 'dataset_ludhiana_demo' && (
                        <button
                          onClick={() => handleDeleteDataset(d.dataset_id)}
                          className="p-1.5 bg-[#1A1B1E] hover:bg-rose-950/80 text-rose-400 rounded-lg border border-zinc-800 hover:border-rose-800 transition-colors"
                          title="Delete Dataset"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* SECTION 3: UPLOAD NEW DATASET WORKSPACE */}
      <div className="dark-surface-card dark-surface-card-hover rounded-2xl p-6 space-y-5 shadow-md">
        <div className="flex items-center justify-between border-b border-zinc-800/80 pb-3">
          <div className="flex items-center space-x-2.5">
            <Upload className="w-4 h-4 text-white" />
            <h3 className="text-xs font-bold text-white uppercase tracking-wide">
              Upload & Staging Workspace for New MPLADS Datasets
            </h3>
          </div>
          <span className="text-[10px] font-mono text-zinc-400 bg-[#1A1B1E] px-2.5 py-0.5 rounded-full border border-zinc-800">
            3 CSV Files Required
          </span>
        </div>

        <div className="space-y-4 text-xs font-sans">
          <div className="space-y-1.5">
            <label className="text-zinc-400 font-mono uppercase text-[10px] font-semibold block">
              OPTIONAL DATASET NAME LABEL:
            </label>
            <input
              type="text"
              value={datasetName}
              onChange={(e) => setDatasetName(e.target.value)}
              placeholder="e.g. Uttar Pradesh MPLADS — Varanasi District (Auto-detected if blank)"
              className="w-full bg-[#1A1B1E] border border-zinc-800 rounded-xl px-3.5 py-2 text-xs text-white placeholder-zinc-500 focus:outline-none focus:border-zinc-600 font-sans"
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-2">
            
            {/* 1. Sanctioned Works CSV */}
            <div className="bg-[#1A1B1E] border border-zinc-800/80 p-4 rounded-xl space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-[11px] font-bold text-white font-mono uppercase">1. SANCTIONED WORKS</span>
                {sanctFile ? (
                  <span className="text-[9px] font-mono px-2 py-0.5 bg-emerald-950/80 text-emerald-300 rounded-full border border-emerald-800 font-bold">READY</span>
                ) : (
                  <span className="text-[9px] font-mono px-2 py-0.5 bg-[#141518] text-zinc-400 rounded-full border border-zinc-700">REQUIRED</span>
                )}
              </div>
              <p className="text-[11px] text-zinc-400 leading-normal">
                Canonical baseline containing Work IDs, sanction amounts, and sanction dates.
              </p>
              <input
                type="file"
                accept=".csv"
                id="sanct-upload"
                className="hidden"
                onChange={(e) => setSanctFile(e.target.files[0] || null)}
              />
              <label
                htmlFor="sanct-upload"
                className="w-full py-2 px-3 rounded-xl bg-[#141518] hover:bg-zinc-800 text-zinc-200 border border-zinc-700/80 text-xs font-mono text-center block cursor-pointer transition-colors button-press-effect truncate"
              >
                {sanctFile ? `✓ ${sanctFile.name} (${(sanctFile.size / 1024).toFixed(1)} KB)` : 'Choose Sanctioned CSV...'}
              </label>
            </div>

            {/* 2. Recommended Works CSV */}
            <div className="bg-[#1A1B1E] border border-zinc-800/80 p-4 rounded-xl space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-[11px] font-bold text-white font-mono uppercase">2. RECOMMENDED WORKS</span>
                {recFile ? (
                  <span className="text-[9px] font-mono px-2 py-0.5 bg-emerald-950/80 text-emerald-300 rounded-full border border-emerald-800 font-bold">READY</span>
                ) : (
                  <span className="text-[9px] font-mono px-2 py-0.5 bg-[#141518] text-zinc-400 rounded-full border border-zinc-700">REQUIRED</span>
                )}
              </div>
              <p className="text-[11px] text-zinc-400 leading-normal">
                MP recommendations feed for measuring administrative sanction delays.
              </p>
              <input
                type="file"
                accept=".csv"
                id="rec-upload"
                className="hidden"
                onChange={(e) => setRecFile(e.target.files[0] || null)}
              />
              <label
                htmlFor="rec-upload"
                className="w-full py-2 px-3 rounded-xl bg-[#141518] hover:bg-zinc-800 text-zinc-200 border border-zinc-700/80 text-xs font-mono text-center block cursor-pointer transition-colors button-press-effect truncate"
              >
                {recFile ? `✓ ${recFile.name} (${(recFile.size / 1024).toFixed(1)} KB)` : 'Choose Recommended CSV...'}
              </label>
            </div>

            {/* 3. Completed Works CSV */}
            <div className="bg-[#1A1B1E] border border-zinc-800/80 p-4 rounded-xl space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-[11px] font-bold text-white font-mono uppercase">3. COMPLETED WORKS</span>
                {compFile ? (
                  <span className="text-[9px] font-mono px-2 py-0.5 bg-emerald-950/80 text-emerald-300 rounded-full border border-emerald-800 font-bold">READY</span>
                ) : (
                  <span className="text-[9px] font-mono px-2 py-0.5 bg-[#141518] text-zinc-400 rounded-full border border-zinc-700">REQUIRED</span>
                )}
              </div>
              <p className="text-[11px] text-zinc-400 leading-normal">
                Completed projects feed for fund disbursement variance cross-feed matching.
              </p>
              <input
                type="file"
                accept=".csv"
                id="comp-upload"
                className="hidden"
                onChange={(e) => setCompFile(e.target.files[0] || null)}
              />
              <label
                htmlFor="comp-upload"
                className="w-full py-2 px-3 rounded-xl bg-[#141518] hover:bg-zinc-800 text-zinc-200 border border-zinc-700/80 text-xs font-mono text-center block cursor-pointer transition-colors button-press-effect truncate"
              >
                {compFile ? `✓ ${compFile.name} (${(compFile.size / 1024).toFixed(1)} KB)` : 'Choose Completed CSV...'}
              </label>
            </div>

          </div>

          {/* Validation Action Button */}
          <div className="flex items-center justify-between pt-2">
            <span className="text-[11px] text-zinc-400">
              {sanctFile && recFile && compFile
                ? 'All 3 files selected. Ready to perform real schema and record validation.'
                : 'Please choose 3 valid CSV files to begin validation.'}
            </span>

            <button
              onClick={handleUploadAndValidate}
              disabled={validating || !sanctFile || !recFile || !compFile}
              className={`px-5 py-2.5 rounded-xl text-xs font-bold font-sans flex items-center space-x-2 transition-all button-press-effect ${
                validating || !sanctFile || !recFile || !compFile
                  ? 'bg-zinc-800 text-zinc-500 cursor-not-allowed border border-zinc-700/50'
                  : 'bg-white text-black hover:bg-zinc-200 shadow-md border border-white'
              }`}
            >
              {validating ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <FileCheck className="w-3.5 h-3.5" />}
              <span>{validating ? 'Validating Staged CSVs...' : 'Validate Uploaded Files'}</span>
            </button>
          </div>

          {validationError && (
            <div className="p-4 bg-rose-950/80 border border-rose-800 rounded-xl text-xs text-rose-300 flex items-start space-x-2">
              <XCircle className="w-4 h-4 shrink-0 mt-0.5 text-rose-400" />
              <span>{validationError}</span>
            </div>
          )}
        </div>
      </div>

      {/* SECTION 4: REAL VALIDATION RESULTS CHECKLIST */}
      {validationResult && (
        <div className="dark-surface-card dark-surface-card-hover rounded-2xl p-6 space-y-4 shadow-md">
          <div className="flex items-center justify-between border-b border-zinc-800/80 pb-3">
            <div className="flex items-center space-x-2.5">
              {validationResult.valid ? (
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              ) : (
                <XCircle className="w-4 h-4 text-rose-400" />
              )}
              <h3 className="text-xs font-bold text-white uppercase tracking-wide">
                Dataset Validation Report
              </h3>
            </div>
            
            <span className={`text-[10px] font-mono px-3 py-0.5 rounded-full font-bold border ${
              validationResult.valid
                ? 'bg-emerald-950/80 text-emerald-300 border-emerald-800'
                : 'bg-rose-950/80 text-rose-300 border-rose-800'
            }`}>
              {validationResult.valid ? 'STATUS: READY FOR ANALYSIS' : 'STATUS: VALIDATION FAILED'}
            </span>
          </div>

          <div className="space-y-3 text-xs">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 font-mono">
              <div className="bg-[#1A1B1E] p-3 rounded-xl border border-zinc-800">
                <span className="text-zinc-400 text-[10px] block">PARSED SANCTIONED</span>
                <span className="text-base font-bold text-white">{validationResult.sanctioned_count} Records</span>
              </div>
              <div className="bg-[#1A1B1E] p-3 rounded-xl border border-zinc-800">
                <span className="text-zinc-400 text-[10px] block">PARSED RECOMMENDED</span>
                <span className="text-base font-bold text-white">{validationResult.recommended_count} Records</span>
              </div>
              <div className="bg-[#1A1B1E] p-3 rounded-xl border border-zinc-800">
                <span className="text-zinc-400 text-[10px] block">PARSED COMPLETED</span>
                <span className="text-base font-bold text-white">{validationResult.completed_count} Records</span>
              </div>
            </div>

            {/* Checklist items */}
            <div className="space-y-2 pt-2">
              <h4 className="text-[11px] font-bold text-zinc-400 uppercase font-mono">Validation Checklist (12 Rules Evaluated):</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                {validationResult.checks.map((c, idx) => (
                  <div key={idx} className="bg-[#1A1B1E] p-3 rounded-xl border border-zinc-800 flex items-center justify-between text-xs">
                    <span className="text-zinc-200 font-medium">{c.name}</span>
                    <span className={`text-[10px] font-mono px-2 py-0.5 rounded-full font-bold border ${
                      c.status === 'PASS'
                        ? 'bg-emerald-950/80 text-emerald-300 border-emerald-800'
                        : 'bg-rose-950/80 text-rose-300 border-rose-800'
                    }`}>
                      {c.status}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {validationResult.errors && validationResult.errors.length > 0 && (
              <div className="p-4 bg-rose-950/80 border border-rose-800 rounded-xl space-y-1 text-xs text-rose-300">
                <strong className="block text-rose-200 uppercase font-mono">Validation Errors Detected:</strong>
                <ul className="list-disc list-inside space-y-0.5">
                  {validationResult.errors.map((err, idx) => (
                    <li key={idx}>{err}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Action Bar: Run ML Analysis */}
            {validationResult.valid && (
              <div className="p-4 bg-[#1A1B1E] border border-zinc-800 rounded-xl flex flex-col sm:flex-row sm:items-center justify-between gap-3 mt-4">
                <div>
                  <h4 className="font-bold text-white text-xs">Ready to Run Intelligence Analysis</h4>
                  <p className="text-[11px] text-zinc-400">
                    Executes 6-feature engineering, Isolation Forest anomaly scoring (S_ml), and hybrid risk calculation (S_risk = 0.60 S_ml + 0.40 S_rule).
                  </p>
                </div>

                <button
                  onClick={handleRunAnalysis}
                  disabled={analyzing}
                  className={`px-5 py-2.5 rounded-xl text-xs font-bold font-sans flex items-center space-x-2 transition-all button-press-effect shrink-0 ${
                    analyzing
                      ? 'bg-indigo-900 text-indigo-300 cursor-not-allowed border border-indigo-700'
                      : 'bg-indigo-600 hover:bg-indigo-500 text-white shadow-md border border-indigo-500'
                  }`}
                >
                  {analyzing ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Play className="w-3.5 h-3.5" />}
                  <span>{analyzing ? 'Executing ML Pipeline...' : 'Run Intelligence Analysis →'}</span>
                </button>
              </div>
            )}

            {analysisError && (
              <div className="p-4 bg-rose-950/80 border border-rose-800 rounded-xl text-xs text-rose-300 flex items-start space-x-2">
                <XCircle className="w-4 h-4 shrink-0 mt-0.5 text-rose-400" />
                <span>{analysisError}</span>
              </div>
            )}
          </div>
        </div>
      )}

      {/* SECTION 5: ANALYSIS COMPLETE RESULTS BANNER */}
      {analysisResult && (
        <div className="dark-surface-card rounded-2xl p-6 space-y-4 border border-indigo-800/80 bg-indigo-950/20 shadow-lg">
          <div className="flex items-center justify-between border-b border-indigo-800/60 pb-3">
            <div className="flex items-center space-x-2.5">
              <Cpu className="w-5 h-5 text-indigo-400" />
              <h3 className="text-xs font-bold text-white uppercase tracking-wide font-sans">
                ML Intelligence Analysis Complete & Activated
              </h3>
            </div>
            <span className="text-[10px] font-mono px-3 py-0.5 rounded-full bg-emerald-950/80 text-emerald-300 border border-emerald-800 font-bold">
              ✓ DATASET ACTIVATED
            </span>
          </div>

          <div className="space-y-4 text-xs font-sans">
            <p className="text-zinc-200 leading-relaxed">
              Successfully trained Isolation Forest kernel (100 estimators), evaluated statutory compliance rule signals, and refreshed SQLite database tables for dataset <strong className="text-white">'{analysisResult.dataset_name}'</strong>.
            </p>

            <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 text-xs font-mono">
              <div className="bg-[#141518] p-3 rounded-xl border border-zinc-800">
                <span className="text-zinc-400 text-[10px] block">TOTAL WORKS</span>
                <span className="text-lg font-bold text-white">{analysisResult.total_scored_works}</span>
              </div>
              <div className="bg-[#141518] p-3 rounded-xl border border-zinc-800">
                <span className="text-zinc-400 text-[10px] block">ML ANOMALIES</span>
                <span className="text-lg font-bold text-indigo-400">{analysisResult.ml_anomaly_candidates}</span>
              </div>
              <div className="bg-[#141518] p-3 rounded-xl border border-zinc-800">
                <span className="text-zinc-400 text-[10px] block">CRITICAL RISK</span>
                <span className="text-lg font-bold text-rose-400">{analysisResult.critical_risk_count}</span>
              </div>
              <div className="bg-[#141518] p-3 rounded-xl border border-zinc-800">
                <span className="text-zinc-400 text-[10px] block">HIGH RISK</span>
                <span className="text-lg font-bold text-amber-400">{analysisResult.high_risk_count}</span>
              </div>
              <div className="bg-[#141518] p-3 rounded-xl border border-zinc-800">
                <span className="text-zinc-400 text-[10px] block">MEDIUM RISK</span>
                <span className="text-lg font-bold text-sky-400">{analysisResult.medium_risk_count}</span>
              </div>
            </div>

            <div className="flex flex-wrap items-center justify-between pt-2 gap-3">
              <span className="text-zinc-400 font-mono text-[11px]">
                Active dataset updated in SQLite. All platform dashboards now display this dataset.
              </span>

              <div className="flex items-center space-x-3">
                <a
                  href={api.getDownloadReportUrl(analysisResult.dataset_id)}
                  target="_blank"
                  rel="noreferrer"
                  className="px-4 py-2 bg-[#1A1B1E] hover:bg-zinc-800 text-emerald-300 border border-emerald-800 rounded-xl text-xs font-bold font-sans flex items-center space-x-1.5 transition-colors button-press-effect"
                >
                  <Download className="w-3.5 h-3.5" />
                  <span>Download Intelligence Report (PDF)</span>
                </a>

                {onNavigateToCommandCenter && (
                  <button
                    onClick={onNavigateToCommandCenter}
                    className="px-4 py-2 bg-white hover:bg-zinc-200 text-black rounded-xl text-xs font-bold font-sans flex items-center space-x-1.5 transition-colors button-press-effect shadow-md"
                  >
                    <span>View Command Center (Page 1) →</span>
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* CONFIRMATION MODAL FOR RESTORE DEMO DATASET */}
      {showRestoreModal && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-xs flex items-center justify-center p-4 overflow-y-auto">
          <div className="bg-[#121315] border border-zinc-800 rounded-2xl max-w-md w-full p-6 space-y-4 shadow-2xl font-sans text-white max-h-[90vh] overflow-y-auto my-auto">
            <div className="flex items-center space-x-2.5 text-amber-400 border-b border-zinc-800 pb-3">
              <RotateCcw className="w-5 h-5" />
              <h3 className="text-sm font-bold uppercase tracking-wide">Restore Demo Benchmark Dataset?</h3>
            </div>

            <p className="text-xs text-zinc-300 leading-relaxed">
              This will re-activate the protected <strong>Punjab MPLADS — Ludhiana District</strong> benchmark dataset (220 Sanctioned Works, 7 ML Anomalies). All stored datasets in the library remain preserved.
            </p>

            <div className="flex items-center justify-end space-x-3 pt-3 border-t border-zinc-800">
              <button
                onClick={() => setShowRestoreModal(false)}
                disabled={restoring}
                className="px-4 py-2 bg-[#1A1B1E] hover:bg-zinc-800 text-zinc-300 rounded-xl text-xs font-semibold border border-zinc-700"
              >
                Cancel
              </button>

              <button
                onClick={handleRestoreDemo}
                disabled={restoring}
                className="px-4 py-2 bg-white hover:bg-zinc-200 text-black rounded-xl text-xs font-bold flex items-center space-x-1.5 shadow-md button-press-effect"
              >
                {restoring ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <RotateCcw className="w-3.5 h-3.5" />}
                <span>{restoring ? 'Restoring Demo...' : 'Confirm Restore'}</span>
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}
