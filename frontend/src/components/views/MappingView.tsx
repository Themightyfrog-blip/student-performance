"use client";

import React, { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { CheckCircle2, AlertTriangle, ArrowRight, Shuffle } from "lucide-react";

interface MappingViewProps {
  onMappingApplied: () => void;
  onNavigate: (viewId: string) => void;
}

export const MappingView: React.FC<MappingViewProps> = ({
  onMappingApplied,
  onNavigate,
}) => {
  const [canonicalFields, setCanonicalFields] = useState<Record<string, any>>({});
  const [selectedMapping, setSelectedMapping] = useState<Record<string, string>>({});
  const [availableColumns, setAvailableColumns] = useState<string[]>([]);
  const [availability, setAvailability] = useState<Record<string, any>>({});
  const [loading, setLoading] = useState(true);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    const init = async () => {
      try {
        setLoading(true);
        const canonRes = await api.getCanonicalFields();
        setCanonicalFields(canonRes.canonical_fields);

        // Fetch buffer status to get available columns
        const status = await api.getStatus();
        if (status.buffer_rows > 0) {
          // Check audit or upload
          const auditRes = await api.getQualityAudit();
          // We can also infer from canon
        }

        // Initialize availability check
        const initialKeys = Object.keys(selectedMapping);
        const availRes = await api.checkMapping(selectedMapping);
        setAvailability(availRes.feature_availability);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    init();
  }, []);

  const handleSelectChange = async (canon: string, val: string) => {
    const updated = { ...selectedMapping };
    if (val === "-- None --") {
      delete updated[canon];
    } else {
      updated[canon] = val;
    }
    setSelectedMapping(updated);

    try {
      const res = await api.checkMapping(updated);
      setAvailability(res.feature_availability);
    } catch {}
  };

  const handleSave = () => {
    setSaved(true);
    onMappingApplied();
    setTimeout(() => setSaved(false), 3000);
  };

  if (loading) {
    return (
      <div className="flex h-64 items-center justify-center text-slate-500">
        <div className="h-6 w-6 animate-spin rounded-full border-2 border-brand-600 border-t-transparent mr-2" />
        Loading Schema Mapping Matrix...
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-slate-900">
          Flexible Schema & Column Mapping
        </h2>
        <p className="mt-1 text-sm text-slate-500">
          Map your spreadsheet columns to canonical university entities. Alias detection automatically resolves standard variants like `roll_no`, `cie`, and `sgpa`.
        </p>
      </div>

      {/* Feature Availability Grid */}
      <div className="rounded-xl border border-[#DDD0B5] bg-white p-6 shadow-xs">
        <h3 className="text-sm font-bold text-stone-900">
          🎯 DWDM PBL Feature Availability Matrix
        </h3>
        <p className="text-xs text-stone-500 mt-1">
          Real-time check of which analytical operations are unlocked by current column mappings:
        </p>
        <div className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {Object.entries(availability).map(([feature, status]: [string, any]) => (
            <div
              key={feature}
              className={`rounded-lg border p-3.5 transition ${
                status.available
                  ? "border-emerald-200 bg-emerald-50/60"
                  : "border-[#DDD0B5] bg-[#FAF8F5]"
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-stone-900">{feature}</span>
                {status.available ? (
                  <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-emerald-700">
                    <CheckCircle2 className="h-3.5 w-3.5" /> Ready
                  </span>
                ) : (
                  <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-amber-700">
                    <AlertTriangle className="h-3.5 w-3.5" /> Inactive
                  </span>
                )}
              </div>
              {!status.available && (
                <p className="mt-1.5 text-[11px] text-stone-500">
                  Missing: <code className="text-rose-600">{status.missing.join(", ")}</code>
                </p>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Mapping Controls */}
      <div className="rounded-xl border border-[#DDD0B5] bg-white p-6 shadow-xs">
        <div className="flex items-center justify-between border-b border-[#EAE0CB] pb-4">
          <div>
            <h3 className="text-sm font-bold text-stone-900">Canonical Entity Mappings</h3>
            <p className="text-xs text-stone-500">Assign source columns to data warehouse target fields</p>
          </div>
          <button
            onClick={handleSave}
            className="inline-flex items-center gap-2 rounded-lg bg-brand-600 px-4 py-2 text-xs font-semibold text-white shadow-xs hover:bg-brand-700 transition"
          >
            <Shuffle className="h-4 w-4" />
            {saved ? "Mapping Confirmed!" : "Save & Apply Mapping"}
          </button>
        </div>

        <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2">
          {Object.entries(canonicalFields).map(([key, info]: [string, any]) => (
            <div key={key} className="space-y-1.5 rounded-lg border border-[#EAE0CB] bg-[#FAF8F5] p-3.5">
              <div className="flex items-center justify-between text-xs">
                <label className="font-semibold text-stone-800">
                  {info.label} {info.required && <span className="text-rose-500">*</span>}
                </label>
                <span className="font-mono text-[10px] text-stone-400">{key}</span>
              </div>
              <input
                type="text"
                placeholder={`Mapped to: ${info.aliases?.[0] || key}`}
                value={selectedMapping[key] || ""}
                onChange={(e) => handleSelectChange(key, e.target.value)}
                className="w-full rounded-md border border-[#DDD0B5] bg-white px-3 py-1.5 text-xs text-stone-800 shadow-xs focus:border-brand-500 focus:outline-hidden"
              />
              <p className="text-[10px] text-stone-400">
                Common aliases: {info.aliases?.slice(0, 4).join(", ")}
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
