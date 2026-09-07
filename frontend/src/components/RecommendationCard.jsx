import { ShieldAlert, ShieldCheck, Info, ArrowRight } from 'lucide-react';
import GlassCard from './GlassCard';

export default function RecommendationCard({ checks, recommendations }) {
  const getSeverityStyles = (sev) => {
    switch (sev) {
      case 'HIGH':
        return {
          bg: 'bg-red-500/10 border-red-500/20',
          text: 'text-red-400',
          badge: 'bg-red-500/20 text-red-300 border-red-500/30',
          icon: ShieldAlert
        };
      case 'MEDIUM':
        return {
          bg: 'bg-amber-500/10 border-amber-500/20',
          text: 'text-amber-400',
          badge: 'bg-amber-500/20 text-amber-300 border-amber-500/30',
          icon: ShieldAlert
        };
      default:
        return {
          bg: 'bg-slate-900/60 border-white/5',
          text: 'text-slate-400',
          badge: 'bg-slate-800 text-slate-300 border-slate-700',
          icon: Info
        };
    }
  };

  return (
    <div className="space-y-6">
      
      {/* ATS Rule Warnings */}
      {checks && checks.length > 0 && (
        <div className="space-y-4">
          <h3 className="text-sm font-bold text-slate-300 uppercase tracking-widest font-mono">
            Compliance Failures & Warnings ({checks.length})
          </h3>
          <div className="grid grid-cols-1 gap-3">
            {checks.map((check, index) => {
              const styles = getSeverityStyles(check.severity);
              const Icon = styles.icon;
              return (
                <div key={index} className={`p-4 rounded-xl border flex gap-4 ${styles.bg}`}>
                  <div className="mt-0.5">
                    <Icon className={`w-5 h-5 ${styles.text}`} />
                  </div>
                  <div className="flex-1">
                    <div className="flex flex-wrap items-center gap-2 mb-1">
                      <span className={`text-[10px] font-bold px-2 py-0.5 rounded border uppercase ${styles.badge}`}>
                        {check.severity}
                      </span>
                      <span className="text-[10px] font-mono text-slate-500 uppercase font-semibold">
                        {check.category}
                      </span>
                    </div>
                    <p className="text-xs text-slate-300 font-medium">
                      {check.explanation}
                    </p>
                    <div className="mt-2 text-xs text-slate-400 flex items-start gap-1 bg-black/15 p-2 rounded border border-white/5">
                      <span className="text-sky-400 font-semibold uppercase text-[9px] mt-0.5 shrink-0">Fix:</span>
                      <span>{check.recommendation}</span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Actionable General Recommendations */}
      {recommendations && recommendations.length > 0 && (
        <div className="space-y-4">
          <h3 className="text-sm font-bold text-slate-300 uppercase tracking-widest font-mono">
            Structured Improvement Roadmap
          </h3>
          <GlassCard className="p-0 overflow-hidden">
            <div className="divide-y divide-white/5">
              {recommendations.map((rec, index) => (
                <div key={index} className="p-4 flex gap-3 items-start hover:bg-white/5 transition-colors">
                  <div className="w-5 h-5 rounded-full bg-sky-500/10 border border-sky-500/20 text-sky-400 flex items-center justify-center text-xs font-bold font-mono shrink-0 mt-0.5">
                    {index + 1}
                  </div>
                  <p className="text-xs text-slate-300 leading-relaxed">
                    {rec}
                  </p>
                </div>
              ))}
            </div>
          </GlassCard>
        </div>
      )}
      
    </div>
  );
}
