import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { UserCheck, Check, Save } from 'lucide-react';
import api, { ClauseItem } from '../api/client';
import { RiskBadge } from '../components/RiskBadge';
import { CategoryBadge } from '../components/CategoryBadge';
import { DisclaimerBanner } from '../components/DisclaimerBanner';

const CATEGORIES = [
  'Termination',
  'Payment',
  'Limitation of Liability',
  'Confidentiality',
  'Indemnification',
  'Auto-Renewal',
  'Dispute Resolution',
  'Other',
];

export const AdminReviewPage: React.FC = () => {
  const queryClient = useQueryClient();
  const [selectedCat, setSelectedCat] = useState<Record<string, string>>({});
  const [notes, setNotes] = useState<Record<string, string>>({});

  const { data: queue = [], isLoading } = useQuery<ClauseItem[]>({
    queryKey: ['admin-review-queue'],
    queryFn: async () => {
      const res = await api.get('/admin/review-queue');
      return res.data;
    },
  });

  const correctMutation = useMutation({
    mutationFn: async ({ clauseId, newCat, note }: { clauseId: string; newCat: string; note: string }) => {
      await api.patch(`/admin/clauses/${clauseId}`, {
        corrected_category: newCat,
        note: note || 'Verified by admin',
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-review-queue'] });
    },
  });

  const handleCorrect = (clause: ClauseItem) => {
    const newCat = selectedCat[clause.id] || clause.primary_category;
    const note = notes[clause.id] || '';
    correctMutation.mutate({ clauseId: clause.id, newCat, note });
  };

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      <DisclaimerBanner compact />

      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-blue-50 border border-blue-200 text-blue-700 dark:bg-blue-600/20 dark:border-blue-500/30 dark:text-blue-400 flex items-center justify-center">
          <UserCheck className="w-5 h-5" />
        </div>
        <div>
          <h1 className="text-2xl font-extrabold text-beige-950 dark:text-white">Clause Review Queue</h1>
          <p className="text-xs text-beige-600 dark:text-slate-400">
            Verify low-confidence machine learning predictions and correct clause taxonomies
          </p>
        </div>
      </div>

      {isLoading ? (
        <div className="p-12 text-center text-sm text-beige-600 dark:text-slate-400">Loading review queue...</div>
      ) : queue.length === 0 ? (
        <div className="glass-panel p-12 rounded-2xl text-center space-y-3">
          <Check className="w-10 h-10 text-emerald-600 dark:text-emerald-400 mx-auto" />
          <h3 className="text-base font-bold text-beige-950 dark:text-white">Review Queue is Clear!</h3>
          <p className="text-xs text-beige-600 dark:text-slate-400 max-w-sm mx-auto">
            All segmented clauses have high classifier confidence or have already been reviewed.
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {queue.map((clause) => {
            const currentSelected = selectedCat[clause.id] || clause.primary_category;

            return (
              <div key={clause.id} className="glass-panel p-6 rounded-2xl border border-beige-200 dark:border-slate-800 space-y-4">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-beige-200 dark:border-slate-800">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs font-bold text-beige-700 dark:text-slate-400 bg-beige-100 dark:bg-slate-800 px-2 py-0.5 rounded border border-beige-200 dark:border-transparent">
                      #{clause.clause_number}
                    </span>
                    <h3 className="font-bold text-sm text-beige-950 dark:text-white">{clause.heading || 'Clause'}</h3>
                    <CategoryBadge category={clause.primary_category} />
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-beige-600 dark:text-slate-400">
                      Confidence: <strong className="text-beige-900 dark:text-white">{Math.round(clause.confidence * 100)}%</strong>
                    </span>
                    <RiskBadge level={clause.risk_flag?.risk_level || 'Low'} score={clause.risk_flag?.risk_score} />
                  </div>
                </div>

                <div className="p-3.5 rounded-xl bg-beige-100/70 dark:bg-slate-950 font-mono text-xs text-beige-900 dark:text-slate-300 leading-relaxed whitespace-pre-wrap max-h-40 overflow-y-auto border border-beige-200 dark:border-slate-800">
                  {clause.text}
                </div>

                <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3 pt-2">
                  <div className="flex items-center gap-2">
                    <label className="text-xs text-beige-700 dark:text-slate-400 font-semibold">Correct Category:</label>
                    <select
                      value={currentSelected}
                      onChange={(e) => setSelectedCat({ ...selectedCat, [clause.id]: e.target.value })}
                      className="px-3 py-1.5 rounded-xl bg-white dark:bg-slate-900 border border-beige-300 dark:border-slate-700 text-xs text-beige-900 dark:text-white focus:outline-none focus:border-brand-600"
                    >
                      {CATEGORIES.map((cat) => (
                        <option key={cat} value={cat}>
                          {cat}
                        </option>
                      ))}
                    </select>
                  </div>

                  <input
                    type="text"
                    placeholder="Correction note (e.g., Unilateral price increase)..."
                    value={notes[clause.id] || ''}
                    onChange={(e) => setNotes({ ...notes, [clause.id]: e.target.value })}
                    className="flex-1 px-3 py-1.5 rounded-xl bg-white dark:bg-slate-900 border border-beige-300 dark:border-slate-700 text-xs text-beige-900 dark:text-white placeholder-beige-400 dark:placeholder-slate-500 focus:outline-none focus:border-brand-600"
                  />

                  <button
                    onClick={() => handleCorrect(clause)}
                    disabled={correctMutation.isPending}
                    className="px-4 py-1.5 rounded-xl text-xs font-bold bg-brand-600 hover:bg-brand-700 text-white shadow-sm transition-colors flex items-center justify-center gap-1.5"
                  >
                    <Save className="w-3.5 h-3.5" />
                    <span>Confirm & Rescore</span>
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
