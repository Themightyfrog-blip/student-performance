"use client";

import React, { useState } from "react";
import { api } from "@/lib/api";
import {
  Upload,
  FileSpreadsheet,
  CheckCircle,
  AlertCircle,
  Zap,
  ArrowRight,
  Database,
  Layers,
} from "lucide-react";

interface UploadViewProps {
  onCommitSuccess: () => void;
  onNavigate: (viewId: string) => void;
}

export const UploadView: React.FC<UploadViewProps> = ({
  onCommitSuccess,
  onNavigate,
}) => {
  const [files, setFiles] = useState<File[]>([]);
  const [uploading, setUploading] = useState(false);
  const [committing, setCommitting] = useState(false);
  const [metadata, setMetadata] = useState<any>(null);
  const [inferred, setInferred] = useState<Record<string, string | null> | null>(null);
  const [message, setMessage] = useState<{ text: string; type: "success" | "error" } | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFiles(Array.from(e.target.files));
    }
  };

  const handleUpload = async () => {
    if (files.length === 0) return;
    try {
      setUploading(true);
      setMessage(null);
      const res = await api.uploadFiles(files);
      setMetadata(res.metadata);
      setInferred(res.inferred_mapping);
      setMessage({
        text: `Successfully uploaded ${files.length} file(s) into memory buffer (${res.metadata.row_count} rows detected).`,
        type: "success",
      });
    } catch (err: any) {
      setMessage({ text: err.message || "Failed to parse uploaded files.", type: "error" });
    } finally {
      setUploading(false);
    }
  };

  const handleCommit = async (enrich: boolean) => {
    try {
      setCommitting(true);
      setMessage(null);
      const res = await api.commitUpload({
        enrich_attendance: enrich,
        deduplicate_strategy: "drop_grain",
        missing_marks_strategy: "impute_subject_mean",
        clean_out_of_bounds: true,
      });
      setMessage({ text: res.message, type: "success" });
      onCommitSuccess();
    } catch (err: any) {
      setMessage({ text: err.message || "Failed to commit into warehouse.", type: "error" });
    } finally {
      setCommitting(false);
    }
  };

  const hasMarks = inferred?.marks_obtained !== null && inferred?.marks_obtained !== undefined;
  const hasAtt = inferred?.attendance_pct !== null && inferred?.attendance_pct !== undefined;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-slate-900">
          Academic Data Ingestion & File Upload
        </h2>
        <p className="mt-1 text-sm text-slate-500">
          Upload your institutional CSV or Excel examination and attendance spreadsheets. Supports single combined files or multiple relational tables.
        </p>
      </div>

      {/* Upload Dropzone */}
      <div className="rounded-xl border border-dashed border-slate-300 bg-white p-8 text-center shadow-sm">
        <input
          type="file"
          id="file-upload"
          multiple
          accept=".csv,.xlsx,.xls"
          onChange={handleFileChange}
          className="hidden"
        />
        <label
          htmlFor="file-upload"
          className="flex cursor-pointer flex-col items-center justify-center space-y-3"
        >
          <div className="rounded-full bg-brand-50 p-4 text-brand-600">
            <Upload className="h-8 w-8" />
          </div>
          <div>
            <span className="font-semibold text-brand-600 hover:text-brand-700">
              Click to choose files
            </span>{" "}
            or drag and drop spreadsheet files
            <p className="text-xs text-slate-500 mt-1">
              Supports .CSV, .XLSX, and .XLS with automatic character encoding detection
            </p>
          </div>
        </label>

        {files.length > 0 && (
          <div className="mt-6 border-t border-slate-100 pt-4">
            <div className="flex flex-wrap items-center justify-center gap-2">
              {files.map((f, i) => (
                <span
                  key={i}
                  className="inline-flex items-center gap-1.5 rounded-lg bg-slate-100 px-3 py-1.5 text-xs font-medium text-slate-800"
                >
                  <FileSpreadsheet className="h-4 w-4 text-brand-600" />
                  {f.name} ({(f.size / 1024).toFixed(1)} KB)
                </span>
              ))}
            </div>
            <button
              onClick={handleUpload}
              disabled={uploading}
              className="mt-4 inline-flex items-center gap-2 rounded-lg bg-brand-600 px-5 py-2 text-sm font-semibold text-white shadow-sm hover:bg-brand-700 disabled:opacity-50"
            >
              {uploading ? "Parsing Spreadsheet..." : "Parse & Buffer Files"}
            </button>
          </div>
        )}
      </div>

      {/* Notification */}
      {message && (
        <div
          className={`flex items-center gap-3 rounded-xl border p-4 text-sm ${
            message.type === "success"
              ? "border-emerald-200 bg-emerald-50 text-emerald-900"
              : "border-red-200 bg-red-50 text-red-900"
          }`}
        >
          {message.type === "success" ? (
            <CheckCircle className="h-5 w-5 text-emerald-600 flex-shrink-0" />
          ) : (
            <AlertCircle className="h-5 w-5 text-red-600 flex-shrink-0" />
          )}
          <span>{message.text}</span>
        </div>
      )}

      {/* Metadata & Actions when buffer populated */}
      {metadata && (
        <div className="space-y-6">
          {/* Ingestion Actions Callout */}
          <div className="rounded-xl border border-[#DDD0B5] bg-[#FAF8F5] p-6 shadow-xs">
            <h3 className="text-base font-bold text-[#8B3103]">
              ⚡ Commit Ingested Records into SQLite Data Warehouse
            </h3>
            <p className="mt-1 text-xs text-stone-700 leading-relaxed">
              Your dataset ({metadata.row_count} rows, {metadata.col_count} columns) is buffered. Choose an ingestion pathway to populate the Star Schema:
            </p>

            <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2">
              {!hasMarks && hasAtt ? (
                <>
                  <div className="rounded-lg border border-[#DDD0B5] bg-white p-4 shadow-xs">
                    <div className="font-semibold text-stone-900 text-sm">
                      Option A: Full PBL Enrichment (Recommended)
                    </div>
                    <p className="mt-1 text-xs text-stone-500">
                      Your file has attendance but lacks marks. Automatically enrich attendance with correlated marks and departments so all 10 PBL modules work seamlessly.
                    </p>
                    <button
                      onClick={() => handleCommit(true)}
                      disabled={committing}
                      className="mt-3 inline-flex w-full items-center justify-center gap-2 rounded-lg bg-[#8B3103] px-4 py-2 text-xs font-semibold text-[#FAF8F5] shadow-xs hover:bg-[#742802] disabled:opacity-50"
                    >
                      <Zap className="h-4 w-4 text-[#EAE0CB]" />
                      {committing ? "Committing..." : "Enrich & Load Warehouse"}
                    </button>
                  </div>

                  <div className="rounded-lg border border-[#DDD0B5] bg-white p-4 shadow-xs">
                    <div className="font-semibold text-stone-900 text-sm">
                      Option B: Raw Attendance Facts Only
                    </div>
                    <p className="mt-1 text-xs text-stone-500">
                      Load only attendance facts into `FactAttendance`. (OLAP exams, decision trees, and GPA roll-ups will remain inactive).
                    </p>
                    <button
                      onClick={() => handleCommit(false)}
                      disabled={committing}
                      className="mt-3 inline-flex w-full items-center justify-center gap-2 rounded-lg border border-[#DDD0B5] bg-white px-4 py-2 text-xs font-semibold text-stone-700 shadow-xs hover:bg-[#FAF8F5] disabled:opacity-50"
                    >
                      <Database className="h-4 w-4 text-[#8B3103]" />
                      {committing ? "Committing..." : "Load Raw Attendance Only"}
                    </button>
                  </div>
                </>
              ) : (
                <div className="sm:col-span-2 rounded-lg border border-[#DDD0B5] bg-white p-4 shadow-xs">
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="font-semibold text-stone-900 text-sm">
                        Standard Star Schema ETL Loading
                      </div>
                      <p className="mt-1 text-xs text-stone-500">
                        Required examination and attendance columns detected. Execute the 3-stage pipeline to populate dimensions and facts.
                      </p>
                    </div>
                    <button
                      onClick={() => handleCommit(false)}
                      disabled={committing}
                      className="inline-flex items-center gap-2 rounded-lg bg-[#8B3103] px-5 py-2.5 text-xs font-semibold text-[#FAF8F5] shadow-xs hover:bg-[#742802] disabled:opacity-50"
                    >
                      <Layers className="h-4 w-4 text-[#EAE0CB]" />
                      {committing ? "Executing ETL..." : "Process & Load into Data Warehouse"}
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Sample Rows Table */}
          {metadata.sample_head && (
            <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
              <div className="border-b border-slate-200 bg-slate-50 px-6 py-3 font-bold text-xs text-slate-700">
                Uploaded Records Preview (First 5 Rows)
              </div>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-slate-200 text-left text-xs">
                  <thead className="bg-slate-100 text-slate-600">
                    <tr>
                      {metadata.columns.map((col: string) => (
                        <th key={col} className="px-3 py-2 font-semibold">
                          {col}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 bg-white">
                    {metadata.sample_head.map((row: any, idx: number) => (
                      <tr key={idx} className="hover:bg-slate-50">
                        {metadata.columns.map((col: string) => (
                          <td key={col} className="px-3 py-2 text-slate-700">
                            {row[col] !== null && row[col] !== undefined ? String(row[col]) : "—"}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
