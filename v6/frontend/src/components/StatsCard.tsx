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
  const colorClasses = {
    primary: 'bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 border-blue-200 dark:border-blue-700/50',
    success: 'bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20 border-green-200 dark:border-green-700/50',
    warning: 'bg-gradient-to-br from-yellow-50 to-yellow-100 dark:from-yellow-900/20 dark:to-yellow-800/20 border-yellow-200 dark:border-yellow-700/50',
    danger: 'bg-gradient-to-br from-red-50 to-red-100 dark:from-red-900/20 dark:to-red-800/20 border-red-200 dark:border-red-700/50',
    info: 'bg-gradient-to-br from-cyan-50 to-cyan-100 dark:from-cyan-900/20 dark:to-cyan-800/20 border-cyan-200 dark:border-cyan-700/50',
  };

  const iconColorClasses = {
    primary: 'text-blue-600 dark:text-blue-400',
    success: 'text-green-600 dark:text-green-400',
    warning: 'text-yellow-600 dark:text-yellow-400',
    danger: 'text-red-600 dark:text-red-400',
    info: 'text-cyan-600 dark:text-cyan-400',
  };

  const changeColorClasses = {
    positive: 'text-green-600 dark:text-green-400 bg-green-50 dark:bg-green-900/20',
    negative: 'text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-900/20',
    neutral: 'text-gray-600 dark:text-gray-400 bg-gray-50 dark:bg-gray-900/20',
  };

  return (
    <div className={`rounded-lg border p-4 ${colorClasses[color]} transition-all duration-200 hover:shadow-md`}>
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
      <p className="text-sm font-medium text-muted-foreground mb-1">{label}</p>

      {/* Value */}
      <h3 className="text-2xl font-bold text-foreground mb-1">{value}</h3>

      {/* Subtext */}
      {subtext && <p className="text-xs text-muted-foreground">{subtext}</p>}
    </div>
  );
};
