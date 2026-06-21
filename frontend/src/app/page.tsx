const stats = [
  { label: "Agents", value: "7", sub: "all online" },
  { label: "Projects", value: "2", sub: "1 active" },
  { label: "Tasks", value: "18", sub: "4 in progress" },
  { label: "Memory", value: "143", sub: "entries stored" },
];

const recent = [
  { time: "14:32", event: "Reviewer approved PR #12", type: "success" },
  { time: "14:15", event: "Coder implemented auth middleware", type: "info" },
  { time: "13:48", event: "Tester found 3 failing tests in core/", type: "error" },
  { time: "13:20", event: "Memory pruned 12 stale entries", type: "info" },
  { time: "12:55", event: "Debugger diagnosed API timeout issue", type: "warning" },
];

export default function Dashboard() {
  return (
    <div className="space-y-8">
      <div className="animate-in">
        <h1 className="text-2xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-muted text-sm mt-1">System overview and recent activity</p>
      </div>

      <div className="grid grid-cols-4 gap-4 animate-in">
        {stats.map((s) => (
          <div key={s.label} className="bg-card border border-border rounded-xl p-5">
            <div className="text-2xl font-mono font-bold text-accent">{s.value}</div>
            <div className="text-sm font-medium mt-1">{s.label}</div>
            <div className="text-xs text-muted mt-0.5">{s.sub}</div>
          </div>
        ))}
      </div>

      <div className="animate-in">
        <h2 className="text-lg font-semibold mb-3">Recent Activity</h2>
        <div className="bg-card border border-border rounded-xl divide-y divide-border">
          {recent.map((r) => (
            <div key={r.time} className="flex items-center gap-4 px-5 py-3 text-sm">
              <span className="font-mono text-xs text-muted w-12 shrink-0">{r.time}</span>
              <span className={`w-1.5 h-1.5 rounded-full shrink-0 ${
                r.type === "success" ? "bg-success" :
                r.type === "error" ? "bg-error" :
                r.type === "warning" ? "bg-accent" : "bg-muted"
              }`} />
              <span>{r.event}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
