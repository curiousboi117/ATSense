import axios from 'axios';

// Create base instance. Using relative /api for proxy, falling back to localhost:8000
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000, // 60s timeout for heavy sentence-transformers/NLP operations
});

export const apiService = {
  getHealth: async () => {
    const response = await api.get('/health');
    return response.data;
  },

  uploadResume: async (file, jobDescription = '', jobTitle = 'Target Role') => {
    const formData = new FormData();
    formData.append('file', file);
    if (jobDescription) {
      formData.append('job_description', jobDescription);
    }
    formData.append('job_title', jobTitle);

    const response = await api.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  matchJob: async (resumeId, jobDescription, jobTitle = 'Target Role') => {
    const formData = new FormData();
    formData.append('resume_id', resumeId);
    formData.append('job_description', jobDescription);
    formData.append('job_title', jobTitle);

    const response = await api.post('/match-job', formData);
    return response.data;
  },

  getHistory: async () => {
    const response = await api.get('/history');
    return response.data;
  },

  getAnalysis: async (id) => {
    const response = await api.get(`/analysis/${id}`);
    return response.data;
  },

  deleteResume: async (id) => {
    const response = await api.delete(`/resume/${id}`);
    return response.data;
  },

  resetDatabase: async () => {
    const response = await api.post('/reset-all');
    return response.data;
  },

  getPDFReportUrl: (id) => {
    return `${API_BASE_URL}/report/${id}/pdf`;
  },

  getJSONReportUrl: (id) => {
    return `${API_BASE_URL}/report/${id}/json`;
  }
};
