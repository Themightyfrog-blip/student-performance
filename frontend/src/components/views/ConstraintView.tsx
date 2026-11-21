"use client";

import React, { useState } from "react";
import { api } from "@/lib/api";
import { MetricCard } from "../ui/MetricCard";
import { Filter, Play, AlertCircle, HelpCircle } from "lucide-react";

export const ConstraintView: React.FC = () => {
  const [thresh, setThresh] = useState(75.0);
  const [minSup, setMinSup] = useState(0.05);
  const [minConf, setMinConf] = useState(0.30);
  const [minLift, setMinLift] = useState(1.0);
  const [results, setResults] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleRunConstraint = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await api.runConstraintMining({
        attendance_threshold: thresh,
        min_support: minSup,
        min_confidence: minConf,
        min_lift: minLift,
      });
      setResults(res);
    } catch (err: any) {
      setError(err.message || "Constraint-based mining failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-slate-900">
          Constraint-Based Association Mining (Question 65)
        </h2>
        <p className="mt-1 text-sm text-slate-500">
          Restrict association rule discovery to students with attendance below the mandatory threshold (default &lt; 75%). Correctly calculates and distinguishes <strong>Conditional Support</strong> from <strong>Global Support</strong>.
        </p>
      </div>

      {/* Threshold Controls Card */}
      <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <h3 className="text-sm font-bold text-slate-900 mb-4">
          Constraint & Pruning Parameters
        </h3>
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-4">
          <div>
            <div className="flex justify-between text-xs font-semibold text-slate-700">
              <span>Attendance Threshold</span>
              <span className="text-rose-600">&lt; {thresh}%</span>
            </div>
            <input
              type="range"
              min="50"
              max="85"
              step="1"
              value={thresh}
              onChange={(e) => setThresh(parseFloat(e.target.value))}
              className="w-full mt-2"
            />
            <p className="text-[11px] text-slate-400 mt-1">Filters cohort under this cutoff</p>
          </div>

          <div>
            <div className="flex justify-between text-xs font-semibold text-slate-700">
              <span>Min Conditional Support</span>
              <span className="text-brand-600">{(minSup * 100).toFixed(0)}%</span>
            </div>
            <input
              type="range"
              min="0.01"
              max="0.50"
              step="0.01"
              value={minSup}
              onChange={(e) => setMinSup(parseFloat(e.target.value))}
              className="w-full mt-2"
            />
            <p className="text-[11px] text-slate-400 mt-1">Within constrained subset</p>
          </div>

          <div>
            <div className="flex justify-between text-xs font-semibold text-slate-700">
              <span>Min Confidence</span>
              <span className="text-brand-600">{(minConf * 100).toFixed(0)}%</span>
            </div>
            <input
              type="range"
              min="0.10"
              max="0.90"
              step="0.05"
              value={minConf}
              onChange={(e) => setMinConf(parseFloat(e.target.value))}
              className="w-full mt-2"
            />
            <p className="text-[11px] text-slate-400 mt-1">Rule certainty cutoff</p>
          </div>

          <div className="flex flex-col justify-end">
            <button
              onClick={handleRunConstraint}
              disabled={loading}
              className="inline-flex items-center justify-center gap-2 rounded-lg bg-brand-600 px-5 py-2.5 text-xs font-semibold text-white shadow-sm hover:bg-brand-700 disabled:opacity-50"
            >
              <Filter className="h-4 w-4" />
              {loading ? "Filtering & Mining..." : "Mine Constrained Cohort"}
            </button>
          </div>
        </div>
      </div>

      {error && (
        <div className="flex items-center gap-2 rounded-xl border border-red-200 bg-red-50 p-4 text-xs text-red-800">
          <AlertCircle className="h-4 w-4 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Results View */}
      {results && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-4">
            <MetricCard
              label="Eligible Students"
              value={results.eligible_students}
              delta={`Of ${results.total_students_full} Total Students`}
              color="amber"
            />
            <MetricCard
              label="Constrained Records"
              value={results.eligible_records}
              delta={`${results.subset_percentage}% of Warehouse`}
              color="amber"
            />
            <MetricCard
              label="Transactions Mined"
              value={results.transactions_count}
              delta="Low Attendance Cohort"
              color="blue"
            />
            <MetricCard
              label="Rules Discovered"
              value={results.rules?.length || 0}
              delta="Question 65 Patterns"
              color="green"
            />
          </div>

          {/* Rules Table */}
          <div className="overflow-hidden rounded-xl border border-[#DDD0B5] bg-white shadow-xs">
            <div className="border-b border-[#EAE0CB] bg-[#FAF8F5] px-6 py-3 text-xs font-bold text-stone-900 flex items-center justify-between">
              <span>Discovered Rules in Constrained Cohort (Attendance &lt; {results.attendance_threshold}%)</span>
              <span className="font-normal text-stone-500">
                Formula: Global Support = Conditional Support × ({results.eligible_records} / {results.total_records_full})
              </span>
            </div>

            {results.rules?.length === 0 ? (
              <div className="p-8 text-center text-xs text-stone-500">
                No rules met the selected support and confidence thresholds in this cohort. Try lowering the support slider.
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-[#EAE0CB] text-left text-xs">
                  <thead className="bg-[#F5EFE6] text-stone-700">
                    <tr>
                      <th className="px-4 py-3 font-semibold">Association Rule</th>
                      <th className="px-4 py-3 font-semibold text-[#8B3103]">Conditional Support (Subset %)</th>
                      <th className="px-4 py-3 font-semibold text-stone-600">Global Support (Full Pop. %)</th>
                      <th className="px-4 py-3 font-semibold">Confidence (%)</th>
                      <th className="px-4 py-3 font-semibold">Lift Ratio</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-stone-100 bg-white">
                    {results.rules.map((r: any, idx: number) => (
                      <tr key={idx} className="hover:bg-[#FAF8F5]">
                        <td className="px-4 py-3 font-mono font-medium text-stone-900">
                          {r.rule_representation}
                        </td>
                        <td className="px-4 py-3 font-bold text-[#8B3103]">
                          {r.conditional_support_pct}%
                        </td>
                        <td className="px-4 py-3 font-semibold text-stone-600">
                          {r.global_support_pct}%
                        </td>
                        <td className="px-4 py-3 text-stone-700 font-semibold">
                          {r.confidence_pct}%
                        </td>
                        <td className="px-4 py-3 font-bold text-stone-800">{r.lift}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
