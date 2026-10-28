import React, { useState, useRef } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import {
  Download, Search, ArrowLeft, ShieldAlert,
  HelpCircle, AlertOctagon, AlertTriangle, Layers, FileText
} from 'lucide-react';
import api, { DocumentItem, ClauseItem, formatDateTime } from '../api/client';
import { RiskBadge } from '../components/RiskBadge';
import { CategoryBadge } from '../components/CategoryBadge';
import { RiskDistributionChart } from '../components/RiskDistributionChart';
import { ClauseDetailDrawer } from '../components/ClauseDetailDrawer';
import { DisclaimerBanner } from '../components/DisclaimerBanner';

export const ResultsPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [selectedClause, setSelectedClause] = useState<ClauseItem | null>(null);
  const [categoryFilter, setCategoryFilter] = useState<string>('All');
  const [riskFilter, setRiskFilter] = useState<string>('All');
  const [needsReviewOnly, setNeedsReviewOnly] = useState<boolean>(false);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [viewMode, setViewMode] = useState<'cards' | 'document'>('cards');
  const [generatingReport, setGeneratingReport] = useState<boolean>(false);

  const clauseRefs = useRef<Record<string, HTMLDivElement | null>>({});

  // 1. Fetch Document info
  const { data: document, isLoading: docLoading } = useQuery<DocumentItem>({
    queryKey: ['document', id],
    queryFn: async () => {
      const res = await api.get(`/documents/${id}`);
      return res.data;
    },
    enabled: !!id,
  });

  // 2. Fetch Clauses with risk flags
  const { data: clauses = [], isLoading: clausesLoading } = useQuery<ClauseItem[]>({
    queryKey: ['clauses', id],
    queryFn: async () => {
      const res = await api.get(`/documents/${id}/clauses`);
      return res.data;
    },
    enabled: !!id,
  });

  // 3. Generate Report Mutation
  const handleDownloadReport = async () => {
    if (!id) return;
    setGeneratingReport(true);
    try {
      const reportRes = await api.post(`/documents/${id}/report`);
      const downloadUrl = reportRes.data.download_url;
      window.open(downloadUrl, '_blank');
    } catch (err) {
      alert('Failed to generate PDF report.');
    } finally {
      setGeneratingReport(false);
    }
  };

  const handleClauseClick = (clause: ClauseItem) => {
    setSelectedClause(clause);
    const el = clauseRefs.current[clause.id];
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  };

  // Filter clauses
  const filteredClauses = clauses.filter((c) => {
    const rf = c.risk_flag;
    const rLevel = rf?.risk_level || 'Low';

    if (categoryFilter !== 'All' && c.primary_category !== categoryFilter) {
      return false;
    }
    if (riskFilter !== 'All' && rLevel !== riskFilter) {
      return false;
    }
    if (needsReviewOnly && !rf?.needs_review) {
      return false;
    }
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      const matchText = c.text.toLowerCase().includes(q);
      const matchHeading = (c.heading || '').toLowerCase().includes(q);
      if (!matchText && !matchHeading) return false;
    }
    return true;
  });

  const highCount = clauses.filter((c) => c.risk_flag?.risk_level === 'High').length;
  const medCount = clauses.filter((c) => c.risk_flag?.risk_level === 'Medium').length;
  const lowCount = clauses.filter((c) => c.risk_flag?.risk_level === 'Low').length;
  const reviewCount = clauses.filter((c) => c.risk_flag?.needs_review).length;

  if (docLoading || clausesLoading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-20 text-center space-y-4">
        <div className="w-10 h-10 border-4 border-brand-600 border-t-transparent rounded-full animate-spin mx-auto" />
        <p className="text-sm text-beige-600 dark:text-slate-400">Loading analysis results...</p>
      </div>
    );
  }

  if (!document) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-20 text-center space-y-4">
        <h2 className="text-xl font-bold text-beige-900 dark:text-white">Document Not Found</h2>
        <Link to="/documents" className="text-brand-600 dark:text-indigo-400 hover:underline text-sm font-semibold">
          Return to contracts list
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      <DisclaimerBanner />

      {/* Top Navigation & Action Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-beige-200 dark:border-slate-800">
        <div className="flex items-center gap-3">
          <Link
            to="/documents"
            className="p-2 rounded-xl border border-beige-200 dark:border-slate-800 bg-white dark:bg-slate-900 text-beige-700 hover:text-beige-950 hover:bg-beige-100 dark:text-slate-400 dark:hover:text-white dark:hover:bg-slate-800 shadow-sm transition-colors"
            title="Back to list"
          >
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl sm:text-2xl font-extrabold text-beige-900 dark:text-white tracking-tight truncate max-w-md">
                {document.filename}
              </h1>
              <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-300 dark:bg-emerald-500/10 dark:text-emerald-400 dark:border-emerald-500/20">
                Audited
              </span>
            </div>
            <p className="text-xs text-beige-600 dark:text-slate-400 mt-0.5">
              {document.page_count} pages • Analyzed on {formatDateTime(document.created_at)}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={handleDownloadReport}
            disabled={generatingReport}
            className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-bold bg-brand-600 hover:bg-brand-700 text-white shadow-sm transition-all disabled:opacity-50"
          >
            <Download className="w-4 h-4" />
            <span>{generatingReport ? 'Generating PDF...' : 'Download PDF Report'}</span>
          </button>
        </div>
      </div>

      {/* Executive Summary Cards & Chart */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
        {/* Metric Cards */}
        <div className="lg:col-span-3 grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div className="glass-panel p-4 rounded-2xl space-y-1">
            <span className="text-xs font-semibold text-beige-600 dark:text-slate-400">Total Clauses</span>
            <div className="text-2xl font-extrabold text-beige-900 dark:text-white">{clauses.length}</div>
            <span className="text-[11px] text-beige-500 dark:text-slate-500">100% segmented</span>
          </div>

          <div className="glass-panel p-4 rounded-2xl space-y-1 border-rose-200 dark:border-rose-500/20 bg-rose-50/40 dark:bg-slate-900/60">
            <span className="text-xs font-semibold text-rose-700 dark:text-rose-300 flex items-center gap-1">
              <AlertOctagon className="w-3.5 h-3.5 text-rose-600 dark:text-rose-400" /> High Risk
            </span>
            <div className="text-2xl font-extrabold text-rose-600 dark:text-rose-400">{highCount}</div>
            <span className="text-[11px] text-rose-700/80 dark:text-rose-400/80 font-medium">Immediate review</span>
          </div>

          <div className="glass-panel p-4 rounded-2xl space-y-1 border-amber-200 dark:border-amber-500/20 bg-amber-50/40 dark:bg-slate-900/60">
            <span className="text-xs font-semibold text-amber-800 dark:text-amber-300 flex items-center gap-1">
              <AlertTriangle className="w-3.5 h-3.5 text-amber-600 dark:text-amber-400" /> Medium Risk
            </span>
            <div className="text-2xl font-extrabold text-amber-600 dark:text-amber-400">{medCount}</div>
            <span className="text-[11px] text-amber-800/80 dark:text-amber-400/80 font-medium">Non-standard terms</span>
          </div>

          <div className="glass-panel p-4 rounded-2xl space-y-1 border-blue-200 dark:border-blue-500/20 bg-blue-50/40 dark:bg-slate-900/60">
            <span className="text-xs font-semibold text-blue-700 dark:text-blue-300 flex items-center gap-1">
              <HelpCircle className="w-3.5 h-3.5 text-blue-600 dark:text-blue-400" /> Needs Review
            </span>
            <div className="text-2xl font-extrabold text-blue-600 dark:text-blue-400">{reviewCount}</div>
            <span className="text-[11px] text-blue-700/80 dark:text-blue-400/80 font-medium">Low confidence</span>
          </div>
        </div>

        {/* Risk Distribution Chart */}
        <div className="glass-panel p-4 rounded-2xl flex flex-col items-center justify-center">
          <span className="text-xs font-semibold text-beige-800 dark:text-slate-300 self-start mb-2">Risk Breakdown</span>
          <RiskDistributionChart high={highCount} medium={medCount} low={lowCount} />
        </div>
      </div>

      {/* Filter and View Toolbar */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 p-3 rounded-2xl bg-white dark:bg-slate-900 border border-beige-200 dark:border-slate-800 shadow-sm transition-colors">
        <div className="flex flex-wrap items-center gap-2">
          {/* Search Query */}
          <div className="relative w-48 sm:w-64">
            <Search className="w-3.5 h-3.5 text-beige-400 dark:text-slate-500 absolute left-3 top-2.5" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search clause text..."
              className="w-full pl-9 pr-3 py-1.5 rounded-xl bg-beige-50 dark:bg-slate-950 border border-beige-200 dark:border-slate-800 text-xs text-beige-900 dark:text-white placeholder-beige-400 dark:placeholder-slate-500 focus:outline-none focus:border-brand-600 transition-colors"
            />
          </div>

          {/* Category Dropdown */}
          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            className="px-3 py-1.5 rounded-xl bg-beige-50 dark:bg-slate-950 border border-beige-200 dark:border-slate-800 text-xs text-beige-800 dark:text-slate-300 focus:outline-none focus:border-brand-600 transition-colors"
          >
            <option value="All">All Categories</option>
            <option value="Termination">Termination</option>
            <option value="Payment">Payment</option>
            <option value="Limitation of Liability">Limitation of Liability</option>
            <option value="Confidentiality">Confidentiality</option>
            <option value="Indemnification">Indemnification</option>
            <option value="Auto-Renewal">Auto-Renewal</option>
            <option value="Dispute Resolution">Dispute Resolution</option>
            <option value="Other">Other</option>
          </select>

          {/* Risk Level Dropdown */}
          <select
            value={riskFilter}
            onChange={(e) => setRiskFilter(e.target.value)}
            className="px-3 py-1.5 rounded-xl bg-beige-50 dark:bg-slate-950 border border-beige-200 dark:border-slate-800 text-xs text-beige-800 dark:text-slate-300 focus:outline-none focus:border-brand-600 transition-colors"
          >
            <option value="All">All Risk Levels</option>
            <option value="High">High Risk</option>
            <option value="Medium">Medium Risk</option>
            <option value="Low">Low Risk</option>
          </select>

          {/* Needs Review Toggle */}
          <button
            onClick={() => setNeedsReviewOnly(!needsReviewOnly)}
            className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition-colors flex items-center gap-1.5 ${
              needsReviewOnly
                ? 'bg-blue-600 text-white shadow-sm'
                : 'bg-beige-50 dark:bg-slate-950 border border-beige-200 dark:border-slate-800 text-beige-700 dark:text-slate-400 hover:text-beige-950 dark:hover:text-white'
            }`}
          >
            <HelpCircle className="w-3.5 h-3.5" />
            <span>Needs Review ({reviewCount})</span>
          </button>
        </div>

        {/* View Mode Toggle */}
        <div className="flex items-center gap-1 bg-beige-100 dark:bg-slate-950 p-1 rounded-xl border border-beige-200 dark:border-slate-800 self-end sm:self-auto">
          <button
            onClick={() => setViewMode('cards')}
            className={`px-3 py-1 rounded-lg text-xs font-bold transition-all flex items-center gap-1.5 ${
              viewMode === 'cards'
                ? 'bg-brand-600 text-white shadow-sm'
                : 'text-beige-700 hover:text-beige-950 dark:text-slate-400 dark:hover:text-white'
            }`}
          >
            <Layers className="w-3.5 h-3.5" />
            <span>Cards</span>
          </button>
          <button
            onClick={() => setViewMode('document')}
            className={`px-3 py-1 rounded-lg text-xs font-bold transition-all flex items-center gap-1.5 ${
              viewMode === 'document'
                ? 'bg-brand-600 text-white shadow-sm'
                : 'text-beige-700 hover:text-beige-950 dark:text-slate-400 dark:hover:text-white'
            }`}
          >
            <FileText className="w-3.5 h-3.5" />
            <span>Document</span>
          </button>
        </div>
      </div>

      {/* Main Content: Cards or Document View */}
      {viewMode === 'cards' ? (
        <div className="space-y-3">
          {filteredClauses.map((clause) => {
            const rf = clause.risk_flag;
            const rLevel = rf?.risk_level || 'Low';
            const rScore = rf?.risk_score || 0;
            const isSelected = selectedClause?.id === clause.id;

            return (
              <div
                key={clause.id}
                ref={(el) => (clauseRefs.current[clause.id] = el)}
                onClick={() => handleClauseClick(clause)}
                className={`p-5 rounded-2xl cursor-pointer transition-all duration-200 border ${
                  isSelected
                    ? 'border-brand-600 bg-brand-50/40 dark:bg-slate-900 ring-2 ring-brand-600 shadow-md'
                    : rLevel === 'High'
                    ? 'border-rose-200 dark:border-rose-500/30 bg-white dark:bg-slate-900/60 hover:border-rose-300 dark:hover:border-rose-500/60 shadow-sm'
                    : rLevel === 'Medium'
                    ? 'border-amber-200 dark:border-amber-500/30 bg-white dark:bg-slate-900/60 hover:border-amber-300 dark:hover:border-amber-500/60 shadow-sm'
                    : 'border-beige-200 dark:border-slate-800 bg-white dark:bg-slate-900/40 hover:border-beige-300 dark:hover:border-slate-700 shadow-sm'
                }`}
              >
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-3">
                  <div className="flex items-center gap-2.5">
                    <span className="font-mono text-xs font-bold text-beige-700 dark:text-slate-400 bg-beige-100 dark:bg-slate-800 border border-beige-200 dark:border-slate-700 px-2 py-0.5 rounded">
                      #{clause.clause_number}
                    </span>
                    <h3 className="font-bold text-sm text-beige-900 dark:text-white">
                      {clause.heading || `Clause ${clause.clause_number}`}
                    </h3>
                    <CategoryBadge category={clause.primary_category} />
                  </div>

                  <div className="flex items-center gap-2">
                    <span className="text-[11px] text-beige-500 dark:text-slate-500">Page {clause.page_number}</span>
                    <RiskBadge level={rLevel} score={rScore} showScore needsReview={rf?.needs_review} />
                  </div>
                </div>

                <p className="text-xs text-beige-800 dark:text-slate-300 font-mono line-clamp-3 leading-relaxed mb-3">
                  {clause.text}
                </p>

                {rf && rf.explanation && (
                  <div className="p-3 rounded-xl bg-beige-50 dark:bg-slate-950/60 border border-beige-200 dark:border-slate-800/80 text-xs text-beige-700 dark:text-slate-400 flex items-start gap-2">
                    <ShieldAlert className="w-4 h-4 text-brand-600 dark:text-indigo-400 shrink-0 mt-0.5" />
                    <span>{rf.explanation}</span>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      ) : (
        /* Full Contract Document Viewer */
        <div className="glass-panel p-8 rounded-3xl border border-beige-200 dark:border-slate-800 space-y-6 max-h-[75vh] overflow-y-auto font-mono text-xs text-beige-800 dark:text-slate-300">
          <div className="text-center pb-4 border-b border-beige-200 dark:border-slate-800 font-sans">
            <h2 className="text-lg font-bold text-beige-900 dark:text-white">{document.filename}</h2>
            <p className="text-xs text-beige-600 dark:text-slate-400">Synchronized High-Risk Clause Viewer</p>
          </div>

          {clauses.map((clause) => {
            const rf = clause.risk_flag;
            const rLevel = rf?.risk_level || 'Low';
            const isSelected = selectedClause?.id === clause.id;

            return (
              <div
                key={clause.id}
                ref={(el) => (clauseRefs.current[clause.id] = el)}
                onClick={() => handleClauseClick(clause)}
                className={`p-4 rounded-xl cursor-pointer transition-all border ${
                  isSelected
                    ? 'ring-2 ring-brand-600 bg-brand-50/60 dark:bg-indigo-950/30'
                    : rLevel === 'High'
                    ? 'bg-rose-50/70 border-rose-200 text-rose-900 dark:bg-rose-950/20 dark:border-rose-500/40 dark:text-rose-100 hover:bg-rose-100/70'
                    : rLevel === 'Medium'
                    ? 'bg-amber-50/70 border-amber-200 text-amber-900 dark:bg-amber-950/15 dark:border-amber-500/30 dark:text-amber-100 hover:bg-amber-100/70'
                    : 'bg-white dark:bg-slate-900/40 border-beige-200 dark:border-slate-800 hover:bg-beige-50 dark:hover:bg-slate-900/80'
                }`}
              >
                <div className="flex items-center justify-between font-sans mb-2">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-beige-900 dark:text-white">[{clause.clause_number}] {clause.heading || ''}</span>
                    <CategoryBadge category={clause.primary_category} />
                  </div>
                  <RiskBadge level={rLevel} score={rf?.risk_score} showScore size="sm" needsReview={rf?.needs_review} />
                </div>
                <div className="whitespace-pre-wrap leading-relaxed">{clause.text}</div>
              </div>
            );
          })}
        </div>
      )}

      {/* Slide-Out Clause Detail Drawer */}
      {selectedClause && (
        <ClauseDetailDrawer
          clause={selectedClause}
          onClose={() => setSelectedClause(null)}
        />
      )}
    </div>
  );
};
