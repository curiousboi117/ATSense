import React from 'react';
import { Sparkles, BarChart, Percent, MessageSquare } from 'lucide-react';
import GlassCard from './GlassCard';

export default function SimilarityMeter({ metrics }) {
  if (!metrics) return null;

  const cards = [
    {
      name: 'Semantic Match',
      value: metrics.semantic_match,
      icon: Sparkles,
      color: 'text-purple-400',
      description: 'SentenceTransformers vector similarity of experience and goals.',
    },
    {
      name: 'TF-IDF Similarity',
      value: metrics.tfidf_match,
      icon: BarChart,
      color: 'text-blue-400',
      description: 'Lexical frequency overlap compared using TF-IDF Vectorization.',
    },
    {
      name: 'Keyword Overlap',
      value: metrics.keyword_match,
      icon: Percent,
      color: 'text-emerald-400',
      description: 'Counts of exact raw term occurrences from job description.',
    },
  ];

  return (
    <div className="space-y-6">
      
      {/* Target Overall Match */}
      <GlassCard className="border-sky-500/20 bg-gradient-to-br from-sky-950/20 to-slate-900/50 p-6 flex flex-col md:flex-row justify-between items-center gap-6">
        <div>
          <h3 className="text-lg font-outfit font-bold text-white flex items-center gap-2">
            <MessageSquare className="w-5 h-5 text-sky-400" />
            Job Compatibility Index
          </h3>
          <p className="text-xs text-slate-400 mt-1 max-w-lg">
            This composite score aggregates semantic embeddings, lexical frequency, and keyword density.
          </p>
          <div className="text-[10px] text-slate-500 font-mono mt-3">
            Matching engine: <span className="text-sky-400">{metrics.method_used}</span>
          </div>
        </div>

        <div className="flex flex-col items-center justify-center bg-slate-900/60 border border-white/5 rounded-2xl px-6 py-4 min-w-[150px]">
          <span className="text-4xl font-extrabold text-sky-400 font-outfit">
            {metrics.overall_match}%
          </span>
          <span className="text-[10px] text-slate-500 font-bold uppercase tracking-widest mt-1">
            Overall Match
          </span>
        </div>
      </GlassCard>

      {/* Breakdown Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {cards.map((card) => {
          const Icon = card.icon;
          return (
            <GlassCard key={card.name} className="flex flex-col justify-between h-full">
              <div>
                <div className="flex justify-between items-center mb-2">
                  <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                    {card.name}
                  </span>
                  <Icon className={`w-4 h-4 ${card.color}`} />
                </div>
                <p className="text-[11px] text-slate-500">
                  {card.description}
                </p>
              </div>

              <div className="mt-4">
                <div className="flex justify-between items-center text-xs mb-1">
                  <span className="text-slate-400">Match Level</span>
                  <span className="font-bold text-slate-200 font-mono">{card.value}%</span>
                </div>
                <div className="h-1.5 w-full bg-slate-950 rounded-full overflow-hidden border border-white/5">
                  <div 
                    className="h-full bg-sky-500 rounded-full" 
                    style={{ width: `${card.value}%` }} 
                  />
                </div>
              </div>
            </GlassCard>
          );
        })}
      </div>

    </div>
  );
}
