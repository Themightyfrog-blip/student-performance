"use client";

import React, { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { Layers, ArrowUpRight, Filter, Table as TableIcon, Download } from "lucide-react";

export const OLAPView: React.FC = () => {
  const [activeTab, setActiveTab] = useState<"cube" | "rollup" | "drilldown" | "slice" | "dice">("cube");
  const [cubeData, setCubeData] = useState<any[]>([]);
  const [rollupData, setRollupData] = useState<any[]>([]);
  const [rollupLevel, setRollupLevel] = useState("Department");
  const [drillData, setDrillData] = useState<any[]>([]);
  const [drillDept, setDrillDept] = useState("All");
  const [drillSem, setDrillSem] = useState<number | undefined>(undefined);
  const [sliceDim, setSliceDim] = useState("Department");
  const [sliceVal, setSliceVal] = useState("Computer Science");
  const [sliceData, setSliceData] = useState<any[]>([]);
  const [diceRanking, setDiceRanking] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  // Load cube data
  const loadCube = async () => {
    try {
      setLoading(true);
      const res = await api.getDataCube();
      setCubeData(res.records || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Load rollup
  const loadRollup = async (level: string) => {
    try {
      setLoading(true);
      const res = await api.getHierarchicalRollup(level);
      setRollupData(res.records || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Load drilldown
  const loadDrilldown = async () => {
    try {
      setLoading(true);
      const res = await api.drillDownStudents(drillDept, drillSem);
      setDrillData(res.records || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Run slice
  const runSlice = async () => {
    try {
      setLoading(true);
      const res = await api.sliceCube(sliceDim, sliceVal);
      setSliceData(res.records || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Run dice
  const runDice = async () => {
    try {
      setLoading(true);
      const res = await api.diceCube(undefined, undefined, ["Pass", "Fail"]);
      setDiceRanking(res.department_ranking || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (activeTab === "cube") loadCube();
    if (activeTab === "rollup") loadRollup(rollupLevel);
    if (activeTab === "drilldown") loadDrilldown();
    if (activeTab === "slice") runSlice();
    if (activeTab === "dice") runDice();
  }, [activeTab]);

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-slate-900">
          OLAP Operations & Multidimensional Data Cube (Question 69)
        </h2>
        <p className="mt-1 text-sm text-slate-500">
          Perform multidimensional aggregations with mathematically verified <strong>Credit-Weighted GPA</strong> [ Σ(GradePoints × Credits) / Σ(Credits) ], Hierarchical Roll-up, Drill-down, Slicing, and Dicing.
        </p>
      </div>

      {/* Tabs with Deep Rust & Pearl Highlights */}
      <div className="flex border-b border-[#EAE0CB]">
        {[
          { id: "cube", label: "🧊 Data Cube" },
          { id: "rollup", label: "🔼 Hierarchical Roll-Up" },
          { id: "drilldown", label: "🔽 Drill-Down to Students" },
          { id: "slice", label: "🔪 Slice Cube" },
          { id: "dice", label: "🎲 Dice Cube & Failure Ranking" },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            className={`border-b-2 px-4 py-2.5 text-xs font-semibold transition ${
              activeTab === tab.id
                ? "border-[#8B3103] text-[#8B3103] font-bold"
                : "border-transparent text-stone-500 hover:text-[#8B3103]"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab 1: Data Cube */}
      {activeTab === "cube" && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-500">
              Showing multidimensional cube at grain <code>(StudentID, SubjectID, Semester)</code>:
            </span>
            <a
              href="/api/reports/data-csv"
              className="inline-flex items-center gap-1.5 rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-xs font-semibold text-slate-700 shadow-sm hover:bg-slate-50"
            >
              <Download className="h-3.5 w-3.5" /> Export Cube CSV
            </a>
          </div>

          <div className="overflow-hidden rounded-xl border border-[#DDD0B5] bg-white shadow-xs">
            <div className="overflow-x-auto max-h-[500px]">
              <table className="min-w-full divide-y divide-[#EAE0CB] text-left text-xs">
                <thead className="bg-[#F5EFE6] text-stone-700 sticky top-0 z-10">
                  <tr>
                    <th className="px-3 py-2.5 font-semibold">Student ID</th>
                    <th className="px-3 py-2.5 font-semibold">Subject ID</th>
                    <th className="px-3 py-2.5 font-semibold">Semester</th>
                    <th className="px-3 py-2.5 font-semibold">Attempts</th>
                    <th className="px-3 py-2.5 font-semibold">Avg Marks</th>
                    <th className="px-3 py-2.5 font-semibold">Pass Count</th>
                    <th className="px-3 py-2.5 font-semibold">Fail Count</th>
                    <th className="px-3 py-2.5 font-semibold">Pass Rate</th>
                    <th className="px-3 py-2.5 font-semibold">Avg Attendance</th>
                    <th className="px-3 py-2.5 font-semibold text-[#8B3103]">Credit-Weighted GPA</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#EAE0CB] bg-white">
                  {cubeData.map((r, i) => (
                    <tr key={i} className="hover:bg-[#FAF8F5]">
                      <td className="px-3 py-2 font-mono font-medium text-stone-900">{r.StudentID}</td>
                      <td className="px-3 py-2 font-mono text-stone-700">{r.SubjectID}</td>
                      <td className="px-3 py-2 text-stone-600">{r.Semester}</td>
                      <td className="px-3 py-2 text-stone-600">{r.Attempts}</td>
                      <td className="px-3 py-2 font-semibold text-stone-900">{r.Avg_Marks ?? "—"}</td>
                      <td className="px-3 py-2 text-emerald-700 font-semibold">{r.Pass_Count}</td>
                      <td className="px-3 py-2 text-rose-700 font-semibold">{r.Fail_Count}</td>
                      <td className="px-3 py-2 font-medium">{r.Pass_Rate_Pct}%</td>
                      <td className="px-3 py-2 text-stone-600">{r.Avg_Attendance_Pct}%</td>
                      <td className="px-3 py-2 font-bold text-[#8B3103]">{r.Credit_Weighted_GPA ?? "—"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Tab 2: Roll-up */}
      {activeTab === "rollup" && (
        <div className="space-y-4">
          <div className="flex items-center gap-3">
            <label className="text-xs font-semibold text-slate-700">Roll-Up Level:</label>
            <select
              value={rollupLevel}
              onChange={(e) => {
                setRollupLevel(e.target.value);
                loadRollup(e.target.value);
              }}
              className="rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-xs text-slate-800 shadow-sm focus:border-brand-500 focus:outline-none"
            >
              <option value="Subject">Subject Level</option>
              <option value="Semester">Semester Level</option>
              <option value="Department">Department Level</option>
              <option value="University">University Level (Top-Level Institutional)</option>
            </select>
          </div>

          <div className="overflow-hidden rounded-xl border border-[#DDD0B5] bg-white shadow-xs">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-[#EAE0CB] text-left text-xs">
                <thead className="bg-[#F5EFE6] text-stone-700">
                  <tr>
                    <th className="px-4 py-3 font-semibold">{rollupLevel}</th>
                    <th className="px-4 py-3 font-semibold">Unique Students</th>
                    <th className="px-4 py-3 font-semibold">Total Attempts</th>
                    <th className="px-4 py-3 font-semibold">Avg Marks</th>
                    <th className="px-4 py-3 font-semibold">Pass Rate</th>
                    <th className="px-4 py-3 font-semibold">Fail Rate</th>
                    <th className="px-4 py-3 font-semibold">Avg Attendance</th>
                    <th className="px-4 py-3 font-semibold text-[#8B3103]">Weighted GPA</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#EAE0CB] bg-white">
                  {rollupData.map((r, i) => (
                    <tr key={i} className="hover:bg-[#FAF8F5]">
                      <td className="px-4 py-3 font-semibold text-stone-900">
                        {r[rollupLevel] || r.Department || r.SubjectID || r.University}
                      </td>
                      <td className="px-4 py-3 text-stone-700">{r.Unique_Students}</td>
                      <td className="px-4 py-3 text-stone-700">{r.Total_Exam_Attempts}</td>
                      <td className="px-4 py-3 font-bold text-stone-900">{r.Avg_Marks}</td>
                      <td className="px-4 py-3 text-emerald-700 font-semibold">{r.Pass_Rate_Pct}%</td>
                      <td className="px-4 py-3 text-rose-700 font-semibold">{r.Fail_Rate_Pct}%</td>
                      <td className="px-4 py-3 text-stone-600">{r.Avg_Attendance}%</td>
                      <td className="px-4 py-3 font-bold text-[#8B3103]">{r.Weighted_GPA}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Tab 3: Drilldown */}
      {activeTab === "drilldown" && (
        <div className="space-y-4">
          <div className="flex flex-wrap items-center gap-3">
            <div>
              <label className="text-xs font-semibold text-slate-700 block mb-1">Department</label>
              <select
                value={drillDept}
                onChange={(e) => setDrillDept(e.target.value)}
                className="rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-xs text-slate-800"
              >
                <option value="All">All Departments</option>
                <option value="Computer Science">Computer Science</option>
                <option value="Information Technology">Information Technology</option>
                <option value="Electronics & Comm">Electronics & Comm</option>
                <option value="Mechanical Eng">Mechanical Eng</option>
              </select>
            </div>
            <div>
              <label className="text-xs font-semibold text-slate-700 block mb-1">Semester</label>
              <select
                value={drillSem || ""}
                onChange={(e) => setDrillSem(e.target.value ? Number(e.target.value) : undefined)}
                className="rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-xs text-slate-800"
              >
                <option value="">All Semesters</option>
                <option value="3">Semester 3</option>
                <option value="4">Semester 4</option>
                <option value="5">Semester 5</option>
              </select>
            </div>
            <button
              onClick={loadDrilldown}
              className="mt-5 rounded-lg bg-brand-600 px-4 py-1.5 text-xs font-semibold text-white hover:bg-brand-700"
            >
              Filter Records
            </button>
          </div>

          <div className="overflow-hidden rounded-xl border border-[#DDD0B5] bg-white shadow-xs">
            <div className="overflow-x-auto max-h-[500px]">
              <table className="min-w-full divide-y divide-[#EAE0CB] text-left text-xs">
                <thead className="bg-[#F5EFE6] text-stone-700 sticky top-0">
                  <tr>
                    <th className="px-3 py-2.5 font-semibold">Student ID</th>
                    <th className="px-3 py-2.5 font-semibold">Student Name</th>
                    <th className="px-3 py-2.5 font-semibold">Department</th>
                    <th className="px-3 py-2.5 font-semibold">Semester</th>
                    <th className="px-3 py-2.5 font-semibold">Subject</th>
                    <th className="px-3 py-2.5 font-semibold">Marks</th>
                    <th className="px-3 py-2.5 font-semibold">Grade</th>
                    <th className="px-3 py-2.5 font-semibold">Status</th>
                    <th className="px-3 py-2.5 font-semibold">Attendance</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#EAE0CB] bg-white">
                  {drillData.map((r, i) => (
                    <tr key={i} className="hover:bg-[#FAF8F5]">
                      <td className="px-3 py-2 font-mono font-medium text-stone-900">{r.StudentID}</td>
                      <td className="px-3 py-2 text-stone-700">{r.StudentName}</td>
                      <td className="px-3 py-2 text-stone-600">{r.Department}</td>
                      <td className="px-3 py-2 text-stone-600">{r.Semester}</td>
                      <td className="px-3 py-2 text-stone-600">{r.SubjectName}</td>
                      <td className="px-3 py-2 font-semibold text-stone-900">{r.MarksObtained}</td>
                      <td className="px-3 py-2 font-semibold">{r.Grade}</td>
                      <td className="px-3 py-2">
                        <span
                          className={`inline-flex rounded-full px-2 py-0.5 text-[10px] font-semibold ${
                            r.ResultStatus === "Pass"
                              ? "bg-emerald-100 text-emerald-800"
                              : "bg-rose-100 text-rose-800"
                          }`}
                        >
                          {r.ResultStatus}
                        </span>
                      </td>
                      <td className="px-3 py-2 text-stone-700">{r.AttendancePercentage}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Tab 4: Slice */}
      {activeTab === "slice" && (
        <div className="space-y-4">
          <div className="flex items-center gap-3">
            <span className="text-xs font-semibold text-slate-700">Slice Dimension:</span>
            <input
              type="text"
              value={sliceVal}
              onChange={(e) => setSliceVal(e.target.value)}
              placeholder="e.g. Computer Science"
              className="rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-xs text-slate-800"
            />
            <button
              onClick={runSlice}
              className="rounded-lg bg-brand-600 px-4 py-1.5 text-xs font-semibold text-white hover:bg-brand-700"
            >
              Execute Slice
            </button>
          </div>

          <div className="overflow-hidden rounded-xl border border-[#DDD0B5] bg-white shadow-xs">
            <div className="overflow-x-auto max-h-[400px]">
              <table className="min-w-full divide-y divide-[#EAE0CB] text-left text-xs">
                <thead className="bg-[#F5EFE6] text-stone-700 sticky top-0">
                  <tr>
                    <th className="px-4 py-2.5 font-semibold">Student ID</th>
                    <th className="px-4 py-2.5 font-semibold">Subject ID</th>
                    <th className="px-4 py-2.5 font-semibold">Avg Marks</th>
                    <th className="px-4 py-2.5 font-semibold">Pass Rate</th>
                    <th className="px-4 py-2.5 font-semibold text-[#8B3103]">Weighted GPA</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#EAE0CB] bg-white">
                  {sliceData.map((r, i) => (
                    <tr key={i} className="hover:bg-[#FAF8F5]">
                      <td className="px-4 py-2 font-mono text-stone-900">{r.StudentID}</td>
                      <td className="px-4 py-2 font-mono text-stone-700">{r.SubjectID}</td>
                      <td className="px-4 py-2 font-semibold text-stone-900">{r.Avg_Marks}</td>
                      <td className="px-4 py-2 text-stone-600">{r.Pass_Rate_Pct}%</td>
                      <td className="px-4 py-2 font-bold text-[#8B3103]">{r.Credit_Weighted_GPA}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Tab 5: Dice & Ranking */}
      {activeTab === "dice" && (
        <div className="space-y-4">
          <div className="rounded-xl border border-[#DDD0B5] bg-white p-6 shadow-xs">
            <h3 className="text-sm font-bold text-stone-900">
              🚨 Department Failure Rate Ranking (Diced Multidimensional Cohort)
            </h3>
            <p className="text-xs text-stone-500 mt-1">
              Ranks departments by course failure frequency with sample sizes:
            </p>

            <div className="mt-4 overflow-x-auto">
              <table className="min-w-full divide-y divide-[#EAE0CB] text-left text-xs">
                <thead className="bg-[#F5EFE6] text-stone-700">
                  <tr>
                    <th className="px-4 py-3 font-semibold">Rank</th>
                    <th className="px-4 py-3 font-semibold">Department</th>
                    <th className="px-4 py-3 font-semibold">Students</th>
                    <th className="px-4 py-3 font-semibold">Total Records</th>
                    <th className="px-4 py-3 font-semibold text-rose-700">Fail Count</th>
                    <th className="px-4 py-3 font-semibold text-rose-700">Failure Rate (%)</th>
                    <th className="px-4 py-3 font-semibold">Avg Attendance</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#EAE0CB] bg-white">
                  {diceRanking.map((r, i) => (
                    <tr key={i} className="hover:bg-[#FAF8F5]">
                      <td className="px-4 py-3 font-bold text-stone-500">#{i + 1}</td>
                      <td className="px-4 py-3 font-semibold text-stone-900">{r.Department}</td>
                      <td className="px-4 py-3 text-stone-700">{r.Student_Count}</td>
                      <td className="px-4 py-3 text-stone-700">{r.Total_Records}</td>
                      <td className="px-4 py-3 font-semibold text-rose-700">{r.Fail_Count}</td>
                      <td className="px-4 py-3 font-bold text-rose-600">{r.Failure_Rate_Pct}%</td>
                      <td className="px-4 py-3 text-stone-600">{r.Avg_Attendance}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
