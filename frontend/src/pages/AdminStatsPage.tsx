import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { BarChart2, FileText, Users, AlertOctagon, Clock, Layers, ShieldCheck } from 'lucide-react';
import api from '../api/client';
import { RiskDistributionChart } from '../components/RiskDistributionChart';
import { DisclaimerBanner } from '../components/DisclaimerBanner';

export const AdminStatsPage: React.FC = () => {
  const { data: stats, isLoading } = useQuery({
    queryKey: ['admin-stats'],
    queryFn: async () => {
      const res = await api.get('/admin/stats');
      return res.data;
    },
  });

  if (isLoading || !stats) {
    return (
      <div className="p-12 text-center text-sm text-beige-600 dark:text-slate-400">Loading system statistics...</div>
    );
  }

  const rb = stats.risk_breakdown || {};
  const catDist = stats.category_distribution || {};

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      <DisclaimerBanner compact />

      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-purple-50 border border-purple-200 text-purple-700 dark:bg-purple-600/20 dark:border-purple-500/30 dark:text-purple-400 flex items-center justify-center">
          <BarChart2 className="w-5 h-5" />
        </div>
        <div>
          <h1 className="text-2xl font-extrabold text-beige-950 dark:text-white">System & ML Performance Metrics</h1>
          <p className="text-xs text-beige-600 dark:text-slate-400">
            Aggregate platform statistics, throughput speeds, and taxonomy distribution
          </p>
        </div>
      </div>

      {/* Metric KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="glass-panel p-5 rounded-2xl space-y-1">
          <div className="flex items-center justify-between text-beige-600 dark:text-slate-400 text-xs font-semibold">
            <span>Total Documents</span>
            <FileText className="w-4 h-4 text-brand-600 dark:text-indigo-400" />
          </div>
          <div className="text-3xl font-extrabold text-beige-950 dark:text-white">{stats.total_documents}</div>
          <span className="text-[11px] text-beige-500 dark:text-slate-500">Processed through pipeline</span>
        </div>

        <div className="glass-panel p-5 rounded-2xl space-y-1">
          <div className="flex items-center justify-between text-beige-600 dark:text-slate-400 text-xs font-semibold">
            <span>Total Clauses</span>
            <Layers className="w-4 h-4 text-teal-600 dark:text-cyan-400" />
          </div>
          <div className="text-3xl font-extrabold text-beige-950 dark:text-white">{stats.total_clauses}</div>
          <span className="text-[11px] text-beige-500 dark:text-slate-500">Segmented & classified</span>
        </div>

        <div className="glass-panel p-5 rounded-2xl space-y-1">
          <div className="flex items-center justify-between text-beige-600 dark:text-slate-400 text-xs font-semibold">
            <span>Active Users</span>
            <Users className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
          </div>
          <div className="text-3xl font-extrabold text-beige-950 dark:text-white">{stats.total_users}</div>
          <span className="text-[11px] text-beige-500 dark:text-slate-500">Registered platform accounts</span>
        </div>

        <div className="glass-panel p-5 rounded-2xl space-y-1">
          <div className="flex items-center justify-between text-beige-600 dark:text-slate-400 text-xs font-semibold">
            <span>Avg Pipeline Speed</span>
            <Clock className="w-4 h-4 text-amber-600 dark:text-amber-400" />
          </div>
          <div className="text-3xl font-extrabold text-beige-950 dark:text-white">{stats.average_processing_time_sec}s</div>
          <span className="text-[11px] text-beige-500 dark:text-slate-500">Per document execution</span>
        </div>
      </div>

      {/* Charts & Breakdown */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Risk Distribution Card */}
        <div className="glass-panel p-6 rounded-2xl space-y-4">
          <h3 className="text-base font-bold text-beige-950 dark:text-white flex items-center gap-2">
            <AlertOctagon className="w-4 h-4 text-rose-600 dark:text-rose-400" />
            Global Clause Risk Breakdown
          </h3>
          <RiskDistributionChart
            high={rb.High || 0}
            medium={rb.Medium || 0}
            low={rb.Low || 0}
          />
          <div className="grid grid-cols-3 gap-2 pt-2 border-t border-beige-200 dark:border-slate-800 text-center text-xs">
            <div>
              <span className="text-beige-600 dark:text-slate-500 font-medium">High Risk</span>
              <p className="font-bold text-rose-600 dark:text-rose-400">{rb.High || 0}</p>
            </div>
            <div>
              <span className="text-beige-600 dark:text-slate-500 font-medium">Medium Risk</span>
              <p className="font-bold text-amber-600 dark:text-amber-400">{rb.Medium || 0}</p>
            </div>
            <div>
              <span className="text-beige-600 dark:text-slate-500 font-medium">Low Risk</span>
              <p className="font-bold text-emerald-600 dark:text-emerald-400">{rb.Low || 0}</p>
            </div>
          </div>
        </div>

        {/* Category Breakdown */}
        <div className="glass-panel p-6 rounded-2xl space-y-4">
          <h3 className="text-base font-bold text-beige-950 dark:text-white flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-brand-600 dark:text-indigo-400" />
            Clauses by Canonical Taxonomy
          </h3>

          <div className="space-y-2.5">
            {Object.entries(catDist).map(([category, count]) => {
              const total = stats.total_clauses || 1;
              const pct = Math.round(((count as number) / total) * 100);

              return (
                <div key={category} className="space-y-1">
                  <div className="flex justify-between text-xs">
                    <span className="text-beige-800 dark:text-slate-300 font-semibold">{category}</span>
                    <span className="text-beige-600 dark:text-slate-400 font-mono">
                      {count as number} ({pct}%)
                    </span>
                  </div>
                  <div className="w-full bg-beige-200 dark:bg-slate-900 h-2 rounded-full overflow-hidden">
                    <div
                      className="bg-brand-600 dark:bg-brand-500 h-full rounded-full transition-all duration-500"
                      style={{ width: `${pct}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};
