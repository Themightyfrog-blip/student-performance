"use client";

import React, { useState, useEffect } from "react";
import { api } from "@/lib/api";
import {
  LayoutDashboard,
  Upload,
  GitPullRequest,
  Cog,
  Database,
  Box,
  GitBranch,
  Filter,
  Binary,
  TrendingUp,
  AlertTriangle,
  FileText,
  RotateCcw,
  Sparkles,
  GraduationCap,
} from "lucide-react";

import { DashboardView } from "@/components/views/DashboardView";
import { UploadView } from "@/components/views/UploadView";
import { MappingView } from "@/components/views/MappingView";
import { ETLView } from "@/components/views/ETLView";
import { SchemaView } from "@/components/views/SchemaView";
import { OLAPView } from "@/components/views/OLAPView";
import { MiningView } from "@/components/views/MiningView";
import { ConstraintView } from "@/components/views/ConstraintView";
import { ClassifierView } from "@/components/views/ClassifierView";
import { CorrelationView } from "@/components/views/CorrelationView";
import { EarlyWarningView } from "@/components/views/EarlyWarningView";
import { ReportsView } from "@/components/views/ReportsView";

export default function Home() {
  const [activeView, setActiveView] = useState("dashboard");
  const [status, setStatus] = useState<any>(null);
  const [resetting, setResetting] = useState(false);

  const refreshStatus = async () => {
    try {
      const res = await api.getStatus();
      setStatus(res);
    } catch (err) {
      console.error("Status fetch error:", err);
    }
  };

  useEffect(() => {
    refreshStatus();
  }, []);

  const handleReset = async () => {
    if (confirm("Are you sure you want to reset the SQLite data warehouse? All student facts will be purged and schemas re-initialized.")) {
      try {
        setResetting(true);
        await api.resetDatabase();
        await refreshStatus();
        alert("Data warehouse successfully reset to empty state.");
      } catch (err: any) {
        alert("Reset failed: " + err.message);
      } finally {
        setResetting(false);
      }
    }
  };

  const navItems = [
    { id: "dashboard", label: "1. Overview & Dashboard", icon: LayoutDashboard },
    { id: "upload", label: "2. Data Upload & Ingestion", icon: Upload },
    { id: "mapping", label: "3. Column Mapping", icon: GitPullRequest },
    { id: "etl", label: "4. Data Quality & ETL Pipeline", icon: Cog },
    { id: "schema", label: "5. Star Schema Architecture", icon: Database },
    { id: "olap", label: "6. OLAP & Data Cube", icon: Box },
    { id: "mining", label: "7. Multi-Level Association Mining", icon: GitBranch },
    { id: "constraint", label: "8. Constraint-Based Mining (<75%)", icon: Filter },
    { id: "classifier", label: "9. Decision Tree Classifier", icon: Binary },
    { id: "correlation", label: "10. Statistical Correlation", icon: TrendingUp },
    { id: "early_warning", label: "11. AI Early-Warning Center", icon: AlertTriangle },
    { id: "reports", label: "12. Export & Academic Reports", icon: FileText },
  ];

  return (
    <div className="flex min-h-screen bg-[#FAF8F5]">
      {/* Sidebar Navigation */}
      <aside className="w-72 flex-shrink-0 border-r border-[#EAE0CB] bg-white flex flex-col justify-between shadow-sm">
        <div>
          {/* Brand Logo & Header */}
          <div className="border-b border-[#EAE0CB] p-5 bg-[#FAF8F5]/60">
            <div className="flex items-center gap-3">
              <div className="rounded-xl bg-[#8B3103] p-2 text-[#EAE0CB] shadow-md">
                <GraduationCap className="h-5 w-5" />
              </div>
              <div>
                <h1 className="text-sm font-extrabold tracking-tight text-[#8B3103] leading-tight">
                  Academic DWDM
                </h1>
                <p className="text-[11px] font-medium text-stone-500">
                  PBL Rubric: Questions 61–70
                </p>
              </div>
            </div>
          </div>

          {/* Navigation Items */}
          <nav className="p-3 space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeView === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveView(item.id)}
                  className={`flex w-full items-center gap-3 rounded-lg px-3 py-2 text-xs font-semibold transition ${
                    isActive
                      ? "bg-[#FAECE2] text-[#8B3103] font-bold shadow-xs border-l-4 border-[#8B3103]"
                      : "text-stone-600 hover:bg-[#FAF8F5] hover:text-[#8B3103]"
                  }`}
                >
                  <Icon className={`h-4 w-4 ${isActive ? "text-[#8B3103]" : "text-stone-400"}`} />
                  <span className="truncate">{item.label}</span>
                </button>
              );
            })}
          </nav>
        </div>

        {/* Live Warehouse Status Pill */}
        <div className="border-t border-[#EAE0CB] p-4 space-y-3 bg-[#FAF8F5]">
          <div className="flex items-center justify-between text-xs font-bold text-[#8B3103]">
            <span>Warehouse Status</span>
            <span
              className={`h-2 w-2 rounded-full ${
                status?.is_populated ? "bg-[#8B3103] animate-pulse" : "bg-stone-300"
              }`}
            />
          </div>

          <div className="space-y-1 text-[11px] text-stone-700 font-mono">
            <div className="flex justify-between">
              <span>Students:</span>
              <strong className="text-stone-900">{status?.table_counts?.DimStudent || 0}</strong>
            </div>
            <div className="flex justify-between">
              <span>Subjects:</span>
              <strong className="text-stone-900">{status?.table_counts?.DimSubject || 0}</strong>
            </div>
            <div className="flex justify-between">
              <span>Exam Facts:</span>
              <strong className="text-stone-900">{status?.table_counts?.FactExamResult || 0}</strong>
            </div>
            <div className="flex justify-between">
              <span>Att. Facts:</span>
              <strong className="text-stone-900">{status?.table_counts?.FactAttendance || 0}</strong>
            </div>
          </div>

          <button
            onClick={handleReset}
            disabled={resetting}
            className="flex w-full items-center justify-center gap-1.5 rounded-lg border border-[#DDD0B5] bg-white px-3 py-1.5 text-xs font-semibold text-stone-700 shadow-sm hover:bg-[#FAECE2] hover:text-[#8B3103] hover:border-[#8B3103] transition disabled:opacity-50"
          >
            <RotateCcw className="h-3.5 w-3.5" />
            {resetting ? "Resetting..." : "Reset Warehouse"}
          </button>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col min-w-0 overflow-y-auto">
        {/* Top Navbar */}
        <header className="sticky top-0 z-20 flex h-14 items-center justify-between border-b border-[#EAE0CB] bg-[#FAF8F5]/95 px-8 backdrop-blur">
          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold uppercase tracking-wider text-stone-400">
              Active Module
            </span>
            <span className="text-stone-300">/</span>
            <span className="text-xs font-bold text-[#8B3103]">
              {navItems.find((n) => n.id === activeView)?.label}
            </span>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={async () => {
                await api.loadSampleData(120);
                await refreshStatus();
                setActiveView("dashboard");
              }}
              className="inline-flex items-center gap-1.5 rounded-lg bg-[#EAE0CB] px-3.5 py-1.5 text-xs font-bold text-[#5D1F02] hover:bg-[#DDD0B5] border border-[#DDD0B5] transition shadow-xs"
            >
              <Sparkles className="h-3.5 w-3.5 text-[#8B3103]" />
              Quick Load Benchmark Data
            </button>
          </div>
        </header>

        {/* Dynamic Views */}
        <div className="p-8 max-w-7xl mx-auto w-full">
          {activeView === "dashboard" && (
            <DashboardView
              onNavigate={(v) => setActiveView(v)}
              onRefreshStatus={refreshStatus}
            />
          )}
          {activeView === "upload" && (
            <UploadView
              onCommitSuccess={() => {
                refreshStatus();
                setActiveView("dashboard");
              }}
              onNavigate={(v) => setActiveView(v)}
            />
          )}
          {activeView === "mapping" && (
            <MappingView
              onMappingApplied={() => setActiveView("etl")}
              onNavigate={(v) => setActiveView(v)}
            />
          )}
          {activeView === "etl" && (
            <ETLView onETLCompleted={refreshStatus} />
          )}
          {activeView === "schema" && <SchemaView />}
          {activeView === "olap" && <OLAPView />}
          {activeView === "mining" && <MiningView />}
          {activeView === "constraint" && <ConstraintView />}
          {activeView === "classifier" && <ClassifierView />}
          {activeView === "correlation" && <CorrelationView />}
          {activeView === "early_warning" && <EarlyWarningView />}
          {activeView === "reports" && <ReportsView />}
        </div>
      </main>
    </div>
  );
}
