"use client";

import React, { useState } from "react";
import { api } from "@/lib/api";
import { MetricCard } from "../ui/MetricCard";
import {
  ShieldCheck,
  Play,
  AlertCircle,
  Binary,
  Layers,
  ChevronDown,
  ChevronUp,
} from "lucide-react";

export const ClassifierView: React.FC = () => {
  const [maxDepth, setMaxDepth] = useState(4);
  const [minSplit, setMinSplit] = useState(8);
  const [criterion, setCriterion] = useState("gini");
  const [metrics, setMetrics] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showTreeRules, setShowTreeRules] = useState(false);

  const handleTrain = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await api.trainDecisionTree({
        max_depth: maxDepth,
        min_samples_split: minSplit,
        criterion: criterion,
      });
      setMetrics(res);
    } catch (err: any) {
      setError(err.message || "Decision tree training failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-slate-900">
          Decision Tree Risk Classifier (Question 67)
        </h2>
        <p className="mt-1 text-sm text-slate-500">
          Supervised machine learning model classifying academic risk (<strong>Pass</strong>, <strong>Fail</strong>, <strong>At-Risk</strong>) with strict zero-target-leakage safeguards and student-grouped validation.
        </p>
      </div>

      {/* Target Leakage Guarantee Badge */}
      <div className="flex items-center gap-3 rounded-xl border border-emerald-200 bg-emerald-50/70 p-4 text-xs text-emerald-900">
        <ShieldCheck className="h-6 w-6 text-emerald-600 flex-shrink-0" />
        <div>
          <span className="font-bold">Strict Zero-Target-Leakage Guarantee:</span>{" "}
          Predictive features are strictly constrained to pre-examination indicators (<code>AttendancePercentage</code>, <code>InternalMarks</code>, <code>PreviousGPA</code>, <code>BacklogCount</code>, <code>Department</code>). Final exam marks, grades, and outcome status are strictly prohibited from the feature matrix.
        </div>
      </div>

      {/* Hyperparameter Controls */}
      <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <h3 className="text-sm font-bold text-slate-900 mb-4">
          Model Hyperparameter Tuning
        </h3>
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-4">
          <div>
            <div className="flex justify-between text-xs font-semibold text-slate-700">
              <span>Tree Maximum Depth</span>
              <span className="text-brand-600">{maxDepth}</span>
            </div>
            <input
              type="range"
              min="2"
              max="7"
              step="1"
              value={maxDepth}
              onChange={(e) => setMaxDepth(parseInt(e.target.value))}
              className="w-full mt-2"
            />
            <p className="text-[11px] text-slate-400 mt-1">Controls model complexity & pruning</p>
          </div>

          <div>
            <div className="flex justify-between text-xs font-semibold text-slate-700">
              <span>Min Samples Split</span>
              <span className="text-brand-600">{minSplit}</span>
            </div>
            <input
              type="range"
              min="2"
              max="20"
              step="1"
              value={minSplit}
              onChange={(e) => setMinSplit(parseInt(e.target.value))}
              className="w-full mt-2"
            />
            <p className="text-[11px] text-slate-400 mt-1">Minimum node samples to branch</p>
          </div>

          <div>
            <label className="text-xs font-semibold text-slate-700 block mb-1">
              Splitting Criterion
            </label>
            <select
              value={criterion}
              onChange={(e) => setCriterion(e.target.value)}
              className="w-full rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-xs text-slate-800 shadow-sm focus:border-brand-500 focus:outline-none"
            >
              <option value="gini">Gini Impurity</option>
              <option value="entropy">Information Gain (Entropy)</option>
            </select>
            <p className="text-[11px] text-slate-400 mt-1">Node impurity function</p>
          </div>

          <div className="flex flex-col justify-end">
            <button
              onClick={handleTrain}
              disabled={loading}
              className="inline-flex items-center justify-center gap-2 rounded-lg bg-brand-600 px-5 py-2.5 text-xs font-semibold text-white shadow-sm hover:bg-brand-700 disabled:opacity-50"
            >
              <Play className="h-4 w-4" />
              {loading ? "Training Decision Tree..." : "Train & Evaluate Classifier"}
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

      {/* Model Performance Results */}
      {metrics && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-4">
            <MetricCard
              label="Overall Test Accuracy"
              value={`${(metrics.accuracy * 100).toFixed(1)}%`}
              delta="Holdout Student Group Evaluation"
              color="green"
            />
            <MetricCard
              label="Macro F1-Score"
              value={`${(metrics.macro_f1 * 100).toFixed(1)}%`}
              delta="Harmonic Mean of Precision/Recall"
              color="blue"
            />
            <MetricCard
              label="Training Samples"
              value={metrics.train_samples}
              delta="GroupShuffleSplit (75%)"
              color="slate"
            />
            <MetricCard
              label="Test Samples"
              value={metrics.test_samples}
              delta="Zero Patient/Student Leakage (25%)"
              color="slate"
            />
          </div>

          {/* Confusion Matrix and Feature Importance */}
          <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
            {/* Confusion Matrix */}
            <div className="rounded-xl border border-[#DDD0B5] bg-white p-6 shadow-xs">
              <h3 className="text-sm font-bold text-stone-900 mb-1">
                Confusion Matrix (Holdout Test Set)
              </h3>
              <p className="text-xs text-stone-500 mb-4">
                Rows = True Classes, Columns = Model Predictions
              </p>
              <div className="overflow-x-auto">
                <table className="min-w-full text-center text-xs">
                  <thead>
                    <tr>
                      <th className="p-2 text-left text-stone-400">Actual \ Predicted</th>
                      {metrics.target_classes.map((cls: string) => (
                        <th key={cls} className="p-2 font-bold text-stone-700 bg-[#FAF8F5] border border-[#EAE0CB] rounded">
                          {cls}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {metrics.confusion_matrix.map((row: number[], rowIdx: number) => (
                      <tr key={rowIdx}>
                        <td className="p-2 text-left font-semibold text-stone-700 bg-[#FAF8F5] border border-[#EAE0CB] rounded">
                          {metrics.target_classes[rowIdx]}
                        </td>
                        {row.map((val: number, colIdx: number) => {
                          const isDiagonal = rowIdx === colIdx;
                          return (
                            <td
                              key={colIdx}
                              className={`p-3 font-bold text-sm ${
                                isDiagonal
                                  ? "bg-[#8B3103] text-[#FAF8F5] rounded"
                                  : val > 0
                                  ? "bg-rose-50 text-rose-700"
                                  : "text-stone-300"
                              }`}
                            >
                              {val}
                            </td>
                          );
                        })}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Feature Importances */}
            <div className="rounded-xl border border-[#DDD0B5] bg-white p-6 shadow-xs">
              <h3 className="text-sm font-bold text-stone-900 mb-1">
                Predictive Feature Importances
              </h3>
              <p className="text-xs text-stone-500 mb-4">
                Relative Gini/Entropy variance reduction contribution
              </p>
              <div className="space-y-3">
                {metrics.feature_importances.map((f: any) => (
                  <div key={f.Feature} className="space-y-1">
                    <div className="flex justify-between text-xs font-medium">
                      <span className="font-mono text-stone-700">{f.Feature}</span>
                      <span className="font-bold text-[#8B3103]">
                        {(f.Importance * 100).toFixed(1)}%
                      </span>
                    </div>
                    <div className="h-2 w-full overflow-hidden rounded-full bg-[#FAF8F5] border border-[#EAE0CB]/50">
                      <div
                        className="h-full rounded-full bg-[#8B3103]"
                        style={{ width: `${Math.max(f.Importance * 100, 2)}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Per-Class Metrics */}
          <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
            <div className="border-b border-slate-200 bg-slate-50 px-6 py-3 font-bold text-xs text-slate-800">
              Per-Class Validation Performance (Precision, Recall, F1)
            </div>
            <table className="min-w-full divide-y divide-slate-200 text-left text-xs">
              <thead className="bg-slate-100 text-slate-700">
                <tr>
                  <th className="px-4 py-2.5 font-semibold">Target Risk Class</th>
                  <th className="px-4 py-2.5 font-semibold">Precision</th>
                  <th className="px-4 py-2.5 font-semibold">Recall</th>
                  <th className="px-4 py-2.5 font-semibold">F1-Score</th>
                  <th className="px-4 py-2.5 font-semibold">Test Sample Support</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 bg-white">
                {metrics.per_class_metrics.map((c: any) => (
                  <tr key={c.Class} className="hover:bg-slate-50">
                    <td className="px-4 py-2.5 font-bold text-slate-900">{c.Class}</td>
                    <td className="px-4 py-2.5 text-slate-700">{c.Precision}</td>
                    <td className="px-4 py-2.5 text-slate-700">{c.Recall}</td>
                    <td className="px-4 py-2.5 font-semibold text-brand-600">{c.F1_Score}</td>
                    <td className="px-4 py-2.5 text-slate-600">{c.Support}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Decision Tree Text Rules */}
          <div className="rounded-xl border border-slate-200 bg-white shadow-sm">
            <button
              onClick={() => setShowTreeRules(!showTreeRules)}
              className="flex w-full items-center justify-between p-4 text-xs font-bold text-slate-800 hover:bg-slate-50"
            >
              <span>🌲 View Interpretable Decision Tree Split Logic</span>
              {showTreeRules ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
            </button>
            {showTreeRules && (
              <div className="border-t border-slate-200 bg-slate-900 p-4 rounded-b-xl overflow-x-auto text-[11px] font-mono text-emerald-400">
                <pre>{metrics.tree_rules_text}</pre>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
