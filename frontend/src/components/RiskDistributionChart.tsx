import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';
import { useTheme } from '../context/ThemeContext';

interface Props {
  high: number;
  medium: number;
  low: number;
  needsReview?: number;
}

const COLORS = {
  High: '#dc2626',
  Medium: '#d97706',
  Low: '#16a34a',
};

export const RiskDistributionChart: React.FC<Props> = ({ high, medium, low }) => {
  const { theme } = useTheme();
  const isDark = theme === 'dark';

  const data = [
    { name: 'High Risk', value: high, color: COLORS.High },
    { name: 'Medium Risk', value: medium, color: COLORS.Medium },
    { name: 'Low Risk', value: low, color: COLORS.Low },
  ].filter((d) => d.value > 0);

  if (data.length === 0) {
    return (
      <div className="h-44 flex items-center justify-center text-xs text-beige-500 dark:text-slate-500">
        No clause risk data available
      </div>
    );
  }

  return (
    <div className="h-44 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            innerRadius={42}
            outerRadius={65}
            paddingAngle={4}
            dataKey="value"
          >
            {data.map((entry, index) => (
              <Cell
                key={`cell-${index}`}
                fill={entry.color}
                stroke={isDark ? '#0f172a' : '#ffffff'}
                strokeWidth={2}
              />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{
              backgroundColor: isDark ? '#0f172a' : '#ffffff',
              borderColor: isDark ? '#334155' : '#e6dfd3',
              borderRadius: '0.75rem',
              color: isDark ? '#f8fafc' : '#231f19',
              fontSize: '12px',
              boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
            }}
          />
          <Legend
            verticalAlign="bottom"
            height={28}
            iconType="circle"
            formatter={(value) => (
              <span className="text-xs font-medium text-beige-700 dark:text-slate-300 ml-1">
                {value}
              </span>
            )}
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
};
