import React from 'react';

interface StatsCardProps {
  icon: string;
  label: string;
  value: string | number;
  change?: number;
  changeType?: 'positive' | 'negative' | 'neutral';
  subtext?: string;
  color?: 'primary' | 'success' | 'warning' | 'danger' | 'info';
}

export const StatsCard: React.FC<StatsCardProps> = ({
  icon,
  label,
  value,
  change,
  changeType = 'neutral',
  subtext,
  color = 'primary',
}) => {
  // Minimal black/white color scheme
  const colorClasses = {
    primary: 'bg-white border-black/20 dark:bg-slate-900 dark:border-white/10',
    success: 'bg-white border-black/20 dark:bg-slate-900 dark:border-white/10',
    warning: 'bg-white border-black/20 dark:bg-slate-900 dark:border-white/10',
    danger: 'bg-white border-black/20 dark:bg-slate-900 dark:border-white/10',
    info: 'bg-white border-black/20 dark:bg-slate-900 dark:border-white/10',
  };

  const iconColorClasses = {
    primary: 'text-black dark:text-white',
    success: 'text-black dark:text-white',
    warning: 'text-black dark:text-white',
    danger: 'text-black dark:text-white',
    info: 'text-black dark:text-white',
  };

  const changeColorClasses = {
    positive: 'text-black dark:text-white bg-gray-100 dark:bg-gray-800 border border-black/10 dark:border-white/10',
    negative: 'text-black dark:text-white bg-gray-100 dark:bg-gray-800 border border-black/10 dark:border-white/10',
    neutral: 'text-black/60 dark:text-white/60 bg-gray-100 dark:bg-gray-800 border border-black/10 dark:border-white/10',
  };

  return (
    <div className={`rounded-lg border-2 p-4 ${colorClasses[color]} transition-all duration-200 hover:shadow-md`}>
      {/* Header with icon and optional change */}
      <div className="flex items-start justify-between mb-3">
        <div className={`text-2xl ${iconColorClasses[color]}`}>
          <span className={`fa-solid ${icon}`} />
        </div>
        {change !== undefined && (
          <div className={`flex items-center gap-1 px-2 py-1 rounded text-sm font-semibold ${changeColorClasses[changeType]}`}>
            <span className={`fa-solid ${changeType === 'positive' ? 'fa-arrow-up' : changeType === 'negative' ? 'fa-arrow-down' : 'fa-minus'}`} />
            <span>{Math.abs(change)}%</span>
          </div>
        )}
      </div>

      {/* Label */}
      <p className="text-sm font-medium text-black/60 dark:text-white/60 mb-1">{label}</p>

      {/* Value */}
      <h3 className="text-2xl font-bold text-black dark:text-white mb-1">{value}</h3>

      {/* Subtext */}
      {subtext && <p className="text-xs text-black/40 dark:text-white/40">{subtext}</p>}
    </div>
  );
};
