"use client";

import {
  Bar,
  BarChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

type ShapItem = {
  label: string;
  contribution_pct: number;
};

export function ShapChart({ factors }: { factors: ShapItem[] }) {
  const data = factors.slice(0, 8).map((f) => ({
    name: f.label.length > 22 ? f.label.slice(0, 20) + "…" : f.label,
    pct: f.contribution_pct,
  }));

  return (
    <div className="glass h-72 rounded-2xl p-4">
      <h3 className="mb-4 font-semibold">Top risk drivers (SHAP)</h3>
      <ResponsiveContainer width="100%" height="85%">
        <BarChart data={data} layout="vertical" margin={{ left: 8, right: 16 }}>
          <XAxis type="number" hide />
          <YAxis type="category" dataKey="name" width={120} tick={{ fill: "#9ca3af", fontSize: 11 }} />
          <Tooltip
            contentStyle={{
              background: "#111827",
              border: "1px solid rgba(255,255,255,0.1)",
              borderRadius: 8,
            }}
          />
          <Bar dataKey="pct" fill="#2563EB" radius={[0, 4, 4, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
