const entries = [
  { key: "user/preferred_model", value: "qwen2.5-coder:7b", category: "preference", age: "2d" },
  { key: "arch/database_schema", value: "SQLite with SQLAlchemy 2.0", category: "architecture", age: "5d" },
  { key: "lesson/auth_pattern", value: "JWT tokens expire at 30min", category: "lesson", age: "1d" },
  { key: "bug/fix_null_error", value: "Missing datetime import in agent.py", category: "bug", age: "3h" },
  { key: "decision/orm_choice", value: "SQLAlchemy over raw SQL for portability", category: "decision", age: "7d" },
];

export default function Memory() {
  return (
    <div className="space-y-6 animate-in">
      <h1 className="text-2xl font-bold tracking-tight">Memory</h1>
      <div className="flex gap-2 mb-2">
        {["all", "preference", "architecture", "lesson", "bug", "decision"].map((c) => (
          <button key={c} type="button" className={`px-3 py-1.5 rounded-lg text-xs font-mono transition-colors ${
            c === "all" ? "bg-accent text-black" : "bg-card border border-border text-muted hover:text-foreground"
          }`}>{c}</button>
        ))}
      </div>
      <div className="bg-card border border-border rounded-xl divide-y divide-border">
        {entries.map((e) => (
          <div key={e.key} className="px-5 py-4">
            <div className="flex items-center justify-between">
              <code className="text-sm font-mono text-accent">{e.key}</code>
              <span className="text-xs text-muted">{e.age}</span>
            </div>
            <div className="text-sm text-muted mt-1">{e.value}</div>
            <span className="text-[10px] text-muted font-mono mt-1.5 inline-block">{e.category}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
