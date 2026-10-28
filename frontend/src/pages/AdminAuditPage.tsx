import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { FileText } from 'lucide-react';
import api, { AuditLogItem } from '../api/client';
import { DisclaimerBanner } from '../components/DisclaimerBanner';

export const AdminAuditPage: React.FC = () => {
  const [selectedAction, setSelectedAction] = useState<string>('all');

  const { data, isLoading } = useQuery<{ total: number; logs: AuditLogItem[] }>({
    queryKey: ['admin-audit-logs', selectedAction],
    queryFn: async () => {
      const url = selectedAction === 'all' ? '/admin/audit-logs' : `/admin/audit-logs?action=${selectedAction}`;
      const res = await api.get(url);
      return res.data;
    },
  });

  const logs = data?.logs || [];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      <DisclaimerBanner compact />

      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-amber-50 border border-amber-200 text-amber-700 dark:bg-amber-600/20 dark:border-amber-500/30 dark:text-amber-400 flex items-center justify-center">
            <FileText className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-2xl font-extrabold text-beige-950 dark:text-white">System Audit Logs</h1>
            <p className="text-xs text-beige-600 dark:text-slate-400">
              Complete chronological audit trail of all security, document analysis, and administrative events
            </p>
          </div>
        </div>

        {/* Action Filter */}
        <select
          value={selectedAction}
          onChange={(e) => setSelectedAction(e.target.value)}
          className="px-3.5 py-2 rounded-xl bg-white dark:bg-slate-900 border border-beige-300 dark:border-slate-700 text-xs text-beige-900 dark:text-white focus:outline-none focus:border-brand-600 shadow-sm"
        >
          <option value="all">All Actions</option>
          <option value="login">User Login</option>
          <option value="register">Registration</option>
          <option value="upload">Document Upload</option>
          <option value="delete_document">Document Deletion</option>
          <option value="correct_clause">Clause Correction</option>
          <option value="update_rule">Rule Modification</option>
          <option value="generate_report">Report Generation</option>
          <option value="download">Report Download</option>
        </select>
      </div>

      {isLoading ? (
        <div className="p-12 text-center text-sm text-beige-600 dark:text-slate-400">Loading audit trail...</div>
      ) : logs.length === 0 ? (
        <div className="glass-panel p-12 rounded-2xl text-center text-beige-600 dark:text-slate-400 text-sm">
          No audit records found matching criteria.
        </div>
      ) : (
        <div className="overflow-x-auto rounded-2xl border border-beige-200 dark:border-slate-800 bg-white dark:bg-slate-900/60 shadow-sm">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="border-b border-beige-200 dark:border-slate-800 bg-beige-100/70 dark:bg-slate-950/70 text-beige-700 dark:text-slate-400 font-semibold uppercase tracking-wider">
                <th className="py-3 px-4">Timestamp</th>
                <th className="py-3 px-4">Action</th>
                <th className="py-3 px-4">Entity Type</th>
                <th className="py-3 px-4">User ID</th>
                <th className="py-3 px-4">IP Address</th>
                <th className="py-3 px-4">Details</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-beige-200 dark:divide-slate-800/60 text-beige-800 dark:text-slate-300 font-mono">
              {logs.map((log) => (
                <tr key={log.id} className="hover:bg-beige-50/70 dark:hover:bg-slate-800/30 transition-colors">
                  <td className="py-3 px-4 text-beige-600 dark:text-slate-400 whitespace-nowrap">
                    {new Date(log.created_at).toLocaleString()}
                  </td>
                  <td className="py-3 px-4">
                    <span className="px-2 py-0.5 rounded-full text-[10px] font-bold font-sans uppercase tracking-wider bg-brand-50 text-brand-700 border border-brand-200 dark:bg-indigo-500/10 dark:text-indigo-400 dark:border-indigo-500/20">
                      {log.action}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-beige-600 dark:text-slate-400">
                    {log.entity_type || '—'}
                  </td>
                  <td className="py-3 px-4 text-beige-600 dark:text-slate-400 truncate max-w-[120px]">
                    {log.user_id ? log.user_id.slice(0, 8) + '...' : 'System'}
                  </td>
                  <td className="py-3 px-4 text-beige-600 dark:text-slate-400">
                    {log.ip_address || '127.0.0.1'}
                  </td>
                  <td className="py-3 px-4 text-[11px] text-beige-700 dark:text-slate-300 max-w-xs truncate">
                    {JSON.stringify(log.details)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
