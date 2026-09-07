import React from 'react';

export default function GlassCard({ children, className = '', hover = true }) {
  return (
    <div className={`glass-panel p-6 rounded-2xl ${hover ? 'glass-panel-hover' : ''} ${className}`}>
      {children}
    </div>
  );
}
