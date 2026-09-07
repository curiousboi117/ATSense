import React from 'react';
import { useAnalyzer } from '../context/AnalyzerContext';
import GlassCard from '../components/GlassCard';
import { Database, AlertTriangle, Cpu, CheckCircle2 } from 'lucide-react';

export default function Profile() {
  const { systemHealth, resetDatabaseAction, history, isLoading } = useAnalyzer();

  const handleReset = async () => {
    if (window.confirm("CRITICAL WARNING: This will permanently delete all uploaded resumes, job matches, and stored analyses from your local SQLite database. This action cannot be undone. Proceed?")) {
      try {
        await resetDatabaseAction();
        alert("Database history wiped successfully.");
      } catch (err) {
        alert("Failed to reset database.");
      }
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-12 space-y-6">
      
      <div className="border-b border-white/5 pb-4">
        <h1 className="font-outfit text-2xl font-bold text-white flex items-center gap-2">
          <Database className="w-6 h-6 text-sky-400" />
          System Parameters & Settings
        </h1>
        <p className="text-xs text-slate-400 mt-1">
          Monitor your local NLP/ML engine status and manage database records.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        
        {/* NLP System Health status */}
        <GlassCard hover={false} className="space-y-4">
          <h3 className="text-xs font-bold text-slate-300 uppercase tracking-widest font-mono flex items-center gap-1.5">
            <Cpu className="w-4.5 h-4.5 text-sky-400" />
            Active NLP Engine Status
          </h3>

          <div className="space-y-3 text-xs">
            <div className="flex justify-between items-center bg-black/15 p-2.5 rounded border border-white/5">
              <span className="text-slate-400">Core NLP (spaCy):</span>
              <span className={`font-semibold ${systemHealth?.nlp_loaded ? 'text-emerald-400' : 'text-amber-400'}`}>
                {systemHealth?.nlp_loaded ? 'Loaded (en_core_web_sm)' : 'Unloaded'}
              </span>
            </div>

            <div className="flex justify-between items-center bg-black/15 p-2.5 rounded border border-white/5">
              <span className="text-slate-400">Semantic Model:</span>
              <span className={`font-semibold ${systemHealth?.model_loaded ? 'text-emerald-400' : 'text-amber-400'}`}>
                {systemHealth?.model_loaded ? 'Loaded' : 'Offline / TF-IDF Fallback'}
              </span>
            </div>

            <div className="flex justify-between items-center bg-black/15 p-2.5 rounded border border-white/5">
              <span className="text-slate-400">Transformer Model:</span>
              <span className="font-mono text-slate-300">
                {systemHealth?.model_name || 'all-MiniLM-L6-v2'}
              </span>
            </div>
          </div>
        </GlassCard>

        {/* Database statistics */}
        <GlassCard hover={false} className="space-y-4">
          <h3 className="text-xs font-bold text-slate-300 uppercase tracking-widest font-mono flex items-center gap-1.5">
            <Database className="w-4.5 h-4.5 text-sky-400" />
            Local SQL Database Parameters
          </h3>

          <div className="space-y-3 text-xs">
            <div className="flex justify-between items-center bg-black/15 p-2.5 rounded border border-white/5">
              <span className="text-slate-400">Database Driver:</span>
              <span className="font-mono text-slate-300">SQLite + SQLAlchemy</span>
            </div>

            <div className="flex justify-between items-center bg-black/15 p-2.5 rounded border border-white/5">
              <span className="text-slate-400">Total Resumes Logged:</span>
              <span className="font-semibold text-slate-200">{history.length} records</span>
            </div>

            <div className="flex justify-between items-center bg-black/15 p-2.5 rounded border border-white/5">
              <span className="text-slate-400">Active User Context:</span>
              <span className="font-mono text-slate-300">default_user (ID=1)</span>
            </div>
          </div>
        </GlassCard>

      </div>

      {/* Database Maintenance options */}
      <GlassCard hover={false} className="border-red-500/10 bg-red-950/5 p-6 space-y-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-red-500/10 border border-red-500/20 flex items-center justify-center text-red-400 shrink-0">
            <AlertTriangle className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-red-400 uppercase tracking-wider font-mono">
              Database Maintenance
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Reset database schemas, remove historical versions, and clear cache logs.
            </p>
          </div>
        </div>

        <div className="border-t border-red-500/10 pt-4 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <div className="text-xs text-slate-400 max-w-md">
            Wiping the database will completely delete all tables. Recommended before conducting fresh student demonstrations or vivas.
          </div>
          
          <button
            onClick={handleReset}
            disabled={isLoading}
            className="px-5 py-2.5 rounded-lg bg-red-500 hover:bg-red-600 transition-colors text-xs font-bold text-white shrink-0 disabled:opacity-50"
          >
            Clear SQLite Database History
          </button>
        </div>
      </GlassCard>

    </div>
  );
}
