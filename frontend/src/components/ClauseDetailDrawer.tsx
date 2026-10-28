import React, { useState } from 'react';
import { X, Copy, Check, ShieldAlert, AlertCircle, FileText, CheckCircle2 } from 'lucide-react';
import { ClauseItem } from '../api/client';
import { RiskBadge } from './RiskBadge';
import { CategoryBadge } from './CategoryBadge';

interface Props {
  clause: ClauseItem | null;
  onClose: () => void;
}

export const ClauseDetailDrawer: React.FC<Props> = ({ clause, onClose }) => {
  const [copied, setCopied] = useState(false);

  if (!clause) return null;

  const rf = clause.risk_flag;
  const riskLevel = rf?.risk_level || 'Low';
  const riskScore = rf?.risk_score || 0;
  const explanation = rf?.explanation || 'No explanation available.';
  const suggestion = rf?.suggestion || 'Terms appear standard.';
  const triggeredRules = rf?.triggered_rules || [];
  const extractedData = rf?.extracted_data || {};
  const spans = extractedData.extracted_spans || {};

  const handleCopy = () => {
    navigator.clipboard.writeText(clause.text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="fixed inset-y-0 right-0 z-50 w-full sm:w-[500px] lg:w-[560px] bg-white dark:bg-slate-900 border-l border-beige-200 dark:border-slate-800 shadow-2xl flex flex-col transition-colors">
      {/* Drawer Header */}
      <div className="px-6 py-5 border-b border-beige-200 dark:border-slate-800 flex items-center justify-between bg-beige-100/70 dark:bg-slate-950/60">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-brand-50 border border-brand-200 text-brand-700 dark:bg-indigo-500/10 dark:border-indigo-500/20 dark:text-indigo-400 flex items-center justify-center font-mono text-sm font-bold">
            #{clause.clause_number}
          </div>
          <div>
            <h3 className="text-base font-bold text-beige-900 dark:text-slate-100 truncate max-w-[280px]">
              {clause.heading || `Clause ${clause.clause_number}`}
            </h3>
            <p className="text-xs text-beige-600 dark:text-slate-400">Page {clause.page_number}</p>
          </div>
        </div>

        <button
          onClick={onClose}
          className="p-1.5 rounded-lg text-beige-600 hover:text-beige-900 hover:bg-beige-200 dark:text-slate-400 dark:hover:text-slate-200 dark:hover:bg-slate-800 transition-colors"
          title="Close drawer"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Drawer Body */}
      <div className="flex-1 overflow-y-auto px-6 py-6 space-y-6">
        {/* Classification & Risk Status Card */}
        <div className="p-4 rounded-xl bg-beige-50 dark:bg-slate-800/40 border border-beige-200 dark:border-slate-700/50 space-y-3">
          <div className="flex items-center justify-between flex-wrap gap-2">
            <div className="flex items-center gap-2">
              <span className="text-xs text-beige-600 dark:text-slate-400 font-medium">Category:</span>
              <CategoryBadge category={clause.primary_category} />
            </div>
            <div className="flex items-center gap-2">
              <span className="text-xs text-beige-600 dark:text-slate-400 font-medium">Risk Level:</span>
              <RiskBadge level={riskLevel} score={riskScore} showScore needsReview={rf?.needs_review} />
            </div>
          </div>

          <div className="flex items-center justify-between text-xs text-beige-600 dark:text-slate-400 pt-2 border-t border-beige-200 dark:border-slate-700/30">
            <span>Model Confidence: <strong className="text-beige-900 dark:text-slate-100">{Math.round(clause.confidence * 100)}%</strong></span>
            {clause.secondary_categories && clause.secondary_categories.length > 0 && (
              <span className="truncate max-w-[220px]">
                Secondary: {clause.secondary_categories.join(', ')}
              </span>
            )}
          </div>
        </div>

        {/* Plain-English Analysis */}
        <div className="space-y-2">
          <h4 className="text-xs font-bold uppercase tracking-wider text-beige-600 dark:text-slate-400 flex items-center gap-1.5">
            <ShieldAlert className="w-4 h-4 text-brand-600 dark:text-indigo-400" />
            Plain-English Explanation
          </h4>
          <div className="p-4 rounded-xl bg-brand-50/80 dark:bg-indigo-950/20 border border-brand-200 dark:border-indigo-500/20 text-sm text-beige-900 dark:text-slate-200 leading-relaxed">
            {explanation}
          </div>
        </div>

        {/* Suggestion & Negotiation Tips */}
        <div className="space-y-2">
          <h4 className="text-xs font-bold uppercase tracking-wider text-beige-600 dark:text-slate-400 flex items-center gap-1.5">
            <CheckCircle2 className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
            Recommended Action
          </h4>
          <div className="p-4 rounded-xl bg-emerald-50/80 dark:bg-emerald-950/20 border border-emerald-200 dark:border-emerald-500/20 text-sm text-emerald-900 dark:text-emerald-200 leading-relaxed font-medium">
            {suggestion}
          </div>
        </div>

        {/* Triggered Rules */}
        {triggeredRules.length > 0 && (
          <div className="space-y-2">
            <h4 className="text-xs font-bold uppercase tracking-wider text-beige-600 dark:text-slate-400 flex items-center gap-1.5">
              <AlertCircle className="w-4 h-4 text-amber-600 dark:text-amber-400" />
              Triggered Risk Rules ({triggeredRules.length})
            </h4>
            <div className="space-y-2">
              {triggeredRules.map((rule, idx) => (
                <div key={idx} className="p-3 rounded-lg bg-beige-50 dark:bg-slate-800/60 border border-beige-200 dark:border-slate-700 text-xs space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="font-mono font-bold text-brand-700 dark:text-indigo-300">{rule.rule_code}</span>
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${
                      rule.severity === 'High'
                        ? 'bg-rose-50 text-rose-700 border-rose-200 dark:bg-rose-500/20 dark:text-rose-300 dark:border-rose-500/30'
                        : 'bg-amber-50 text-amber-800 border-amber-200 dark:bg-amber-500/20 dark:text-amber-300 dark:border-amber-500/30'
                    }`}>
                      {rule.severity} ({rule.points} pts)
                    </span>
                  </div>
                  <p className="text-beige-800 dark:text-slate-300">{rule.reason}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Extracted Details & CUAD Spans */}
        {Object.keys(spans).length > 0 && (
          <div className="space-y-2">
            <h4 className="text-xs font-bold uppercase tracking-wider text-beige-600 dark:text-slate-400 flex items-center gap-1.5">
              <FileText className="w-4 h-4 text-teal-600 dark:text-cyan-400" />
              Extracted Contract Details
            </h4>
            <div className="space-y-2">
              {Object.entries(spans).map(([q, ans], idx) => (
                <div key={idx} className="p-3 rounded-lg bg-beige-50 dark:bg-slate-800/40 border border-beige-200 dark:border-slate-700/50 text-xs">
                  <p className="text-beige-600 dark:text-slate-400 font-medium mb-1">{q}</p>
                  <p className="text-teal-800 dark:text-cyan-300 font-mono bg-teal-50 dark:bg-cyan-950/30 px-2 py-1 rounded border border-teal-200 dark:border-cyan-800/30">
                    "{String(ans)}"
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Full Clause Text with Copy */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <h4 className="text-xs font-bold uppercase tracking-wider text-beige-600 dark:text-slate-400">
              Clause Text
            </h4>
            <button
              onClick={handleCopy}
              className="flex items-center gap-1.5 text-xs text-brand-600 dark:text-indigo-400 hover:text-brand-800 dark:hover:text-indigo-300 font-semibold"
            >
              {copied ? (
                <>
                  <Check className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400" />
                  <span className="text-emerald-600 dark:text-emerald-400">Copied!</span>
                </>
              ) : (
                <>
                  <Copy className="w-3.5 h-3.5" />
                  <span>Copy Text</span>
                </>
              )}
            </button>
          </div>
          <div className="p-4 rounded-xl bg-beige-100/70 dark:bg-slate-950 border border-beige-200 dark:border-slate-800 text-xs font-mono text-beige-900 dark:text-slate-300 whitespace-pre-wrap leading-relaxed max-h-60 overflow-y-auto">
            {clause.text}
          </div>
        </div>

        {/* Legal Disclaimer in drawer */}
        <div className="p-3 rounded-lg bg-beige-100/60 dark:bg-slate-950/80 border border-beige-200 dark:border-slate-800 text-[11px] text-beige-600 dark:text-slate-400 text-center">
          This automated clause evaluation is informational only and is not legal advice.
        </div>
      </div>
    </div>
  );
};
