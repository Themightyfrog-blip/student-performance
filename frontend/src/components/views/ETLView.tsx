"use client";

import React, { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { MetricCard } from "../ui/MetricCard";
import {
  Settings2,
  CheckCircle,
  AlertTriangle,
  Play,
  RotateCcw,
  ListFilter,
  FileCheck,
} from "lucide-react";

interface ETLViewProps {
  onETLCompleted: () => void;
}

export const ETLView: React.FC<ETLViewProps> = ({ onETLCompleted }) => {
  const [audit, setAudit] = useState<any>(null);
  const [auditLogs, setAuditLogs] = useState<any[]>([]);
  const [dedup, setDedup] = useState("drop_grain");
  const [missingStrat, setMissingStrat] = useState("impute_subject_mean");
  const [cleanBounds, setCleanBounds] = useState(true);
  const [running, setRunning] = useState(false);
  const [summary, setSummary] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    try {
      setLoading(true);
      const auditRes = await api.getQualityAudit();
      setAudit(auditRes.audit);
      const logsRes = await api.getAuditLogs(15);
      setAuditLogs(logsRes.audit_logs);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleExecuteETL = async () => {
    try {
      setRunning(true);
      const res = await api.commitUpload({
        deduplicate_strategy: dedup,
        missing_marks_strategy: missingStrat,
        clean_out_of_bounds: cleanBounds,
      });
      setSummary(res.summary);
      await loadData();
      onETLCompleted();
    } catch (err: any) {
      alert("ETL execution failed: " + err.message);
    } finally {
      setRunning(false);
    }
  };

  if (loading) {
    return (
      <div className="flex h-64 items-center justify-center text-slate-500">
        <div className="h-6 w-6 animate-spin rounded-full border-2 border-brand-600 border-t-transparent mr-2" />
        Auditing Data Quality & Loading Pipeline...
      </div>
    );
  }

  const m = audit?.metrics || {
    duplicate_rows: 0,
    duplicate_grain_records: 0,
    missing_marks_count: 0,
    out_of_range_marks_count: 0,
    invalid_attendance_count: 0,
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-slate-900">
          3-Stage ETL Pipeline & Data Quality Profiler
        </h2>
        <p className="mt-1 text-sm text-slate-500">
          Extract, audit quality, apply configurable transformations (bounds cleaning, subject-mean imputation), and load dimensions and facts into the SQLite star schema.
        </p>
      </div>

      {/* Pre-ETL Data Quality Audit Cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <MetricCard
          label="Data Quality Score"
          value={audit ? `${audit.quality_score}%` : "100%"}
          delta="Pre-ETL Health Rating"
          color={audit?.quality_score >= 80 ? "green" : "amber"}
          icon={<FileCheck className="h-5 w-5" />}
        />
        <MetricCard
          label="Duplicate Records"
          value={m.duplicate_rows + m.duplicate_grain_records}
          delta={`${m.duplicate_grain_records} Grain Duplicates`}
          color={m.duplicate_rows === 0 ? "slate" : "amber"}
          icon={<AlertTriangle className="h-5 w-5" />}
        />
        <MetricCard
          label="Missing Exam Marks"
          value={m.missing_marks_count}
          delta="Requires Mean Imputation"
          color={m.missing_marks_count === 0 ? "slate" : "amber"}
          icon={<AlertTriangle className="h-5 w-5" />}
        />
        <MetricCard
          label="Out-of-Bounds Values"
          value={m.out_of_range_marks_count + m.invalid_attendance_count}
          delta="Clipped to [0, 100]"
          color={m.out_of_range_marks_count === 0 ? "slate" : "red"}
          icon={<AlertTriangle className="h-5 w-5" />}
        />
      </div>

      {/* Anomaly Issues Box */}
      {audit?.issues && audit.issues.length > 0 && (
        <div className="rounded-xl border border-amber-200 bg-amber-50/70 p-5 text-xs text-amber-900">
          <div className="flex items-center gap-2 font-bold text-amber-800">
            <AlertTriangle className="h-4 w-4" />
            <span>Identified Data Quality Anomalies:</span>
          </div>
          <ul className="mt-2 list-disc list-inside space-y-1">
            {audit.issues.map((iss: string, idx: number) => (
              <li key={idx}>{iss}</li>
            ))}
          </ul>
        </div>
      )}

      {/* ETL Transformation Settings Card */}
      <div className="rounded-xl border border-[#DDD0B5] bg-white p-6 shadow-xs">
        <h3 className="text-base font-bold text-stone-900 flex items-center gap-2">
          <Settings2 className="h-5 w-5 text-brand-600" />
          ETL Transformation Configuration
        </h3>
        <p className="text-xs text-stone-500 mt-1">
          Adjust pipeline strategies before loading into the SQLite warehouse:
        </p>

        <div className="mt-5 grid grid-cols-1 gap-4 sm:grid-cols-3">
          <div>
            <label className="text-xs font-semibold text-stone-700 block mb-1">
              Duplicate Resolution Strategy
            </label>
            <select
              value={dedup}
              onChange={(e) => setDedup(e.target.value)}
              className="w-full rounded-lg border border-[#DDD0B5] bg-white px-3 py-2 text-xs text-stone-800 shadow-xs focus:border-brand-500 focus:outline-hidden"
            >
              <option value="drop_grain">Drop Duplicate Fact Grain (Recommended)</option>
              <option value="drop_exact">Drop Exact Duplicates Only</option>
              <option value="none">Preserve All Records</option>
            </select>
          </div>

          <div>
            <label className="text-xs font-semibold text-stone-700 block mb-1">
              Missing Marks Handling
            </label>
            <select
              value={missingStrat}
              onChange={(e) => setMissingStrat(e.target.value)}
              className="w-full rounded-lg border border-[#DDD0B5] bg-white px-3 py-2 text-xs text-stone-800 shadow-xs focus:border-brand-500 focus:outline-hidden"
            >
              <option value="impute_subject_mean">Impute Subject Mean (is_imputed=1)</option>
              <option value="drop">Drop Missing Records</option>
              <option value="leave_missing">Leave Missing (NaN)</option>
            </select>
          </div>

          <div className="flex items-center space-x-3 pt-5">
            <input
              type="checkbox"
              id="clean-bounds"
              checked={cleanBounds}
              onChange={(e) => setCleanBounds(e.target.checked)}
              className="h-4 w-4 rounded border-[#DDD0B5] text-brand-600 focus:ring-brand-500"
            />
            <label htmlFor="clean-bounds" className="text-xs font-medium text-stone-700">
              Clip Out-of-Bounds Values to [0, 100]
            </label>
          </div>
        </div>

        <div className="mt-6 border-t border-[#EAE0CB] pt-4 flex justify-end">
          <button
            onClick={handleExecuteETL}
            disabled={running}
            className="inline-flex items-center gap-2 rounded-lg bg-brand-600 px-5 py-2.5 text-xs font-semibold text-white shadow-xs hover:bg-brand-700 disabled:opacity-50 transition"
          >
            <Play className="h-4 w-4" />
            {running ? "Executing 3-Stage ETL..." : "Run ETL Pipeline & Load Warehouse"}
          </button>
        </div>
      </div>

      {/* Execution Summary If Run */}
      {summary && (
        <div className="rounded-xl border border-emerald-200 bg-emerald-50/70 p-6 shadow-xs">
          <div className="flex items-center gap-2 font-bold text-emerald-900 text-sm">
            <CheckCircle className="h-5 w-5 text-emerald-600" />
            <span>ETL Batch Execution {summary.batch_id} Completed</span>
          </div>
          <div className="mt-4 grid grid-cols-2 gap-3 sm:grid-cols-4 text-xs">
            <div className="bg-white rounded p-3 border border-emerald-100">
              <span className="text-stone-500">Ingested Rows:</span>{" "}
              <strong className="text-stone-900">{summary.initial_rows}</strong>
            </div>
            <div className="bg-white rounded p-3 border border-emerald-100">
              <span className="text-stone-500">Duplicates Removed:</span>{" "}
              <strong className="text-stone-900">{summary.duplicates_removed}</strong>
            </div>
            <div className="bg-white rounded p-3 border border-emerald-100">
              <span className="text-stone-500">Marks Imputed:</span>{" "}
              <strong className="text-stone-900">{summary.missing_marks_imputed}</strong>
            </div>
            <div className="bg-white rounded p-3 border border-emerald-100">
              <span className="text-stone-500">Exam Facts Loaded:</span>{" "}
              <strong className="text-stone-900">{summary.loaded_exam_facts}</strong>
            </div>
          </div>
        </div>
      )}

      {/* Recent Warehouse Audit Trail */}
      <div className="overflow-hidden rounded-xl border border-[#DDD0B5] bg-white shadow-xs">
        <div className="border-b border-[#EAE0CB] bg-[#FAF8F5] px-6 py-3 font-bold text-xs text-stone-900 flex items-center justify-between">
          <span>ETL Audit Trail & Lineage Logs (ETLAuditLog)</span>
          <button
            onClick={loadData}
            className="text-xs text-brand-600 hover:text-brand-800 inline-flex items-center gap-1 font-semibold"
          >
            <RotateCcw className="h-3.5 w-3.5" /> Refresh Logs
          </button>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-[#EAE0CB] text-left text-xs">
            <thead className="bg-[#F5EFE6] text-stone-700">
              <tr>
                <th className="px-4 py-2.5 font-semibold">Timestamp</th>
                <th className="px-4 py-2.5 font-semibold">Batch ID</th>
                <th className="px-4 py-2.5 font-semibold">Stage</th>
                <th className="px-4 py-2.5 font-semibold">Action</th>
                <th className="px-4 py-2.5 font-semibold">Records Affected</th>
                <th className="px-4 py-2.5 font-semibold">Details</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#EAE0CB] bg-white">
              {auditLogs.map((log: any) => (
                <tr key={log.LogId} className="hover:bg-[#FAF8F5]">
                  <td className="px-4 py-2.5 font-mono text-[11px] text-stone-500">
                    {log.Timestamp}
                  </td>
                  <td className="px-4 py-2.5 font-mono text-[11px] text-stone-700">
                    {log.BatchId}
                  </td>
                  <td className="px-4 py-2.5">
                    <span className="inline-flex rounded bg-[#F5EFE6] border border-[#DDD0B5] px-2 py-0.5 text-[10px] font-semibold text-[#8B3103]">
                      {log.Stage}
                    </span>
                  </td>
                  <td className="px-4 py-2.5 font-medium text-stone-800">{log.Action}</td>
                  <td className="px-4 py-2.5 text-stone-600 font-semibold">{log.RecordsAffected}</td>
                  <td className="px-4 py-2.5 text-stone-500 text-[11px] max-w-xs truncate">
                    {log.Details || "—"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
