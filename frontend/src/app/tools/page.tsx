"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";

export default function ToolsPage() {
  const [tab, setTab] = useState<"tools" | "skills">("tools");
  const [tools, setTools] = useState<any[]>([]);
  const [skills, setSkills] = useState<any[]>([]);
  const [result, setResult] = useState<any>(null);
  const [toolName, setToolName] = useState("");
  const [toolArgs, setToolArgs] = useState("{}");
  const [skillName, setSkillName] = useState("");
  const [skillArgs, setSkillArgs] = useState("{}");

  useEffect(() => { api.tools.list().then(setTools).catch(() => {}); api.skills.list().then(setSkills).catch(() => {}); }, []);

  function runTool() {
    setResult(null);
    api.tools.execute(toolName, JSON.parse(toolArgs || "{}")).then(setResult).catch((e) => setResult({ error: e.message }));
  }
  function runSkill() {
    setResult(null);
    api.skills.execute(skillName, JSON.parse(skillArgs || "{}")).then(setResult).catch((e) => setResult({ error: e.message }));
  }

  return (
    <div className="space-y-8">
      <div className="animate-in">
        <h1 className="text-2xl font-bold tracking-tight">Tools & Skills</h1>
        <p className="text-muted text-sm mt-1">Browse and execute available tools and skills</p>
      </div>

      <div className="flex gap-2 border-b border-border pb-2 animate-in">
        <button type="button" onClick={() => setTab("tools")}
          className={`px-4 py-2 rounded-lg text-sm font-medium ${tab === "tools" ? "bg-accent/10 text-accent" : "text-muted"}`}>Tools ({tools.length})</button>
        <button type="button" onClick={() => setTab("skills")}
          className={`px-4 py-2 rounded-lg text-sm font-medium ${tab === "skills" ? "bg-accent/10 text-accent" : "text-muted"}`}>Skills ({skills.length})</button>
      </div>

      {tab === "tools" && (
        <div className="space-y-4 animate-in">
          <div className="bg-card border border-border rounded-xl p-5">
            <h2 className="text-sm font-semibold mb-3">Execute Tool</h2>
            <div className="flex gap-2 mb-2">
              <select value={toolName} onChange={(e) => setToolName(e.target.value)}
                className="bg-surface border border-border rounded-lg px-3 py-2 text-sm flex-1">
                <option value="">Select tool...</option>
                {tools.map((t: any) => <option key={t.name ?? t} value={t.name ?? t}>{t.name ?? t}</option>)}
              </select>
              <button type="button" onClick={runTool} disabled={!toolName}
                className="px-4 py-2 bg-accent text-black rounded-lg text-sm font-medium disabled:opacity-40">Execute</button>
            </div>
            <input value={toolArgs} onChange={(e) => setToolArgs(e.target.value)} placeholder='{"key": "value"}'
              className="w-full bg-surface border border-border rounded-lg px-3 py-2 text-sm font-mono" />
          </div>

          <div className="grid gap-3">
            {tools.map((t: any) => (
              <div key={t.name ?? t} className="bg-card border border-border rounded-xl p-4">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm font-medium font-mono">{t.name ?? t}</span>
                </div>
                {t.description && <p className="text-xs text-muted">{t.description}</p>}
                {t.parameters && <div className="text-[10px] text-muted mt-1 font-mono">params: {Object.keys(t.parameters).join(", ")}</div>}
              </div>
            ))}
          </div>
        </div>
      )}

      {tab === "skills" && (
        <div className="space-y-4 animate-in">
          <div className="bg-card border border-border rounded-xl p-5">
            <h2 className="text-sm font-semibold mb-3">Execute Skill</h2>
            <div className="flex gap-2 mb-2">
              <select value={skillName} onChange={(e) => setSkillName(e.target.value)}
                className="bg-surface border border-border rounded-lg px-3 py-2 text-sm flex-1">
                <option value="">Select skill...</option>
                {skills.map((s: any) => <option key={s.name ?? s} value={s.name ?? s}>{s.name ?? s}</option>)}
              </select>
              <button type="button" onClick={runSkill} disabled={!skillName}
                className="px-4 py-2 bg-accent text-black rounded-lg text-sm font-medium disabled:opacity-40">Execute</button>
            </div>
            <input value={skillArgs} onChange={(e) => setSkillArgs(e.target.value)} placeholder='{"spec": "..."}'
              className="w-full bg-surface border border-border rounded-lg px-3 py-2 text-sm font-mono" />
          </div>

          <div className="grid gap-3">
            {skills.map((s: any) => (
              <div key={s.name ?? s} className="bg-card border border-border rounded-xl p-4">
                <span className="text-sm font-medium font-mono">{s.name ?? s}</span>
                {s.description && <p className="text-xs text-muted mt-1">{s.description}</p>}
              </div>
            ))}
          </div>
        </div>
      )}

      {result && (
        <div className="bg-card border border-border rounded-xl p-5 animate-in">
          <h3 className="text-sm font-semibold mb-2">Result</h3>
          <pre className="text-xs font-mono text-muted max-h-96 overflow-auto whitespace-pre-wrap">{JSON.stringify(result, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}
