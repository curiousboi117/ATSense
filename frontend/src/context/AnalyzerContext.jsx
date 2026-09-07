import React, { createContext, useState, useContext, useEffect } from 'react';
import { apiService } from '../services/api';

const AnalyzerContext = createContext();

export const AnalyzerProvider = ({ children }) => {
  const [currentAnalysis, setCurrentAnalysis] = useState(null);
  const [history, setHistory] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [systemHealth, setSystemHealth] = useState(null);

  useEffect(() => {
    checkHealth();
    loadHistoryAction();
  }, []);

  const checkHealth = async () => {
    try {
      const health = await apiService.getHealth();
      setSystemHealth(health);
    } catch (err) {
      console.error("Health check failed:", err);
    }
  };

  const loadHistoryAction = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await apiService.getHistory();
      setHistory(data);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to load history list.");
    } finally {
      setIsLoading(false);
    }
  };

  const uploadResumeAction = async (file, jobDescription = '', jobTitle = 'Target Role') => {
    setIsLoading(true);
    setError(null);
    try {
      const result = await apiService.uploadResume(file, jobDescription, jobTitle);
      setCurrentAnalysis(result);
      // Reload history to include the new version
      const hist = await apiService.getHistory();
      setHistory(hist);
      return result;
    } catch (err) {
      const errMsg = err.response?.data?.detail || "Failed to process resume upload.";
      setError(errMsg);
      throw new Error(errMsg);
    } finally {
      setIsLoading(false);
    }
  };

  const matchJobAction = async (resumeId, jobDescription, jobTitle = 'Target Role') => {
    setIsLoading(true);
    setError(null);
    try {
      const result = await apiService.matchJob(resumeId, jobDescription, jobTitle);
      setCurrentAnalysis(result);
      const hist = await apiService.getHistory();
      setHistory(hist);
      return result;
    } catch (err) {
      const errMsg = err.response?.data?.detail || "Failed to compare job description.";
      setError(errMsg);
      throw new Error(errMsg);
    } finally {
      setIsLoading(false);
    }
  };

  const loadAnalysisAction = async (id) => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await apiService.getAnalysis(id);
      setCurrentAnalysis(data);
      return data;
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to load analysis details.");
    } finally {
      setIsLoading(false);
    }
  };

  const deleteAnalysisAction = async (resumeId) => {
    setIsLoading(true);
    setError(null);
    try {
      await apiService.deleteResume(resumeId);
      if (currentAnalysis && currentAnalysis.resume_id === resumeId) {
        setCurrentAnalysis(null);
      }
      const hist = await apiService.getHistory();
      setHistory(hist);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to delete resume records.");
    } finally {
      setIsLoading(false);
    }
  };

  const resetDatabaseAction = async () => {
    setIsLoading(true);
    setError(null);
    try {
      await apiService.resetDatabase();
      setCurrentAnalysis(null);
      setHistory([]);
    } catch (err) {
      setError("Failed to reset database history.");
    } finally {
      setIsLoading(false);
    }
  };

  const clearCurrentAnalysis = () => {
    setCurrentAnalysis(null);
    setError(null);
  };

  return (
    <AnalyzerContext.Provider
      value={{
        currentAnalysis,
        history,
        isLoading,
        error,
        systemHealth,
        checkHealth,
        uploadResumeAction,
        matchJobAction,
        loadHistoryAction,
        loadAnalysisAction,
        deleteAnalysisAction,
        resetDatabaseAction,
        clearCurrentAnalysis,
        setError,
      }}
    >
      {children}
    </AnalyzerContext.Provider>
  );
};

export const useAnalyzer = () => useContext(AnalyzerContext);
