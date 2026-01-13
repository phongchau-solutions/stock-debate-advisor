import React from 'react';

interface ChartData {
  label: string;
  value: number;
  color: string;
}

interface BarChartProps {
  title: string;
  data: ChartData[];
  height?: number;
}

interface ConfidenceChartProps {
  title: string;
  average: number;
  distribution: {
    high: number;    // 80-100%
    medium: number;  // 50-79%
    low: number;     // 0-49%
  };
}

export const BarChart: React.FC<BarChartProps> = ({ title, data, height = 250 }) => {
  const maxValue = Math.max(...data.map((d) => d.value));

  return (
    <div className="rounded-lg border-2 border-black/20 dark:border-white/10 bg-white dark:bg-slate-900 p-4">
      <h3 className="font-semibold text-sm text-black dark:text-white mb-4">{title}</h3>
      <div style={{ height: `${height}px` }} className="flex items-end justify-between gap-2">
        {data.map((item, idx) => {
          const percentage = (item.value / maxValue) * 100;
          return (
            <div key={idx} className="flex-1 flex flex-col items-center gap-2">
              <div className="w-full flex flex-col items-end">
                <div
                  className={`w-full rounded-t-md transition-all duration-300 hover:opacity-80 ${item.color}`}
                  style={{ height: `${Math.max(percentage, 5)}%` }}
                  title={`${item.label}: ${item.value}`}
                />
              </div>
              <p className="text-xs text-black/40 dark:text-white/40 text-center font-medium">{item.label}</p>
              <p className="text-sm font-bold text-black dark:text-white">{item.value}</p>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export const ConfidenceChart: React.FC<ConfidenceChartProps> = ({ title, average, distribution }) => {
  const total = distribution.high + distribution.medium + distribution.low;
  const highPct = total > 0 ? Math.round((distribution.high / total) * 100) : 0;
  const mediumPct = total > 0 ? Math.round((distribution.medium / total) * 100) : 0;
  const lowPct = total > 0 ? Math.round((distribution.low / total) * 100) : 0;

  return (
    <div className="rounded-lg border-2 border-black/20 dark:border-white/10 bg-white dark:bg-slate-900 p-4">
      <h3 className="font-semibold text-sm text-black dark:text-white mb-4">{title}</h3>

      {/* Average Confidence */}
      <div className="mb-4 p-3 rounded-md bg-gray-100 dark:bg-gray-800 border-2 border-black/20 dark:border-white/10">
        <p className="text-xs text-black/60 dark:text-white/60 mb-1">Average Confidence Score</p>
        <p className="text-3xl font-bold text-black dark:text-white">{average}%</p>
      </div>

      {/* Distribution Bars */}
      <div className="space-y-2">
        {/* High Confidence */}
        <div>
          <div className="flex items-center justify-between mb-1">
            <p className="text-xs font-medium text-black/60 dark:text-white/60">High (80-100%)</p>
            <p className="text-sm font-bold text-black dark:text-white">{distribution.high}</p>
          </div>
          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
            <div className="h-2 bg-black dark:bg-white rounded-full" style={{ width: `${highPct}%` }} />
          </div>
        </div>

        {/* Medium Confidence */}
        <div>
          <div className="flex items-center justify-between mb-1">
            <p className="text-xs font-medium text-black/60 dark:text-white/60">Medium (50-79%)</p>
            <p className="text-sm font-bold text-black dark:text-white">{distribution.medium}</p>
          </div>
          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
            <div className="h-2 bg-gray-500 dark:bg-gray-400 rounded-full" style={{ width: `${mediumPct}%` }} />
          </div>
        </div>

        {/* Low Confidence */}
        <div>
          <div className="flex items-center justify-between mb-1">
            <p className="text-xs font-medium text-black/60 dark:text-white/60">Low (0-49%)</p>
            <p className="text-sm font-bold text-black dark:text-white">{distribution.low}</p>
          </div>
          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
            <div className="h-2 bg-gray-400 dark:bg-gray-500 rounded-full" style={{ width: `${lowPct}%` }} />
          </div>
        </div>
      </div>
    </div>
  );
};

export const LineChart: React.FC<{
  title: string;
  data: Array<{ label: string; value: number }>;
}> = ({ title, data }) => {
  const maxValue = Math.max(...data.map((d) => d.value));
  const minValue = Math.min(...data.map((d) => d.value));
  const range = maxValue - minValue || 1;

  return (
    <div className="rounded-lg border-2 border-black/20 dark:border-white/10 bg-white dark:bg-slate-900 p-4">
      <h3 className="font-semibold text-sm text-black dark:text-white mb-4">{title}</h3>
      <div className="flex items-end justify-between gap-1 h-48">
        {data.map((item, idx) => {
          const normalized = (item.value - minValue) / range;
          const height = Math.max(normalized * 100, 5);

          return (
            <div
              key={idx}
              className="flex-1 flex flex-col items-center"
              title={`${item.label}: ${item.value}`}
            >
              <div
                className="w-full bg-black dark:bg-white rounded-t-sm opacity-60 hover:opacity-100 transition-opacity"
                style={{ height: `${height}%` }}
              />
              <p className="text-xs text-black/40 dark:text-white/40 mt-2 text-center truncate max-w-full">{item.label}</p>
            </div>
          );
        })}
      </div>
    </div>
  );
};
