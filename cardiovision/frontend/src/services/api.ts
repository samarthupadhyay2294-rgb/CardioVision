/** Browser uses same-origin /api (Next.js rewrite → backend). Server-side uses env URL. */
export const API_BASE =
  typeof window !== "undefined"
    ? ""
    : process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

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

export async function ensureGuestSession(): Promise<string> {
  const existing = localStorage.getItem("cv_guest");
  if (existing) return existing;
  const res = await fetch(`${API_BASE}/api/auth/guest-session`, { method: "POST" });
  const data = await res.json();
  localStorage.setItem("cv_guest", data.guest_session);
  return data.guest_session;
}

async function parseError(res: Response): Promise<string> {
  try {
    const err = await res.json();
    const detail = err.detail;
    if (typeof detail === "string") return detail;
    if (Array.isArray(detail)) return detail.map((d: { msg?: string }) => d.msg).join(", ");
    return "Request failed";
  } catch {
    return res.status === 0 ? "Cannot reach API — is the backend running on port 8000?" : `Request failed (${res.status})`;
  }
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
  const { report_id } = await uploadRes.json();

  const analyzeRes = await fetch(`${API_BASE}/api/analyze/${report_id}`, {
    method: "POST",
    headers: headers(),
  });
  if (!analyzeRes.ok) throw new Error(await parseError(analyzeRes));
  return analyzeRes.json();
}

export async function getReport(id: string): Promise<AnalysisResult> {
  const res = await fetch(`${API_BASE}/api/report/${id}`, { headers: headers() });
  if (!res.ok) throw new Error("Report not found");
  return res.json();
}

export async function login(email: string, password: string) {
  const res = await fetch(`${API_BASE}/api/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) throw new Error("Invalid credentials");
  const data = await res.json();
  localStorage.setItem("cv_token", data.access_token);
  return data;
}

export async function register(email: string, password: string, full_name?: string) {
  const res = await fetch(`${API_BASE}/api/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password, full_name }),
  });
  if (!res.ok) {
    const e = await res.json().catch(() => ({}));
    throw new Error(e.detail || "Registration failed");
  }
  const data = await res.json();
  localStorage.setItem("cv_token", data.access_token);
  return data;
}

export async function getDashboard() {
  const res = await fetch(`${API_BASE}/api/dashboard`, { headers: headers() });
  if (!res.ok) throw new Error("Dashboard unavailable");
  return res.json();
}

export async function getHistory() {
  const res = await fetch(`${API_BASE}/api/history`, { headers: headers() });
  if (!res.ok) throw new Error("History unavailable");
  return res.json();
}

export function pdfDownloadUrl(reportId: string) {
  const base =
    typeof window !== "undefined"
      ? window.location.origin
      : process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
  return `${base}/api/pdf/${reportId}`;
}
