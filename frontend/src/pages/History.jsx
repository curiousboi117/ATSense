import React from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAnalyzer } from '../context/AnalyzerContext';
import GlassCard from '../components/GlassCard';
import { History as HistoryIcon, FileText, Trash2, Download, Eye, Sparkles } from 'lucide-react';
import { apiService } from '../services/api';

export default function History() {
  const { history, loadAnalysisAction, deleteAnalysisAction, isLoading } = useAnalyzer();
  const navigate = useNavigate();

  const handleView = async (id) => {
    await loadAnalysisAction(id);
    navigate('/dashboard');
  };

  const handleDelete = async (resumeId, e) => {
    e.stopPropagation();
    if (window.confirm("Are you sure you want to delete this resume version and all associated analysis records?")) {
      await deleteAnalysisAction(resumeId);
    }
  };

  if (isLoading && history.length === 0) {
    return (
      <div className="flex items-center justify-center min-h-[calc(100vh-10rem)]">
        <p className="text-sm text-slate-400">Loading history records...</p>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto px-4 py-12 space-y-6">
      
      <div className="border-b border-white/5 pb-4">
        <h1 className="font-outfit text-2xl font-bold text-white flex items-center gap-2">
          <HistoryIcon className="w-6 h-6 text-sky-400" />
          Iterative Analysis History
        </h1>
        <p className="text-xs text-slate-400 mt-1">
          Review previously analyzed resume versions and their job description compatibility logs.
        </p>
      </div>

      {history.length === 0 ? (
        <div className="max-w-md mx-auto text-center py-16">
          <GlassCard hover={false} className="border-sky-500/10 p-8 space-y-4">
            <div className="w-12 h-12 rounded-xl bg-sky-500/10 border border-sky-500/20 flex items-center justify-center text-sky-400 mx-auto">
              <HistoryIcon className="w-6 h-6" />
            </div>
            <h3 className="font-outfit font-bold text-white text-lg">No Analysis History Found</h3>
            <p className="text-xs text-slate-400">
              You haven't uploaded or analyzed any resumes yet. Start by optimizing your first copy.
            </p>
            <Link
              to="/upload"
              className="btn-primary block py-2.5 rounded-lg text-xs font-bold text-white text-center"
            >
              Analyze Resume Now
            </Link>
          </GlassCard>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4">
          {history.map((item) => (
            <GlassCard 
              key={item.id} 
              className="p-5 flex flex-col md:flex-row justify-between items-start md:items-center gap-6 border-white/5 hover:border-sky-500/20 bg-slate-900/40"
            >
              <div className="flex items-start gap-4">
                {/* Version Circle badge */}
                <div className="w-12 h-12 rounded-xl bg-sky-500/10 border border-sky-500/20 text-sky-400 font-mono font-bold text-sm flex items-center justify-center shrink-0">
                  v{item.version}
                </div>

                <div className="space-y-1">
                  <h3 className="text-sm font-bold text-slate-200 truncate max-w-sm">
                    {item.filename}
                  </h3>
                  <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-[11px] text-slate-500">
                    <span>Uploaded {new Date(item.created_at).toLocaleDateString()}</span>
                    <span>•</span>
                    <span className="text-slate-400">
                      Target: {item.job_title || "Generic / No Job Match"}
                    </span>
                  </div>
                </div>
              </div>

              {/* Actions & Score */}
              <div className="flex items-center gap-6 w-full md:w-auto justify-between md:justify-end border-t md:border-none border-white/5 pt-4 md:pt-0">
                <div className="text-left md:text-right shrink-0">
                  <p className="text-[10px] text-slate-500 font-bold uppercase tracking-widest font-mono">ATS Score</p>
                  <p className="text-lg font-extrabold text-sky-400 font-outfit">{item.ats_score}/100</p>
                </div>

                <div className="flex items-center gap-2">
                  <button
                    onClick={() => handleView(item.id)}
                    className="p-2 rounded-lg bg-slate-800 border border-white/5 hover:bg-slate-700 text-sky-400 transition-colors cursor-pointer"
                    title="View Report"
                  >
                    <Eye className="w-4 h-4" />
                  </button>

                  <a
                    href={apiService.getPDFReportUrl(item.id)}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="p-2 rounded-lg bg-slate-800 border border-white/5 hover:bg-slate-700 text-slate-300 transition-colors"
                    title="Download PDF"
                  >
                    <Download className="w-4 h-4" />
                  </a>

                  <button
                    onClick={(e) => handleDelete(item.resume_id, e)}
                    className="p-2 rounded-lg bg-slate-800 border border-white/5 hover:bg-red-950/30 hover:border-red-500/20 text-red-400 transition-colors cursor-pointer"
                    title="Delete History"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>

            </GlassCard>
          ))}
        </div>
      )}

    </div>
  );
}
