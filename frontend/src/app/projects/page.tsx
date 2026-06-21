const projects = [
  { name: "CAMera Core", status: "active", tasks: 12, done: 8, updated: "2m ago" },
  { name: "Web Dashboard", status: "active", tasks: 6, done: 2, updated: "15m ago" },
  { name: "Legacy Migrator", status: "paused", tasks: 9, done: 9, updated: "3d ago" },
];

export default function Projects() {
  return (
    <div className="space-y-6 animate-in">
      <h1 className="text-2xl font-bold tracking-tight">Projects</h1>
      <div className="grid gap-3">
        {projects.map((p) => (
          <div key={p.name} className="bg-card border border-border rounded-xl p-5 flex items-center justify-between">
            <div>
              <div className="font-semibold">{p.name}</div>
              <div className="text-sm text-muted mt-0.5">{p.tasks} tasks · {p.done} completed</div>
            </div>
            <div className="flex items-center gap-4">
              <div className="text-xs text-muted font-mono">{p.updated}</div>
              <span className={`px-2.5 py-1 rounded-full text-xs font-mono font-medium ${
                p.status === "active" ? "bg-success/10 text-success" : "bg-muted/10 text-muted"
              }`}>{p.status}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
