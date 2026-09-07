import React, { useState, useEffect } from 'react';
import { Loader2 } from 'lucide-react';
import GlassCard from './GlassCard';

export default function LoadingAnalysis() {
  const [stepIndex, setStepIndex] = useState(0);

  const steps = [
    'Verifying document structure & boundaries...',
    'Running whitespace normalizers...',
    'Activating spaCy language model...',
    'Performing Named Entity Recognition...',
    'Parsing sections and headings...',
    'Extracting skills against taxonomy engine...',
    'Comparing keyword densities...',
    'Analyzing structural compliance (ATS rules)...',
    'Calculating semantic match embeddings...',
    'Compiling final explainable scores...'
  ];

  useEffect(() => {
    const interval = setInterval(() => {
      setStepIndex((prev) => (prev < steps.length - 1 ? prev + 1 : prev));
    }, 1200);

    return () => clearInterval(interval);
  }, []);

  return (
    <GlassCard hover={false} className="max-w-md mx-auto py-12 flex flex-col items-center justify-center text-center gap-6 border-sky-500/25">
      <div className="relative flex items-center justify-center">
        <div className="absolute inset-0 w-16 h-16 rounded-full border border-sky-500/10 blur-md animate-pulse" />
        <Loader2 className="w-10 h-10 text-sky-400 animate-spin" />
      </div>

      <div className="space-y-2">
        <h3 className="font-outfit font-bold text-white text-lg">
          Analyzing Resume
        </h3>
        <div className="h-5 overflow-hidden">
          <p className="text-xs text-sky-400 font-mono tracking-wide animate-pulse">
            {steps[stepIndex]}
          </p>
        </div>
        <p className="text-[10px] text-slate-500 max-w-xs mx-auto">
          Please wait. Tokenizing, scanning, and semantic comparisons might take a few moments.
        </p>
      </div>

      {/* Progress slider placeholder */}
      <div className="w-48 h-1 bg-slate-900 rounded-full overflow-hidden border border-white/5 mt-2">
        <div 
          className="h-full bg-sky-500 rounded-full transition-all duration-1000 ease-out" 
          style={{ width: `${((stepIndex + 1) / steps.length) * 100}%` }}
        />
      </div>
    </GlassCard>
  );
}
