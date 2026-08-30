// Centralized REST API Service Client connecting React Pages to FastAPI Backend

// Production Backend URL
const API_BASE_URL = "https://mplad-intelligence-sih-2026.onrender.com/api";

async function request(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;

  const config = {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  };

  // If body is FormData, delete Content-Type
  // so browser automatically sets multipart/form-data boundary
  if (options.body instanceof FormData && config.headers) {
    delete config.headers["Content-Type"];
  }

  try {
    const response = await fetch(url, config);

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));

      throw new Error(
        errorData.detail || `HTTP Error ${response.status}`
      );
    }

    return await response.json();

  } catch (err) {
    console.error(`API Fetch Error [${endpoint}]:`, err);
    throw err;
  }
}

export const api = {

  // ============================================
  // HEALTH CHECK
  // ============================================

  getHealth: () => request("/health"),


  // ============================================
  // OVERVIEW KPIs
  // ============================================

  getOverviewKpis: () => request("/overview/kpis"),


  // ============================================
  // RISK QUEUE
  // ============================================

  getRiskQueue: ({
    page = 1,
    page_size = 50,
    category = "ALL",
    severity = "ALL",
    search = "",
  } = {}) => {

    const params = new URLSearchParams({
      page: String(page),
      page_size: String(page_size),
    });

    if (category && category !== "ALL") {
      params.append("category", category);
    }

    if (severity && severity !== "ALL") {
      params.append("severity", severity);
    }

    if (search && search.trim()) {
      params.append("search", search.trim());
    }

    return request(
      `/projects/risk-queue?${params.toString()}`
    );
  },


  // ============================================
  // PROJECT INTELLIGENCE
  // ============================================

  getProjectIntelligence: (workId) => {
    const encodedId = encodeURIComponent(workId);

    return request(
      `/projects/${encodedId}/intelligence`
    );
  },


  // ============================================
  // INVESTIGATION CASE
  // ============================================

  getInvestigationCase: (workId) => {
    const encodedId = encodeURIComponent(workId);

    return request(
      `/projects/${encodedId}/investigation`
    );
  },


  // ============================================
  // INVESTIGATION ACTION
  // ============================================

  postInvestigationAction: (
    workId,
    action,
    details = "",
    actor = "State Nodal Officer"
  ) => {

    const encodedId = encodeURIComponent(workId);

    return request(
      `/projects/${encodedId}/investigation-action`,
      {
        method: "POST",
        body: JSON.stringify({
          action,
          details,
          actor,
        }),
      }
    );
  },


  // ============================================
  // INVESTIGATION NOTES
  // ============================================

  getInvestigationNotes: (workId) => {
    const encodedId = encodeURIComponent(workId);

    return request(
      `/projects/${encodedId}/notes`
    );
  },


  postInvestigationNote: (
    workId,
    noteText,
    officerName = "State Nodal Officer"
  ) => {

    const encodedId = encodeURIComponent(workId);

    return request(
      `/projects/${encodedId}/notes`,
      {
        method: "POST",
        body: JSON.stringify({
          note_text: noteText,
          officer_name: officerName,
        }),
      }
    );
  },


  // ============================================
  // AUDIT LOGS
  // ============================================

  getAuditLogs: ({
    page = 1,
    page_size = 25,
    work_id = "",
    action_type = "",
  } = {}) => {

    const params = new URLSearchParams({
      page: String(page),
      page_size: String(page_size),
    });

    if (work_id) {
      params.append("work_id", work_id);
    }

    if (action_type) {
      params.append("action_type", action_type);
    }

    return request(
      `/audit-logs?${params.toString()}`
    );
  },


  clearAuditLogs: () => {
    return request("/audit-logs", {
      method: "DELETE",
    });
  },


  // ============================================
  // DATASET MANAGEMENT & MULTI-DATASET LIBRARY
  // ============================================

  // Get Active Dataset Metadata & Counts
  getActiveDataset: () => request("/datasets/active"),


  // List All Stored Datasets
  listDatasets: () => request("/datasets"),


  // Switch Active Dataset
  switchDataset: (datasetId) => {
    return request(
      `/datasets/${encodeURIComponent(datasetId)}/activate`,
      {
        method: "POST",
      }
    );
  },


  // Delete Stored Dataset
  deleteDataset: (datasetId) => {
    return request(
      `/datasets/${encodeURIComponent(datasetId)}`,
      {
        method: "DELETE",
      }
    );
  },


  // Upload 3 CSV Files to Staging
  uploadDatasetFiles: (formData) => {
    return request("/datasets/upload", {
      method: "POST",
      body: formData,
    });
  },


  // Validate Staged CSV Files
  validateDataset: () => {
    return request("/datasets/validate", {
      method: "POST",
    });
  },


  // Run Real ML Intelligence Analysis Pipeline
  runIntelligenceAnalysis: (datasetName = "") => {
    return request("/datasets/analyze", {
      method: "POST",
      body: JSON.stringify({
        dataset_name: datasetName,
      }),
    });
  },


  // Restore Demo Dataset
  restoreDemoDataset: () => {
    return request("/datasets/restore-demo", {
      method: "POST",
    });
  },


  // ============================================
  // DOWNLOAD PDF REPORT
  // ============================================

  getDownloadReportUrl: (datasetId) => {
    return `${API_BASE_URL}/datasets/${encodeURIComponent(
      datasetId
    )}/report-pdf`;
  },
};