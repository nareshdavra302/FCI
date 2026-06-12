const COLORS = ["#22d3ee", "#a78bfa", "#f472b6", "#fb923c", "#4ade80", "#94a3b8"];

export function riskColor(level: string): string {
  switch (level) {
    case "critical":
      return "bg-red-500/20 text-red-300 border-red-500/40";
    case "high":
      return "bg-orange-500/20 text-orange-300 border-orange-500/40";
    case "medium":
      return "bg-yellow-500/20 text-yellow-300 border-yellow-500/40";
    default:
      return "bg-slate-500/20 text-slate-300 border-slate-500/40";
  }
}

export function categoryColor(index: number): string {
  return COLORS[index % COLORS.length];
}

export function DateRangePicker({
  value,
  onChange,
  autoRefresh,
  onAutoRefreshChange,
}: {
  value: number;
  onChange: (hours: number) => void;
  autoRefresh?: boolean;
  onAutoRefreshChange?: (v: boolean) => void;
}) {
  const options = [
    { label: "1h", hours: 1 },
    { label: "24h", hours: 24 },
    { label: "7d", hours: 168 },
  ];

  return (
    <div className="flex flex-wrap items-center gap-3">
      <div className="flex rounded-lg border border-slate-700 overflow-hidden">
        {options.map((opt) => (
          <button
            key={opt.hours}
            onClick={() => onChange(opt.hours)}
            className={`px-3 py-1.5 text-sm ${
              value === opt.hours ? "bg-cyan-600 text-white" : "bg-slate-900 text-slate-400 hover:text-white"
            }`}
          >
            {opt.label}
          </button>
        ))}
      </div>
      {onAutoRefreshChange && (
        <label className="flex items-center gap-2 text-sm text-slate-400">
          <input
            type="checkbox"
            checked={autoRefresh}
            onChange={(e) => onAutoRefreshChange(e.target.checked)}
            className="rounded border-slate-600"
          />
          Auto-refresh (30s)
        </label>
      )}
    </div>
  );
}
