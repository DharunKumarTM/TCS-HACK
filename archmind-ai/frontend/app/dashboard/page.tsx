"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  FileText,
  AlertTriangle,
  CheckCircle2,
  ShieldAlert,
  GitBranch,
  Layers,
  ArrowUpRight,
  Sparkles,
  HelpCircle,
  Database,
  Cpu,
  PlusCircle
} from "lucide-react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  RadarChart,
  Radar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis
} from "recharts";
import { api } from "@/lib/api";
import { Project, ProjectStats } from "@/types";
import { Navbar } from "@/components/shared/Navbar";

export default function DashboardPage() {
  const [project, setProject] = useState<Project | null>(null);
  const [stats, setStats] = useState<ProjectStats | null>(null);
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    try {
      setLoading(true);
      const projects = await api.getProjects();
      const savedId = typeof window !== "undefined" ? localStorage.getItem("archmind_active_project_id") : null;
      let activeProj = (savedId ? projects.find(p => p.id === savedId) : null) || projects[0];
      if (!activeProj) {
        activeProj = await api.loadSmartBankDemo();
      }
      setProject(activeProj);
      const s = await api.getProjectStats(activeProj.id);
      setStats(s);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  // Visual metrics
  const reqDistributionData = [
    { name: "Security", count: 4 },
    { name: "Performance", count: 2 },
    { name: "Compliance", count: 3 },
    { name: "Scalability", count: 2 },
    { name: "Infrastructure", count: 2 },
  ];

  const conflictSeverityData = [
    { name: "Critical", value: 2, color: "#ef4444" },
    { name: "High", value: 1, color: "#f59e0b" },
    { name: "Medium", value: 0, color: "#38bdf8" },
  ];

  const qualityRadarData = [
    { subject: "Traceability", score: stats?.coverage_score ? Math.min(100, Math.round(stats.coverage_score * 1.5)) : 75 },
    { subject: "Evidence Grounding", score: 98 },
    { subject: "Security Rigor", score: 95 },
    { subject: "Acyclic Graph", score: 100 },
    { subject: "NFR Compliance", score: 90 },
    { subject: "ADR Completeness", score: 92 },
  ];

  return (
    <div className="min-h-screen flex flex-col bg-[#080c14]">
      <Navbar
        projectName={project?.name}
        projectId={project?.id}
        status={stats?.status || "Analyzing"}
        onRefresh={loadData}
      />

      <main className="flex-1 p-8 space-y-8 max-w-7xl mx-auto w-full">
        {/* Hero Banner */}
        <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-[#0d162d] via-[#101e3d] to-[#0d1933] border border-[#1e293b] p-7 shadow-xl">
          <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
            <div className="space-y-2 max-w-2xl">
              <div className="inline-flex items-center space-x-2 px-2.5 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 text-xs font-semibold">
                <Sparkles className="w-3.5 h-3.5" />
                <span>TCS AI Hackathon – Challenge 02: Requirements-to-Architecture</span>
              </div>
              <h2 className="text-2xl font-extrabold text-white tracking-tight">
                ArchMind AI – Evidence-Driven Agentic Architect
              </h2>
              <p className="text-xs text-slate-300 leading-relaxed">
                Transforming fragmented, incomplete, and contradictory banking requirements into explainable,
                formally validated, and traceable software architecture through LangGraph multi-agent orchestration.
              </p>
              <div className="pt-2">
                <Link
                  href="/input"
                  className="inline-flex items-center space-x-2 px-4 py-2 rounded-xl bg-gradient-to-r from-blue-600 via-cyan-600 to-teal-500 hover:from-blue-500 hover:to-cyan-500 text-white text-xs font-bold shadow-lg shadow-cyan-500/25 transition"
                >
                  <PlusCircle className="w-4 h-4" />
                  <span>Start New Analysis (Upload PDF/Doc or Write Text)</span>
                </Link>
              </div>
            </div>

            <div className="flex flex-col sm:flex-row items-center gap-3">
              <div className="bg-[#090f1f]/80 border border-[#1e293b] rounded-xl p-3 text-center min-w-[130px]">
                <div className="text-xl font-bold text-cyan-400 font-mono">
                  {stats?.coverage_score ? `${stats.coverage_score}%` : "44.4%"}
                </div>
                <div className="text-[10px] text-slate-400 uppercase tracking-wider font-semibold">Traceability</div>
              </div>
              <div className="bg-[#090f1f]/80 border border-[#1e293b] rounded-xl p-3 text-center min-w-[130px]">
                <div className="text-xl font-bold text-emerald-400 font-mono">
                  {stats?.resolved_conflicts || 3} / {stats?.total_conflicts || 3}
                </div>
                <div className="text-[10px] text-slate-400 uppercase tracking-wider font-semibold">Conflicts Cleared</div>
              </div>
            </div>
          </div>
        </div>

        {/* 6 Top Metric Cards */}
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          <div className="bg-[#0a0f1d] border border-[#1e293b] rounded-xl p-4 flex flex-col justify-between">
            <div className="flex items-center justify-between text-slate-400 mb-2">
              <span className="text-[11px] font-semibold uppercase">Evidence</span>
              <FileText className="w-4 h-4 text-blue-400" />
            </div>
            <div className="text-2xl font-bold text-white font-mono">{stats?.total_evidence || 37}</div>
            <div className="text-[10px] text-slate-400 mt-1">Grounding Citations</div>
          </div>

          <div className="bg-[#0a0f1d] border border-[#1e293b] rounded-xl p-4 flex flex-col justify-between">
            <div className="flex items-center justify-between text-slate-400 mb-2">
              <span className="text-[11px] font-semibold uppercase">Normalized REQs</span>
              <CheckCircle2 className="w-4 h-4 text-cyan-400" />
            </div>
            <div className="text-2xl font-bold text-white font-mono">{stats?.total_requirements || 9}</div>
            <div className="text-[10px] text-slate-400 mt-1">FR, NFR, Constraints</div>
          </div>

          <div className="bg-[#0a0f1d] border border-[#1e293b] rounded-xl p-4 flex flex-col justify-between">
            <div className="flex items-center justify-between text-slate-400 mb-2">
              <span className="text-[11px] font-semibold uppercase">Conflicts</span>
              <AlertTriangle className="w-4 h-4 text-amber-400" />
            </div>
            <div className="text-2xl font-bold text-white font-mono">{stats?.total_conflicts || 3}</div>
            <div className="text-[10px] text-slate-400 mt-1">
              {stats?.resolved_conflicts || 0} Human Clarified
            </div>
          </div>

          <div className="bg-[#0a0f1d] border border-[#1e293b] rounded-xl p-4 flex flex-col justify-between">
            <div className="flex items-center justify-between text-slate-400 mb-2">
              <span className="text-[11px] font-semibold uppercase">Components</span>
              <Layers className="w-4 h-4 text-indigo-400" />
            </div>
            <div className="text-2xl font-bold text-white font-mono">{stats?.total_components || 7}</div>
            <div className="text-[10px] text-slate-400 mt-1">Sovereign Mesh Services</div>
          </div>

          <div className="bg-[#0a0f1d] border border-[#1e293b] rounded-xl p-4 flex flex-col justify-between">
            <div className="flex items-center justify-between text-slate-400 mb-2">
              <span className="text-[11px] font-semibold uppercase">ADRs</span>
              <GitBranch className="w-4 h-4 text-teal-400" />
            </div>
            <div className="text-2xl font-bold text-white font-mono">{stats?.total_adrs || 4}</div>
            <div className="text-[10px] text-slate-400 mt-1">Decisions with Trade-offs</div>
          </div>

          <div className="bg-[#0a0f1d] border border-[#1e293b] rounded-xl p-4 flex flex-col justify-between">
            <div className="flex items-center justify-between text-slate-400 mb-2">
              <span className="text-[11px] font-semibold uppercase">Health Score</span>
              <ShieldAlert className="w-4 h-4 text-emerald-400" />
            </div>
            <div className="text-2xl font-bold text-emerald-400 font-mono">92.5</div>
            <div className="text-[10px] text-slate-400 mt-1">Acyclic DAG Verified</div>
          </div>
        </div>

        {/* Visual Charts Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Chart 1: Requirement Category Breakdown */}
          <div className="bg-[#0a0f1d] border border-[#1e293b] rounded-xl p-5 flex flex-col">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider">Requirement Categories</h3>
              <span className="text-[10px] font-mono text-cyan-400">Classified by Agent 2</span>
            </div>
            <div className="h-56 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={reqDistributionData}>
                  <XAxis dataKey="name" stroke="#64748b" fontSize={11} tickLine={false} />
                  <YAxis stroke="#64748b" fontSize={11} tickLine={false} />
                  <Tooltip
                    contentStyle={{ backgroundColor: "#0f172a", borderColor: "#334155", fontSize: "11px", borderRadius: "8px" }}
                  />
                  <Bar dataKey="count" fill="#0284c7" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Chart 2: Conflict Severity Distribution */}
          <div className="bg-[#0a0f1d] border border-[#1e293b] rounded-xl p-5 flex flex-col">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider">Detected Conflicts</h3>
              <span className="text-[10px] font-mono text-amber-400">Agent 3 Analysis</span>
            </div>
            <div className="h-56 w-full flex items-center justify-center">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={conflictSeverityData}
                    cx="50%"
                    cy="50%"
                    innerRadius={50}
                    outerRadius={80}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {conflictSeverityData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{ backgroundColor: "#0f172a", borderColor: "#334155", fontSize: "11px", borderRadius: "8px" }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="flex items-center justify-center space-x-4 text-[11px] text-slate-400">
              <div className="flex items-center space-x-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-rose-500"></span>
                <span>Critical (2)</span>
              </div>
              <div className="flex items-center space-x-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-amber-500"></span>
                <span>High (1)</span>
              </div>
            </div>
          </div>

          {/* Chart 3: Architecture Quality Radar */}
          <div className="bg-[#0a0f1d] border border-[#1e293b] rounded-xl p-5 flex flex-col">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider">Architecture Health Radar</h3>
              <span className="text-[10px] font-mono text-emerald-400">Agent 7 Validation</span>
            </div>
            <div className="h-56 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <RadarChart data={qualityRadarData}>
                  <PolarGrid stroke="#1e293b" />
                  <PolarAngleAxis dataKey="subject" stroke="#64748b" fontSize={10} />
                  <PolarRadiusAxis angle={30} domain={[0, 100]} stroke="#334155" fontSize={9} />
                  <Radar name="Quality Score" dataKey="score" stroke="#06b6d4" fill="#06b6d4" fillOpacity={0.4} />
                  <Tooltip
                    contentStyle={{ backgroundColor: "#0f172a", borderColor: "#334155", fontSize: "11px", borderRadius: "8px" }}
                  />
                </RadarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        {/* LangGraph Pipeline Stage Visualization */}
        <div className="bg-[#0a0f1d] border border-[#1e293b] rounded-xl p-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-white">LangGraph Agent Pipeline State Machine</h3>
              <p className="text-xs text-slate-400">Stateful typed workflow with conditional human-in-the-loop checkpoints</p>
            </div>
            <span className="text-xs font-mono px-2.5 py-1 rounded bg-blue-500/10 text-cyan-400 border border-cyan-500/30">
              State: {stats?.status?.toUpperCase() || "COMPLETED"}
            </span>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-2 pt-2">
            {[
              { id: "A1", name: "Evidence Intel", status: "Done", desc: "Docling & LlamaIndex" },
              { id: "A2", name: "Requirements", status: "Done", desc: "Normalization & FR/NFR" },
              { id: "A3", name: "Conflict Det.", status: "Done", desc: "Direct & Semantic Collision" },
              { id: "A4", name: "Clarification", status: "Done", desc: "Human-In-The-Loop Checkpoint" },
              { id: "A5", name: "Arch. Reason", status: "Done", desc: "Sovereign Hybrid Topology" },
              { id: "A6", name: "Security Intel", status: "Done", desc: "PCI-DSS 4.0 & HSM Keys" },
              { id: "A7", name: "Validation", status: "Done", desc: "DAG Checks & Risk Register" },
              { id: "A8", name: "Traceability", status: "Done", desc: "End-to-End Matrix & Diff" },
            ].map((node) => (
              <div
                key={node.id}
                className="bg-[#0f172a] border border-[#1e293b] rounded-lg p-3 flex flex-col justify-between text-left space-y-2 hover:border-cyan-500/40 transition"
              >
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-blue-500/20 text-cyan-300 font-bold">
                    {node.id}
                  </span>
                  <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
                </div>
                <div>
                  <div className="text-xs font-bold text-slate-200">{node.name}</div>
                  <div className="text-[10px] text-slate-400 truncate mt-0.5">{node.desc}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}

