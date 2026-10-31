"use client";

import { useEffect, useState } from "react";
import { Zap, Play, CheckCircle2, AlertTriangle, ArrowRight, Layers, Database, ShieldCheck, Check } from "lucide-react";
import { api } from "@/lib/api";
import { RequirementItem, ChangeImpactResult, Project } from "@/types";
import { Navbar } from "@/components/shared/Navbar";

export default function ImpactAnalysisPage() {
  const [project, setProject] = useState<Project | null>(null);
  const [requirements, setRequirements] = useState<RequirementItem[]>([]);
  const [selectedReqCode, setSelectedReqCode] = useState<string>("REQ-005");
  const [modifiedText, setModifiedText] = useState<string>(
    "The core banking backend services and database connection tier must sustain 500,000 active concurrent sessions and 35,000 transactions per second during national promotional events."
  );
  const [simulating, setSimulating] = useState(false);
  const [result, setResult] = useState<ChangeImpactResult | null>(null);
  const [applied, setApplied] = useState(false);
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    try {
      setLoading(true);
      const projects = await api.getProjects();
      const savedId = typeof window !== "undefined" ? localStorage.getItem("archmind_active_project_id") : null;
      const active = (savedId ? projects.find(p => p.id === savedId) : null) || projects[0] || (await api.loadSmartBankDemo());
      setProject(active);

      const reqs = await api.getRequirements(active.id);
      setRequirements(reqs);

      // Pre-select first scalability requirement if available
      const scaleReq = reqs.find((r) => r.category === "Scalability") || reqs[0];
      if (scaleReq) {
        setSelectedReqCode(scaleReq.req_code);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleSelectReq = (code: string) => {
    setSelectedReqCode(code);
    const found = requirements.find((r) => r.req_code === code);
    if (found) {
      if (found.category === "Scalability" || found.title.includes("Concurrent")) {
        setModifiedText(
          "The core banking backend services and database connection tier must sustain 500,000 active concurrent sessions and 35,000 transactions per second during promotional peaks."
        );
      } else if (found.category === "Performance" || found.title.includes("Latency")) {
        setModifiedText(
          "The end-to-end authentication and token issuance handshake must complete within 500 milliseconds at the 99th percentile under peak load."
        );
      } else {
        setModifiedText(found.description + " (Modified strict SLA criteria)");
      }
    }
  };

  const handleSimulate = async () => {
    if (!project || !selectedReqCode || !modifiedText) return;
    setSimulating(true);
    setApplied(false);
    try {
      const res = await api.simulateChangeImpact(project.id, selectedReqCode, modifiedText);
      setResult(res);
    } catch (err) {
      console.error(err);
    } finally {
      setSimulating(false);
    }
  };

  const handleApply = async () => {
    if (!result?.id) return;
    try {
      await api.applyChangeImpact(result.id);
      setApplied(true);
      await loadData();
    } catch (err) {
      console.error(err);
    }
  };

  const selectedReq = requirements.find((r) => r.req_code === selectedReqCode);

  return (
    <div className="min-h-screen flex flex-col bg-[#080c14]">
      <Navbar projectName={project?.name} projectId={project?.id} onRefresh={loadData} />

      <main className="flex-1 p-8 space-y-6 max-w-7xl mx-auto w-full">
        {/* Header */}
        <div className="border-b border-[#1e293b] pb-6">
          <div className="flex items-center space-x-2">
            <Zap className="w-5 h-5 text-cyan-400" />
            <h1 className="text-xl font-bold text-white tracking-tight">Change Impact Simulator</h1>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Predict downstream ripple effects across components, APIs, ADRs, database architectures, and risk profiles before approving requirement mutations.
          </p>
        </div>

        {/* Interactive Editor Form */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left: Original Requirement Selection */}
          <div className="bg-[#0a0f1d] border border-[#1e293b] rounded-xl p-5 space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-slate-300 uppercase tracking-wider">
                1. Select Target Requirement
              </span>
              <span className="text-[10px] font-mono text-cyan-400">Baseline Specification</span>
            </div>

            <div>
              <label className="text-[10px] font-semibold text-slate-400 uppercase block mb-1">Requirement</label>
              <select
                value={selectedReqCode}
                onChange={(e) => handleSelectReq(e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-[#0f172a] border border-[#1e293b] text-xs text-white focus:outline-none focus:border-cyan-500 font-mono"
              >
                {requirements.map((r) => (
                  <option key={r.req_code} value={r.req_code}>
                    {r.req_code} — {r.title} ({r.category})
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="text-[10px] font-semibold text-slate-400 uppercase block mb-1">Original Text</label>
              <div className="p-3.5 rounded-lg bg-[#070b14] border border-[#1e293b] text-xs text-slate-300 leading-relaxed font-sans min-h-[110px]">
                {selectedReq?.description || "Select a requirement to inspect baseline."}
              </div>
            </div>

            <div className="flex items-center space-x-3 text-[11px] text-slate-400">
              <span>Category: <strong className="text-slate-200">{selectedReq?.category}</strong></span>
              <span>Priority: <strong className="text-cyan-400">{selectedReq?.priority}</strong></span>
              <span>Status: <strong className="text-emerald-400">{selectedReq?.approval_status}</strong></span>
            </div>
          </div>

          {/* Right: Modified Requirement Proposal */}
          <div className="bg-[#0a0f1d] border border-cyan-500/30 rounded-xl p-5 space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-white uppercase tracking-wider">
                2. Enter Proposed Modification
              </span>
              <span className="text-[10px] font-mono text-cyan-400">What-If Simulation</span>
            </div>

            <div>
              <label className="text-[10px] font-semibold text-slate-400 uppercase block mb-1">
                Modified Specification Statement
              </label>
              <textarea
                rows={5}
                value={modifiedText}
                onChange={(e) => setModifiedText(e.target.value)}
                className="w-full p-3 rounded-lg bg-[#070b14] border border-cyan-500/40 text-xs text-white focus:outline-none focus:border-cyan-400 font-sans leading-relaxed"
                placeholder="Modify concurrency, latency, or deployment parameters..."
              />
            </div>

            <div className="flex items-center justify-between pt-2">
              <span className="text-[11px] text-slate-400">
                Agent 8 will evaluate affected components, APIs, and ADRs.
              </span>
              <button
                onClick={handleSimulate}
                disabled={simulating || !modifiedText}
                className="flex items-center space-x-1.5 px-4 py-2 rounded-lg bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500 text-white text-xs font-semibold shadow-lg shadow-cyan-600/20 transition disabled:opacity-50"
              >
                <Play className="w-3.5 h-3.5 fill-white" />
                <span>{simulating ? "Simulating Impact..." : "Simulate Impact"}</span>
              </button>
            </div>
          </div>
        </div>

        {/* Simulation Output Area */}
        {result && (
          <div className="bg-[#0a0f1d] border border-cyan-500/40 rounded-xl p-6 space-y-6 shadow-2xl animate-in fade-in">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-[#1e293b] pb-4 gap-3">
              <div>
                <span className="text-xs font-mono font-bold px-2 py-0.5 rounded bg-cyan-500/20 text-cyan-400 border border-cyan-500/30">
                  IMPACT SIMULATION RESULTS FOR {result.target_req_code}
                </span>
                <p className="text-xs text-slate-300 mt-1 font-semibold">{result.comparison_summary}</p>
              </div>

              {!applied ? (
                <button
                  onClick={handleApply}
                  className="flex items-center space-x-1.5 px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold transition"
                >
                  <Check className="w-3.5 h-3.5" />
                  <span>Approve & Apply to Project</span>
                </button>
              ) : (
                <span className="flex items-center space-x-1.5 text-emerald-400 text-xs font-bold">
                  <CheckCircle2 className="w-4 h-4" />
                  <span>Requirement Update Approved</span>
                </span>
              )}
            </div>

            {/* Affected Architecture Entities */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-[#0f172a] p-4 rounded-xl border border-[#1e293b]">
                <span className="text-[10px] font-semibold text-slate-400 uppercase block mb-2">
                  Directly Affected Components ({result.affected_components.length})
                </span>
                <div className="flex flex-wrap gap-1.5">
                  {result.affected_components.map((c) => (
                    <span key={c} className="px-2 py-0.5 rounded bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 font-mono text-[11px] font-bold">
                      {c}
                    </span>
                  ))}
                </div>
              </div>

              <div className="bg-[#0f172a] p-4 rounded-xl border border-[#1e293b]">
                <span className="text-[10px] font-semibold text-slate-400 uppercase block mb-2">
                  Affected API Endpoints ({result.affected_apis.length})
                </span>
                <div className="space-y-1">
                  {result.affected_apis.map((a, i) => (
                    <div key={i} className="text-slate-300 font-mono text-[10px]">
                      {a}
                    </div>
                  ))}
                </div>
              </div>

              <div className="bg-[#0f172a] p-4 rounded-xl border border-[#1e293b]">
                <span className="text-[10px] font-semibold text-slate-400 uppercase block mb-2">
                  Impacted ADRs ({result.affected_adrs.length})
                </span>
                <div className="flex flex-wrap gap-1.5">
                  {result.affected_adrs.map((adr) => (
                    <span key={adr} className="px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 font-mono text-[11px] font-bold">
                      {adr}
                    </span>
                  ))}
                </div>
              </div>
            </div>

            {/* Infrastructure & Database Implications */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-[#0f172a] p-4 rounded-xl border border-[#1e293b] space-y-2">
                <span className="text-xs font-bold text-white uppercase tracking-wider block">
                  Mandatory Infrastructure Changes
                </span>
                <ul className="space-y-1.5 text-xs text-slate-300 list-disc list-inside">
                  {result.infrastructure_changes.map((inf, i) => (
                    <li key={i}>{inf}</li>
                  ))}
                </ul>
              </div>

              <div className="bg-[#0f172a] p-4 rounded-xl border border-[#1e293b] space-y-2">
                <span className="text-xs font-bold text-white uppercase tracking-wider block">
                  Performance & Scalability Risks
                </span>
                <ul className="space-y-1.5 text-xs text-rose-300 list-disc list-inside">
                  {result.performance_risks.map((pr, i) => (
                    <li key={i}>{pr}</li>
                  ))}
                </ul>
              </div>
            </div>

            {result.database_implications && (
              <div className="bg-[#070b14] p-4 rounded-xl border border-cyan-500/30 text-xs">
                <span className="text-cyan-400 font-bold block mb-1">Database & Storage Implications:</span>
                <p className="text-slate-300 leading-relaxed">{result.database_implications}</p>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}

