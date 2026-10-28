import React from 'react';

interface Props {
  category: string;
}

const CATEGORY_STYLES: Record<string, string> = {
  Termination:
    'bg-rose-50 text-rose-700 border-rose-200 dark:bg-rose-500/10 dark:text-rose-300 dark:border-rose-500/20',
  Payment:
    'bg-emerald-50 text-emerald-700 border-emerald-200 dark:bg-emerald-500/10 dark:text-emerald-300 dark:border-emerald-500/20',
  'Limitation of Liability':
    'bg-amber-50 text-amber-800 border-amber-200 dark:bg-amber-500/10 dark:text-amber-300 dark:border-amber-500/20',
  Confidentiality:
    'bg-sky-50 text-sky-700 border-sky-200 dark:bg-sky-500/10 dark:text-sky-300 dark:border-sky-500/20',
  Indemnification:
    'bg-purple-50 text-purple-700 border-purple-200 dark:bg-purple-500/10 dark:text-purple-300 dark:border-purple-500/20',
  'Auto-Renewal':
    'bg-indigo-50 text-indigo-700 border-indigo-200 dark:bg-indigo-500/10 dark:text-indigo-300 dark:border-indigo-500/20',
  'Dispute Resolution':
    'bg-teal-50 text-teal-700 border-teal-200 dark:bg-cyan-500/10 dark:text-cyan-300 dark:border-cyan-500/20',
  Other:
    'bg-beige-150 text-beige-700 border-beige-300 dark:bg-slate-500/10 dark:text-slate-400 dark:border-slate-500/20',
};

export const CategoryBadge: React.FC<Props> = ({ category }) => {
  const style = CATEGORY_STYLES[category] || CATEGORY_STYLES['Other'];

  return (
    <span className={`inline-flex items-center text-xs font-semibold px-2.5 py-0.5 rounded-lg border ${style}`}>
      {category}
    </span>
  );
};
