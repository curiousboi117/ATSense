import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  BarChart3,
  History,
  LayoutDashboard,
  LogIn,
  LogOut,
  UploadCloud,
  User,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function Navbar() {
  const { isAuthenticated, logout } = useAuth();
  const location = useLocation();

  const navLinks = [
    { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
    { name: 'Analytics', path: '/analytics', icon: BarChart3 },
    { name: 'History', path: '/history', icon: History },
    { name: 'Profile/Settings', path: '/profile', icon: User },
  ];

  return (
    <header className="sticky top-0 z-50 w-full border-b border-white/5 bg-[#0b0f19]/80 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">

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

        <nav className="hidden md:flex items-center gap-1">
          {isAuthenticated ? (
            <>
              {navLinks.map((link) => {
                const Icon = link.icon;
                const isActive = location.pathname === link.path;

                return (
                  <Link
                    key={link.path}
                    to={link.path}
                    className={`px-3 py-2 rounded-lg text-sm font-medium flex items-center gap-1.5 transition-all ${
                      isActive
                        ? 'text-white bg-white/10'
                        : 'text-slate-400 hover:text-white hover:bg-white/5'
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                    <span className="hidden lg:inline">
                      {link.name}
                    </span>
                  </Link>
                );
              })}

              <Link
                to="/upload"
                className="btn-primary px-4 py-2 rounded-lg text-sm font-medium text-white flex items-center gap-1.5 ml-1"
              >
                <UploadCloud className="w-4 h-4" />
                Analyze
              </Link>

              <button
                type="button"
                onClick={logout}
                className="px-3 py-2 rounded-lg text-sm font-medium text-slate-400 hover:text-red-400 hover:bg-white/5 transition-all flex items-center gap-1.5"
              >
                <LogOut className="w-4 h-4" />
                <span className="hidden lg:inline">
                  Logout
                </span>
              </button>
            </>
          ) : (
            <Link
              to="/login"
              className="btn-primary px-4 py-2 rounded-lg text-sm font-medium text-white flex items-center gap-1.5"
            >
              <LogIn className="w-4 h-4" />
              Sign in
            </Link>
          )}
        </nav>

      </div>
    </header>
  );
}