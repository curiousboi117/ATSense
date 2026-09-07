import React from 'react';
import { Check, AlertCircle } from 'lucide-react';

export default function SkillBadge({ name, type = 'standard' }) {
  const badgeStyles = {
    standard: 'bg-slate-900/60 text-slate-300 border-white/5 hover:border-slate-700/80',
    matched: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20 hover:bg-emerald-500/15',
    missing: 'bg-red-500/10 text-red-400 border-red-500/20 hover:bg-red-500/15',
  };

  return (
    <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-medium border transition-colors ${badgeStyles[type]}`}>
      {type === 'matched' && <Check className="w-3.5 h-3.5 stroke-[3]" />}
      {type === 'missing' && <AlertCircle className="w-3.5 h-3.5 stroke-[2.5]" />}
      {name}
    </span>
  );
}
