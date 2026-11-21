"use client";

import React, { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { MetricCard } from "../ui/MetricCard";
import { TrendingUp, AlertCircle, Info, Grid } from "lucide-react";

export const CorrelationView: React.FC = () => {
  const [corr, setCorr] = useState<any>(null);
  const [matrixData, setMatrixData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        const [cRes, mRes] = await Promise.all([
          api.analyzeCorrelation(),
          api.getCorrelationMatrix(),
        ]);
        setCorr(cRes);
        setMatrixData(mRes);
      } catch (err: any) {
        setError(err.message || "Failed to compute correlation.");
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="flex h-64 items-center justify-center text-stone-500">
        <div className="h-6 w-6 animate-spin rounded-full border-2 border-[#8B3103] border-t-transparent mr-2" />
        Running SciPy Statistical Correlation Analysis...
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center gap-2 rounded-xl border border-amber-200 bg-amber-50 p-6 text-sm text-amber-800">
        <AlertCircle className="h-5 w-5 flex-shrink-0" />
        <span>{error}</span>
      </div>
    );
  }

  const points = corr?.scatter_points || [];

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-stone-900">
          Statistical Correlation Analysis (Question 68)
        </h2>
        <p className="mt-1 text-sm text-stone-500">
          Evaluate linear and monotonic relationships between attendance and examination performance using SciPy Pearson $r$, Spearman rank correlation $\rho$, exact $p$-values, and ordinary least squares linear regression.
        </p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-4">
        <MetricCard
          label="Pearson Correlation (r)"
          value={corr.pearson_r.toFixed(3)}
          delta={`${corr.strength} ${corr.direction}`}
          color="rust"
          icon={<TrendingUp className="h-5 w-5" />}
        />
        <MetricCard
          label="Pearson p-Value"
          value={corr.pearson_p_value < 0.001 ? "< 0.001" : corr.pearson_p_value.toExponential(2)}
          delta={corr.pearson_p_value < 0.05 ? "Statistically Significant (p < 0.05)" : "Not Significant"}
          color="green"
        />
        <MetricCard
          label="Spearman Rank (ρ)"
          value={corr.spearman_rho.toFixed(3)}
          delta="Monotonic Relationship"
          color="rust"
        />
        <MetricCard
          label="Regression R²"
          value={corr.trendline_r2.toFixed(3)}
          delta={`Slope: ${corr.slope.toFixed(2)} | Intercept: ${corr.intercept.toFixed(1)}`}
          color="pearl"
        />
      </div>

      {/* Academic Finding Callout */}
      <div className="flex items-start gap-3 rounded-xl border border-[#DDD0B5] bg-[#FAF8F5] p-4 text-xs text-stone-800">
        <Info className="h-5 w-5 text-[#8B3103] flex-shrink-0 mt-0.5" />
        <div>
          <span className="font-bold text-[#8B3103]">Statistical Finding:</span> {corr.interpretation}
        </div>
      </div>

      {/* Scatter Plot with Regression Trendline */}
      <div className="rounded-xl border border-[#DDD0B5] bg-white p-6 shadow-xs">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-sm font-bold text-stone-900">
              Attendance (%) vs Final Exam Score Scatter Plot
            </h3>
            <p className="text-xs text-stone-500">
              Fitted OLS Line: Marks = {corr.slope.toFixed(2)} × Attendance + {corr.intercept.toFixed(1)} (R² = {corr.trendline_r2.toFixed(3)})
            </p>
          </div>
          <span className="rounded bg-[#FAECE2] px-2.5 py-1 text-xs font-bold text-[#8B3103] border border-[#EAE0CB]">
            {corr.observations} Paired Student Observations
          </span>
        </div>

        {/* Responsive SVG Scatter Plot with Deep Rust dots and regression line */}
        <div className="relative h-72 w-full border border-[#EAE0CB] rounded-lg bg-[#FAF8F5]/80 p-2">
          <svg className="h-full w-full overflow-visible" viewBox="0 0 500 250">
            {/* Grid lines */}
            <line x1="40" y1="210" x2="480" y2="210" stroke="#DDD0B5" strokeWidth="1" />
            <line x1="40" y1="20" x2="40" y2="210" stroke="#DDD0B5" strokeWidth="1" />

            {/* X-axis labels */}
            <text x="40" y="225" fontSize="10" fill="#7A6B4D" textAnchor="middle">0%</text>
            <text x="150" y="225" fontSize="10" fill="#7A6B4D" textAnchor="middle">25%</text>
            <text x="260" y="225" fontSize="10" fill="#7A6B4D" textAnchor="middle">50%</text>
            <text x="370" y="225" fontSize="10" fill="#8B3103" fontWeight="bold" textAnchor="middle">75% (Min)</text>
            <text x="480" y="225" fontSize="10" fill="#7A6B4D" textAnchor="middle">100%</text>

            {/* Y-axis labels */}
            <text x="32" y="210" fontSize="10" fill="#7A6B4D" textAnchor="end">0</text>
            <text x="32" y="115" fontSize="10" fill="#7A6B4D" textAnchor="end">50</text>
            <text x="32" y="25" fontSize="10" fill="#7A6B4D" textAnchor="end">100</text>

            {/* Scatter dots in Deep Rust (#8B3103) */}
            {points.map((pt: any, i: number) => {
              const cx = 40 + (pt.AttendancePercentage / 100) * 440;
              const cy = 210 - (pt.MarksObtained / 100) * 190;
              return (
                <circle
                  key={i}
                  cx={cx}
                  cy={cy}
                  r="3.5"
                  fill="#8B3103"
                  opacity="0.65"
                  className="transition hover:opacity-100 hover:r-5"
                >
                  <title>{`Attendance: ${pt.AttendancePercentage}%, Marks: ${pt.MarksObtained}`}</title>
                </circle>
              );
            })}

            {/* Fitted Regression Line in Rust Accent */}
            {(() => {
              const y1 = Math.max(0, Math.min(100, corr.intercept));
              const y2 = Math.max(0, Math.min(100, corr.slope * 100 + corr.intercept));
              const svgY1 = 210 - (y1 / 100) * 190;
              const svgY2 = 210 - (y2 / 100) * 190;
              return (
                <line
                  x1="40"
                  y1={svgY1}
                  x2="480"
                  y2={svgY2}
                  stroke="#5D1F02"
                  strokeWidth="2.5"
                  strokeDasharray="4 2"
                />
              );
            })()}
          </svg>
        </div>
      </div>

      {/* Multivariable Pairwise Pearson Correlation Heatmap */}
      {matrixData && (
        <div className="rounded-xl border border-[#DDD0B5] bg-white p-6 shadow-xs">
          <div className="flex items-center gap-2 mb-4">
            <Grid className="h-5 w-5 text-[#8B3103]" />
            <h3 className="text-sm font-bold text-stone-900">
              Numeric Academic Variable Correlation Heatmap
            </h3>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full text-center text-xs">
              <thead>
                <tr>
                  <th className="p-2 text-left text-stone-400">Variable</th>
                  {matrixData.columns.map((col: string) => (
                    <th key={col} className="p-2 font-mono text-[11px] text-stone-700 bg-[#FAF8F5] rounded border border-[#EAE0CB]">
                      {col}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {matrixData.columns.map((rowCol: string) => (
                  <tr key={rowCol}>
                    <td className="p-2 text-left font-mono font-semibold text-stone-800 bg-[#FAF8F5] rounded border border-[#EAE0CB]">
                      {rowCol}
                    </td>
                    {matrixData.columns.map((colCol: string) => {
                      const val = matrixData.matrix[rowCol]?.[colCol] ?? 0;
                      let bg = "bg-white text-stone-700";
                      if (val > 0.6) bg = "bg-[#8B3103] text-[#FAF8F5] font-bold";
                      else if (val > 0.3) bg = "bg-[#BD4809]/20 text-[#5D1F02] font-semibold";
                      else if (val < -0.3) bg = "bg-rose-100 text-rose-800";
                      else if (val < 0) bg = "bg-rose-50 text-rose-700";

                      return (
                        <td key={colCol} className={`p-2.5 font-mono text-xs rounded border border-[#EAE0CB]/40 ${bg}`}>
                          {val.toFixed(2)}
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
