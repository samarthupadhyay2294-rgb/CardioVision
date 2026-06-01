"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { getDashboard, getHistory } from "@/services/api";
import { useAuthStore } from "@/store/auth";

export default function DashboardPage() {
  const router = useRouter();
  const token = useAuthStore((s) => s.token);
  const hydrate = useAuthStore((s) => s.hydrate);
  const [dash, setDash] = useState<Record<string, unknown> | null>(null);
  const [history, setHistory] = useState<{ reports: Array<Record<string, unknown>> } | null>(
    null
  );

  useEffect(() => {
    hydrate();
    if (!localStorage.getItem("cv_token")) {
      router.push("/auth");
      return;
    }
    Promise.all([getDashboard(), getHistory()])
      .then(([d, h]) => {
        setDash(d);
        setHistory(h);
      })
      .catch(() => router.push("/auth"));
  }, [hydrate, router, token]);

  if (!dash) {
    return (
      <div className="mx-auto max-w-6xl px-4 py-24">
        <div className="h-40 animate-pulse rounded-3xl bg-white/5" />
      </div>
    );
  }

  const summary = dash.health_summary as Record<string, number>;
  const trend = (dash.risk_trend as Array<{ date: string; risk_pct: number }>) || [];

  return (
    <div className="mx-auto max-w-6xl px-4 py-12">
      <h1 className="text-3xl font-bold">Health Dashboard</h1>
      <p className="mt-1 text-white/60">Track reports, trends, and cardiovascular risk over time.</p>

      <div className="mt-10 grid gap-6 sm:grid-cols-3">
        <div className="glass rounded-2xl p-6">
          <p className="text-sm text-white/50">Total reports</p>
          <p className="text-3xl font-bold text-primary">{summary.total_reports}</p>
        </div>
        <div className="glass rounded-2xl p-6">
          <p className="text-sm text-white/50">Average risk</p>
          <p className="text-3xl font-bold text-secondary">{summary.average_risk}%</p>
        </div>
        <div className="glass rounded-2xl p-6">
          <p className="text-sm text-white/50">Latest risk</p>
          <p className="text-3xl font-bold">{summary.latest_risk ?? "—"}%</p>
        </div>
      </div>

      <div className="glass mt-10 h-80 rounded-2xl p-6">
        <h2 className="font-semibold">Risk trend</h2>
        <ResponsiveContainer width="100%" height="90%" className="mt-4">
          <LineChart data={trend}>
            <XAxis dataKey="date" tick={{ fill: "#6b7280", fontSize: 11 }} />
            <YAxis domain={[0, 100]} tick={{ fill: "#6b7280", fontSize: 11 }} />
            <Tooltip
              contentStyle={{
                background: "#111827",
                border: "1px solid rgba(255,255,255,0.1)",
              }}
            />
            <Line type="monotone" dataKey="risk_pct" stroke="#2563EB" strokeWidth={2} dot />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="glass mt-10 rounded-2xl p-6">
        <h2 className="font-semibold">Report history</h2>
        <ul className="mt-4 divide-y divide-white/5">
          {(history?.reports || []).map((r) => (
            <li key={String(r.report_id)} className="flex items-center justify-between py-3">
              <div>
                <p className="font-medium">{String(r.file_name)}</p>
                <p className="text-xs text-white/50">{String(r.created_at)}</p>
              </div>
              <div className="flex items-center gap-4">
                <span className="text-secondary">{String(r.risk_pct ?? "—")}%</span>
                <Link
                  href={`/results/${r.report_id}`}
                  className="text-sm text-primary hover:underline"
                >
                  View
                </Link>
              </div>
            </li>
          ))}
        </ul>
        {!history?.reports?.length && (
          <p className="mt-4 text-sm text-white/50">
            No saved reports yet.{" "}
            <Link href="/analyze" className="text-primary">
              Analyze a report
            </Link>
          </p>
        )}
      </div>
    </div>
  );
}
