import React from 'react';

export default function Footer() {
  return (
    <footer className="w-full border-t border-white/5 bg-[#070a13] py-8 text-center text-slate-500 text-xs">
      <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-4">
        <div>
          <span className="font-semibold text-slate-400">ATSense</span> — Explainable Resume Analytics System
        </div>
        <div className="flex gap-4">
          <span className="hover:text-slate-400 cursor-help">NLP Methodology</span>
          <span className="hover:text-slate-400 cursor-help">Scoring Configuration</span>
          <span className="hover:text-slate-400 cursor-help">Academic Project (B.Tech AI & DS)</span>
        </div>
        <div>
          &copy; {new Date().getFullYear()} ATSense. All rights reserved.
        </div>
      </div>
    </footer>
  );
}
