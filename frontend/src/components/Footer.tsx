import React from 'react';
import { Shield, Lock, Cpu } from 'lucide-react';

export const Footer: React.FC = () => {
  return (
    <footer className="border-t border-beige-200 dark:border-slate-800 bg-beige-100/60 dark:bg-slate-950 py-10 mt-auto transition-colors">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-6">
        <div className="flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded-md bg-brand-600 flex items-center justify-center text-white">
              <Shield className="w-3.5 h-3.5 text-white" />
            </div>
            <span className="font-bold text-sm text-beige-900 dark:text-slate-200">ClauseGuard AI</span>
            <span className="text-xs text-beige-600 dark:text-slate-500">— Contract Risk Extraction & Flagging</span>
          </div>

          <div className="flex items-center gap-6 text-xs text-beige-700 dark:text-slate-400">
            <div className="flex items-center gap-1.5">
              <Lock className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400" />
              <span>100% Local Inference & Privacy</span>
            </div>
            <div className="flex items-center gap-1.5">
              <Cpu className="w-3.5 h-3.5 text-brand-600 dark:text-indigo-400" />
              <span>Legal-BERT Engine</span>
            </div>
          </div>
        </div>

        <div className="pt-4 border-t border-beige-200 dark:border-slate-900 text-center text-xs text-beige-600 dark:text-slate-500 space-y-1">
          <p className="text-beige-700 dark:text-slate-400 font-medium">
            This tool is informational and is not legal advice.
          </p>
          <p>© {new Date().getFullYear()} ClauseGuard. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
};
