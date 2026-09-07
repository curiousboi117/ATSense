import React from 'react';
import { Link } from 'react-router-dom';
import { useAnalyzer } from '../context/AnalyzerContext';
import GlassCard from '../components/GlassCard';
import { LineChart, BarChart3, TrendingUp, Info } from 'lucide-react';

export default function Analytics() {
  const { history } = useAnalyzer();

  // Reverse history to read chronologically: v1, v2, v3...
  const sortedHistory = [...history].sort((a, b) => a.version - b.version);
  const dataPoints = sortedHistory.map(item => ({
    version: `v${item.version}`,
    score: item.ats_score,
    job: item.job_title || 'N/A'
  }));

  if (history.length < 2) {
    return (
      <div className="max-w-2xl mx-auto py-20 px-4 text-center space-y-6">
        <GlassCard hover={false} className="border-sky-500/10 p-8 space-y-4">
          <div className="w-12 h-12 rounded-xl bg-sky-500/10 border border-sky-500/20 flex items-center justify-center text-sky-400 mx-auto">
            <LineChart className="w-6 h-6" />
          </div>
          <h3 className="font-outfit font-bold text-white text-lg">Progression Analytics Locked</h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            The improvement simulator requires at least **2 iterations** of your resume (e.g. Upload v1, resolve findings, then upload v2).
          </p>
          <div className="text-[11px] text-slate-500 italic max-w-xs mx-auto">
            Currently, you have {history.length} resume(s) uploaded in your SQLite database.
          </div>
          <Link
            to="/upload"
            className="btn-primary inline-flex px-6 py-2.5 rounded-lg text-xs font-bold text-white"
          >
            Upload Next Version (v{history.length + 1})
          </Link>
        </GlassCard>
      </div>
    );
  }

  // Calculate score improvement: latest - earliest
  const earliestScore = dataPoints[0].score;
  const latestScore = dataPoints[dataPoints.length - 1].score;
  const improvement = latestScore - earliestScore;

  // Render SVG line chart path calculations
  const chartWidth = 500;
  const chartHeight = 200;
  const padding = 30;
  
  const getCoordinates = () => {
    const coords = [];
    const stepX = (chartWidth - padding * 2) / (dataPoints.length - 1);
    
    dataPoints.forEach((pt, idx) => {
      const x = padding + idx * stepX;
      // Map score 0-100 to y position (where Y=0 is top, Y=chartHeight is bottom)
      const usableHeight = chartHeight - padding * 2;
      const y = chartHeight - padding - (pt.score / 100) * usableHeight;
      coords.push({ x, y, ...pt });
    });
    return coords;
  };

  const coords = getCoordinates();
  
  // Build SVG Path string
  const pathD = coords.reduce((acc, pt, idx) => {
    if (idx === 0) return `M ${pt.x} ${pt.y}`;
    return `${acc} L ${pt.x} ${pt.y}`;
  }, '');

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      
      <div className="border-b border-white/5 pb-4">
        <h1 className="font-outfit text-2xl font-bold text-white flex items-center gap-2">
          <TrendingUp className="w-6 h-6 text-sky-400" />
          Improvement Simulator Trend
        </h1>
        <p className="text-xs text-slate-400 mt-1">
          Visualizing resume optimization gains across uploaded versions and matched targets.
        </p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        
        <GlassCard hover={false} className="p-5 flex justify-between items-center bg-slate-900/40">
          <div>
            <span className="text-[10px] text-slate-500 font-bold uppercase tracking-widest font-mono">
              Initial Score
            </span>
            <h3 className="text-2xl font-extrabold text-slate-200 mt-1">
              {earliestScore}/100
            </h3>
            <p className="text-[10px] text-slate-400 mt-1">First upload (v1)</p>
          </div>
          <div className="w-10 h-10 rounded-lg bg-slate-800 border border-white/5 flex items-center justify-center text-slate-400 text-xs font-bold font-mono">
            v1
          </div>
        </GlassCard>

        <GlassCard hover={false} className="p-5 flex justify-between items-center bg-slate-900/40">
          <div>
            <span className="text-[10px] text-slate-500 font-bold uppercase tracking-widest font-mono">
              Latest Optimized Score
            </span>
            <h3 className="text-2xl font-extrabold text-white mt-1">
              {latestScore}/100
            </h3>
            <p className="text-[10px] text-slate-400 mt-1">Most recent upload (v{dataPoints.length})</p>
          </div>
          <div className="w-10 h-10 rounded-lg bg-sky-500/10 border border-sky-500/20 flex items-center justify-center text-sky-400 text-xs font-bold font-mono">
            v{dataPoints.length}
          </div>
        </GlassCard>

        <GlassCard hover={false} className="p-5 flex justify-between items-center border-sky-500/15 bg-sky-950/5">
          <div>
            <span className="text-[10px] text-sky-500 font-bold uppercase tracking-widest font-mono">
              Overall Improvement
            </span>
            <h3 className={`text-2xl font-extrabold mt-1 ${improvement >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
              {improvement >= 0 ? `+${improvement.toFixed(1)}` : improvement.toFixed(1)} pts
            </h3>
            <p className="text-[10px] text-slate-400 mt-1">Incremental score gain</p>
          </div>
          <div className={`w-10 h-10 rounded-lg flex items-center justify-center text-xs font-bold font-mono ${
            improvement >= 0 
              ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400' 
              : 'bg-red-500/10 border-red-500/20 text-red-400'
          }`}>
            {improvement >= 0 ? '▲' : '▼'}
          </div>
        </GlassCard>

      </div>

      {/* SVG Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Progression Line Graph */}
        <GlassCard hover={false} className="lg:col-span-2 space-y-4">
          <div className="flex justify-between items-center">
            <h3 className="text-xs font-bold text-slate-300 uppercase tracking-widest font-mono">
              ATS Compliance Score Progression Chart
            </h3>
            <span className="text-[10px] text-slate-500 font-mono">
              X: Version, Y: Score (0-100)
            </span>
          </div>

          <div className="w-full bg-black/25 rounded-2xl p-4 border border-white/5 flex items-center justify-center">
            <svg 
              viewBox={`0 0 ${chartWidth} ${chartHeight}`} 
              className="w-full max-w-xl h-auto overflow-visible"
            >
              {/* Grid Lines */}
              <line x1={padding} y1={padding} x2={chartWidth - padding} y2={padding} stroke="rgba(255,255,255,0.05)" strokeDasharray="3" />
              <line x1={padding} y1={chartHeight / 2} x2={chartWidth - padding} y2={chartHeight / 2} stroke="rgba(255,255,255,0.05)" strokeDasharray="3" />
              <line x1={padding} y1={chartHeight - padding} x2={chartWidth - padding} y2={chartHeight - padding} stroke="rgba(255,255,255,0.1)" />
              
              {/* Axes */}
              <line x1={padding} y1={padding} x2={padding} y2={chartHeight - padding} stroke="rgba(255,255,255,0.1)" />

              {/* Line path */}
              <path 
                d={pathD} 
                fill="none" 
                stroke="#0ea5e9" 
                strokeWidth="3" 
                strokeLinecap="round" 
                strokeLinejoin="round" 
              />
              
              {/* Area under the line */}
              <path 
                d={`${pathD} L ${coords[coords.length-1].x} ${chartHeight - padding} L ${coords[0].x} ${chartHeight - padding} Z`} 
                fill="url(#grad)" 
                stroke="none"
              />

              {/* Points */}
              {coords.map((pt, idx) => (
                <g key={idx} className="cursor-pointer group">
                  <circle 
                    cx={pt.x} 
                    cy={pt.y} 
                    r="5" 
                    fill="#0ea5e9" 
                    stroke="#ffffff" 
                    strokeWidth="1.5"
                  />
                  {/* Tooltip on circle hover */}
                  <text 
                    x={pt.x} 
                    y={pt.y - 12} 
                    textAnchor="middle" 
                    fill="#38bdf8" 
                    fontSize="10" 
                    fontWeight="bold" 
                    className="opacity-0 group-hover:opacity-100 transition-opacity font-mono"
                  >
                    {pt.score}%
                  </text>
                  {/* X Axis label */}
                  <text 
                    x={pt.x} 
                    y={chartHeight - padding + 15} 
                    textAnchor="middle" 
                    fill="rgba(255,255,255,0.5)" 
                    fontSize="10" 
                    fontWeight="500"
                  >
                    {pt.version}
                  </text>
                </g>
              ))}

              {/* Gradients */}
              <defs>
                <linearGradient id="grad" x1="0%" y1="0%" x2="0%" y2="100%">
                  <stop offset="0%" stopColor="#0ea5e9" stopOpacity="0.25" />
                  <stop offset="100%" stopColor="#0ea5e9" stopOpacity="0.0" />
                </linearGradient>
              </defs>
            </svg>
          </div>
        </GlassCard>

        {/* Info Explainer side card */}
        <GlassCard hover={false} className="lg:col-span-1 p-5 space-y-4 bg-slate-900/20 border-white/5">
          <h3 className="text-xs font-bold text-slate-300 uppercase tracking-widest font-mono flex items-center gap-1.5">
            <Info className="w-4 h-4 text-sky-400" />
            Progression Details
          </h3>
          
          <div className="space-y-3 text-xs divide-y divide-white/5">
            <div className="pb-3">
              <p className="text-slate-400">Total optimization steps:</p>
              <p className="text-sm font-bold text-slate-200 mt-0.5">{dataPoints.length} updates logged</p>
            </div>
            
            <div className="py-3">
              <p className="text-slate-400">Latest matched target job:</p>
              <p className="text-sm font-bold text-sky-400 mt-0.5">{dataPoints[dataPoints.length - 1].job}</p>
            </div>
            
            <div className="py-3">
              <p className="text-slate-400">Improvement status:</p>
              <p className="text-sm font-bold text-emerald-400 mt-0.5">
                {improvement >= 15 
                  ? "Highly optimized path! Keep resolving medium severity findings."
                  : "Incremental gains detected. Focus on adding quantifiable results."
                }
              </p>
            </div>
          </div>
        </GlassCard>

      </div>

    </div>
  );
}
