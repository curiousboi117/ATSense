import React from 'react';
import { motion } from 'framer-motion';

export default function ScoreCircle({ score, size = 160, label = "ATS Score" }) {
  const radius = (size / 2) - 10;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  // Determine color based on score
  const getColor = (s) => {
    if (s >= 80) return '#10b981'; // emerald
    if (s >= 60) return '#f59e0b'; // amber
    return '#ef4444'; // red
  };

  const activeColor = getColor(score);

  return (
    <div className="flex flex-col items-center justify-center">
      <div className="relative animate-pulse-subtle" style={{ width: size, height: size }}>
        
        {/* Ambient Glow */}
        <div 
          className="absolute inset-0 rounded-full blur-2xl opacity-15 transition-all duration-1000" 
          style={{ backgroundColor: activeColor }}
        />

        <svg width={size} height={size} className="transform -rotate-90">
          {/* Background circle */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            className="stroke-slate-800/80"
            strokeWidth="10"
            fill="transparent"
          />
          {/* Progress circle */}
          <motion.circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke={activeColor}
            strokeWidth="10"
            fill="transparent"
            strokeDasharray={circumference}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset }}
            transition={{ duration: 1.2, ease: "easeOut" }}
            strokeLinecap="round"
          />
        </svg>

        {/* Center label */}
        <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
          <motion.span 
            initial={{ opacity: 0, scale: 0.5 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.8 }}
            className="font-outfit text-4xl font-extrabold tracking-tight text-white"
          >
            {Math.round(score)}
          </motion.span>
          <span className="text-[10px] text-slate-500 font-bold tracking-widest uppercase -mt-1">
            / 100
          </span>
        </div>
      </div>
      <span className="text-[11px] font-bold text-slate-400 mt-4 uppercase tracking-widest font-mono">
        {label}
      </span>
    </div>
  );
}
