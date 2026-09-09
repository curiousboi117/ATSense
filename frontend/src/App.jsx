import React from 'react';
import {
  BrowserRouter as Router,
  Navigate,
  Route,
  Routes,
} from 'react-router-dom';

import { AnalyzerProvider } from './context/AnalyzerContext';
import { AuthProvider } from './context/AuthContext';

import Footer from './components/Footer';
import Navbar from './components/Navbar';
import ProtectedRoute from './components/ProtectedRoute';

import Analytics from './pages/Analytics';
import Dashboard from './pages/Dashboard';
import History from './pages/History';
import JobMatch from './pages/JobMatch';
import Landing from './pages/Landing';
import Login from './pages/Login';
import Profile from './pages/Profile';
import Upload from './pages/Upload';

export default function App() {
  return (
    <AuthProvider>
      <AnalyzerProvider>
        <Router>
          <div className="flex flex-col min-h-screen">
            <Navbar />

            <main className="flex-1 bg-[#0b0f19] text-slate-100">
              <Routes>
                <Route
                  path="/"
                  element={<Landing />}
                />

                <Route
                  path="/login"
                  element={<Login />}
                />

                <Route
                  path="/upload"
                  element={
                    <ProtectedRoute>
                      <Upload />
                    </ProtectedRoute>
                  }
                />

                <Route
                  path="/dashboard"
                  element={
                    <ProtectedRoute>
                      <Dashboard />
                    </ProtectedRoute>
                  }
                />

                <Route
                  path="/match-job"
                  element={
                    <ProtectedRoute>
                      <JobMatch />
                    </ProtectedRoute>
                  }
                />

                <Route
                  path="/analytics"
                  element={
                    <ProtectedRoute>
                      <Analytics />
                    </ProtectedRoute>
                  }
                />

                <Route
                  path="/history"
                  element={
                    <ProtectedRoute>
                      <History />
                    </ProtectedRoute>
                  }
                />

                <Route
                  path="/profile"
                  element={
                    <ProtectedRoute>
                      <Profile />
                    </ProtectedRoute>
                  }
                />

                <Route
                  path="*"
                  element={<Navigate to="/" replace />}
                />
              </Routes>
            </main>

            <Footer />
          </div>
        </Router>
      </AnalyzerProvider>
    </AuthProvider>
  );
}