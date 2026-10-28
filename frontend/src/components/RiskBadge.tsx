import React from 'react';
import { AlertOctagon, AlertTriangle, CheckCircle2, HelpCircle } from 'lucide-react';

interface Props {
  level: 'High' | 'Medium' | 'Low' | string;
  score?: number;
  showScore?: boolean;
  needsReview?: boolean;
  size?: 'sm' | 'md' | 'lg';
}

export const RiskBadge: React.FC<Props> = ({
  level,
  score,
  showScore = false,
  needsReview = false,
  size = 'md',
}) => {
  const normLevel = level ? level.toLowerCase() : 'low';

  let config = {
    bg: 'bg-emerald-50 text-emerald-700 border-emerald-300 dark:bg-emerald-500/15 dark:border-emerald-500/30 dark:text-emerald-400',
    icon: CheckCircle2,
    label: 'Low Risk',
  };

  if (normLevel === 'high') {
    config = {
      bg: 'bg-rose-50 text-rose-700 border-rose-300 dark:bg-rose-500/15 dark:border-rose-500/30 dark:text-rose-400',
      icon: AlertOctagon,
      label: 'High Risk',
    };
  } else if (normLevel === 'medium') {
    config = {
      bg: 'bg-amber-50 text-amber-800 border-amber-300 dark:bg-amber-500/15 dark:border-amber-500/30 dark:text-amber-400',
      icon: AlertTriangle,
      label: 'Medium Risk',
    };
  }

  const Icon = config.icon;

  const sizeClasses = {
    sm: 'text-xs px-2 py-0.5 gap-1',
    md: 'text-xs px-2.5 py-1 gap-1.5',
    lg: 'text-sm px-3.5 py-1.5 gap-2',
  }[size];

  const iconSizes = {
    sm: 'w-3 h-3',
    md: 'w-3.5 h-3.5',
    lg: 'w-4 h-4',
  }[size];

  return (
    <div className="inline-flex items-center gap-1.5">
      <span className={`inline-flex items-center font-semibold rounded-full border ${config.bg} ${sizeClasses}`}>
        <Icon className={`${iconSizes} shrink-0`} />
        <span>{config.label}</span>
        {showScore && score !== undefined && (
          <span className="opacity-80 font-mono ml-0.5">({score}/100)</span>
        )}
      </span>

      {needsReview && (
        <span
          className="inline-flex items-center gap-1 text-[11px] font-semibold px-2 py-0.5 rounded-full bg-blue-50 text-blue-700 border border-blue-300 dark:bg-blue-500/15 dark:border-blue-500/30 dark:text-blue-300"
          title="Low classifier confidence or ambiguous wording requires human verification"
        >
          <HelpCircle className="w-3 h-3 shrink-0 text-blue-600 dark:text-blue-400" />
          <span>Needs Review</span>
        </span>
      )}
    </div>
  );
};
