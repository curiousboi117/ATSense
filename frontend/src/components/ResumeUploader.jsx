import React, { useState, useRef } from 'react';
import { Upload, FileText, FileDown, AlertTriangle, ArrowRight, Check } from 'lucide-react';
import GlassCard from './GlassCard';

export default function ResumeUploader({ onAnalyze }) {
  const [file, setFile] = useState(null);
  const [jobDescription, setJobDescription] = useState('');
  const [jobTitle, setJobTitle] = useState('');
  const [dragActive, setDragActive] = useState(false);
  const [validationError, setValidationError] = useState('');
  const fileInputRef = useRef(null);

  const validateFile = (selectedFile) => {
    setValidationError('');
    if (!selectedFile) return false;

    const allowedExtensions = ['.pdf', '.docx'];
    const filename = selectedFile.name.lowerCase ? selectedFile.name.toLowerCase() : selectedFile.name;
    const fileExtension = filename.substring(filename.lastIndexOf('.'));

    if (!allowedExtensions.includes(fileExtension)) {
      setValidationError('Unsupported file format. Only PDF and DOCX files are allowed.');
      return false;
    }

    if (selectedFile.size > 5 * 1024 * 1024) {
      setValidationError('File size exceeds the 5MB limit.');
      return false;
    }

    return true;
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const droppedFile = e.dataTransfer.files[0];
      if (validateFile(droppedFile)) {
        setFile(droppedFile);
      }
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      if (validateFile(selectedFile)) {
        setFile(selectedFile);
      }
    }
  };

  const onButtonClick = () => {
    fileInputRef.current.click();
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!file) {
      setValidationError('Please upload a resume file first.');
      return;
    }
    onAnalyze(file, jobDescription, jobTitle);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      
      {/* Upload zone */}
      <div 
        onDragEnter={handleDrag}
        onDragOver={handleDrag}
        onDragLeave={handleDrag}
        onDrop={handleDrop}
        onClick={onButtonClick}
        className={`border-2 border-dashed rounded-2xl p-8 text-center cursor-pointer transition-all ${
          dragActive 
            ? 'border-sky-400 bg-sky-500/5' 
            : file 
              ? 'border-emerald-500/30 bg-emerald-500/5' 
              : 'border-white/10 hover:border-white/20 bg-slate-900/40 hover:bg-slate-900/60'
        }`}
      >
        <input 
          ref={fileInputRef}
          type="file" 
          className="hidden" 
          accept=".pdf,.docx" 
          onChange={handleFileChange}
        />
        
        <div className="flex flex-col items-center justify-center gap-3">
          {file ? (
            <div className="w-12 h-12 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
              <Check className="w-6 h-6 stroke-[2.5]" />
            </div>
          ) : (
            <div className="w-12 h-12 rounded-xl bg-sky-500/10 border border-sky-500/20 flex items-center justify-center text-sky-400">
              <Upload className="w-6 h-6" />
            </div>
          )}

          {file ? (
            <div>
              <p className="text-sm font-bold text-slate-200 truncate max-w-md mx-auto">
                {file.name}
              </p>
              <p className="text-xs text-slate-500 mt-1">
                {(file.size / (1024 * 1024)).toFixed(2)} MB • Click to replace file
              </p>
            </div>
          ) : (
            <div>
              <p className="text-sm font-bold text-slate-200">
                Drag and drop your resume here, or <span className="text-sky-400">browse files</span>
              </p>
              <p className="text-xs text-slate-500 mt-1.5">
                Supports PDF and DOCX (Max 5MB)
              </p>
            </div>
          )}
        </div>
      </div>

      {validationError && (
        <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-xs flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 shrink-0" />
          <span>{validationError}</span>
        </div>
      )}

      {/* Target Job Profile fields (optional) */}
      <GlassCard hover={false} className="p-5 space-y-4">
        <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest font-mono">
          Compare Against Target Job Description (Optional)
        </h3>
        
        <div className="space-y-3">
          <div className="space-y-1">
            <label className="text-xs text-slate-400 font-medium">Job Title / Target Role</label>
            <input 
              type="text" 
              placeholder="e.g. Senior Machine Learning Engineer" 
              value={jobTitle} 
              onChange={(e) => setJobTitle(e.target.value)}
              className="w-full bg-[#070a13] border border-white/5 focus:border-sky-500/50 rounded-xl px-3 py-2 text-xs text-slate-200 outline-none transition-colors"
            />
          </div>
          
          <div className="space-y-1">
            <label className="text-xs text-slate-400 font-medium">Paste Job Description</label>
            <textarea 
              rows={6}
              placeholder="Paste the target job description requirements, skills, and qualifications here..." 
              value={jobDescription} 
              onChange={(e) => setJobDescription(e.target.value)}
              className="w-full bg-[#070a13] border border-white/5 focus:border-sky-500/50 rounded-xl px-3 py-2 text-xs text-slate-200 outline-none transition-colors resize-none font-sans"
            />
          </div>
        </div>
      </GlassCard>

      {/* Submission */}
      <button 
        type="submit" 
        className="w-full btn-primary py-3 rounded-xl text-sm font-bold text-white flex items-center justify-center gap-2"
      >
        <span>Run ATSense Optimizer</span>
        <ArrowRight className="w-4 h-4" />
      </button>

    </form>
  );
}
