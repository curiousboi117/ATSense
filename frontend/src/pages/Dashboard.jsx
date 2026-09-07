import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAnalyzer } from '../context/AnalyzerContext';
import ScoreCircle from '../components/ScoreCircle';
import ScoreBreakdown from '../components/ScoreBreakdown';
import SkillBadge from '../components/SkillBadge';
import SimilarityMeter from '../components/SimilarityMeter';
import RecommendationCard from '../components/RecommendationCard';
import GlassCard from '../components/GlassCard';
import { 
  FileText, User, Mail, Phone, MapPin, ExternalLink, 
  Download, Code, ClipboardList, ShieldAlert, Sparkles, RefreshCw
} from 'lucide-react';
import { apiService } from '../services/api';

export default function Dashboard() {
  const { currentAnalysis, isLoading } = useAnalyzer();
  const [activeTab, setActiveTab] = useState('skills');

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[calc(100vh-10rem)]">
        <div className="text-center space-y-3">
          <RefreshCw className="w-8 h-8 text-sky-400 animate-spin mx-auto" />
          <p className="text-sm text-slate-400">Loading analysis data...</p>
        </div>
      </div>
    );
  }

  if (!currentAnalysis) {
    return (
      <div className="max-w-md mx-auto py-20 px-4 text-center space-y-6">
        <GlassCard hover={false} className="border-sky-500/10 p-8 space-y-4">
          <div className="w-12 h-12 rounded-xl bg-sky-500/10 border border-sky-500/20 flex items-center justify-center text-sky-400 mx-auto">
            <FileText className="w-6 h-6" />
          </div>
          <h3 className="font-outfit font-bold text-white text-lg">No Active Analysis</h3>
          <p className="text-xs text-slate-400">
            Please upload a resume first to run the NLP parsing, compliance audits, and job matching.
          </p>
          <Link
            to="/upload"
            className="btn-primary block py-2.5 rounded-lg text-xs font-bold text-white text-center"
          >
            Go to Upload Page
          </Link>
        </GlassCard>
      </div>
    );
  }

  const pInfo = currentAnalysis.personal_info || {};
  const skills = currentAnalysis.skills || {};
  const hasJd = !!currentAnalysis.similarity_metrics;
  const breakDown = currentAnalysis.score_breakdown || {};

  // Formulate key highlights for explainability box
  const getExplainabilityHighlights = () => {
    const highlights = [];
    const checks = currentAnalysis.ats_checks || [];
    
    // Positive highlights
    if (breakDown.skills >= 80) highlights.push({ text: "Excellent technical skill set variety.", type: 'pos' });
    if (breakDown.experience >= 80) highlights.push({ text: "Experience timeline and action verbs are strong.", type: 'pos' });
    if (breakDown.projects >= 80) highlights.push({ text: "Detailed projects description with context.", type: 'pos' });
    if (breakDown.formatting >= 90) highlights.push({ text: "High formatting compliance and metadata integrity.", type: 'pos' });
    
    // Negative highlights from checks
    const highSeverity = checks.filter(c => c.severity === 'HIGH');
    const medSeverity = checks.filter(c => c.severity === 'MEDIUM');
    
    highSeverity.forEach(c => {
      highlights.push({ text: c.explanation, type: 'neg' });
    });
    
    if (highlights.length < 5) {
      medSeverity.slice(0, 3).forEach(c => {
        highlights.push({ text: c.explanation, type: 'neg' });
      });
    }
    
    return highlights.slice(0, 5); // Limit to 5
  };

  const highlights = getExplainabilityHighlights();

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      
      {/* Top action header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 border-b border-white/5 pb-4">
        <div>
          <h1 className="font-outfit text-2xl font-bold text-white flex items-center gap-2">
            Analysis Report v{currentAnalysis.resume_version}
            <span className="text-xs font-mono font-normal text-slate-500 bg-slate-900 border border-white/5 px-2 py-0.5 rounded">
              ID: {currentAnalysis.id}
            </span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            File: {currentAnalysis.resume_filename} • Analyzed on {new Date(currentAnalysis.created_at).toLocaleString()}
          </p>
        </div>

        {/* Download links */}
        <div className="flex gap-2">
          <a
            href={apiService.getPDFReportUrl(currentAnalysis.id)}
            target="_blank"
            rel="noopener noreferrer"
            className="btn-secondary px-3 py-2 rounded-lg text-xs font-medium text-slate-300 hover:text-white flex items-center gap-1.5"
          >
            <Download className="w-3.5 h-3.5" />
            PDF Report
          </a>
          
          <a
            href={apiService.getJSONReportUrl(currentAnalysis.id)}
            download
            className="btn-secondary px-3 py-2 rounded-lg text-xs font-medium text-slate-300 hover:text-white flex items-center gap-1.5"
          >
            <Download className="w-3.5 h-3.5" />
            JSON Export
          </a>

          <Link
            to={`/match-job?resume_id=${currentAnalysis.resume_id}`}
            className="btn-primary px-3 py-2 rounded-lg text-xs font-bold text-white flex items-center gap-1.5"
          >
            <Sparkles className="w-3.5 h-3.5" />
            Match New Job
          </Link>
        </div>
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Left Side: Score & Candidate Info */}
        <div className="lg:col-span-1 space-y-6">
          
          {/* Score & Explainability card */}
          <GlassCard className="text-center py-6 px-4 space-y-6">
            <ScoreCircle score={currentAnalysis.ats_score} size={150} label="ATS COMPLIANCE SCORE" />
            
            {/* Explainability Highlight Box */}
            <div className="text-left bg-black/25 rounded-xl p-4 border border-white/5 space-y-2">
              <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest font-mono block mb-1">
                Score Explanation
              </span>
              <ul className="space-y-1.5">
                {highlights.map((h, i) => (
                  <li key={i} className="text-xs leading-relaxed flex items-start gap-1.5">
                    <span className={`text-base leading-none shrink-0 ${h.type === 'pos' ? 'text-emerald-500' : 'text-red-500'}`}>
                      {h.type === 'pos' ? '•' : '•'}
                    </span>
                    <span className={h.type === 'pos' ? 'text-emerald-400' : 'text-slate-300'}>
                      {h.text}
                    </span>
                  </li>
                ))}
              </ul>
            </div>
            
            <ScoreBreakdown breakdown={breakDown} />
          </GlassCard>

          {/* Contact Details extracted */}
          <GlassCard hover={false} className="space-y-4">
            <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest font-mono flex items-center gap-1.5">
              <User className="w-4 h-4 text-sky-400" />
              Extracted Contact Details
            </h3>
            
            <div className="space-y-2.5 text-xs">
              <div className="flex items-center gap-2 text-slate-300">
                <User className="w-4 h-4 text-slate-500" />
                <span className="font-semibold text-slate-200">{pInfo.name || "Name not detected"}</span>
              </div>
              
              <div className="flex items-center gap-2 text-slate-300">
                <Mail className="w-4 h-4 text-slate-500" />
                <span>{pInfo.email || "Email not detected"}</span>
              </div>
              
              <div className="flex items-center gap-2 text-slate-300">
                <Phone className="w-4 h-4 text-slate-500" />
                <span>{pInfo.phone || "Phone not detected"}</span>
              </div>

              <div className="flex items-center gap-2 text-slate-300">
                <MapPin className="w-4 h-4 text-slate-500" />
                <span>{pInfo.location || "Location not detected"}</span>
              </div>
            </div>

            {pInfo.links && pInfo.links.length > 0 && (
              <div className="border-t border-white/5 pt-3 mt-3 space-y-1.5">
                <span className="text-[10px] text-slate-500 font-bold uppercase tracking-widest font-mono">
                  Online Presence
                </span>
                <div className="flex flex-col gap-1.5 text-xs text-sky-400 font-mono">
                  {pInfo.links.map((link, idx) => (
                    <a 
                      key={idx} 
                      href={link.startsWith('http') ? link : `https://${link}`} 
                      target="_blank" 
                      rel="noopener noreferrer" 
                      className="hover:underline flex items-center gap-1 truncate"
                    >
                      <ExternalLink className="w-3 h-3 shrink-0" />
                      {link}
                    </a>
                  ))}
                </div>
              </div>
            )}
          </GlassCard>

        </div>

        {/* Right Side: Details Tabbed Section */}
        <div className="lg:col-span-2 space-y-6">
          
          {/* Tab buttons */}
          <div className="flex border-b border-white/5 gap-2">
            <button
              onClick={() => setActiveTab('skills')}
              className={`px-4 py-2 border-b-2 text-xs font-bold uppercase tracking-wider transition-colors flex items-center gap-1.5 ${
                activeTab === 'skills'
                  ? 'border-sky-500 text-sky-400'
                  : 'border-transparent text-slate-400 hover:text-slate-200'
              }`}
            >
              <Code className="w-4 h-4" />
              Skills Audit
            </button>
            
            <button
              onClick={() => setActiveTab('audits')}
              className={`px-4 py-2 border-b-2 text-xs font-bold uppercase tracking-wider transition-colors flex items-center gap-1.5 ${
                activeTab === 'audits'
                  ? 'border-sky-500 text-sky-400'
                  : 'border-transparent text-slate-400 hover:text-slate-200'
              }`}
            >
              <ClipboardList className="w-4 h-4" />
              ATS Audits
            </button>
            
            <button
              onClick={() => setActiveTab('match')}
              className={`px-4 py-2 border-b-2 text-xs font-bold uppercase tracking-wider transition-colors flex items-center gap-1.5 ${
                activeTab === 'match'
                  ? 'border-sky-500 text-sky-400'
                  : 'border-transparent text-slate-400 hover:text-slate-200'
              }`}
            >
              <Sparkles className="w-4 h-4" />
              Job Match
            </button>
          </div>

          {/* Tab panels */}
          <div className="min-h-[400px]">
            {activeTab === 'skills' && (
              <div className="space-y-6">
                
                {/* Categorized extracted taxonomy */}
                <div className="space-y-4">
                  <h3 className="text-sm font-bold text-slate-300 uppercase tracking-widest font-mono">
                    Extracted Resume Skills Taxonomy
                  </h3>
                  
                  {anySkillsExist(skills) ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {Object.entries(skills).map(([cat, list]) => {
                        if (list.length === 0) return null;
                        const catLabel = cat.replace('_', ' ').replace(/\b\w/g, c => c.toUpperCase());
                        return (
                          <GlassCard key={cat} hover={false} className="p-4 space-y-3">
                            <span className="text-xs font-mono font-bold text-sky-400 uppercase tracking-wider">
                              {catLabel}
                            </span>
                            <div className="flex flex-wrap gap-1.5">
                              {list.map(s => (
                                <SkillBadge 
                                  key={s} 
                                  name={s} 
                                  type={
                                    hasJd 
                                      ? currentAnalysis.similarity_metrics.matched_skills.includes(s) 
                                        ? 'matched' 
                                        : 'standard' 
                                      : 'standard'
                                  } 
                                />
                              ))}
                            </div>
                          </GlassCard>
                        );
                      })}
                    </div>
                  ) : (
                    <div className="text-center py-10 bg-slate-900/30 rounded-xl border border-white/5 text-xs text-slate-500">
                      No explicit skills detected in the resume text. Consider adding a skills section.
                    </div>
                  )}
                </div>

                {/* Match skill summaries if JD exists */}
                {hasJd && (
                  <div className="space-y-4 pt-4 border-t border-white/5">
                    <h3 className="text-sm font-bold text-slate-300 uppercase tracking-widest font-mono">
                      Target Job Description Skill-Gap Analysis
                    </h3>
                    
                    <div className="grid grid-cols-1 gap-4">
                      {/* Matched */}
                      <GlassCard hover={false} className="p-4 space-y-3 border-emerald-500/10">
                        <span className="text-xs font-bold text-emerald-400 uppercase tracking-wider flex items-center gap-1.5">
                          Matched Skills ({currentAnalysis.similarity_metrics.matched_skills.length})
                        </span>
                        <div className="flex flex-wrap gap-1.5">
                          {currentAnalysis.similarity_metrics.matched_skills.map(s => (
                            <SkillBadge key={s} name={s} type="matched" />
                          ))}
                          {currentAnalysis.similarity_metrics.matched_skills.length === 0 && (
                            <span className="text-xs text-slate-500 italic">No skills matched.</span>
                          )}
                        </div>
                      </GlassCard>

                      {/* Missing */}
                      <GlassCard hover={false} className="p-4 space-y-3 border-red-500/10">
                        <span className="text-xs font-bold text-red-400 uppercase tracking-wider flex items-center gap-1.5">
                          Missing Skills ({currentAnalysis.similarity_metrics.missing_skills.length})
                        </span>
                        <div className="flex flex-wrap gap-1.5">
                          {currentAnalysis.similarity_metrics.missing_skills.map(s => (
                            <SkillBadge key={s} name={s} type="missing" />
                          ))}
                          {currentAnalysis.similarity_metrics.missing_skills.length === 0 && (
                            <span className="text-xs text-emerald-500 italic">All skills matched! No missing skills detected.</span>
                          )}
                        </div>
                      </GlassCard>
                    </div>
                  </div>
                )}

              </div>
            )}

            {activeTab === 'audits' && (
              <RecommendationCard 
                checks={currentAnalysis.ats_checks} 
                recommendations={currentAnalysis.recommendations} 
              />
            )}

            {activeTab === 'match' && (
              <div className="space-y-6">
                {hasJd ? (
                  <div className="space-y-4">
                    <div className="flex justify-between items-center">
                      <h3 className="text-sm font-bold text-slate-300 uppercase tracking-widest font-mono">
                        Target Job Match Details
                      </h3>
                      <span className="text-xs font-mono text-slate-500">
                        Job Title: <span className="text-slate-300">{currentAnalysis.job_title}</span>
                      </span>
                    </div>
                    <SimilarityMeter metrics={currentAnalysis.similarity_metrics} />
                  </div>
                ) : (
                  <div className="max-w-md mx-auto py-12 text-center space-y-4">
                    <p className="text-xs text-slate-400">
                      You did not paste a job description when uploading this resume.
                    </p>
                    <Link
                      to={`/match-job?resume_id=${currentAnalysis.resume_id}`}
                      className="btn-primary inline-flex px-6 py-2.5 rounded-lg text-xs font-bold text-white items-center gap-1.5"
                    >
                      <Sparkles className="w-4 h-4" />
                      Paste Job Description & Compare
                    </Link>
                  </div>
                )}
              </div>
            )}
          </div>

        </div>

      </div>

    </div>
  );
}

function anySkillsExist(skills) {
  for (const cat in skills) {
    if (skills[cat].length > 0) return true;
  }
  return false;
}
