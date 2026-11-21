"use client";

import React, { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { MetricCard } from "../ui/MetricCard";
import {
  Users,
  BookOpen,
  Award,
  Clock,
  CheckCircle2,
  AlertTriangle,
  PlayCircle,
  Database,
  ArrowRight,
} from "lucide-react";

interface DashboardViewProps {
  onNavigate: (viewId: string) => void;
  onRefreshStatus: () => void;
}

export const DashboardView: React.FC<DashboardViewProps> = ({
  onNavigate,
  onRefreshStatus,
}) => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [seeding, setSeeding] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await api.getDashboard();
      setData(res);
    } catch (err: any) {
      setError(err.message || "Failed to load dashboard data.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleSeedData = async () => {
    try {
      setSeeding(true);
      await api.loadSampleData(120);
      await loadData();
      onRefreshStatus();
    } catch (err: any) {
      alert("Error seeding data: " + err.message);
    } finally {
      setSeeding(false);
    }
  };

  if (loading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <div className="flex items-center space-x-3 text-stone-600">
          <div className="h-6 w-6 animate-spin rounded-full border-2 border-[#8B3103] border-t-transparent" />
          <span className="text-sm font-medium">Loading Academic Dashboard...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-xl border border-red-200 bg-red-50 p-6 text-red-800">
        <div className="flex items-center space-x-2 font-semibold">
          <AlertTriangle className="h-5 w-5 text-red-600" />
          <span>Backend Connection Error</span>
        </div>
        <p className="mt-2 text-sm text-red-700">{error}</p>
        <button
          onClick={loadData}
          className="mt-4 rounded-lg bg-red-600 px-4 py-2 text-xs font-semibold text-white hover:bg-red-700"
        >
          Retry Connection
        </button>
      </div>
    );
  }

  const isEmpty = data?.is_empty;

  return (
    <div className="space-y-6">
      {/* Hero Banner with Deep Rust (#8B3103) & Pearl (#EAE0CB) Theme */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-[#8B3103] via-[#742802] to-[#5D1F02] p-8 text-[#FAF8F5] shadow-md border border-[#EAE0CB]/20">
        <div className="relative z-10 max-w-3xl">
          <div className="inline-flex items-center gap-2 rounded-full bg-[#EAE0CB]/15 px-3 py-1 text-xs font-semibold text-[#EAE0CB] backdrop-blur-md border border-[#EAE0CB]/25">
            <span className="h-2 w-2 rounded-full bg-[#EAE0CB]"></span>
            DWDM PBL University Evaluation (Questions 61–70)
          </div>
          <h1 className="mt-4 text-3xl font-extrabold tracking-tight sm:text-4xl text-[#FAF8F5]">
            Student Performance Data Warehouse & AI Early-Warning System
          </h1>
          <p className="mt-3 text-sm text-[#EAE0CB] sm:text-base leading-relaxed">
            Integrating relational Star Schema storage, automated 3-stage ETL,
            multidimensional OLAP cubes, multi-level Apriori rule mining,
            zero-target-leakage Decision Tree risk classification, and faculty decision support.
          </p>
        </div>
      </div>

      {/* Empty State Banner */}
      {isEmpty ? (
        <div className="rounded-2xl border border-[#DDD0B5] bg-white p-8 text-center shadow-xs">
          <Database className="mx-auto h-12 w-12 text-[#8B3103]/60" />
          <h3 className="mt-4 text-lg font-bold text-stone-900">
            Data Warehouse Database Has No Records Yet
          </h3>
          <p className="mx-auto mt-2 max-w-md text-sm text-stone-600">
            Populate SQLite with real university records by uploading your institutional spreadsheet or instantly load the pre-configured academic benchmark dataset.
          </p>
          <div className="mt-6 flex flex-wrap items-center justify-center gap-3">
            <button
              onClick={handleSeedData}
              disabled={seeding}
              className="inline-flex items-center gap-2 rounded-lg bg-[#8B3103] px-5 py-2.5 text-sm font-semibold text-[#FAF8F5] shadow-xs transition hover:bg-[#742802] disabled:opacity-50"
            >
              <PlayCircle className="h-4 w-4" />
              {seeding ? "Generating & Ingesting..." : "Load 120-Student Benchmark Dataset"}
            </button>
            <button
              onClick={() => onNavigate("upload")}
              className="inline-flex items-center gap-2 rounded-lg border border-[#DDD0B5] bg-white px-5 py-2.5 text-sm font-semibold text-stone-700 transition hover:bg-[#FAF8F5]"
            >
              Upload Custom File <ArrowRight className="h-4 w-4" />
            </button>
          </div>
        </div>
      ) : (
        <>
          {/* KPI Metrics Cards */}
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-5">
            <MetricCard
              label="Enrolled Students"
              value={data.kpis.enrolled_students.toLocaleString()}
              delta="Active Cohort"
              icon={<Users className="h-5 w-5" />}
              color="rust"
            />
            <MetricCard
              label="Offered Courses"
              value={data.kpis.offered_subjects}
              delta="Active Curriculum"
              icon={<BookOpen className="h-5 w-5" />}
              color="rust"
            />
            <MetricCard
              label="Average Final Marks"
              value={
                data.kpis.average_marks !== null
                  ? `${data.kpis.average_marks} / 100`
                  : "N/A"
              }
              delta="Pass Threshold: 40.0"
              icon={<Award className="h-5 w-5" />}
              color="pearl"
            />
            <MetricCard
              label="Average Attendance"
              value={`${data.kpis.average_attendance}%`}
              delta={`${data.kpis.low_attendance_count} Low (<75%)`}
              icon={<Clock className="h-5 w-5" />}
              color={data.kpis.average_attendance >= 75 ? "rust" : "amber"}
            />
            <MetricCard
              label="Pass Rate"
              value={`${data.kpis.pass_rate}%`}
              delta={`Failure Rate: ${data.kpis.fail_rate}%`}
              icon={<CheckCircle2 className="h-5 w-5" />}
              color={data.kpis.pass_rate >= 80 ? "rust" : "amber"}
            />
          </div>

          {/* Departmental & Attendance Charts */}
          <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
            {/* Departmental Pass Rate */}
            <div className="rounded-xl border border-[#DDD0B5] bg-white p-6 shadow-xs">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-base font-bold text-stone-900">
                    Departmental Pass Rate (%)
                  </h3>
                  <p className="text-xs text-stone-500">
                    Aggregated academic performance by branch
                  </p>
                </div>
                <span className="rounded bg-[#FAECE2] px-2.5 py-1 text-xs font-bold text-[#8B3103]">
                  OLAP Dimension
                </span>
              </div>
              <div className="mt-6 space-y-4">
                {data.department_pass_rates?.map((d: any) => (
                  <div key={d.department} className="space-y-1">
                    <div className="flex justify-between text-xs font-medium">
                      <span className="text-stone-700">{d.department}</span>
                      <span className="font-semibold text-stone-900">
                        {d.pass_rate}% ({d.pass_count}/{d.total})
                      </span>
                    </div>
                    <div className="h-2.5 w-full overflow-hidden rounded-full bg-[#FAF8F5] border border-[#EAE0CB]/50">
                      <div
                        className="h-full rounded-full bg-[#8B3103] transition-all duration-500"
                        style={{ width: `${d.pass_rate}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Attendance Tier Distribution */}
            <div className="rounded-xl border border-[#DDD0B5] bg-white p-6 shadow-xs">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-base font-bold text-stone-900">
                    Attendance Cohort Distribution
                  </h3>
                  <p className="text-xs text-stone-500">
                    Institutional threshold breakdown (75% Minimum)
                  </p>
                </div>
                <span className="rounded bg-[#FAECE2] px-2.5 py-1 text-xs font-bold text-[#8B3103]">
                  Question 65 Constraint
                </span>
              </div>
              <div className="mt-6 grid grid-cols-3 gap-3">
                {data.attendance_distribution?.map((att: any) => {
                  const isLow = att.category.includes("<75%");
                  const isNormal = att.category.includes("75-85%");
                  return (
                    <div
                      key={att.category}
                      className={`rounded-xl border p-4 text-center ${
                        isLow
                          ? "border-red-200 bg-red-50 text-red-900"
                          : isNormal
                          ? "border-[#DDD0B5] bg-[#FAF8F5] text-stone-900"
                          : "border-[#8B3103]/20 bg-[#FAECE2] text-[#8B3103]"
                      }`}
                    >
                      <div className="text-xs font-semibold">{att.category}</div>
                      <div className="mt-2 text-2xl font-bold">{att.count}</div>
                      <div className="mt-1 text-[11px] opacity-75">Records</div>
                    </div>
                  );
                })}
              </div>
              <div className="mt-6 rounded-lg bg-[#FAF8F5] p-4 text-xs text-stone-700 border border-[#EAE0CB]">
                💡 <strong>Academic Insight:</strong> Students under the 75% threshold undergo constraint-based mining and AI risk triage to identify early failure probabilities.
              </div>
            </div>
          </div>

          {/* Quick Preview Table */}
          {data.preview_records && data.preview_records.length > 0 && (
            <div className="overflow-hidden rounded-xl border border-[#DDD0B5] bg-white shadow-xs">
              <div className="border-b border-[#EAE0CB] bg-[#FAF8F5] px-6 py-4 flex items-center justify-between">
                <h3 className="text-sm font-bold text-stone-900">
                  Data Warehouse Active Records Preview (First 10 Rows)
                </h3>
                <button
                  onClick={() => onNavigate("olap")}
                  className="inline-flex items-center text-xs font-bold text-[#8B3103] hover:text-[#742802]"
                >
                  Explore Full Data Cube <ArrowRight className="ml-1 h-3.5 w-3.5" />
                </button>
              </div>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-[#EAE0CB] text-left text-xs">
                  <thead className="bg-[#F5EFE6] text-stone-700">
                    <tr>
                      <th className="px-4 py-3 font-semibold">Student ID</th>
                      <th className="px-4 py-3 font-semibold">Student Name</th>
                      <th className="px-4 py-3 font-semibold">Department</th>
                      <th className="px-4 py-3 font-semibold">Sem</th>
                      <th className="px-4 py-3 font-semibold">Subject</th>
                      <th className="px-4 py-3 font-semibold">Marks</th>
                      <th className="px-4 py-3 font-semibold">Grade</th>
                      <th className="px-4 py-3 font-semibold">Status</th>
                      <th className="px-4 py-3 font-semibold">Attendance</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-stone-100 bg-white">
                    {data.preview_records.map((r: any, idx: number) => (
                      <tr key={idx} className="hover:bg-[#FAF8F5]">
                        <td className="px-4 py-3 font-mono font-medium text-stone-900">
                          {r.StudentID}
                        </td>
                        <td className="px-4 py-3 text-stone-700">{r.StudentName}</td>
                        <td className="px-4 py-3 text-stone-600">{r.Department}</td>
                        <td className="px-4 py-3 text-stone-600">{r.Semester}</td>
                        <td className="px-4 py-3 text-stone-600">{r.SubjectName || "—"}</td>
                        <td className="px-4 py-3 font-bold text-[#8B3103]">
                          {r.MarksObtained !== null ? r.MarksObtained : "—"}
                        </td>
                        <td className="px-4 py-3 font-semibold text-stone-700">
                          {r.Grade || "—"}
                        </td>
                        <td className="px-4 py-3">
                          <span
                            className={`inline-flex rounded-full px-2 py-0.5 text-[11px] font-bold ${
                              r.ResultStatus === "Pass"
                                ? "bg-emerald-100 text-emerald-800"
                                : r.ResultStatus === "Fail"
                                ? "bg-rose-100 text-rose-800"
                                : "bg-stone-100 text-stone-600"
                            }`}
                          >
                            {r.ResultStatus || "—"}
                          </span>
                        </td>
                        <td className="px-4 py-3 font-medium text-stone-800">
                          {r.AttendancePercentage !== null
                            ? `${r.AttendancePercentage}%`
                            : "—"}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
};
