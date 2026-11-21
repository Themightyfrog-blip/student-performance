"use client";

import React, { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { MetricCard } from "../ui/MetricCard";
import { AlertOctagon, AlertTriangle, CheckCircle, ShieldAlert, UserCheck } from "lucide-react";

export const EarlyWarningView: React.FC = () => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [updatingId, setUpdatingId] = useState<string | null>(null);

  const loadTriage = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await api.getEarlyWarningDashboard();
      setData(res);
    } catch (err: any) {
      setError(err.message || "Failed to load early-warning triage center.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTriage();
  }, []);

  const handleStatusChange = async (studentId: string, newStatus: string) => {
    try {
      setUpdatingId(studentId);
      await api.updateStudentStatus(studentId, newStatus);
      // Update local state
      setData((prev: any) => ({
        ...prev,
        priority_queue: prev.priority_queue.map((s: any) =>
          s.StudentID === studentId ? { ...s, Faculty_Review_Status: newStatus } : s
        ),
      }));
    } catch (err: any) {
      alert("Status update failed: " + err.message);
    } finally {
      setUpdatingId(null);
    }
  };

  if (loading) {
    return (
      <div className="flex h-64 items-center justify-center text-slate-500">
        <div className="h-6 w-6 animate-spin rounded-full border-2 border-brand-600 border-t-transparent mr-2" />
        Generating Student Risk Triage Queue...
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center gap-2 rounded-xl border border-amber-200 bg-amber-50 p-6 text-sm text-amber-800">
        <AlertTriangle className="h-5 w-5 flex-shrink-0" />
        <span>{error}</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-slate-900">
          AI Early-Warning Decision Support Center (Question 70)
        </h2>
        <p className="mt-1 text-sm text-slate-500">
          Proactively flags students at risk of course failure prior to final examinations, pinpoints causal multi-factor triggers, and orchestrates academic intervention workflows for faculty advisors.
        </p>
      </div>

      {/* Metric Cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-4">
        <MetricCard
          label="Total Assessed"
          value={data.total_assessed}
          delta="Active Student Profiles"
          color="slate"
        />
        <MetricCard
          label="Critical Risk (Fail)"
          value={data.critical_risk_count}
          delta="Immediate Counseling Needed"
          color="red"
          icon={<AlertOctagon className="h-5 w-5" />}
        />
        <MetricCard
          label="At-Risk (Borderline)"
          value={data.at_risk_count}
          delta="Remedial Mentoring Required"
          color="amber"
          icon={<AlertTriangle className="h-5 w-5" />}
        />
        <MetricCard
          label="On-Track (Passing)"
          value={data.on_track_count}
          delta={`${(100 - data.risk_percentage).toFixed(1)}% Satisfactory`}
          color="green"
          icon={<CheckCircle className="h-5 w-5" />}
        />
      </div>

      {/* Advisory Callout */}
      <div className="rounded-xl border border-amber-200 bg-amber-50/70 p-4 text-xs text-amber-900 flex items-start gap-3">
        <ShieldAlert className="h-5 w-5 text-amber-700 flex-shrink-0 mt-0.5" />
        <div>
          <span className="font-bold">Faculty Advisory Notice:</span> Predictions serve as early decision-support alerts to schedule remedial instruction and counseling before final exams. They do not constitute final academic evaluation marks.
        </div>
      </div>

      {/* Priority Student Triage Table */}
      <div className="overflow-hidden rounded-xl border border-[#DDD0B5] bg-white shadow-xs">
        <div className="border-b border-[#EAE0CB] bg-[#FAF8F5] px-6 py-3 font-bold text-xs text-stone-900 flex justify-between">
          <span>Student Risk Triage Queue</span>
          <span className="font-normal text-stone-500">{data.priority_queue?.length} Students Evaluated</span>
        </div>

        <div className="overflow-x-auto max-h-[600px]">
          <table className="min-w-full divide-y divide-[#EAE0CB] text-left text-xs">
            <thead className="bg-[#F5EFE6] text-stone-700 sticky top-0 z-10">
              <tr>
                <th className="px-4 py-3 font-semibold">Student ID</th>
                <th className="px-4 py-3 font-semibold">Name & Dept</th>
                <th className="px-3 py-3 font-semibold">Attendance</th>
                <th className="px-3 py-3 font-semibold">Internals (/50)</th>
                <th className="px-3 py-3 font-semibold">Backlogs</th>
                <th className="px-4 py-3 font-semibold">Predicted Risk</th>
                <th className="px-4 py-3 font-semibold">Recommended Intervention</th>
                <th className="px-4 py-3 font-semibold">Review Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-stone-100 bg-white">
              {data.priority_queue?.map((s: any) => {
                const isCritical = s.Predicted_Risk_Category === "Fail";
                const isAtRisk = s.Predicted_Risk_Category === "At-Risk";
                return (
                  <tr key={s.StudentID} className="hover:bg-slate-50">
                    <td className="px-4 py-3 font-mono font-medium text-slate-900">{s.StudentID}</td>
                    <td className="px-4 py-3">
                      <div className="font-semibold text-slate-900">{s.StudentName}</div>
                      <div className="text-[11px] text-slate-500">{s.Department}</div>
                    </td>
                    <td className="px-3 py-3 font-medium text-slate-800">
                      {s.AttendancePercentage?.toFixed(1)}%
                    </td>
                    <td className="px-3 py-3 font-medium text-slate-800">
                      {s.InternalMarks !== null ? s.InternalMarks.toFixed(1) : "—"}
                    </td>
                    <td className="px-3 py-3 font-semibold text-slate-700">{s.BacklogCount}</td>
                    <td className="px-4 py-3">
                      <span
                        className={`inline-flex rounded-full px-2.5 py-1 text-[11px] font-bold ${
                          isCritical
                            ? "bg-rose-100 text-rose-800 border border-rose-200"
                            : isAtRisk
                            ? "bg-amber-100 text-amber-800 border border-amber-200"
                            : "bg-emerald-100 text-emerald-800"
                        }`}
                      >
                        {s.Predicted_Risk_Category}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-slate-700 max-w-xs">
                      <div className="font-medium text-slate-900">{s.Triage_Action}</div>
                      <div className="text-[10px] text-slate-500 mt-0.5">{s.Intervention_Reason}</div>
                    </td>
                    <td className="px-4 py-3">
                      <select
                        value={s.Faculty_Review_Status}
                        onChange={(e) => handleStatusChange(s.StudentID, e.target.value)}
                        disabled={updatingId === s.StudentID}
                        className={`rounded border px-2 py-1 text-[11px] font-medium focus:outline-none ${
                          s.Faculty_Review_Status === "Resolved"
                            ? "border-emerald-300 bg-emerald-50 text-emerald-800"
                            : s.Faculty_Review_Status === "Intervention Scheduled"
                            ? "border-blue-300 bg-blue-50 text-blue-800"
                            : "border-slate-300 bg-white text-slate-700"
                        }`}
                      >
                        <option value="Pending Review">Pending Review</option>
                        <option value="Intervention Scheduled">Intervention Scheduled</option>
                        <option value="Resolved">Resolved</option>
                      </select>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
