const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

export type Failure = {
  id: string;
  service_name: string;
  endpoint: string;
  method: string;
  status_code: number;
  error_message: string;
  stack_trace: string | null;
  error_category: string;
  request_metadata: Record<string, unknown> | null;
  timestamp: string;
  incident_group_id: string | null;
  created_at: string;
};

export type PaginatedFailures = {
  items: Failure[];
  total: number;
  page: number;
  page_size: number;
};

export type OverviewStats = {
  total_failures: number;
  failures_per_hour: number;
  delta_percent: number;
  period_hours: number;
};

export type TrendPoint = { bucket: string; count: number };
export type ServiceCount = { service_name: string; count: number };
export type CategoryCount = { category: string; count: number };
export type HeatmapCell = { service_name: string; hour: number; count: number };
export type CorrelationEntry = {
  services: string[];
  category: string;
  count: number;
  window_start: string;
  window_end: string;
};

export type InsightReport = {
  id: string;
  incident_group_id: string;
  summary: string;
  root_cause_hypotheses: string[];
  recommendations: string[];
  risk_level: string;
  remediation_steps: string[];
  operational_signals: Record<string, unknown> | null;
  generated_by: string;
  created_at: string;
};

function qs(params: Record<string, string | number | undefined>): string {
  const search = new URLSearchParams();
  Object.entries(params).forEach(([k, v]) => {
    if (v !== undefined && v !== "") search.set(k, String(v));
  });
  const s = search.toString();
  return s ? `?${s}` : "";
}

async function fetchJson<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, init);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export const api = {
  overview: (from?: string, to?: string) =>
    fetchJson<OverviewStats>(`/api/v1/analytics/overview${qs({ from, to })}`),
  trends: (interval = "hour", from?: string, to?: string) =>
    fetchJson<TrendPoint[]>(`/api/v1/analytics/trends${qs({ interval, from, to })}`),
  services: (from?: string, to?: string) =>
    fetchJson<ServiceCount[]>(`/api/v1/analytics/services${qs({ from, to })}`),
  categories: (from?: string, to?: string) =>
    fetchJson<CategoryCount[]>(`/api/v1/analytics/categories${qs({ from, to })}`),
  heatmap: (from?: string, to?: string) =>
    fetchJson<HeatmapCell[]>(`/api/v1/analytics/heatmap${qs({ from, to })}`),
  correlation: (from?: string, to?: string) =>
    fetchJson<CorrelationEntry[]>(`/api/v1/analytics/correlation${qs({ from, to })}`),
  incidents: (params: Record<string, string | number | undefined>) =>
    fetchJson<PaginatedFailures>(`/api/v1/incidents${qs(params)}`),
  incident: (id: string) => fetchJson<Failure>(`/api/v1/incidents/${id}`),
  insights: () => fetchJson<InsightReport[]>("/api/v1/insights"),
  insight: (groupId: string) => fetchJson<InsightReport>(`/api/v1/insights/${groupId}`),
  analyze: (body: { from_time?: string; to_time?: string; incident_group_id?: string }) =>
    fetchJson<InsightReport[]>("/api/v1/insights/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    }),
};

export function rangeToIso(hours: number): { from: string; to: string } {
  const to = new Date();
  const from = new Date(to.getTime() - hours * 3600 * 1000);
  return { from: from.toISOString(), to: to.toISOString() };
}
