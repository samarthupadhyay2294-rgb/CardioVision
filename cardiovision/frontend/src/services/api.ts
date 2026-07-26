/**
 * API Base URL resolution:
 * Uses process.env.NEXT_PUBLIC_API_URL when set (e.g. on Render deployment).
 * In browser, falls back to "" (Next.js same-origin rewrites) if env is not defined.
 * Server-side falls back to http://127.0.0.1:8000.
 */
export const API_BASE =
  process.env.NEXT_PUBLIC_API_URL
    ? process.env.NEXT_PUBLIC_API_URL.replace(/\/$/, "")
    : typeof window !== "undefined"
    ? ""
    : "http://127.0.0.1:8000";

export type AnalysisResult = {
  report_id: string;
  status: string;
  risk_pct?: number;
  risk_category?: string;
  disease_risks?: Record<string, number>;
  shap_factors?: Array<{
    feature: string;
    label: string;
    contribution_pct: number;
    direction: string;
  }>;
  explanations?: string[];
  recommendations?: Record<string, string[]>;
  features?: Record<string, number>;
  parameters?: Array<{
    name: string;
    value: number;
    status: string;
    normal_range?: string;
  }>;
  patient_summary?: Record<string, unknown>;
  pdf_url?: string;
};

function headers(): HeadersInit {
  const h: HeadersInit = { "Content-Type": "application/json" };
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("cv_token");
    const guest = localStorage.getItem("cv_guest");
    if (token) h["Authorization"] = `Bearer ${token}`;
    if (guest) h["X-Guest-Session"] = guest;
  }
  return h;
}

function uploadHeaders(): HeadersInit {
  const h: HeadersInit = {};
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("cv_token");
    const guest = localStorage.getItem("cv_guest");
    if (token) h["Authorization"] = `Bearer ${token}`;
    if (guest) h["X-Guest-Session"] = guest;
  }
  return h;
}

async function safeJson<T = any>(res: Response): Promise<T> {
  const text = await res.text();
  try {
    return JSON.parse(text);
  } catch {
    throw new Error(
      `Invalid response from server (HTTP ${res.status}): ${text.slice(0, 150) || "Empty response"}`
    );
  }
}

async function parseError(res: Response): Promise<string> {
  if (res.status === 429) {
    return "Too many requests. Please wait a few seconds before trying again.";
  }
  if (res.status === 502 || res.status === 503 || res.status === 504) {
    return "Backend service is starting up on Render (free tier cold start). Please wait 30 seconds and try again.";
  }
  try {
    const text = await res.text();
    try {
      const err = JSON.parse(text);
      const detail = err.detail || err.message || err.error;
      if (typeof detail === "string") return detail;
      if (Array.isArray(detail)) return detail.map((d: { msg?: string }) => d.msg).join(", ");
    } catch {
      if (text && text.trim().length > 0 && text.trim().length < 200) {
        return text.trim();
      }
    }
    return `Request failed with status ${res.status}`;
  } catch {
    return res.status === 0
      ? "Cannot reach API — is the backend running?"
      : `Request failed (${res.status})`;
  }
}

export async function ensureGuestSession(): Promise<string> {
  if (typeof window !== "undefined") {
    const existing = localStorage.getItem("cv_guest");
    if (existing) return existing;
  }
  const res = await fetch(`${API_BASE}/api/auth/guest-session`, { method: "POST" });
  if (!res.ok) throw new Error(await parseError(res));
  const data = await safeJson(res);
  if (typeof window !== "undefined" && data?.guest_session) {
    localStorage.setItem("cv_guest", data.guest_session);
  }
  return data.guest_session;
}

export async function uploadAndAnalyze(file: File): Promise<AnalysisResult> {
  await ensureGuestSession();
  const form = new FormData();
  form.append("file", file);

  const uploadRes = await fetch(`${API_BASE}/api/upload`, {
    method: "POST",
    headers: uploadHeaders(),
    body: form,
  });
  if (!uploadRes.ok) throw new Error(await parseError(uploadRes));
  const { report_id } = await safeJson(uploadRes);

  const analyzeRes = await fetch(`${API_BASE}/api/analyze/${report_id}`, {
    method: "POST",
    headers: headers(),
  });
  if (!analyzeRes.ok) throw new Error(await parseError(analyzeRes));
  return safeJson(analyzeRes);
}

export async function getReport(id: string): Promise<AnalysisResult> {
  const res = await fetch(`${API_BASE}/api/report/${id}`, { headers: headers() });
  if (!res.ok) throw new Error(await parseError(res));
  return safeJson(res);
}

export async function login(email: string, password: string) {
  const res = await fetch(`${API_BASE}/api/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) throw new Error(await parseError(res));
  const data = await safeJson(res);
  if (typeof window !== "undefined" && data?.access_token) {
    localStorage.setItem("cv_token", data.access_token);
  }
  return data;
}

export async function register(email: string, password: string, full_name?: string) {
  const res = await fetch(`${API_BASE}/api/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password, full_name }),
  });
  if (!res.ok) throw new Error(await parseError(res));
  const data = await safeJson(res);
  if (typeof window !== "undefined" && data?.access_token) {
    localStorage.setItem("cv_token", data.access_token);
  }
  return data;
}

export async function getDashboard() {
  const res = await fetch(`${API_BASE}/api/dashboard`, { headers: headers() });
  if (!res.ok) throw new Error(await parseError(res));
  return safeJson(res);
}

export async function getHistory() {
  const res = await fetch(`${API_BASE}/api/history`, { headers: headers() });
  if (!res.ok) throw new Error(await parseError(res));
  return safeJson(res);
}

export function pdfDownloadUrl(reportId: string) {
  const base = API_BASE || (typeof window !== "undefined" ? window.location.origin : "http://127.0.0.1:8000");
  return `${base}/api/pdf/${reportId}`;
}

