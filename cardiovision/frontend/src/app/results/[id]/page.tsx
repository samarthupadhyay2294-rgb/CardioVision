"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { Download, UserPlus } from "lucide-react";
import { Button } from "@/components/ui/button";
import { RiskGauge } from "@/components/results/risk-gauge";
import { DiseaseCards } from "@/components/results/disease-cards";
import { ShapChart } from "@/components/results/shap-chart";
import { getReport, pdfDownloadUrl, type AnalysisResult } from "@/services/api";

export default function ResultsPage() {
  const { id } = useParams<{ id: string }>();
  const [data, setData] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getReport(id)
      .then(setData)
      .catch(() => setError("Could not load results"));
  }, [id]);

  if (error) {
    return (
      <div className="mx-auto max-w-lg px-4 py-24 text-center">
        <p className="text-danger">{error}</p>
        <Link href="/analyze" className="mt-4 inline-block text-primary">
          Try again
        </Link>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="mx-auto max-w-6xl px-4 py-24">
        <div className="animate-pulse space-y-4">
          <div className="h-48 rounded-3xl bg-white/5" />
          <div className="h-32 rounded-2xl bg-white/5" />
        </div>
      </div>
    );
  }

  const rec = data.recommendations || {};

  return (
    <div className="mx-auto max-w-6xl px-4 py-12">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold">Analysis Results</h1>
          <p className="mt-1 text-white/60">
            Patient: {(data.patient_summary?.name as string) || "Guest"} · Report {id.slice(0, 8)}
          </p>
        </div>
        <div className="flex gap-2">
          <a href={pdfDownloadUrl(id)} target="_blank" rel="noreferrer">
            <Button variant="secondary">
              <Download className="h-4 w-4" />
              Download PDF
            </Button>
          </a>
          <Link href="/auth">
            <Button>
              <UserPlus className="h-4 w-4" />
              Save history (Sign up)
            </Button>
          </Link>
        </div>
      </div>

      <div className="mt-10 grid gap-8 lg:grid-cols-3">
        <div className="lg:col-span-1">
          {data.risk_pct != null && data.risk_category && (
            <RiskGauge value={data.risk_pct} category={data.risk_category} />
          )}
        </div>
        <div className="lg:col-span-2">
          {data.disease_risks && <DiseaseCards risks={data.disease_risks} />}
        </div>
      </div>

      <div className="mt-10 grid gap-8 lg:grid-cols-2">
        {data.shap_factors && data.shap_factors.length > 0 && (
          <ShapChart factors={data.shap_factors} />
        )}
        <div className="glass rounded-2xl p-6">
          <h3 className="font-semibold">Key risk factors</h3>
          <ul className="mt-4 space-y-2 text-sm text-white/80">
            {(data.explanations || []).map((e) => (
              <li key={e}>• {e}</li>
            ))}
          </ul>
        </div>
      </div>

      {data.parameters && (
        <div className="glass mt-10 overflow-x-auto rounded-2xl p-6">
          <h3 className="mb-4 font-semibold">Extracted parameters</h3>
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="border-b border-white/10 text-white/50">
                <th className="pb-2 pr-4">Parameter</th>
                <th className="pb-2 pr-4">Value</th>
                <th className="pb-2">Status</th>
              </tr>
            </thead>
            <tbody>
              {data.parameters.map((p) => (
                <tr key={p.name} className="border-b border-white/5">
                  <td className="py-2 pr-4 capitalize">{p.name.replace(/_/g, " ")}</td>
                  <td className="py-2 pr-4">{p.value}</td>
                  <td
                    className={`py-2 capitalize ${
                      p.status === "high"
                        ? "text-danger"
                        : p.status === "low"
                          ? "text-warning"
                          : "text-success"
                    }`}
                  >
                    {p.status}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <div className="mt-10 grid gap-6 md:grid-cols-2">
        {(["diet", "exercise", "lifestyle", "follow_up", "monitoring"] as const).map((key) => {
          const items = rec[key];
          if (!items?.length) return null;
          return (
            <div key={key} className="glass rounded-2xl p-6">
              <h3 className="font-semibold capitalize">{key.replace("_", " ")}</h3>
              <ul className="mt-3 space-y-2 text-sm text-white/70">
                {items.map((r: string) => (
                  <li key={r}>• {r}</li>
                ))}
              </ul>
            </div>
          );
        })}
      </div>
    </div>
  );
}
