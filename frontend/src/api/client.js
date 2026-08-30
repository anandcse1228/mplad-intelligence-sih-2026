// Centralized REST API Service Client connecting React Pages to FastAPI Backend (http://127.0.0.1:8000)

const API_BASE_URL = "http://127.0.0.1:8000/api";

async function request(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  const config = {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  };

  // If body is FormData, delete Content-Type to let browser set boundary automatically
  if (options.body instanceof FormData && config.headers) {
    delete config.headers["Content-Type"];
  }

  try {
    const response = await fetch(url, config);
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP Error ${response.status}`);
    }
    return await response.json();
  } catch (err) {
    console.error(`API Fetch Error [${endpoint}]:`, err);
    throw err;
  }
}

export const api = {
  // Health Check
  getHealth: () => request('/health'),

  // Overview KPIs (Page 1, 3, 5)
  getOverviewKpis: () => request('/overview/kpis'),

  // Risk Queue Paginated (Page 1 preview, Page 2 full queue, Page 3 analytics)
  getRiskQueue: ({ page = 1, page_size = 50, category = 'ALL', severity = 'ALL', search = '' } = {}) => {
    const params = new URLSearchParams({
      page: String(page),
      page_size: String(page_size),
    });
    if (category && category !== 'ALL') params.append('category', category);
    if (severity && severity !== 'ALL') params.append('severity', severity);
    if (search && search.trim()) params.append('search', search.trim());

    return request(`/projects/risk-queue?${params.toString()}`);
  },

  // Project Intelligence Record (Page 4)
  getProjectIntelligence: (workId) => {
    const encodedId = encodeURIComponent(workId);
    return request(`/projects/${encodedId}/intelligence`);
  },

  // Investigation Case Status (Page 4)
  getInvestigationCase: (workId) => {
    const encodedId = encodeURIComponent(workId);
    return request(`/projects/${encodedId}/investigation`);
  },

  // Investigation Status Action (Page 4)
  postInvestigationAction: (workId, action, details = '', actor = 'State Nodal Officer') => {
    const encodedId = encodeURIComponent(workId);
    return request(`/projects/${encodedId}/investigation-action`, {
      method: 'POST',
      body: JSON.stringify({ action, details, actor }),
    });
  },

  // Get Investigation Notes (Page 4)
  getInvestigationNotes: (workId) => {
    const encodedId = encodeURIComponent(workId);
    return request(`/projects/${encodedId}/notes`);
  },

  // Post Investigation Note (Page 4)
  postInvestigationNote: (workId, noteText, officerName = 'State Nodal Officer') => {
    const encodedId = encodeURIComponent(workId);
    return request(`/projects/${encodedId}/notes`, {
      method: 'POST',
      body: JSON.stringify({ note_text: noteText, officer_name: officerName }),
    });
  },

  // Get Audit Logs (Page 6)
  getAuditLogs: ({ page = 1, page_size = 25, work_id = '', action_type = '' } = {}) => {
    const params = new URLSearchParams({
      page: String(page),
      page_size: String(page_size),
    });
    if (work_id) params.append('work_id', work_id);
    if (action_type) params.append('action_type', action_type);

    return request(`/audit-logs?${params.toString()}`);
  },

  // Clear Audit Logs (Page 6)
  clearAuditLogs: () => {
    return request('/audit-logs', { method: 'DELETE' });
  },

  // ----------------------------------------------------
  // DATASET MANAGEMENT & MULTI-DATASET LIBRARY API
  // ----------------------------------------------------

  // Get Active Dataset Metadata & Counts
  getActiveDataset: () => request('/datasets/active'),

  // List All Stored Datasets in Library
  listDatasets: () => request('/datasets'),

  // Switch Active Dataset to Target ID
  switchDataset: (datasetId) => {
    return request(`/datasets/${encodeURIComponent(datasetId)}/activate`, {
      method: 'POST',
    });
  },

  // Delete Stored Dataset from Library
  deleteDataset: (datasetId) => {
    return request(`/datasets/${encodeURIComponent(datasetId)}`, {
      method: 'DELETE',
    });
  },

  // Upload 3 CSV Files to Staging
  uploadDatasetFiles: (formData) => {
    return request('/datasets/upload', {
      method: 'POST',
      body: formData,
    });
  },

  // Validate Staged CSV Files
  validateDataset: () => {
    return request('/datasets/validate', {
      method: 'POST',
    });
  },

  // Run Real ML Intelligence Analysis Pipeline
  runIntelligenceAnalysis: (datasetName = '') => {
    return request('/datasets/analyze', {
      method: 'POST',
      body: JSON.stringify({ dataset_name: datasetName }),
    });
  },

  // Restore / Activate Pristine Benchmark Demo Dataset
  restoreDemoDataset: () => {
    return request('/datasets/restore-demo', {
      method: 'POST',
    });
  },

  // Download PDF Report URL
  getDownloadReportUrl: (datasetId) => {
    return `${API_BASE_URL}/datasets/${encodeURIComponent(datasetId)}/report-pdf`;
  },
};
