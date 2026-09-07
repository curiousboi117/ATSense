import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, Cpu, LineChart, Code, Sparkles, FileText, CheckCircle2 } from 'lucide-react';
import GlassCard from '../components/GlassCard';

export default function Landing() {
  const features = [
    {
      title: "Academic NLP Pipeline",
      description: "Uses spaCy tokenization, Named Entity Recognition (NER), and sentence segmentation to extract details clean.",
      icon: Cpu
    },
    {
      title: "Taxonomy Skill Extractor",
      description: "Classifies technical, tool, and soft skills into programming, web, data, AI/ML, and cloud profiles.",
      icon: Code
    },
    {
      title: "Explainable ATS Auditor",
      description: "Scans structural compliance, formatting errors, weak verbs, and quantifiable metric densities deterministically.",
      icon: CheckCircle2
    },
    {
      title: "Iterative Improvement Simulator",
      description: "Tracks resume progression scores (v1, v2, v3) showing resolved issues and delta score gains.",
      icon: LineChart
    },
    {
      title: "Job-Description Matching",
      description: "Combines Keyword density, TF-IDF cosine matching, and SentenceTransformer semantic embeddings.",
      icon: Sparkles
    },
    {
      title: "Academic Evaluation Metrics",
      description: "Built-in automated simulator testing extraction precision, recall, and F1 metrics.",
      icon: FileText
    }
  ];

  return (
    <div className="space-y-20 py-12 md:py-20 grid-bg min-h-[calc(100vh-10rem)]">
      
      {/* Hero section */}
      <section className="max-w-4xl mx-auto text-center px-4 space-y-6">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-sky-500/10 border border-sky-500/20 text-xs font-semibold text-sky-400 font-mono">
          <Sparkles className="w-3.5 h-3.5" />
          AI & DATA SCIENCE RESEARCH PROJECT
        </div>
        
        <h1 className="font-outfit text-4xl sm:text-6xl font-extrabold tracking-tight text-white leading-tight">
          ATSense: Explainable Resume Analysis & <span className="gradient-text-blue-purple text-glow-blue">Job Matching</span>
        </h1>
        
        <p className="text-base sm:text-lg text-slate-400 max-w-2xl mx-auto leading-relaxed">
          An explainable NLP and machine-learning based system for automated resume auditing, ATS score optimization, semantic skill-gap extraction, and iterative version comparison.
        </p>

        <div className="flex flex-col sm:flex-row justify-center items-center gap-4 pt-4">
          <Link
            to="/upload"
            className="btn-primary w-full sm:w-auto px-8 py-3 rounded-xl text-sm font-bold text-white flex items-center justify-center gap-2 group"
          >
            <span>Optimize My Resume</span>
            <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
          </Link>
          
          <Link
            to="/history"
            className="btn-secondary w-full sm:w-auto px-8 py-3 rounded-xl text-sm font-bold text-slate-300 hover:text-white flex items-center justify-center gap-2"
          >
            <span>Review History</span>
          </Link>
        </div>
      </section>

      {/* Features grid */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-12">
        <div className="text-center space-y-2">
          <h2 className="font-outfit text-2xl sm:text-3xl font-bold text-white">
            Under the Hood: Technical Pipeline
          </h2>
          <p className="text-xs sm:text-sm text-slate-500 max-w-md mx-auto">
            Deep dive into the NLP and similarity architectures driving the analysis.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feature, idx) => {
            const Icon = feature.icon;
            return (
              <GlassCard key={idx} className="flex flex-col gap-4">
                <div className="w-10 h-10 rounded-xl bg-sky-500/10 border border-sky-500/20 flex items-center justify-center text-sky-400">
                  <Icon className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="font-outfit text-base font-bold text-white mb-1">
                    {feature.title}
                  </h3>
                  <p className="text-xs text-slate-400 leading-relaxed">
                    {feature.description}
                  </p>
                </div>
              </GlassCard>
            );
          })}
        </div>
      </section>

      {/* Academic block */}
      <section className="max-w-4xl mx-auto px-4">
        <GlassCard hover={false} className="border-sky-500/15 bg-sky-950/5 text-center p-8 space-y-4">
          <h3 className="text-xs font-bold text-sky-400 uppercase tracking-widest font-mono">
            Academic Contributions
          </h3>
          <p className="text-sm font-semibold text-slate-300">
            "An explainable NLP and machine-learning based system for automated resume analysis, ATS scoring, semantic job matching, skill-gap identification, and iterative resume improvement."
          </p>
          <p className="text-xs text-slate-500 max-w-xl mx-auto leading-relaxed">
            This application utilizes lexical matching algorithms (TF-IDF), vector similarity comparisons, and SpaCy rules to ensure deterministic explainability, bypassing simple black-box evaluations.
          </p>
        </GlassCard>
      </section>

    </div>
  );
}
