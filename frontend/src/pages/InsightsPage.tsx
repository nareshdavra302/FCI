import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { api, rangeToIso } from "../api/client";
import { riskColor } from "../components/common";

export function InsightsPage() {
  const queryClient = useQueryClient();
  const range = rangeToIso(24);

  const { data, isLoading } = useQuery({
    queryKey: ["insights"],
    queryFn: api.insights,
  });

  const analyze = useMutation({
    mutationFn: () => api.analyze({ from_time: range.from, to_time: range.to }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["insights"] }),
  });

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <h2 className="text-xl font-semibold">AI Insights</h2>
        <button
          onClick={() => analyze.mutate()}
          disabled={analyze.isPending}
          className="rounded bg-cyan-600 px-4 py-2 text-sm font-medium hover:bg-cyan-500 disabled:opacity-50"
        >
          {analyze.isPending ? "Analyzing..." : "Analyze now (last 24h)"}
        </button>
      </div>

      {analyze.isError && (
        <p className="text-sm text-red-400">Analysis failed. Ensure the API is running and failures exist.</p>
      )}

      {isLoading ? (
        <p className="text-slate-400">Loading insights...</p>
      ) : !data?.length ? (
        <div className="rounded-lg border border-slate-800 bg-slate-900 p-8 text-center text-slate-400">
          <p>No insight reports yet.</p>
          <p className="mt-2 text-sm">Run the failure simulator, then click Analyze now.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {data.map((report) => (
            <Link
              key={report.id}
              to={`/insights/${report.incident_group_id}`}
              className="block rounded-lg border border-slate-800 bg-slate-900 p-4 hover:border-slate-600"
            >
              <div className="flex flex-wrap items-center gap-3">
                <span className={`rounded border px-2 py-0.5 text-xs uppercase ${riskColor(report.risk_level)}`}>
                  {report.risk_level}
                </span>
                <span className="rounded bg-slate-800 px-2 py-0.5 text-xs text-slate-400">{report.generated_by}</span>
                <span className="text-xs text-slate-500">{new Date(report.created_at).toLocaleString()}</span>
              </div>
              <p className="mt-2 text-sm text-slate-200">{report.summary}</p>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
