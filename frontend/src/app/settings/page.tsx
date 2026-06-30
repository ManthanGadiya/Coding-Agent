"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";

export default function SettingsPage() {
  const [mode, setMode] = useState("");
  const [models, setModels] = useState<string[]>([]);
  const [selectedModel, setSelectedModel] = useState("");
  const [mcpServers, setMcpServers] = useState<any[]>([]);
  const [serverName, setServerName] = useState("");
  const [serverType, setServerType] = useState("stdio");
  const [serverCmd, setServerCmd] = useState("");
  const [tab, setTab] = useState<"autonomy" | "mcp">("autonomy");

  useEffect(() => {
    api.autonomy.mode().then((d) => setMode(d.mode)).catch(() => {});
    api.llm.models().then((d: any) => { const m = Array.isArray(d) ? d : []; setModels(m); if (m.length) setSelectedModel(m[0]); }).catch(() => {});
    api.mcp.servers().then(setMcpServers).catch(() => {});
  }, []);

  function setAutonomy(m: string) { api.autonomy.setMode(m).then(() => setMode(m)).catch(() => {}); }
  function setLlm(m: string) { setSelectedModel(m); api.llm.select(m).catch(() => {}); }

  function addServer() {
    const config = serverType === "stdio" ? { command: serverCmd } : { url: serverCmd };
    api.mcp.add(serverName, { transport: serverType, ...config }).then(() => {
      api.mcp.servers().then(setMcpServers); setServerName(""); setServerCmd("");
    }).catch(() => {});
  }
  function removeServer(name: string) { api.mcp.remove(name).then(() => api.mcp.servers().then(setMcpServers)).catch(() => {}); }
  function connectServer(name: string) { api.mcp.connect(name).then(() => api.mcp.servers().then(setMcpServers)).catch(() => {}); }
  function disconnectServer(name: string) { api.mcp.disconnect(name).then(() => api.mcp.servers().then(setMcpServers)).catch(() => {}); }

  return (
    <div className="space-y-8">
      <div className="animate-in">
        <h1 className="text-2xl font-bold tracking-tight">Settings</h1>
        <p className="text-muted text-sm mt-1">Autonomy, LLM, and MCP server configuration</p>
      </div>

      <div className="flex gap-2 border-b border-border pb-2 animate-in">
        <button type="button" onClick={() => setTab("autonomy")}
          className={`px-4 py-2 rounded-lg text-sm font-medium ${tab === "autonomy" ? "bg-accent/10 text-accent" : "text-muted"}`}>Autonomy & LLM</button>
        <button type="button" onClick={() => setTab("mcp")}
          className={`px-4 py-2 rounded-lg text-sm font-medium ${tab === "mcp" ? "bg-accent/10 text-accent" : "text-muted"}`}>MCP Servers ({mcpServers.length})</button>
      </div>

      {tab === "autonomy" && (
        <div className="space-y-4 animate-in">
          <div className="bg-card border border-border rounded-xl p-5">
            <h2 className="text-sm font-semibold mb-3">Autonomy Mode</h2>
            <div className="flex gap-2">
              {["teaching", "build", "autonomous"].map((m) => (
                <button key={m} type="button" onClick={() => setAutonomy(m)}
                  className={`px-4 py-2 rounded-lg text-sm font-medium capitalize ${mode === m ? "bg-accent text-black" : "bg-surface border border-border text-muted"}`}>{m}</button>
              ))}
            </div>
            <p className="text-xs text-muted mt-2">
              {mode === "teaching" && "Teaching: blocks HIGH/CRITICAL operations"}
              {mode === "build" && "Build: allows up to HIGH operations"}
              {mode === "autonomous" && "Autonomous: allows all operations"}
            </p>
          </div>

          <div className="bg-card border border-border rounded-xl p-5">
            <h2 className="text-sm font-semibold mb-3">LLM Model</h2>
            <select value={selectedModel} onChange={(e) => setLlm(e.target.value)}
              className="bg-surface border border-border rounded-lg px-3 py-2 text-sm w-full max-w-xs">
              {models.map((m) => <option key={m} value={m}>{m}</option>)}
            </select>
            {models.length === 0 && <p className="text-xs text-muted mt-2">No models available. Start Ollama or configure an API provider.</p>}
          </div>

          <div className="bg-card border border-border rounded-xl p-5">
            <h2 className="text-sm font-semibold mb-3">Autonomy Check</h2>
            <TestAction label="Execute tool" action="execute" resource="tool:code_generator" />
            <TestAction label="Delete project" action="delete" resource="project:*" />
            <TestAction label="Modify system" action="modify" resource="system:config" />
          </div>
        </div>
      )}

      {tab === "mcp" && (
        <div className="space-y-4 animate-in">
          <div className="bg-card border border-border rounded-xl p-5">
            <h2 className="text-sm font-semibold mb-3">Add MCP Server</h2>
            <div className="flex flex-wrap gap-2 mb-3">
              <input value={serverName} onChange={(e) => setServerName(e.target.value)} placeholder="Server name"
                className="bg-surface border border-border rounded-lg px-3 py-2 text-sm flex-1" />
              <select value={serverType} onChange={(e) => setServerType(e.target.value)}
                className="bg-surface border border-border rounded-lg px-3 py-2 text-sm">
                <option value="stdio">STDIO</option>
                <option value="sse">SSE</option>
              </select>
              <input value={serverCmd} onChange={(e) => setServerCmd(e.target.value)}
                placeholder={serverType === "stdio" ? "Command (e.g. npx ...)" : "URL (e.g. https://..."}
                className="bg-surface border border-border rounded-lg px-3 py-2 text-sm flex-[2]" />
              <button type="button" onClick={addServer} disabled={!serverName || !serverCmd}
                className="px-4 py-2 bg-accent text-black rounded-lg text-sm font-medium disabled:opacity-40">Add</button>
            </div>
          </div>

          {mcpServers.map((s: any) => (
            <div key={s.name} className="bg-card border border-border rounded-xl p-4">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium">{s.name}</span>
                  <span className={`w-2 h-2 rounded-full ${s.connected ? "bg-success" : "bg-muted"}`} />
                  <span className="text-[10px] text-muted">{s.transport ?? s.type ?? "?"}</span>
                </div>
                <div className="flex gap-2">
                  {!s.connected && <button type="button" onClick={() => connectServer(s.name)}
                    className="px-2 py-1 text-xs bg-accent/10 text-accent rounded-lg">Connect</button>}
                  {s.connected && <button type="button" onClick={() => disconnectServer(s.name)}
                    className="px-2 py-1 text-xs bg-yellow-500/10 text-yellow-500 rounded-lg">Disconnect</button>}
                  <button type="button" onClick={() => removeServer(s.name)}
                    className="px-2 py-1 text-xs bg-red-500/10 text-red-500 rounded-lg">Remove</button>
                </div>
              </div>
              {s.tools && <div className="text-xs text-muted">{s.tools.length} tools</div>}
            </div>
          ))}
          {mcpServers.length === 0 && <p className="text-sm text-muted">No MCP servers configured.</p>}
        </div>
      )}
    </div>
  );
}

function TestAction({ label, action, resource }: { label: string; action: string; resource: string }) {
  const [result, setResult] = useState<any>(null);
  return (
    <div className="flex items-center gap-3 mb-2">
      <span className="text-sm text-muted w-32">{label}</span>
      <button type="button" onClick={() => api.autonomy.check(action, resource).then(setResult).catch(() => setResult({allowed: false}))}
        className="px-3 py-1 text-xs bg-surface border border-border rounded-lg">Test</button>
      {result && <span className={`text-xs font-mono ${result.allowed ? "text-success" : "text-red-500"}`}>{result.allowed ? "Allowed" : "Blocked"}</span>}
    </div>
  );
}
