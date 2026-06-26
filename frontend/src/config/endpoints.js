// API base configuration and endpoint urls mapping
const getApiBaseUrl = () => {
  // If we are in dev mode, we can point to localhost:8000 directly. 
  // We will allow Vite proxy or absolute URLs.
  // Using absolute URL ensures simple setup when running dev servers independently.
  return import.meta.env.VITE_API_URL || 'http://localhost:8000';
};

export const API_BASE = getApiBaseUrl();

export const ENDPOINTS = {
  health: `${API_BASE}/health`,
  metrics: `${API_BASE}/metrics`,
  uploadResume: `${API_BASE}/upload-resume`,
  candidateStatus: (candidateId) => `${API_BASE}/candidate/${candidateId}`,
  candidateMatches: (candidateId) => `${API_BASE}/candidate/${candidateId}/matches`,
  uploadJobs: `${API_BASE}/jobs/upload`,
  jobsEmbeddingStatus: `${API_BASE}/jobs/embedding-status`,
  deleteJobs: `${API_BASE}/jobs`,
};
