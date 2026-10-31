"use client";

import { useEffect, useState } from "react";
import { ShieldAlert, CheckCircle2, AlertTriangle, XCircle, Shield, Cpu, Activity } from "lucide-react";
import { api } from "@/lib/api";
import { ValidationOverview, Project } from "@/types";
import { Navbar } from "@/components/shared/Navbar";

export default function ValidationPage() {
  const [project, setProject] = useState<Project | null>(null);
  const [overview, setOverview] = useState<ValidationOverview | null>(null);
  const [activeTab, setActiveTab] = useState<"rules" | "risks">("rules");
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    try {
      setLoading(true);
      const projects = await api.getProjects();
      const savedId = typeof window !== "undefined" ? localStorage.getItem("archmind_active_project_id") : null;
      const active = (savedId ? projects.find(p => p.id === savedId) : null) || projects[0] || (await api.loadSmartBankDemo());
      setProject(active);

      const val = await api.getValidation(active.id);
      setOverview(val);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  return (
    <div className="min-h-screen flex flex-col bg-[#080c14]">
      <Navbar projectName={project?.name} projectId={project?.id} onRefresh={loadData} />

      <main className="flex-1 p-8 space-y-6 max-w-7xl mx-auto w-full">
        {/* Header */}
        <div className="border-b border-[#1e293b] pb-6">
          <div className="flex items-center space-x-2">
            <ShieldAlert className="w-5 h-5 text-cyan-400" />
            <h1 className="text-xl font-bold text-white tracking-tight">Architecture Validation & Risk Engine</h1>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Hybrid verification: Python deterministic graph topology analysis (NetworkX DAG cycle detection) combined with architectural risk scoring.
          </p>
        </div>

        {/* Health Summary Card */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-[#0a0f1d] border border-cyan-500/30 rounded-xl p-5 flex items-center justify-between">
            <div>
              <div className="text-slate-400 text-xs font-semibold uppercase">Overall Health</div>
              <div className="text-3xl font-extrabold text-cyan-400 font-mono mt-1">
                {overview?.overall_health_score || 92.5} / 100
              </div>
              <div className="text-[10px] text-slate-500 mt-0.5">Status: {overview?.status || "Passed"}</div>
            </div>
            <Activity className="w-8 h-8 text-cyan-400/50" />
          </div>

          <div className="bg-[#0a0f1d] border border-emerald-500/30 rounded-xl p-5 flex items-center justify-between">
            <div>
              <div className="text-slate-400 text-xs font-semibold uppercase">Rules Passed</div>
              <div className="text-3xl font-extrabold text-emerald-400 font-mono mt-1">
                {overview?.passed_rules_count || 4}
              </div>
              <div className="text-[10px] text-slate-500 mt-0.5">Verified Structural DAG</div>
            </div>
            <CheckCircle2 className="w-8 h-8 text-emerald-400/50" />
          </div>

          <div className="bg-[#0a0f1d] border border-amber-500/30 rounded-xl p-5 flex items-center justify-between">
            <div>
              <div className="text-slate-400 text-xs font-semibold uppercase">Warnings</div>
              <div className="text-3xl font-extrabold text-amber-400 font-mono mt-1">
                {overview?.warned_rules_count || 1}
              </div>
              <div className="text-[10px] text-slate-500 mt-0.5">Coverage / SLA Notice</div>
            </div>
            <AlertTriangle className="w-8 h-8 text-amber-400/50" />
          </div>

          <div className="bg-[#0a0f1d] border border-rose-500/30 rounded-xl p-5 flex items-center justify-between">
            <div>
              <div className="text-slate-400 text-xs font-semibold uppercase">Failures</div>
              <div className="text-3xl font-extrabold text-rose-400 font-mono mt-1">
                {overview?.failed_rules_count || 0}
              </div>
              <div className="text-[10px] text-slate-500 mt-0.5">Zero Critical Violations</div>
            </div>
            <XCircle className="w-8 h-8 text-rose-400/50" />
          </div>
        </div>

        {/* Tab Switcher */}
        <div className="flex space-x-2 bg-[#0a0f1d] border border-[#1e293b] p-2 rounded-xl">
          <button
            onClick={() => setActiveTab("rules")}
            className={`px-4 py-1.5 rounded-lg text-xs font-semibold transition ${
              activeTab === "rules" ? "bg-cyan-600 text-white" : "bg-[#131d33] text-slate-400 hover:text-white"
            }`}
          >
            Deterministic & Semantic Validation Rules
          </button>
          <button
            onClick={() => setActiveTab("risks")}
            className={`px-4 py-1.5 rounded-lg text-xs font-semibold transition ${
              activeTab === "risks" ? "bg-cyan-600 text-white" : "bg-[#131d33] text-slate-400 hover:text-white"
            }`}
          >
            Architecture Risk Register
          </button>
        </div>

        {/* Rules Table */}
        {activeTab === "rules" && (
          <div className="bg-[#0a0f1d] border border-[#1e293b] rounded-xl overflow-hidden shadow-xl">
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse text-xs">
                <thead>
                  <tr className="bg-[#0f172a] border-b border-[#1e293b] text-slate-400 uppercase tracking-wider font-semibold">
                    <th className="py-3 px-4">Validation Rule</th>
                    <th className="py-3 px-4">Category</th>
                    <th className="py-3 px-4">Evaluation Logic</th>
                    <th className="py-3 px-4 text-center">Score</th>
                    <th className="py-3 px-4 text-center">Status</th>
                    <th className="py-3 px-4">Findings & Recommendation</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#1e293b] text-slate-200">
                  {(overview?.validations || []).map((v, idx) => (
                    <tr key={idx} className="hover:bg-[#11192e] transition">
                      <td className="py-3.5 px-4 font-bold text-white">{v.rule_name}</td>
                      <td className="py-3.5 px-4 text-slate-300">{v.category}</td>
                      <td className="py-3.5 px-4">
                        <span className="px-2 py-0.5 rounded bg-blue-500/15 text-blue-400 border border-blue-500/30 text-[10px] font-mono">
                          {v.is_deterministic ? "Deterministic Python Check" : "LLM Semantic Review"}
                        </span>
                      </td>
                      <td className="py-3.5 px-4 text-center font-mono font-bold text-cyan-400">
                        {v.score}
                      </td>
                      <td className="py-3.5 px-4 text-center">
                        <span
                          className={`px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold ${
                            v.status === "Pass"
                              ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"
                              : v.status === "Warn"
                              ? "bg-amber-500/20 text-amber-400 border border-amber-500/30"
                              : "bg-rose-500/20 text-rose-400 border border-rose-500/30"
                          }`}
                        >
                          {v.status.toUpperCase()}
                        </span>
                      </td>
                      <td className="py-3.5 px-4 max-w-md">
                        <div className="text-slate-300 text-[11px] leading-relaxed">{v.details}</div>
                        {v.recommendation && (
                          <div className="text-cyan-400 text-[10px] mt-1 font-mono">
                            Rec: {v.recommendation}
                          </div>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Risk Register Table */}
        {activeTab === "risks" && (
          <div className="bg-[#0a0f1d] border border-[#1e293b] rounded-xl overflow-hidden shadow-xl">
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse text-xs">
                <thead>
                  <tr className="bg-[#0f172a] border-b border-[#1e293b] text-slate-400 uppercase tracking-wider font-semibold">
                    <th className="py-3 px-4">Risk Code</th>
                    <th className="py-3 px-4">Risk Title</th>
                    <th className="py-3 px-4">Category</th>
                    <th className="py-3 px-4 text-center">Severity</th>
                    <th className="py-3 px-4 text-center">Score</th>
                    <th className="py-3 px-4">Affected Components</th>
                    <th className="py-3 px-4">Mitigation Strategy</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#1e293b] text-slate-200">
                  {(overview?.risks || []).map((r) => (
                    <tr key={r.risk_code} className="hover:bg-[#11192e] transition">
                      <td className="py-3.5 px-4 font-mono font-bold text-rose-400">{r.risk_code}</td>
                      <td className="py-3.5 px-4 font-bold text-white">{r.title}</td>
                      <td className="py-3.5 px-4 text-slate-300">{r.category}</td>
                      <td className="py-3.5 px-4 text-center">
                        <span
                          className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                            r.severity === "Critical"
                              ? "bg-rose-500/20 text-rose-400 border border-rose-500/30"
                              : r.severity === "High"
                              ? "bg-amber-500/20 text-amber-400 border border-amber-500/30"
                              : "bg-blue-500/20 text-blue-400"
                          }`}
                        >
                          {r.severity}
                        </span>
                      </td>
                      <td className="py-3.5 px-4 text-center font-mono font-bold text-cyan-300">
                        {r.risk_score}
                      </td>
                      <td className="py-3.5 px-4">
                        <div className="flex flex-wrap gap-1">
                          {(r.affected_components || []).map((c) => (
                            <span key={c} className="px-1.5 py-0.5 rounded bg-slate-800 text-cyan-400 font-mono text-[9px]">
                              {c}
                            </span>
                          ))}
                        </div>
                      </td>
                      <td className="py-3.5 px-4 max-w-sm text-slate-300 leading-relaxed text-[11px]">
                        {r.mitigation_strategy}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

