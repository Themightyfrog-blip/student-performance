"use client";

import React, { useState } from "react";
import { api } from "@/lib/api";
import { GitBranch, Play, AlertCircle, HelpCircle } from "lucide-react";

export const MiningView: React.FC = () => {
  const [sup1, setSup1] = useState(0.05);
  const [conf1, setConf1] = useState(0.30);
  const [sup2, setSup2] = useState(0.02);
  const [conf2, setConf2] = useState(0.30);
  const [lift, setLift] = useState(1.0);
  const [results, setResults] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<"lvl1" | "lvl2">("lvl1");

  const handleRunMining = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await api.runMultiLevelMining({
        min_support_lvl1: sup1,
        min_confidence_lvl1: conf1,
        min_support_lvl2: sup2,
        min_confidence_lvl2: conf2,
        min_lift: lift,
      });
      setResults(res);
    } catch (err: any) {
      setError(err.message || "Association mining execution failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-slate-900">
          Multi-Level Association Rule Mining (Question 69)
        </h2>
        <p className="mt-1 text-sm text-slate-500">
          Discover frequent academic co-occurrences across concept hierarchies: Level 1 (Department $\rightarrow$ Result Status) and Level 2 (Subject Code $\rightarrow$ Letter Grade) using Apriori.
        </p>
      </div>

      {/* Control Sliders */}
      <div className="rounded-xl border border-[#DDD0B5] bg-white p-6 shadow-xs">
        <h3 className="text-sm font-bold text-stone-900 mb-4">
          Mining Threshold Parameters
        </h3>
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-3">
          <div className="space-y-3">
            <div>
              <div className="flex justify-between text-xs font-semibold text-stone-700">
                <span>Min Support (Level 1 - Dept)</span>
                <span className="text-[#8B3103] font-bold">{(sup1 * 100).toFixed(0)}%</span>
              </div>
              <input
                type="range"
                min="0.01"
                max="0.40"
                step="0.01"
                value={sup1}
                onChange={(e) => setSup1(parseFloat(e.target.value))}
                className="w-full mt-1.5 accent-[#8B3103]"
              />
            </div>
            <div>
              <div className="flex justify-between text-xs font-semibold text-stone-700">
                <span>Min Support (Level 2 - Subject)</span>
                <span className="text-[#8B3103] font-bold">{(sup2 * 100).toFixed(1)}%</span>
              </div>
              <input
                type="range"
                min="0.005"
                max="0.20"
                step="0.005"
                value={sup2}
                onChange={(e) => setSup2(parseFloat(e.target.value))}
                className="w-full mt-1.5 accent-[#8B3103]"
              />
            </div>
          </div>

          <div className="space-y-3">
            <div>
              <div className="flex justify-between text-xs font-semibold text-stone-700">
                <span>Min Confidence (Level 1)</span>
                <span className="text-[#8B3103] font-bold">{(conf1 * 100).toFixed(0)}%</span>
              </div>
              <input
                type="range"
                min="0.1"
                max="0.9"
                step="0.05"
                value={conf1}
                onChange={(e) => setConf1(parseFloat(e.target.value))}
                className="w-full mt-1.5 accent-[#8B3103]"
              />
            </div>
            <div>
              <div className="flex justify-between text-xs font-semibold text-stone-700">
                <span>Min Confidence (Level 2)</span>
                <span className="text-[#8B3103] font-bold">{(conf2 * 100).toFixed(0)}%</span>
              </div>
              <input
                type="range"
                min="0.1"
                max="0.9"
                step="0.05"
                value={conf2}
                onChange={(e) => setConf2(parseFloat(e.target.value))}
                className="w-full mt-1.5 accent-[#8B3103]"
              />
            </div>
          </div>

          <div className="flex flex-col justify-between">
            <div>
              <div className="flex justify-between text-xs font-semibold text-stone-700">
                <span>Min Lift Ratio</span>
                <span className="text-[#8B3103] font-bold">{lift.toFixed(1)}x</span>
              </div>
              <input
                type="range"
                min="1.0"
                max="4.0"
                step="0.1"
                value={lift}
                onChange={(e) => setLift(parseFloat(e.target.value))}
                className="w-full mt-1.5 accent-[#8B3103]"
              />
            </div>
            <button
              onClick={handleRunMining}
              disabled={loading}
              className="mt-4 inline-flex items-center justify-center gap-2 rounded-lg bg-brand-600 px-5 py-2.5 text-xs font-semibold text-white shadow-xs hover:bg-brand-700 disabled:opacity-50 transition"
            >
              <Play className="h-4 w-4" />
              {loading ? "Mining Transactions..." : "Run Multi-Level Apriori"}
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

      {/* Rules Tabs */}
      {results && (
        <div className="space-y-4">
          <div className="flex border-b border-[#EAE0CB]">
            <button
              onClick={() => setActiveTab("lvl1")}
              className={`border-b-2 px-4 py-2.5 text-xs font-semibold transition ${
                activeTab === "lvl1"
                  ? "border-[#8B3103] text-[#8B3103] font-bold"
                  : "border-transparent text-stone-500 hover:text-[#8B3103]"
              }`}
            >
              🏛️ Level 1: Department → Result Status ({results.level1?.rules?.length || 0} Rules)
            </button>
            <button
              onClick={() => setActiveTab("lvl2")}
              className={`border-b-2 px-4 py-2.5 text-xs font-semibold transition ${
                activeTab === "lvl2"
                  ? "border-[#8B3103] text-[#8B3103] font-bold"
                  : "border-transparent text-stone-500 hover:text-[#8B3103]"
              }`}
            >
              📚 Level 2: Subject Code → Letter Grade ({results.level2?.rules?.length || 0} Rules)
            </button>
          </div>

          {activeTab === "lvl1" && (
            <div className="overflow-hidden rounded-xl border border-[#DDD0B5] bg-white shadow-xs">
              <div className="border-b border-[#EAE0CB] bg-[#FAF8F5] px-6 py-3 text-xs text-stone-700 flex justify-between">
                <span>Concept Hierarchy: <strong>University → Department → Result Status</strong></span>
                <span>Transactions Mined: <strong>{results.level1.transaction_count}</strong></span>
              </div>
              {results.level1?.rules?.length === 0 ? (
                <div className="p-8 text-center text-xs text-stone-500">
                  No rules met the support and confidence threshold. Try lowering the support slider.
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-[#EAE0CB] text-left text-xs">
                    <thead className="bg-[#F5EFE6] text-stone-700">
                      <tr>
                        <th className="px-4 py-3 font-semibold">Association Rule (Antecedent ⇒ Consequent)</th>
                        <th className="px-4 py-3 font-semibold">Support (%)</th>
                        <th className="px-4 py-3 font-semibold">Confidence (%)</th>
                        <th className="px-4 py-3 font-semibold text-[#8B3103]">Lift Ratio</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-[#EAE0CB] bg-white">
                      {results.level1.rules.map((r: any, idx: number) => (
                        <tr key={idx} className="hover:bg-[#FAF8F5]">
                          <td className="px-4 py-3 font-mono font-medium text-stone-900">
                            {r.rule_representation}
                          </td>
                          <td className="px-4 py-3 text-stone-700 font-semibold">{r.support_pct}%</td>
                          <td className="px-4 py-3 text-stone-700 font-semibold">{r.confidence_pct}%</td>
                          <td className="px-4 py-3 text-[#8B3103] font-bold">{r.lift}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}

          {activeTab === "lvl2" && (
            <div className="overflow-hidden rounded-xl border border-[#DDD0B5] bg-white shadow-xs">
              <div className="border-b border-[#EAE0CB] bg-[#FAF8F5] px-6 py-3 text-xs text-stone-700 flex justify-between">
                <span>Concept Hierarchy: <strong>Department → Subject Code → Letter Grade</strong></span>
                <span>Transactions Mined: <strong>{results.level2.transaction_count}</strong></span>
              </div>
              {results.level2?.rules?.length === 0 ? (
                <div className="p-8 text-center text-xs text-stone-500">
                  No rules met the support and confidence threshold. Try lowering the support slider.
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-[#EAE0CB] text-left text-xs">
                    <thead className="bg-[#F5EFE6] text-stone-700">
                      <tr>
                        <th className="px-4 py-3 font-semibold">Association Rule (Antecedent ⇒ Consequent)</th>
                        <th className="px-4 py-3 font-semibold">Support (%)</th>
                        <th className="px-4 py-3 font-semibold">Confidence (%)</th>
                        <th className="px-4 py-3 font-semibold text-[#8B3103]">Lift Ratio</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-[#EAE0CB] bg-white">
                      {results.level2.rules.map((r: any, idx: number) => (
                        <tr key={idx} className="hover:bg-[#FAF8F5]">
                          <td className="px-4 py-3 font-mono font-medium text-stone-900">
                            {r.rule_representation}
                          </td>
                          <td className="px-4 py-3 text-stone-700 font-semibold">{r.support_pct}%</td>
                          <td className="px-4 py-3 text-stone-700 font-semibold">{r.confidence_pct}%</td>
                          <td className="px-4 py-3 text-[#8B3103] font-bold">{r.lift}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}

          <div className="rounded-lg bg-slate-50 border border-slate-200 p-4 text-xs text-slate-600">
            ℹ️ <strong>Academic Note:</strong> Association rules discover statistical co-occurrences in transactions; they describe historical correlation patterns rather than proven causal mechanisms.
          </div>
        </div>
      )}
    </div>
  );
};
