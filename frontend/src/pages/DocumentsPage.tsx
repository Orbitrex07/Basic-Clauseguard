import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { FileText, Upload, Trash2, ArrowUpRight, Search, AlertOctagon, CheckCircle2, Clock, AlertCircle } from 'lucide-react';
import api, { DocumentItem } from '../api/client';
import { DisclaimerBanner } from '../components/DisclaimerBanner';

export const DocumentsPage: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [deleteConfirmId, setDeleteConfirmId] = useState<string | null>(null);
  const queryClient = useQueryClient();

  const { data: documents = [], isLoading, error } = useQuery<DocumentItem[]>({
    queryKey: ['documents'],
    queryFn: async () => {
      const res = await api.get('/documents');
      return res.data;
    },
    refetchInterval: 3000,
  });

  const deleteMutation = useMutation({
    mutationFn: async (id: string) => {
      await api.delete(`/documents/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents'] });
      setDeleteConfirmId(null);
    },
  });

  const filteredDocs = documents.filter((d) =>
    d.filename.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      <DisclaimerBanner compact />

      {/* Header & Upload CTA */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-beige-950 dark:text-white tracking-tight">
            Contract Repository
          </h1>
          <p className="text-xs sm:text-sm text-beige-600 dark:text-slate-400 mt-1">
            Manage your analyzed commercial agreements and risk extractions
          </p>
        </div>

        <Link
          to="/upload"
          className="inline-flex items-center justify-center gap-2 px-5 py-2.5 rounded-xl font-bold bg-brand-600 hover:bg-brand-700 text-white shadow-sm transition-all text-sm"
        >
          <Upload className="w-4 h-4" />
          <span>Upload Contract</span>
        </Link>
      </div>

      {/* Search Bar */}
      <div className="relative max-w-md">
        <Search className="w-4 h-4 text-beige-400 dark:text-slate-500 absolute left-3.5 top-3" />
        <input
          type="text"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          placeholder="Filter contracts by filename..."
          className="w-full pl-10 pr-4 py-2 rounded-xl bg-white dark:bg-slate-900 border border-beige-200 dark:border-slate-800 text-sm text-beige-900 dark:text-white placeholder-beige-400 dark:placeholder-slate-500 focus:outline-none focus:border-brand-600 transition-colors shadow-sm"
        />
      </div>

      {/* Documents Table */}
      {isLoading ? (
        <div className="p-12 text-center text-sm text-beige-600 dark:text-slate-400">Loading contracts...</div>
      ) : error ? (
        <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 dark:bg-rose-500/10 dark:border-rose-500/20 dark:text-rose-300 text-xs">
          Failed to load documents.
        </div>
      ) : filteredDocs.length === 0 ? (
        <div className="glass-panel p-12 rounded-2xl text-center space-y-4">
          <div className="w-12 h-12 rounded-xl bg-beige-100 dark:bg-slate-800 text-beige-600 dark:text-slate-400 flex items-center justify-center mx-auto">
            <FileText className="w-6 h-6" />
          </div>
          <div>
            <h3 className="text-base font-bold text-beige-900 dark:text-slate-200">No contracts found</h3>
            <p className="text-xs text-beige-600 dark:text-slate-400 max-w-sm mx-auto mt-1">
              Upload your first agreement to start automated clause extraction and risk analysis.
            </p>
          </div>
          <Link
            to="/upload"
            className="inline-flex items-center gap-2 px-4 py-2 rounded-xl font-bold bg-brand-600 text-white text-xs hover:bg-brand-700 shadow-sm transition-colors"
          >
            <Upload className="w-3.5 h-3.5" />
            <span>Upload Now</span>
          </Link>
        </div>
      ) : (
        <div className="overflow-x-auto rounded-2xl border border-beige-200 dark:border-slate-800 bg-white dark:bg-slate-900/60 shadow-sm">
          <table className="w-full text-left border-collapse text-sm">
            <thead>
              <tr className="border-b border-beige-200 dark:border-slate-800 bg-beige-100/70 dark:bg-slate-950/70 text-xs text-beige-700 dark:text-slate-400 font-semibold uppercase tracking-wider">
                <th className="py-3.5 px-4">Contract Name</th>
                <th className="py-3.5 px-4">Uploaded</th>
                <th className="py-3.5 px-4">Pages / Size</th>
                <th className="py-3.5 px-4">Status</th>
                <th className="py-3.5 px-4">High Risk</th>
                <th className="py-3.5 px-4">Clauses</th>
                <th className="py-3.5 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-beige-200 dark:divide-slate-800/60 text-beige-800 dark:text-slate-300">
              {filteredDocs.map((doc) => {
                const highRisk = doc.summary?.high_risk_count ?? 0;
                const totalClauses = doc.summary?.total_clauses ?? 0;

                return (
                  <tr key={doc.id} className="hover:bg-beige-50/70 dark:hover:bg-slate-800/30 transition-colors">
                    <td className="py-3.5 px-4">
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-lg bg-brand-50 border border-brand-200 text-brand-700 dark:bg-indigo-500/10 dark:border-indigo-500/20 dark:text-indigo-400 flex items-center justify-center shrink-0">
                          <FileText className="w-4 h-4" />
                        </div>
                        <div>
                          <Link
                            to={`/documents/${doc.id}`}
                            className="font-semibold text-beige-950 dark:text-slate-100 hover:text-brand-600 dark:hover:text-indigo-400 transition-colors block truncate max-w-xs"
                          >
                            {doc.filename}
                          </Link>
                          <span className="text-[11px] text-beige-500 dark:text-slate-500 uppercase">{doc.mime_type.split('/').pop()}</span>
                        </div>
                      </div>
                    </td>

                    <td className="py-3.5 px-4 text-xs text-beige-600 dark:text-slate-400">
                      {new Date(doc.created_at).toLocaleDateString()}
                    </td>

                    <td className="py-3.5 px-4 text-xs text-beige-600 dark:text-slate-400">
                      {doc.page_count} pgs • {formatFileSize(doc.file_size)}
                    </td>

                    <td className="py-3.5 px-4">
                      {doc.status === 'done' ? (
                        <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-300 dark:bg-emerald-500/15 dark:border-emerald-500/30 dark:text-emerald-400">
                          <CheckCircle2 className="w-3 h-3" />
                          Done
                        </span>
                      ) : doc.status === 'failed' ? (
                        <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-rose-50 text-rose-700 border border-rose-300 dark:bg-rose-500/15 dark:border-rose-500/30 dark:text-rose-400">
                          <AlertCircle className="w-3 h-3" />
                          Failed
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-brand-50 text-brand-700 border border-brand-300 dark:bg-indigo-500/15 dark:border-indigo-500/30 dark:text-indigo-300 animate-pulse">
                          <Clock className="w-3 h-3" />
                          {doc.status} ({doc.progress}%)
                        </span>
                      )}
                    </td>

                    <td className="py-3.5 px-4">
                      {highRisk > 0 ? (
                        <span className="inline-flex items-center gap-1 text-xs font-bold px-2 py-0.5 rounded-md bg-rose-50 text-rose-700 border border-rose-200 dark:bg-rose-500/20 dark:text-rose-400 dark:border-rose-500/30">
                          <AlertOctagon className="w-3 h-3" />
                          {highRisk} High
                        </span>
                      ) : (
                        <span className="text-xs text-beige-500 dark:text-slate-500">0</span>
                      )}
                    </td>

                    <td className="py-3.5 px-4 text-xs text-beige-600 dark:text-slate-400">
                      {totalClauses} clauses
                    </td>

                    <td className="py-3.5 px-4 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <Link
                          to={`/documents/${doc.id}`}
                          className="px-3 py-1 rounded-lg text-xs font-semibold bg-brand-50 hover:bg-brand-600 text-brand-700 hover:text-white dark:bg-indigo-600/20 dark:hover:bg-indigo-600 dark:text-indigo-300 dark:hover:text-white transition-colors flex items-center gap-1"
                        >
                          <span>Open</span>
                          <ArrowUpRight className="w-3 h-3" />
                        </Link>

                        <button
                          onClick={() => setDeleteConfirmId(doc.id)}
                          className="p-1.5 rounded-lg text-beige-400 hover:text-rose-600 hover:bg-beige-100 dark:text-slate-500 dark:hover:text-rose-400 dark:hover:bg-slate-800 transition-colors"
                          title="Delete contract"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {deleteConfirmId && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
          <div className="glass-panel p-6 rounded-2xl max-w-sm w-full space-y-4 border border-rose-300 dark:border-rose-500/30 shadow-2xl">
            <div className="flex items-center gap-3 text-rose-600 dark:text-rose-400">
              <AlertCircle className="w-6 h-6 shrink-0" />
              <h3 className="font-bold text-base text-beige-950 dark:text-white">Delete Contract?</h3>
            </div>
            <p className="text-xs text-beige-700 dark:text-slate-300">
              This will permanently delete this document along with all segmented clauses, risk flags, and generated reports from storage.
            </p>
            <div className="flex items-center justify-end gap-3 pt-2">
              <button
                onClick={() => setDeleteConfirmId(null)}
                className="px-3.5 py-1.5 rounded-xl text-xs font-semibold text-beige-700 hover:bg-beige-100 dark:text-slate-300 dark:hover:bg-slate-800 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={() => deleteMutation.mutate(deleteConfirmId)}
                disabled={deleteMutation.isPending}
                className="px-4 py-1.5 rounded-xl text-xs font-bold bg-rose-600 hover:bg-rose-700 text-white transition-colors"
              >
                {deleteMutation.isPending ? 'Deleting...' : 'Delete Permanently'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
