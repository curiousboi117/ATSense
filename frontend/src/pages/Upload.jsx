import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAnalyzer } from '../context/AnalyzerContext';
import ResumeUploader from '../components/ResumeUploader';
import LoadingAnalysis from '../components/LoadingAnalysis';
import { AlertCircle } from 'lucide-react';

export default function Upload() {
  const { uploadResumeAction, isLoading, error, setError } = useAnalyzer();
  const navigate = useNavigate();

  const handleAnalyze = async (file, jobDescription, jobTitle) => {
    try {
      await uploadResumeAction(file, jobDescription, jobTitle);
      navigate('/dashboard');
    } catch (err) {
      console.error("Upload process failed:", err);
    }
  };

  if (isLoading) {
    return (
      <div className="py-20">
        <LoadingAnalysis />
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto px-4 py-12 space-y-8">
      
      <div className="text-center space-y-2">
        <h1 className="font-outfit text-3xl sm:text-4xl font-extrabold text-white">
          Optimize Your Resume
        </h1>
        <p className="text-xs sm:text-sm text-slate-400 max-w-md mx-auto">
          Upload your resume in PDF or DOCX format to receive structured compliance scores and semantic gaps.
        </p>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-xs flex items-start gap-2 max-w-2xl mx-auto">
          <AlertCircle className="w-5 h-5 shrink-0" />
          <div className="space-y-1">
            <span className="font-bold">Analysis Failed</span>
            <p className="text-slate-300">{error}</p>
          </div>
        </div>
      )}

      <div className="max-w-2xl mx-auto">
        <ResumeUploader onAnalyze={handleAnalyze} />
      </div>

    </div>
  );
}
