import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Scale, Edit2, X, Check } from 'lucide-react';
import api, { RiskRule } from '../api/client';
import { CategoryBadge } from '../components/CategoryBadge';
import { DisclaimerBanner } from '../components/DisclaimerBanner';

export const AdminRulesPage: React.FC = () => {
  const queryClient = useQueryClient();
  const [editingRule, setEditingRule] = useState<RiskRule | null>(null);

  const { data: rules = [], isLoading } = useQuery<RiskRule[]>({
    queryKey: ['admin-rules'],
    queryFn: async () => {
      const res = await api.get('/admin/rules');
      return res.data;
    },
  });

  const updateMutation = useMutation({
    mutationFn: async (rule: Partial<RiskRule> & { id: string }) => {
      const { id, ...data } = rule;
      await api.put(`/admin/rules/${id}`, data);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-rules'] });
      setEditingRule(null);
    },
  });

  const handleToggle = (rule: RiskRule) => {
    updateMutation.mutate({
      id: rule.id,
      is_enabled: !rule.is_enabled,
    });
  };

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingRule) return;
    updateMutation.mutate({
      id: editingRule.id,
      points: Number(editingRule.points),
      severity: editingRule.severity,
      pattern_value: editingRule.pattern_value,
      reason: editingRule.reason,
      suggestion: editingRule.suggestion,
      is_enabled: editingRule.is_enabled,
    });
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      <DisclaimerBanner compact />

      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-700 dark:bg-emerald-600/20 dark:border-emerald-500/30 dark:text-emerald-400 flex items-center justify-center">
            <Scale className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-2xl font-extrabold text-beige-950 dark:text-white">Risk Rules Engine Configuration</h1>
            <p className="text-xs text-beige-600 dark:text-slate-400">
              Customize risk weights, detection regex patterns, and severity thresholds without code redeployment
            </p>
          </div>
        </div>
      </div>

      {isLoading ? (
        <div className="p-12 text-center text-sm text-beige-600 dark:text-slate-400">Loading risk rules...</div>
      ) : (
        <div className="overflow-x-auto rounded-2xl border border-beige-200 dark:border-slate-800 bg-white dark:bg-slate-900/60 shadow-sm">
          <table className="w-full text-left border-collapse text-sm">
            <thead>
              <tr className="border-b border-beige-200 dark:border-slate-800 bg-beige-100/70 dark:bg-slate-950/70 text-xs text-beige-700 dark:text-slate-400 font-semibold uppercase tracking-wider">
                <th className="py-3 px-4">Rule Code</th>
                <th className="py-3 px-4">Category</th>
                <th className="py-3 px-4">Severity</th>
                <th className="py-3 px-4">Points</th>
                <th className="py-3 px-4">Pattern Type</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-beige-200 dark:divide-slate-800/60 text-beige-800 dark:text-slate-300">
              {rules.map((r) => (
                <tr key={r.id} className="hover:bg-beige-50/70 dark:hover:bg-slate-800/30 transition-colors">
                  <td className="py-3 px-4 font-mono text-xs font-bold text-brand-700 dark:text-indigo-300">
                    {r.rule_code}
                  </td>
                  <td className="py-3 px-4">
                    <CategoryBadge category={r.category} />
                  </td>
                  <td className="py-3 px-4">
                    <span
                      className={`px-2 py-0.5 rounded text-[11px] font-bold border ${
                        r.severity === 'High'
                          ? 'bg-rose-50 text-rose-700 border-rose-200 dark:bg-rose-500/20 dark:text-rose-300 dark:border-rose-500/30'
                          : r.severity === 'Medium'
                          ? 'bg-amber-50 text-amber-800 border-amber-200 dark:bg-amber-500/20 dark:text-amber-300 dark:border-amber-500/30'
                          : 'bg-emerald-50 text-emerald-700 border-emerald-200 dark:bg-emerald-500/20 dark:text-emerald-300 dark:border-emerald-500/30'
                      }`}
                    >
                      {r.severity}
                    </span>
                  </td>
                  <td className="py-3 px-4 font-mono text-xs font-bold text-beige-950 dark:text-white">
                    {r.points} / 100
                  </td>
                  <td className="py-3 px-4 font-mono text-[11px] text-beige-600 dark:text-slate-400">
                    {r.pattern_type}
                  </td>
                  <td className="py-3 px-4">
                    <button
                      onClick={() => handleToggle(r)}
                      className={`inline-flex items-center gap-1.5 text-xs font-semibold px-2 py-0.5 rounded-full border ${
                        r.is_enabled
                          ? 'bg-emerald-50 text-emerald-700 border-emerald-200 dark:bg-emerald-500/15 dark:border-emerald-500/30 dark:text-emerald-400'
                          : 'bg-beige-100 text-beige-500 border-beige-200 dark:bg-slate-800 dark:border-slate-700 dark:text-slate-500'
                      }`}
                    >
                      {r.is_enabled ? (
                        <>
                          <Check className="w-3 h-3" />
                          <span>Enabled</span>
                        </>
                      ) : (
                        <span>Disabled</span>
                      )}
                    </button>
                  </td>
                  <td className="py-3 px-4 text-right">
                    <button
                      onClick={() => setEditingRule(r)}
                      className="p-1.5 rounded-lg text-beige-500 hover:text-beige-950 hover:bg-beige-100 dark:text-slate-400 dark:hover:text-white dark:hover:bg-slate-800 transition-colors"
                      title="Edit rule"
                    >
                      <Edit2 className="w-4 h-4" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Edit Rule Modal */}
      {editingRule && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
          <div className="glass-panel p-6 rounded-2xl max-w-lg w-full space-y-4 border border-beige-300 dark:border-slate-700 shadow-2xl">
            <div className="flex items-center justify-between border-b border-beige-200 dark:border-slate-800 pb-3">
              <h3 className="font-bold text-base text-beige-950 dark:text-white">
                Edit Rule: <span className="font-mono text-brand-700 dark:text-indigo-400">{editingRule.rule_code}</span>
              </h3>
              <button onClick={() => setEditingRule(null)} className="text-beige-400 hover:text-beige-950 dark:text-slate-400 dark:hover:text-white">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleSave} className="space-y-4 text-xs">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-beige-700 dark:text-slate-400 font-semibold mb-1">Severity</label>
                  <select
                    value={editingRule.severity}
                    onChange={(e) => setEditingRule({ ...editingRule, severity: e.target.value })}
                    className="w-full p-2 rounded-xl bg-white dark:bg-slate-900 border border-beige-300 dark:border-slate-700 text-beige-900 dark:text-white"
                  >
                    <option value="High">High</option>
                    <option value="Medium">Medium</option>
                    <option value="Low">Low</option>
                  </select>
                </div>

                <div>
                  <label className="block text-beige-700 dark:text-slate-400 font-semibold mb-1">Risk Points (0-100)</label>
                  <input
                    type="number"
                    min={0}
                    max={100}
                    value={editingRule.points}
                    onChange={(e) => setEditingRule({ ...editingRule, points: Number(e.target.value) })}
                    className="w-full p-2 rounded-xl bg-white dark:bg-slate-900 border border-beige-300 dark:border-slate-700 text-beige-900 dark:text-white"
                  />
                </div>
              </div>

              <div>
                <label className="block text-beige-700 dark:text-slate-400 font-semibold mb-1">Pattern Value (Regex or JSON)</label>
                <textarea
                  rows={3}
                  value={editingRule.pattern_value}
                  onChange={(e) => setEditingRule({ ...editingRule, pattern_value: e.target.value })}
                  className="w-full p-2 rounded-xl bg-white dark:bg-slate-900 border border-beige-300 dark:border-slate-700 text-beige-900 dark:text-white font-mono text-[11px]"
                />
              </div>

              <div>
                <label className="block text-beige-700 dark:text-slate-400 font-semibold mb-1">Explanation Reason</label>
                <input
                  type="text"
                  value={editingRule.reason}
                  onChange={(e) => setEditingRule({ ...editingRule, reason: e.target.value })}
                  className="w-full p-2 rounded-xl bg-white dark:bg-slate-900 border border-beige-300 dark:border-slate-700 text-beige-900 dark:text-white"
                />
              </div>

              <div>
                <label className="block text-beige-700 dark:text-slate-400 font-semibold mb-1">Recommendation Suggestion</label>
                <input
                  type="text"
                  value={editingRule.suggestion || ''}
                  onChange={(e) => setEditingRule({ ...editingRule, suggestion: e.target.value })}
                  className="w-full p-2 rounded-xl bg-white dark:bg-slate-900 border border-beige-300 dark:border-slate-700 text-beige-900 dark:text-white"
                />
              </div>

              <div className="flex items-center justify-end gap-3 pt-3 border-t border-beige-200 dark:border-slate-800">
                <button
                  type="button"
                  onClick={() => setEditingRule(null)}
                  className="px-4 py-2 rounded-xl text-beige-700 hover:bg-beige-100 dark:text-slate-400 dark:hover:text-white transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={updateMutation.isPending}
                  className="px-5 py-2 rounded-xl font-bold bg-brand-600 hover:bg-brand-700 text-white shadow-sm transition-colors"
                >
                  {updateMutation.isPending ? 'Saving...' : 'Save Rule'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
