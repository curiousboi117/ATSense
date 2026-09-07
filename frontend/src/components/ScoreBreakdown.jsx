import React from 'react';
import { motion } from 'framer-motion';

export default function ScoreBreakdown({ breakdown }) {
  if (!breakdown) return null;

  const getBarColor = (score) => {
    if (score >= 80) return 'bg-emerald-500';
    if (score >= 60) return 'bg-amber-500';
    return 'bg-red-500';
  };

  return (
    <div className="space-y-4">
      <h3 className="text-sm font-bold text-slate-300 uppercase tracking-widest font-mono">
        Audit Metric Breakdown
      </h3>
      <div className="space-y-3">
        {Object.entries(breakdown).map(([key, value]) => {
          const displayName = key.replace('_', ' ').replace(/\b\w/g, c => c.toUpperCase());
          return (
            <div key={key} className="space-y-1">
              <div className="flex justify-between items-center text-xs">
                <span className="text-slate-400 font-medium">{displayName}</span>
                <span className="text-slate-200 font-bold font-mono">{value}%</span>
              </div>
              <div className="h-1.5 w-full bg-slate-900 rounded-full overflow-hidden border border-white/5">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${value}%` }}
                  transition={{ duration: 1, ease: "easeOut" }}
                  className={`h-full rounded-full ${getBarColor(value)}`}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
