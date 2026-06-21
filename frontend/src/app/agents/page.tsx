const agents = [
  { name: "Orchestrator", type: "manager", status: "idle", tasks: 24, icon: "⧉" },
  { name: "Coder", type: "implementation", status: "busy", tasks: 18, icon: "⊡" },
  { name: "Reviewer", type: "quality", status: "idle", tasks: 31, icon: "⊟" },
  { name: "Tester", type: "validation", status: "idle", tasks: 27, icon: "⊠" },
  { name: "Memory", type: "knowledge", status: "idle", tasks: 143, icon: "⊞" },
  { name: "Debugger", type: "diagnostics", status: "busy", tasks: 9, icon: "⊡" },
];

export default function Agents() {
  return (
    <div className="space-y-6 animate-in">
      <h1 className="text-2xl font-bold tracking-tight">Agents</h1>
      <div className="grid grid-cols-3 gap-4">
        {agents.map((a) => (
          <div key={a.name} className="bg-card border border-border rounded-xl p-5">
            <div className="flex items-center justify-between mb-3">
              <div className="w-10 h-10 rounded-lg bg-accent/10 flex items-center justify-center text-accent text-lg">{a.icon}</div>
              <span className={`px-2 py-0.5 rounded-full text-xs font-mono ${
                a.status === "busy" ? "bg-accent/10 text-accent" : "bg-success/10 text-success"
              }`}>{a.status}</span>
            </div>
            <div className="font-semibold">{a.name}</div>
            <div className="text-xs text-muted mt-0.5">{a.type}</div>
            <div className="text-xs text-muted mt-2 font-mono">{a.tasks} tasks processed</div>
          </div>
        ))}
      </div>
    </div>
  );
}
