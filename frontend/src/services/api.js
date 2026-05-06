/**
 * Centralised API client.
 * All requests go through axios with the base URL from .env.
 * Add auth token header here when you implement auth.
 */
import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://localhost:8000",
  timeout: 30000,
});

// ── Resume ────────────────────────────────────────────────────────────────────
export const resumeApi = {
  upload: (file) => {
    const form = new FormData();
    form.append("file", file);
    return api.post("/api/v1/resumes/upload", form, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
  list: () => api.get("/api/v1/resumes/"),
  get: (id) => api.get(`/api/v1/resumes/${id}`),
  delete: (id) => api.delete(`/api/v1/resumes/${id}`),
};

// ── Jobs ──────────────────────────────────────────────────────────────────────
export const jobsApi = {
  search: (params) => api.get("/api/v1/jobs/search", { params }),
  match: (resumeId, params) =>
    api.post(`/api/v1/jobs/match/${resumeId}`, null, { params }),
  list: () => api.get("/api/v1/jobs/"),
  get: (id) => api.get(`/api/v1/jobs/${id}`),
};

// ── Applications ──────────────────────────────────────────────────────────────
export const applicationsApi = {
  create: (payload) => api.post("/api/v1/applications/", payload),
  list: () => api.get("/api/v1/applications/"),
  stats: () => api.get("/api/v1/applications/stats"),
  get: (id) => api.get(`/api/v1/applications/${id}`),
  updateStatus: (id, payload) =>
    api.patch(`/api/v1/applications/${id}/status`, payload),
  delete: (id) => api.delete(`/api/v1/applications/${id}`),
};

// ── AI ────────────────────────────────────────────────────────────────────────
export const aiApi = {
  generate: (payload) => api.post("/api/v1/ai/generate", payload),
  streamResumeUrl: (applicationId, tone = "professional") =>
    `${api.defaults.baseURL}/api/v1/ai/stream/resume/${applicationId}?tone=${tone}`,
  streamCoverLetterUrl: (applicationId, tone = "professional") =>
    `${api.defaults.baseURL}/api/v1/ai/stream/cover-letter/${applicationId}?tone=${tone}`,
};

// ── Demo ──────────────────────────────────────────────────────────────────────
export const demoApi = {
  getResume: () => api.get("/api/v1/demo/resume"),
  getJobs: () => api.get("/api/v1/demo/jobs"),
  getApplications: () => api.get("/api/v1/demo/applications"),
};

export default api;
