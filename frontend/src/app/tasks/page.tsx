const tasks = [
  { title: "Implement auth middleware", project: "CAMera Core", status: "in_progress", agent: "Coder" },
  { title: "Review PR #12", project: "CAMera Core", status: "pending", agent: "Reviewer" },
  { title: "Write API integration tests", project: "Web Dashboard", status: "pending", agent: "Tester" },
  { title: "Fix timeout in memory search", project: "CAMera Core", status: "in_progress", agent: "Debugger" },
  { title: "Design project settings page", project: "Web Dashboard", status: "completed", agent: "Coder" },
];

const badge = (s: string) => {
  const m: Record<string, string> = {
    in_progress: "bg-accent/10 text-accent",
    pending: "bg-muted/10 text-muted",
    completed: "bg-success/10 text-success",
  };
  return m[s] || "bg-muted/10 text-muted";
};

export default function Tasks() {
  return (
    <div className="space-y-6 animate-in">
      <h1 className="text-2xl font-bold tracking-tight">Tasks</h1>
      <div className="bg-card border border-border rounded-xl divide-y divide-border">
        {tasks.map((t) => (
          <div key={t.title} className="flex items-center gap-4 px-5 py-4">
            <input type="checkbox" aria-label={`Mark "${t.title}" as complete`} className="accent-accent rounded" />
            <div className="flex-1 min-w-0">
              <div className="text-sm font-medium truncate">{t.title}</div>
              <div className="text-xs text-muted">{t.project}</div>
            </div>
            <span className="text-xs text-muted font-mono shrink-0">{t.agent}</span>
            <span className={`px-2 py-0.5 rounded-full text-xs font-mono shrink-0 ${badge(t.status)}`}>
              {t.status.replace("_", " ")}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
