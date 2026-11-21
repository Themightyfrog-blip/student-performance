import React from "react";

interface MetricCardProps {
  label: string;
  value: string | number;
  delta?: string | null;
  icon?: React.ReactNode;
  color?: "rust" | "pearl" | "blue" | "green" | "amber" | "red" | "slate";
}

export const MetricCard: React.FC<MetricCardProps> = ({
  label,
  value,
  delta,
  icon,
  color = "rust",
}) => {
  const colorMap = {
    rust: "border-[#DDD0B5] bg-white text-[#5D1F02]",
    pearl: "border-[#DDD0B5] bg-[#FAF8F5] text-[#461701]",
    blue: "border-[#DDD0B5] bg-white text-[#5D1F02]",
    green: "border-emerald-200 bg-white text-emerald-950",
    amber: "border-amber-200 bg-white text-amber-950",
    red: "border-rose-200 bg-white text-rose-950",
    slate: "border-[#DDD0B5] bg-white text-stone-900",
  };

  return (
    <div
      className={`rounded-xl border p-5 shadow-xs transition-all hover:shadow-md ${colorMap[color]}`}
    >
      <div className="flex items-center justify-between">
        <span className="text-xs font-bold uppercase tracking-wider text-stone-500">
          {label}
        </span>
        {icon && <div className="text-[#8B3103]">{icon}</div>}
      </div>
      <div className="mt-2 text-2xl font-extrabold tracking-tight text-stone-900">
        {value}
      </div>
      {delta && (
        <div className="mt-1 text-xs font-medium text-stone-500">{delta}</div>
      )}
    </div>
  );
};
