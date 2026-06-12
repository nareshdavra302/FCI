import { useQuery } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { api, rangeToIso } from "../api/client";
import { DateRangePicker } from "../components/common";

export function IncidentsPage() {
  const [hours, setHours] = useState(24);
  const [service, setService] = useState("");
  const [category, setCategory] = useState("");
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const range = useMemo(() => rangeToIso(hours), [hours]);

  const { data, isLoading } = useQuery({
    queryKey: ["incidents", range, service, category, search, page],
    queryFn: () =>
      api.incidents({
        from: range.from,
        to: range.to,
        service: service || undefined,
        category: category || undefined,
        search: search || undefined,
        page,
        page_size: 20,
      }),
  });

  const totalPages = data ? Math.ceil(data.total / data.page_size) : 1;

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <h2 className="text-xl font-semibold">Incidents</h2>
        <DateRangePicker value={hours} onChange={setHours} />
      </div>

      <div className="grid gap-3 sm:grid-cols-4">
        <input
          className="rounded border border-slate-700 bg-slate-900 px-3 py-2 text-sm"
          placeholder="Search..."
          value={search}
          onChange={(e) => { setSearch(e.target.value); setPage(1); }}
        />
        <select
          className="rounded border border-slate-700 bg-slate-900 px-3 py-2 text-sm"
          value={service}
          onChange={(e) => { setService(e.target.value); setPage(1); }}
        >
          <option value="">All services</option>
          <option value="service-a">service-a</option>
          <option value="service-b">service-b</option>
          <option value="service-c">service-c</option>
        </select>
        <select
          className="rounded border border-slate-700 bg-slate-900 px-3 py-2 text-sm"
          value={category}
          onChange={(e) => { setCategory(e.target.value); setPage(1); }}
        >
          <option value="">All categories</option>
          <option value="database">database</option>
          <option value="timeout">timeout</option>
          <option value="dependency">dependency</option>
          <option value="authentication">authentication</option>
          <option value="configuration">configuration</option>
          <option value="unknown">unknown</option>
        </select>
      </div>

      {isLoading ? (
        <p className="text-slate-400">Loading incidents...</p>
      ) : (
        <div className="overflow-x-auto rounded-lg border border-slate-800">
          <table className="w-full text-sm">
            <thead className="bg-slate-900 text-left text-slate-400">
              <tr>
                <th className="p-3">Time</th>
                <th className="p-3">Service</th>
                <th className="p-3">Endpoint</th>
                <th className="p-3">Category</th>
                <th className="p-3">Error</th>
              </tr>
            </thead>
            <tbody>
              {data?.items.map((item) => (
                <tr key={item.id} className="border-t border-slate-800 hover:bg-slate-900/50">
                  <td className="p-3 whitespace-nowrap">{new Date(item.timestamp).toLocaleString()}</td>
                  <td className="p-3">{item.service_name}</td>
                  <td className="p-3">
                    <Link to={`/incidents/${item.id}`} className="text-cyan-400 hover:underline">
                      {item.method} {item.endpoint}
                    </Link>
                  </td>
                  <td className="p-3">
                    <span className="rounded bg-slate-800 px-2 py-0.5 text-xs">{item.error_category}</span>
                  </td>
                  <td className="p-3 max-w-md truncate text-slate-400">{item.error_message}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <div className="flex items-center justify-between text-sm text-slate-400">
        <span>{data?.total ?? 0} total incidents</span>
        <div className="flex gap-2">
          <button
            disabled={page <= 1}
            onClick={() => setPage((p) => p - 1)}
            className="rounded border border-slate-700 px-3 py-1 disabled:opacity-40"
          >
            Prev
          </button>
          <span>Page {page} / {totalPages}</span>
          <button
            disabled={page >= totalPages}
            onClick={() => setPage((p) => p + 1)}
            className="rounded border border-slate-700 px-3 py-1 disabled:opacity-40"
          >
            Next
          </button>
        </div>
      </div>
    </div>
  );
}
