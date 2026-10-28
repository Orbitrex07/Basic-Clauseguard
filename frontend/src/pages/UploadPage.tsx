import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Upload, FileText, AlertCircle, ArrowRight, Loader2, Shield } from 'lucide-react';
import api from '../api/client';
import { DisclaimerBanner } from '../components/DisclaimerBanner';

export const UploadPage: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [documentId, setDocumentId] = useState<string | null>(null);
  const [docStatus, setDocStatus] = useState<string>('idle');
  const [pipelineProgress, setPipelineProgress] = useState<number>(0);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();

  // Poll status when documentId exists
  useEffect(() => {
    let interval: any = null;
    if (documentId && docStatus !== 'done' && docStatus !== 'failed') {
      interval = setInterval(async () => {
        try {
          const res = await api.get(`/documents/${documentId}/status`);
          const st = res.data.status;
          const prog = res.data.progress;
          setDocStatus(st);
          setPipelineProgress(prog);

          if (st === 'done') {
            clearInterval(interval);
            setTimeout(() => {
              navigate(`/documents/${documentId}`);
            }, 800);
          } else if (st === 'failed') {
            clearInterval(interval);
            setError(res.data.error_message || 'Pipeline analysis failed.');
          }
        } catch (err: any) {
          clearInterval(interval);
          setError(err.response?.data?.detail || 'Error checking processing status.');
        }
      }, 2000);
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [documentId, docStatus, navigate]);

  const handleFileChange = (selected: File | null) => {
    setError(null);
    if (!selected) return;

    const lower = selected.name.toLowerCase();
    if (!lower.endsWith('.pdf') && !lower.endsWith('.docx')) {
      setError('Unsupported file type. Please upload an English contract in PDF or DOCX format.');
      return;
    }

    if (selected.size > 20 * 1024 * 1024) {
      setError('File size exceeds the 20 MB limit.');
      return;
    }

    setFile(selected);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFileChange(e.dataTransfer.files[0]);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;

    setError(null);
    setUploading(true);
    setUploadProgress(0);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await api.post('/documents', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: (progressEvent) => {
          if (progressEvent.total) {
            const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total);
            setUploadProgress(percent);
          }
        },
      });

      setDocumentId(res.data.id);
      setDocStatus(res.data.status);
      setPipelineProgress(res.data.progress);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to upload contract. Please ensure it is a valid PDF or DOCX file.');
      setUploading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-6">
      <DisclaimerBanner compact />

      <div className="text-center space-y-2">
        <h1 className="text-3xl font-extrabold text-beige-950 dark:text-white tracking-tight">
          Upload Contract for AI Audit
        </h1>
        <p className="text-sm text-beige-600 dark:text-slate-400 max-w-xl mx-auto">
          ClauseGuard will parse, segment, classify, and score your agreement using local Legal-BERT and explainable risk rules.
        </p>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 dark:bg-rose-500/10 dark:border-rose-500/20 dark:text-rose-300 text-xs flex items-center gap-2.5">
          <AlertCircle className="w-5 h-5 shrink-0 text-rose-600 dark:text-rose-400" />
          <span>{error}</span>
        </div>
      )}

      {/* Upload Form & Dropzone */}
      {!uploading ? (
        <form onSubmit={handleSubmit} className="space-y-6">
          <div
            onDragOver={(e) => e.preventDefault()}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
            className={`border-2 border-dashed rounded-3xl p-12 text-center cursor-pointer transition-all ${
              file
                ? 'border-brand-600 bg-brand-50/50 dark:border-indigo-500 dark:bg-indigo-950/20'
                : 'border-beige-300 dark:border-slate-800 hover:border-brand-600 dark:hover:border-indigo-500/60 bg-white dark:bg-slate-900/40 hover:bg-beige-50 dark:hover:bg-slate-900/80 shadow-sm'
            }`}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,.docx"
              className="hidden"
              onChange={(e) => handleFileChange(e.target.files ? e.target.files[0] : null)}
            />

            <div className="space-y-4 max-w-md mx-auto">
              <div className="w-16 h-16 rounded-2xl bg-brand-50 border border-brand-200 text-brand-700 dark:bg-indigo-500/10 dark:border-indigo-500/20 dark:text-indigo-400 flex items-center justify-center mx-auto">
                {file ? <FileText className="w-8 h-8" /> : <Upload className="w-8 h-8" />}
              </div>

              {file ? (
                <div>
                  <h3 className="text-base font-bold text-beige-950 dark:text-white truncate">{file.name}</h3>
                  <p className="text-xs text-brand-700 dark:text-indigo-300 mt-1 font-semibold">
                    {(file.size / (1024 * 1024)).toFixed(2)} MB • Ready to analyze
                  </p>
                  <p className="text-[11px] text-beige-500 dark:text-slate-500 mt-2">Click to select another file</p>
                </div>
              ) : (
                <div>
                  <h3 className="text-base font-bold text-beige-950 dark:text-white">
                    Drag and drop your contract here, or <span className="text-brand-600 dark:text-indigo-400">browse</span>
                  </h3>
                  <p className="text-xs text-beige-600 dark:text-slate-400 mt-1">
                    Accepts English <strong>PDF</strong> and <strong>DOCX</strong> contracts (Max 20 MB, up to 60 pages)
                  </p>
                </div>
              )}
            </div>
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-xs text-beige-600 dark:text-slate-400">
              <Shield className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
              <span>Processed locally. Data never leaves your infrastructure.</span>
            </div>

            <button
              type="submit"
              disabled={!file}
              className="px-6 py-3 rounded-xl font-bold bg-brand-600 hover:bg-brand-700 text-white shadow-sm transition-all flex items-center gap-2 disabled:opacity-40 disabled:cursor-not-allowed"
            >
              <span>Start Extraction</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </form>
      ) : (
        /* Processing Progress View */
        <div className="glass-panel p-8 sm:p-12 rounded-3xl space-y-8 border border-beige-200 dark:border-slate-800 text-center shadow-sm">
          <div className="w-16 h-16 rounded-2xl bg-brand-50 border border-brand-200 text-brand-700 dark:bg-indigo-600/20 dark:border-indigo-500/30 dark:text-indigo-400 flex items-center justify-center mx-auto">
            <Loader2 className="w-8 h-8 animate-spin" />
          </div>

          <div className="space-y-2">
            <h3 className="text-xl font-extrabold text-beige-950 dark:text-white capitalize">
              {docStatus === 'queued' && 'Queued for processing...'}
              {docStatus === 'parsing' && 'Parsing pages & normalizing text...'}
              {docStatus === 'classifying' && 'Classifying clauses with Legal-BERT...'}
              {docStatus === 'scoring' && 'Evaluating risk rules & extracting spans...'}
              {docStatus === 'done' && 'Analysis complete! Redirecting...'}
              {docStatus === 'failed' && 'Processing failed.'}
            </h3>
            <p className="text-xs text-beige-600 dark:text-slate-400">
              Contract: <span className="text-beige-900 dark:text-slate-200 font-semibold">{file?.name}</span>
            </p>
          </div>

          {/* Progress Bar */}
          <div className="space-y-2 max-w-lg mx-auto">
            <div className="w-full bg-beige-200 dark:bg-slate-800 h-3 rounded-full overflow-hidden p-0.5 border border-beige-300 dark:border-slate-700/50">
              <div
                className="bg-brand-600 dark:bg-brand-500 h-full rounded-full transition-all duration-500 ease-out"
                style={{ width: `${Math.max(uploadProgress > 0 && !documentId ? uploadProgress : pipelineProgress, 5)}%` }}
              />
            </div>
            <div className="flex items-center justify-between text-xs text-beige-600 dark:text-slate-400 font-mono">
              <span>Status: <strong className="text-brand-700 dark:text-indigo-400 capitalize">{docStatus}</strong></span>
              <span>{Math.max(uploadProgress > 0 && !documentId ? uploadProgress : pipelineProgress, 5)}%</span>
            </div>
          </div>

          {/* Processing Stages Indicator */}
          <div className="grid grid-cols-4 gap-2 text-[11px] max-w-lg mx-auto pt-4 border-t border-beige-200 dark:border-slate-800/80">
            <div className={`p-2 rounded-xl ${['parsing', 'classifying', 'scoring', 'done'].includes(docStatus) ? 'text-brand-800 dark:text-indigo-300 font-bold bg-brand-50 dark:bg-indigo-950/30 border border-brand-200 dark:border-transparent' : 'text-beige-400 dark:text-slate-600'}`}>
              1. Parse
            </div>
            <div className={`p-2 rounded-xl ${['classifying', 'scoring', 'done'].includes(docStatus) ? 'text-brand-800 dark:text-indigo-300 font-bold bg-brand-50 dark:bg-indigo-950/30 border border-brand-200 dark:border-transparent' : 'text-beige-400 dark:text-slate-600'}`}>
              2. Segment
            </div>
            <div className={`p-2 rounded-xl ${['scoring', 'done'].includes(docStatus) ? 'text-brand-800 dark:text-indigo-300 font-bold bg-brand-50 dark:bg-indigo-950/30 border border-brand-200 dark:border-transparent' : 'text-beige-400 dark:text-slate-600'}`}>
              3. Classify
            </div>
            <div className={`p-2 rounded-xl ${docStatus === 'done' ? 'text-emerald-800 dark:text-emerald-300 font-bold bg-emerald-50 dark:bg-emerald-950/30 border border-emerald-200 dark:border-transparent' : 'text-beige-400 dark:text-slate-600'}`}>
              4. Risk Score
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
