import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { LayoutDashboard, UploadCloud, History, BarChart3, User, Database } from 'lucide-react';
import { useAnalyzer } from '../context/AnalyzerContext';

export default function Navbar() {
  const location = useLocation();
  const { systemHealth } = useAnalyzer();

  const navLinks = [
    { name: 'Upload', path: '/upload', icon: UploadCloud },
    { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
    { name: 'Analytics', path: '/analytics', icon: BarChart3 },
    { name: 'History', path: '/history', icon: History },
    { name: 'Profile/Settings', path: '/profile', icon: User },
  ];

  return (
    <header className="sticky top-0 z-50 w-full border-b border-white/5 bg-[#0b0f19]/80 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        
        {/* Branding & Logo */}
        <Link to="/" className="flex items-center gap-3 group">
          <div className="w-8 h-8 rounded-lg overflow-hidden border border-sky-500/20 group-hover:border-sky-400/50 transition-colors flex items-center justify-center bg-slate-900/50">
            <img 
              src="/assets/ATSense_Logo.png" 
              alt="ATSense Logo" 
              className="w-7 h-7 object-contain"
              onError={(e) => {
                e.target.style.display = 'none';
              }}
            />
          </div>
          <div>
            <span className="font-outfit text-xl font-bold tracking-tight text-white group-hover:text-glow-blue transition-all">
              ATSense
            </span>
            <span className="text-[9px] text-sky-400/80 block -mt-1 font-mono tracking-widest font-semibold uppercase">
              NLP Engine
            </span>
          </div>
        </Link>

        {/* Navigation Links */}
        <nav className="hidden md:flex items-center gap-1">
          {navLinks.map((link) => {
            const Icon = link.icon;
            const isActive = location.pathname === link.path;
            return (
              <Link
                key={link.path}
                to={link.path}
                className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                  isActive
                    ? 'text-sky-400 bg-sky-500/5 border border-sky-500/10'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-white/5'
                }`}
              >
                <Icon className="w-4 h-4" />
                {link.name}
              </Link>
            );
          })}
        </nav>

        {/* Health status badge */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-slate-900/80 border border-white/5 text-[11px] text-slate-400">
            <span className={`w-2 h-2 rounded-full ${systemHealth ? 'bg-emerald-500' : 'bg-amber-500 animate-pulse'}`} />
            <span className="hidden sm:inline font-mono">
              {systemHealth ? 'Core NLP Active' : 'Connecting Engine...'}
            </span>
          </div>
          
          <Link
            to="/upload"
            className="btn-primary px-4 py-2 rounded-lg text-sm font-medium text-white flex items-center gap-1.5"
          >
            <UploadCloud className="w-4 h-4" />
            Analyze
          </Link>
        </div>

      </div>
    </header>
  );
}
