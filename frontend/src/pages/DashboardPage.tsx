import { useQuery } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { api, rangeToIso } from "../api/client";
import { categoryColor, DateRangePicker } from "../components/common";
import { KpiCard } from "../components/KpiCard";

export function DashboardPage() {
  const [hours, setHours] = useState(24);
  const [autoRefresh, setAutoRefresh] = useState(false);
  const range = useMemo(() => rangeToIso(hours), [hours]);

  const refetchInterval = autoRefresh ? 30000 : false;

  const overview = useQuery({
    queryKey: ["overview", range],
    queryFn: () => api.overview(range.from, range.to),
    refetchInterval,
  });
  const trends = useQuery({
    queryKey: ["trends", range],
    queryFn: () => api.trends("hour", range.from, range.to),
    refetchInterval,
  });
  const services = useQuery({
    queryKey: ["services", range],
    queryFn: () => api.services(range.from, range.to),
    refetchInterval,
  });
  const categories = useQuery({
    queryKey: ["categories", range],
    queryFn: () => api.categories(range.from, range.to),
    refetchInterval,
  });
  const heatmap = useQuery({
    queryKey: ["heatmap", range],
    queryFn: () => api.heatmap(range.from, range.to),
    refetchInterval,
  });
  const correlation = useQuery({
    queryKey: ["correlation", range],
    queryFn: () => api.correlation(range.from, range.to),
    refetchInterval,
  });

  const heatmapMatrix = useMemo(() => {
    const servicesList = [...new Set(heatmap.data?.map((c) => c.service_name) ?? [])];
    return servicesList.map((service) => {
      const row: Record<string, string | number> = { service };
      for (let h = 0; h < 24; h++) {
        row[`h${h}`] = heatmap.data?.find((c) => c.service_name === service && c.hour === h)?.count ?? 0;
      }
      return row;
    });
  }, [heatmap.data]);

  if (overview.isLoading) return <p className="text-slate-400">Loading dashboard...</p>;

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <h2 className="text-xl font-semibold">Failure Dashboard</h2>
        <DateRangePicker
          value={hours}
          onChange={setHours}
          autoRefresh={autoRefresh}
          onAutoRefreshChange={setAutoRefresh}
        />
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <KpiCard label="Total Failures" value={overview.data?.total_failures ?? 0} />
        <KpiCard label="Failures / Hour" value={overview.data?.failures_per_hour ?? 0} />
        <KpiCard
          label="Delta vs Prior Period"
          value={`${overview.data?.delta_percent ?? 0}%`}
          hint={`Over ${overview.data?.period_hours ?? 0}h window`}
        />
        <KpiCard label="Correlated Windows" value={correlation.data?.length ?? 0} />
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <div className="rounded-lg border border-slate-800 bg-slate-900 p-4">
          <h3 className="mb-4 text-sm font-medium text-slate-300">Failure Trends</h3>
          <ResponsiveContainer width="100%" height={240}>
            <LineChart data={trends.data ?? []}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="bucket" tick={{ fill: "#94a3b8", fontSize: 11 }} tickFormatter={(v) => new Date(v).toLocaleTimeString()} />
              <YAxis tick={{ fill: "#94a3b8", fontSize: 11 }} />
              <Tooltip contentStyle={{ background: "#0f172a", border: "1px solid #334155" }} />
              <Line type="monotone" dataKey="count" stroke="#22d3ee" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="rounded-lg border border-slate-800 bg-slate-900 p-4">
          <h3 className="mb-4 text-sm font-medium text-slate-300">Top Failing Services</h3>
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={services.data ?? []}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="service_name" tick={{ fill: "#94a3b8", fontSize: 11 }} />
              <YAxis tick={{ fill: "#94a3b8", fontSize: 11 }} />
              <Tooltip contentStyle={{ background: "#0f172a", border: "1px solid #334155" }} />
              <Bar dataKey="count" fill="#a78bfa" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <div className="rounded-lg border border-slate-800 bg-slate-900 p-4">
          <h3 className="mb-4 text-sm font-medium text-slate-300">Error Categories</h3>
          <ResponsiveContainer width="100%" height={240}>
            <PieChart>
              <Pie data={categories.data ?? []} dataKey="count" nameKey="category" cx="50%" cy="50%" outerRadius={80} label>
                {(categories.data ?? []).map((_, i) => (
                  <Cell key={i} fill={categoryColor(i)} />
                ))}
              </Pie>
              <Tooltip contentStyle={{ background: "#0f172a", border: "1px solid #334155" }} />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="rounded-lg border border-slate-800 bg-slate-900 p-4">
          <h3 className="mb-4 text-sm font-medium text-slate-300">Service × Hour Heatmap</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead>
                <tr>
                  <th className="p-1 text-left text-slate-500">Service</th>
                  {Array.from({ length: 24 }, (_, h) => (
                    <th key={h} className="p-1 text-slate-500">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {heatmapMatrix.map((row) => (
                  <tr key={row.service as string}>
                    <td className="p-1 text-slate-300">{row.service as string}</td>
                    {Array.from({ length: 24 }, (_, h) => {
                      const count = Number(row[`h${h}`] ?? 0);
                      const intensity = Math.min(count * 40, 255);
                      return (
                        <td
                          key={h}
                          className="p-1 text-center"
                          style={{ background: count ? `rgba(34, 211, 238, ${intensity / 255})` : "transparent" }}
                          title={`${count} failures`}
                        >
                          {count || ""}
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {correlation.data && correlation.data.length > 0 && (
        <div className="rounded-lg border border-slate-800 bg-slate-900 p-4">
          <h3 className="mb-4 text-sm font-medium text-slate-300">Failure Correlation</h3>
          <div className="space-y-2">
            {correlation.data.slice(0, 5).map((entry, i) => (
              <div key={i} className="rounded border border-slate-800 bg-slate-950 p-3 text-sm">
                <span className="text-cyan-400">{entry.services.join(" + ")}</span>
                <span className="text-slate-500"> · {entry.category} · {entry.count} failures</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
