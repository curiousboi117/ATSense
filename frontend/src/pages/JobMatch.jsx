import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate, Link } from 'react-router-dom';
import { useAnalyzer } from '../context/AnalyzerContext';
import GlassCard from '../components/GlassCard';
import { Sparkles, FileText, ArrowLeft, ArrowRight, AlertTriangle } from 'lucide-react';
import LoadingAnalysis from '../components/LoadingAnalysis';

export default function JobMatch() {
  const [searchParams] = useSearchParams();
  const resumeId = searchParams.get('resume_id');
  const navigate = useNavigate();
  
  const { matchJobAction, history, isLoading, error, setError } = useAnalyzer();
  const [jobDescription, setJobDescription] = useState('');
  const [jobTitle, setJobTitle] = useState('');
  const [selectedResume, setSelectedResume] = useState(null);

  useEffect(() => {
    setError(null);
    if (resumeId && history.length > 0) {
      const match = history.find(item => item.resume_id === parseInt(resumeId));
      if (match) {
        setSelectedResume(match);
      }
    } else if (history.length > 0) {
      // Default to the latest uploaded resume
      setSelectedResume(history[0]);
    }
  }, [resumeId, history]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!selectedResume) {
      setError("Please select or upload a resume first.");
      return;
    }
    if (!jobDescription.strip || !jobDescription.trim()) {
      setError("Please paste the job description text.");
      return;
    }

    try {
      await matchJobAction(selectedResume.resume_id, jobDescription, jobTitle);
      navigate('/dashboard');
    } catch (err) {
      console.error("Job matching trigger failed:", err);
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
      
      <div className="flex items-center gap-2">
        <Link to="/dashboard" className="text-slate-400 hover:text-white flex items-center gap-1 text-xs">
          <ArrowLeft className="w-3.5 h-3.5" />
          Back to Dashboard
        </Link>
      </div>

      <div className="text-center space-y-2">
        <h1 className="font-outfit text-3xl font-extrabold text-white flex items-center justify-center gap-2">
          <Sparkles className="w-7 h-7 text-sky-400" />
          Compare Against Job Description
        </h1>
        <p className="text-xs text-slate-400 max-w-md mx-auto">
          Evaluate how compatible your resume is with a specific role. We will recalculate the ATS index using semantic NLP.
        </p>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-xs flex items-start gap-2 max-w-2xl mx-auto">
          <AlertTriangle className="w-5 h-5 shrink-0" />
          <div className="space-y-1">
            <span className="font-bold">Match Verification Failed</span>
            <p className="text-slate-300">{error}</p>
          </div>
        </div>
      )}

      {/* Selected Resume context */}
      {selectedResume && (
        <div className="p-4 rounded-xl bg-slate-900/60 border border-white/5 flex justify-between items-center max-w-2xl mx-auto">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-sky-500/10 border border-sky-500/20 flex items-center justify-center text-sky-400">
              <FileText className="w-5 h-5" />
            </div>
            <div>
              <p className="text-xs text-slate-400 uppercase tracking-widest font-mono">Comparing Resume</p>
              <p className="text-sm font-bold text-slate-200">{selectedResume.filename} (v{selectedResume.version})</p>
            </div>
          </div>
          <div className="text-right">
            <p className="text-xs text-slate-400 uppercase tracking-widest font-mono">Current ATS Score</p>
            <p className="text-sm font-bold text-sky-400">{selectedResume.ats_score}/100</p>
          </div>
        </div>
      )}

      <form onSubmit={handleSubmit} className="max-w-2xl mx-auto space-y-6">
        <GlassCard hover={false} className="space-y-4">
          <div className="space-y-1">
            <label className="text-xs text-slate-400 font-semibold uppercase tracking-wider font-mono">
              Job Title / Target Profile
            </label>
            <input 
              type="text" 
              placeholder="e.g. Lead Machine Learning Architect" 
              value={jobTitle} 
              onChange={(e) => setJobTitle(e.target.value)}
              className="w-full bg-[#070a13] border border-white/5 focus:border-sky-500/50 rounded-xl px-3 py-2.5 text-xs text-slate-200 outline-none transition-colors"
            />
          </div>

          <div className="space-y-1">
            <label className="text-xs text-slate-400 font-semibold uppercase tracking-wider font-mono">
              Target Job Description
            </label>
            <textarea 
              rows={8}
              placeholder="Paste the target job description requirements, skills, and qualifications here..." 
              value={jobDescription} 
              onChange={(e) => setJobDescription(e.target.value)}
              className="w-full bg-[#070a13] border border-white/5 focus:border-sky-500/50 rounded-xl px-3 py-2.5 text-xs text-slate-200 outline-none transition-colors resize-none font-sans"
              required
            />
          </div>
        </GlassCard>

        <button 
          type="submit" 
          className="w-full btn-primary py-3 rounded-xl text-sm font-bold text-white flex items-center justify-center gap-2"
        >
          <span>Calculate Semantic Match</span>
          <ArrowRight className="w-4 h-4" />
        </button>
      </form>

    </div>
  );
}
