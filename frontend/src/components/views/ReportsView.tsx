"use client";

import React, { useEffect, useState } from "react";
import { api } from "@/lib/api";
import {
  FileText,
  Download,
  ShieldCheck,
  CheckCircle2,
  FileSpreadsheet,
  Globe,
  Award,
} from "lucide-react";

export const ReportsView: React.FC = () => {
  const [rubric, setRubric] = useState<any[]>([]);
  const [anonymize, setAnonymize] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchRubric = async () => {
      try {
        setLoading(true);
        const res = await api.getRubric();
        setRubric(res.rubric || []);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchRubric();
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-stone-900">
          Export Data & Generate PBL Academic Reports
        </h2>
        <p className="mt-1 text-sm text-stone-500">
          Download publication-ready academic project reports, verified datasets, and audit trails mapped against DWDM evaluation rubric Questions 61–70.
        </p>
      </div>

      {/* FERPA Anonymization Banner */}
      <div className="flex items-center justify-between rounded-xl border border-[#DDD0B5] bg-white p-5 shadow-xs">
        <div className="flex items-center gap-3">
          <ShieldCheck className="h-6 w-6 text-[#8B3103] flex-shrink-0" />
          <div>
            <span className="font-bold text-sm text-stone-900">
              FERPA Academic Privacy Anonymization Mode
            </span>
            <p className="text-xs text-stone-500">
              When enabled, student identifiers and names are pseudonymized (e.g. <code>ANON-001</code>) in generated PDF and HTML reports.
            </p>
          </div>
        </div>
        <label className="relative inline-flex cursor-pointer items-center">
          <input
            type="checkbox"
            checked={anonymize}
            onChange={(e) => setAnonymize(e.target.checked)}
            className="sr-only peer"
          />
          <div className="w-11 h-6 bg-stone-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-stone-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-[#8B3103]"></div>
        </label>
      </div>

      {/* Main Download Options */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
        {/* PDF Download Card in Deep Rust & Pearl Theme */}
        <div className="rounded-xl border border-[#DDD0B5] bg-gradient-to-br from-[#FAECE2] to-white p-6 shadow-xs flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between">
              <span className="rounded bg-[#8B3103] px-2.5 py-1 text-xs font-bold text-[#EAE0CB]">
                Official ReportLab PDF
              </span>
              <FileText className="h-6 w-6 text-[#8B3103]" />
            </div>
            <h3 className="mt-3 text-lg font-bold text-stone-900">
              Consolidated Academic PBL Report (PDF)
            </h3>
            <p className="mt-1 text-xs text-stone-600 leading-relaxed">
              Generates an all-inclusive, multi-page publication-quality PDF containing Star Schema architecture, ETL lineage logs, multidimensional OLAP cubes, multi-level Apriori rules, Decision Tree metrics with zero-target-leakage certification, and evaluator sign-off blocks.
            </p>
          </div>
          <a
            href={`/api/reports/pdf?anonymize=${anonymize}`}
            download
            className="mt-6 inline-flex w-full items-center justify-center gap-2 rounded-lg bg-[#8B3103] px-4 py-2.5 text-xs font-bold text-[#FAF8F5] shadow-xs hover:bg-[#742802] transition"
          >
            <Download className="h-4 w-4" /> Download Academic PDF Report
          </a>
        </div>

        {/* HTML Report Card */}
        <div className="rounded-xl border border-[#DDD0B5] bg-white p-6 shadow-xs flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between">
              <span className="rounded bg-[#FAF8F5] border border-[#DDD0B5] px-2.5 py-1 text-xs font-bold text-stone-700">
                Browser Responsive
              </span>
              <Globe className="h-6 w-6 text-[#8B3103]" />
            </div>
            <h3 className="mt-3 text-lg font-bold text-stone-900">
              Executive Project Summary (HTML)
            </h3>
            <p className="mt-1 text-xs text-stone-600 leading-relaxed">
              Standalone, self-contained HTML report with live styling, warehouse statistics, ETL batch metrics, decision logic tree rules, and correlation findings ready to share or view in any browser.
            </p>
          </div>
          <a
            href={`/api/reports/html?anonymize=${anonymize}`}
            target="_blank"
            rel="noopener noreferrer"
            className="mt-6 inline-flex w-full items-center justify-center gap-2 rounded-lg border border-[#DDD0B5] bg-[#FAF8F5] px-4 py-2.5 text-xs font-bold text-stone-700 shadow-xs hover:bg-[#EAE0CB] transition"
          >
            <Globe className="h-4 w-4" /> View / Download Executive HTML Report
          </a>
        </div>
      </div>

      {/* CSV Dataset Downloads */}
      <div className="rounded-xl border border-[#DDD0B5] bg-white p-6 shadow-xs">
        <h3 className="text-sm font-bold text-stone-900 mb-3">
          Raw Warehouse Datasets & Audit Trails (CSV)
        </h3>
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
          <a
            href="/api/reports/data-csv"
            download
            className="flex items-center justify-between rounded-lg border border-[#DDD0B5] p-4 hover:bg-[#FAF8F5] text-xs transition"
          >
            <div className="flex items-center gap-3">
              <FileSpreadsheet className="h-5 w-5 text-[#8B3103]" />
              <div>
                <div className="font-semibold text-stone-900">Integrated Data Warehouse Dataset</div>
                <div className="text-[11px] text-stone-500">Denormalized fact & dimension outcomes</div>
              </div>
            </div>
            <Download className="h-4 w-4 text-stone-400" />
          </a>

          <a
            href="/api/reports/data-csv"
            download
            className="flex items-center justify-between rounded-lg border border-[#DDD0B5] p-4 hover:bg-[#FAF8F5] text-xs transition"
          >
            <div className="flex items-center gap-3">
              <FileSpreadsheet className="h-5 w-5 text-[#BD4809]" />
              <div>
                <div className="font-semibold text-stone-900">ETL Pipeline Audit Trail</div>
                <div className="text-[11px] text-stone-500">Batch IDs, timestamps, and lineage events</div>
              </div>
            </div>
            <Download className="h-4 w-4 text-stone-400" />
          </a>
        </div>
      </div>

      {/* PBL Rubric Question Mapping */}
      <div className="overflow-hidden rounded-xl border border-[#DDD0B5] bg-white shadow-xs">
        <div className="border-b border-[#EAE0CB] bg-[#FAF8F5] px-6 py-3 font-bold text-xs text-stone-800">
          PBL Evaluation Rubric Mapping & Requirements Matrix (Questions 61–70)
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-[#EAE0CB] text-left text-xs">
            <thead className="bg-[#F5EFE6] text-stone-700">
              <tr>
                <th className="px-4 py-3 font-semibold">Category</th>
                <th className="px-4 py-3 font-semibold">Question</th>
                <th className="px-4 py-3 font-semibold">Academic Requirement</th>
                <th className="px-4 py-3 font-semibold">Module</th>
                <th className="px-4 py-3 font-semibold">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-stone-100 bg-white">
              {rubric.map((r: any, idx: number) => (
                <tr key={idx} className="hover:bg-[#FAF8F5]">
                  <td className="px-4 py-2.5 font-medium text-stone-900">{r.category}</td>
                  <td className="px-4 py-2.5 font-bold text-[#8B3103]">{r.question}</td>
                  <td className="px-4 py-2.5 text-stone-700">{r.title}</td>
                  <td className="px-4 py-2.5 font-mono text-[11px] text-stone-500">{r.module}</td>
                  <td className="px-4 py-2.5">
                    <span className="inline-flex items-center gap-1 rounded bg-[#FAECE2] px-2 py-0.5 text-[10px] font-bold text-[#8B3103] border border-[#EAE0CB]">
                      <CheckCircle2 className="h-3 w-3" /> {r.status}
                    </span>
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
