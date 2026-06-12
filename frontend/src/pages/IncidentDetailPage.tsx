import { useQuery } from "@tanstack/react-query";
import { Link, useParams } from "react-router-dom";
import { api } from "../api/client";

export function IncidentDetailPage() {
  const { id } = useParams<{ id: string }>();

  const { data, isLoading, error } = useQuery({
    queryKey: ["incident", id],
    queryFn: () => api.incident(id!),
    enabled: !!id,
  });

  const related = useQuery({
    queryKey: ["related", data?.incident_group_id],
    queryFn: () =>
      api.incidents({
        incident_group_id: data!.incident_group_id!,
        page: 1,
        page_size: 10,
      }),
    enabled: !!data?.incident_group_id,
  });

  if (isLoading) return <p className="text-slate-400">Loading incident...</p>;
  if (error || !data) return <p className="text-red-400">Incident not found</p>;

  return (
    <div className="space-y-6">
      <Link to="/incidents" className="text-sm text-cyan-400 hover:underline">← Back to incidents</Link>

      <div>
        <h2 className="text-xl font-semibold">{data.method} {data.endpoint}</h2>
        <p className="text-sm text-slate-400">{data.service_name} · {new Date(data.timestamp).toLocaleString()}</p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        <div className="rounded-lg border border-slate-800 bg-slate-900 p-4">
          <h3 className="text-sm font-medium text-slate-300">Details</h3>
          <dl className="mt-3 space-y-2 text-sm">
            <div className="flex justify-between"><dt className="text-slate-500">Status</dt><dd>{data.status_code}</dd></div>
            <div className="flex justify-between"><dt className="text-slate-500">Category</dt><dd>{data.error_category}</dd></div>
            <div className="flex justify-between"><dt className="text-slate-500">Group ID</dt><dd className="truncate max-w-xs">{data.incident_group_id ?? "—"}</dd></div>
          </dl>
          {data.incident_group_id && (
            <Link to={`/insights/${data.incident_group_id}`} className="mt-4 inline-block text-sm text-cyan-400 hover:underline">
              View AI insights →
            </Link>
          )}
        </div>

        <div className="rounded-lg border border-slate-800 bg-slate-900 p-4">
          <h3 className="text-sm font-medium text-slate-300">Error Message</h3>
          <p className="mt-2 text-sm text-red-300">{data.error_message}</p>
        </div>
      </div>

      {data.stack_trace && (
        <div className="rounded-lg border border-slate-800 bg-slate-950 p-4">
          <h3 className="text-sm font-medium text-slate-300">Stack Trace</h3>
          <pre className="mt-2 overflow-x-auto text-xs text-slate-400">{data.stack_trace}</pre>
        </div>
      )}

      {data.request_metadata && (
        <div className="rounded-lg border border-slate-800 bg-slate-900 p-4">
          <h3 className="text-sm font-medium text-slate-300">Request Metadata</h3>
          <pre className="mt-2 overflow-x-auto text-xs text-slate-400">{JSON.stringify(data.request_metadata, null, 2)}</pre>
        </div>
      )}

      {data.incident_group_id && related.data && related.data.items.length > 0 && (
        <div className="rounded-lg border border-slate-800 bg-slate-900 p-4">
          <h3 className="text-sm font-medium text-slate-300">Related Failures (same group)</h3>
          <ul className="mt-2 space-y-1 text-sm text-slate-400">
            {related.data.items.filter((i) => i.id !== data.id).slice(0, 5).map((i) => (
              <li key={i.id}>
                <Link to={`/incidents/${i.id}`} className="text-cyan-400 hover:underline">
                  {i.endpoint}
                </Link>
                {" "}— {i.error_message.slice(0, 60)}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
