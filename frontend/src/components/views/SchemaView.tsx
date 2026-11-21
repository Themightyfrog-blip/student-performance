"use client";

import React, { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { Database, Key, Layers, GitBranch, ArrowRight } from "lucide-react";

export const SchemaView: React.FC = () => {
  const [schemaInfo, setSchemaInfo] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchSchema = async () => {
      try {
        setLoading(true);
        const res = await api.getSchemaInfo();
        setSchemaInfo(res);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchSchema();
  }, []);

  if (loading) {
    return (
      <div className="flex h-64 items-center justify-center text-slate-500">
        <div className="h-6 w-6 animate-spin rounded-full border-2 border-brand-600 border-t-transparent mr-2" />
        Loading Star Schema Architecture...
      </div>
    );
  }

  const facts = schemaInfo?.fact_grains || {};
  const dimensions = schemaInfo?.dimensions || {};

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-slate-900">
          Relational Star Schema Architecture (Questions 61–62)
        </h2>
        <p className="mt-1 text-sm text-slate-500">
          Formal dimensional model with declared fact grain, surrogate keys, and composite uniqueness constraints enforcing data warehouse integrity.
        </p>
      </div>

      {/* Fact Table Details */}
      <div className="space-y-4">
        <h3 className="text-base font-bold text-stone-900 flex items-center gap-2">
          <Database className="h-5 w-5 text-brand-600" />
          Fact Tables & Granularity Declarations
        </h3>

        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          {Object.entries(facts).map(([name, info]: [string, any]) => (
            <div key={name} className="rounded-xl border border-[#DDD0B5] bg-white p-6 shadow-xs">
              <div className="flex items-center justify-between">
                <span className="font-mono text-base font-bold text-stone-900">{name}</span>
                <span className="rounded bg-[#FAECE2] border border-[#DDD0B5] px-2.5 py-1 text-xs font-semibold text-[#8B3103]">
                  Fact Table
                </span>
              </div>
              <div className="mt-3 space-y-2 text-xs">
                <div>
                  <span className="font-semibold text-stone-500">Declared Grain:</span>{" "}
                  <span className="text-stone-800">{info.grain}</span>
                </div>
                <div>
                  <span className="font-semibold text-stone-500">Surrogate Key:</span>{" "}
                  <code className="text-[#8B3103] font-bold">{info.surrogate_key}</code>
                </div>
                <div>
                  <span className="font-semibold text-stone-500">Foreign Keys:</span>{" "}
                  <span className="text-stone-700">{info.dimension_keys?.join(", ")}</span>
                </div>
              </div>

              <div className="mt-4 border-t border-[#EAE0CB] pt-3">
                <span className="text-xs font-bold text-stone-700">Numeric Measures:</span>
                <div className="mt-2 space-y-1.5">
                  {info.measures?.map((m: any, idx: number) => (
                    <div key={idx} className="flex justify-between text-xs bg-[#FAF8F5] p-2 rounded border border-[#EAE0CB]">
                      <span className="font-semibold text-stone-800">{m.name}</span>
                      <span className="text-stone-500">{m.type}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Dimension Tables */}
      <div className="space-y-4">
        <h3 className="text-base font-bold text-stone-900 flex items-center gap-2">
          <Layers className="h-5 w-5 text-brand-600" />
          Dimension Dictionaries & Concept Hierarchies
        </h3>

        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Object.entries(dimensions).map(([dName, dInfo]: [string, any]) => (
            <div key={dName} className="rounded-xl border border-[#DDD0B5] bg-white p-5 shadow-xs space-y-2">
              <div className="flex items-center justify-between">
                <span className="font-mono text-sm font-bold text-stone-900">{dName}</span>
                <span className="rounded bg-[#F5EFE6] border border-[#DDD0B5] px-2 py-0.5 text-[10px] font-semibold text-stone-700">
                  Dimension
                </span>
              </div>
              <div className="text-xs space-y-1 text-stone-600">
                <div>
                  <span className="text-stone-400">PK:</span>{" "}
                  <code className="text-[#8B3103] font-bold">{dInfo.surrogate_key}</code> |{" "}
                  <span className="text-stone-400">Natural:</span> {dInfo.natural_key}
                </div>
                <div>
                  <span className="text-stone-400">Hierarchy:</span>{" "}
                  <strong className="text-stone-800">{dInfo.hierarchy}</strong>
                </div>
                <div>
                  <span className="text-stone-400">Attributes:</span> {dInfo.attributes?.join(", ")}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
