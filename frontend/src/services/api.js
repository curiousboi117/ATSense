import axios from 'axios';

const API_BASE_URL =
  import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api';

const TOKEN_KEY = 'atsense_access_token';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000,
});

api.interceptors.request.use((config) => {
  const token = sessionStorage.getItem(TOKEN_KEY);

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});

export const authStorage = {
  getToken: () => sessionStorage.getItem(TOKEN_KEY),

  setToken: (token) => {
    sessionStorage.setItem(TOKEN_KEY, token);
  },

  clearToken: () => {
    sessionStorage.removeItem(TOKEN_KEY);
  },
};

export const apiService = {
  login: async (username, password) => {
    const response = await api.post('/auth/login', {
      username,
      password,
    });

    return response.data;
  },

  getHealth: async () => {
    const response = await api.get('/health');
    return response.data;
  },

  uploadResume: async (
    file,
    jobDescription = '',
    jobTitle = 'Target Role'
  ) => {
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

  matchJob: async (
    resumeId,
    jobDescription,
    jobTitle = 'Target Role'
  ) => {
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

    downloadPDFReport: async (id) => {
    const response = await api.get(`/report/${id}/pdf`, {
      responseType: 'blob',
    });

    return response.data;
  },

  downloadJSONReport: async (id) => {
    const response = await api.get(`/report/${id}/json`, {
      responseType: 'blob',
    });

    return response.data;
  },

  getPDFReportUrl: (id) => {
    return `${API_BASE_URL}/report/${id}/pdf`;
  },

  getJSONReportUrl: (id) => {
    return `${API_BASE_URL}/report/${id}/json`;
  },
};