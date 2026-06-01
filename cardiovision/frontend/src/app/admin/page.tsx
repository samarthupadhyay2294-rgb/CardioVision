"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

export default function AdminPage() {
  const router = useRouter();
  const [data, setData] = useState<Record<string, unknown> | null>(null);

  useEffect(() => {
    const token = localStorage.getItem("cv_token");
    if (!token) {
      router.push("/auth");
      return;
    }
    fetch(`${process.env.NEXT_PUBLIC_API_URL || ""}/api/admin/overview`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((r) => {
        if (!r.ok) throw new Error("Forbidden");
        return r.json();
      })
      .then(setData)
      .catch(() => router.push("/dashboard"));
  }, [router]);

  if (!data) return <div className="p-24 text-center">Loading admin panel...</div>;

  const dist = data.risk_distribution as Record<string, number>;
  const stats = [
    { label: "Users", value: String(data.users ?? 0) },
    { label: "Reports", value: String(data.reports ?? 0) },
    { label: "Predictions", value: String(data.predictions ?? 0) },
    { label: "Avg risk", value: `${data.average_risk ?? 0}%` },
  ];

  return (
    <div className="mx-auto max-w-6xl px-4 py-12">
      <h1 className="text-3xl font-bold">Admin Dashboard</h1>
      <div className="mt-10 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((item) => (
          <div key={item.label} className="glass rounded-2xl p-6">
            <p className="text-sm text-white/50">{item.label}</p>
            <p className="text-2xl font-bold">{item.value}</p>
          </div>
        ))}
      </div>
      <div className="glass mt-8 rounded-2xl p-6">
        <h2 className="font-semibold">Risk distribution</h2>
        <div className="mt-4 grid grid-cols-4 gap-4 text-center">
          {Object.entries(dist || {}).map(([k, v]) => (
            <div key={k} className="rounded-xl bg-white/5 p-4">
              <p className="text-2xl font-bold text-primary">{v}</p>
              <p className="text-xs capitalize text-white/50">{k}</p>
            </div>
          ))}
        </div>
        <p className="mt-6 text-sm text-success">System: {String(data.system_health)}</p>
      </div>
    </div>
  );
}
