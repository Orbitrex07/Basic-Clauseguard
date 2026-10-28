import React from 'react';
import { AlertTriangle, Info } from 'lucide-react';

interface Props {
  compact?: boolean;
}

export const DisclaimerBanner: React.FC<Props> = ({ compact = false }) => {
  if (compact) {
    return (
      <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-amber-50 text-amber-900 border border-amber-200 dark:bg-amber-500/10 dark:border-amber-500/20 dark:text-amber-300 text-xs font-medium">
        <Info className="w-3.5 h-3.5 shrink-0 text-amber-600 dark:text-amber-400" />
        <span>This tool is informational and is not legal advice.</span>
      </div>
    );
  }

  return (
    <div className="w-full bg-amber-50/90 border-y border-amber-200 dark:bg-amber-500/10 dark:border-amber-500/20 py-2.5 px-4 transition-colors">
      <div className="max-w-7xl mx-auto flex items-center justify-between gap-3 text-xs sm:text-sm text-amber-900 dark:text-amber-200">
        <div className="flex items-center gap-2.5">
          <AlertTriangle className="w-4 h-4 text-amber-600 dark:text-amber-400 shrink-0" />
          <span>
            <strong className="font-semibold text-amber-950 dark:text-amber-300">Notice:</strong> This tool is informational and is not legal advice. Always consult qualified legal counsel for critical binding agreements.
          </span>
        </div>
        <span className="hidden md:inline-block px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-amber-200/70 text-amber-900 dark:bg-amber-500/20 dark:text-amber-300 uppercase tracking-wider">
          Informational Only
        </span>
      </div>
    </div>
  );
};
