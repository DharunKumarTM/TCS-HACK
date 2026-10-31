"use client";

import { useEffect, useState } from "react";
import {
  Network,
  Layers,
  ArrowRight,
  Server,
  Shield,
  FileCode,
  Share2,
  Workflow,
  Globe,
  Database,
  CheckCircle2,
  AlertTriangle,
  Sliders,
  Cpu,
  Zap,
  RotateCcw,
  Sparkles,
  Check,
  X,
  ChevronDown,
  ChevronUp,
  Scale,
  History,
  TrendingUp,
  Lock,
  Activity,
  ArrowUpRight
} from "lucide-react";
import { api } from "@/lib/api";
import {
  ArchitectureComponent,
  APIEndpoint,
  DataFlow,
  Project,
  TechStackItem,
  ArchitectureEvolutionModel
} from "@/types";
import { Navbar } from "@/components/shared/Navbar";
import { MermaidViewer } from "@/components/shared/MermaidViewer";
import { ReactFlowGraph } from "@/components/architecture/ReactFlowGraph";

export default function ArchitecturePage() {
  const [project, setProject] = useState<Project | null>(null);
  const [activeTab, setActiveTab] = useState<string>("evolution");
  const [components, setComponents] = useState<ArchitectureComponent[]>([]);
  const [apis, setApis] = useState<APIEndpoint[]>([]);
  const [flows, setFlows] = useState<DataFlow[]>([]);
  const [diagrams, setDiagrams] = useState<Record<string, string>>({});
  const [styleDesc, setStyleDesc] = useState<string>("");
  const [loading, setLoading] = useState(true);

  // Tech Stack & Evolution States
  const [techStacks, setTechStacks] = useState<TechStackItem[]>([]);
  const [oldArch, setOldArch] = useState<ArchitectureEvolutionModel | null>(null);
  const [newArch, setNewArch] = useState<ArchitectureEvolutionModel | null>(null);
  const [matrix, setMatrix] = useState<any[]>([]);
  const [confirmationStatus, setConfirmationStatus] = useState<string>("Pending Review");
  const [confirmedBy, setConfirmedBy] = useState<string | null>(null);
  const [confirmedAt, setConfirmedAt] = useState<string | null>(null);
  const [architectNotes, setArchitectNotes] = useState<string | null>(null);

  // Modals & UI States
  const [evolutionView, setEvolutionView] = useState<"cards" | "side_by_side" | "old_diagram" | "new_diagram" | "matrix">("cards");
  const [expandedStackIdx, setExpandedStackIdx] = useState<number | null>(0);
  const [confirmModalOpen, setConfirmModalOpen] = useState(false);
  const [customizeModalOpen, setCustomizeModalOpen] = useState(false);
  const [revisionModalOpen, setRevisionModalOpen] = useState(false);

  // Modal Inputs
  const [architectNameInput, setArchitectNameInput] = useState("Lead Enterprise Architect");
  const [notesInput, setNotesInput] = useState("Target architecture and tech stack validated against latency SLAs, sovereign data residency, and high-concurrency benchmarks.");
  const [selectedCategory, setSelectedCategory] = useState<string>("");
  const [selectedAlternative, setSelectedAlternative] = useState<string>("");
  const [actionInProgress, setActionInProgress] = useState(false);

  const loadData = async () => {
    try {
      setLoading(true);
      const projects = await api.getProjects();
      const savedId = typeof window !== "undefined" ? localStorage.getItem("archmind_active_project_id") : null;
      const active = (savedId ? projects.find((p) => p.id === savedId) : null) || projects[0] || (await api.loadSmartBankDemo());
      setProject(active);

      const arch = await api.getArchitecture(active.id);
      setComponents(arch.components || []);
      setApis(arch.apis || []);
      setFlows(arch.data_flows || []);
      setDiagrams(arch.mermaid_diagrams || {});
      setStyleDesc(arch.style_justification || "");

      // Tech Stack Recommendations & Evolution
      setTechStacks(arch.tech_stack_recommendations || []);
      setOldArch(arch.old_architecture || null);
      setNewArch(arch.new_architecture || null);
      setMatrix(arch.comparison_matrix || []);
      setConfirmationStatus(arch.confirmation_status || "Pending Review");
      setConfirmedBy(arch.confirmed_by || null);
      setConfirmedAt(arch.confirmed_at || null);
      setArchitectNotes(arch.architect_notes || null);

      if (arch.tech_stack_recommendations && arch.tech_stack_recommendations.length > 0) {
        setSelectedCategory(arch.tech_stack_recommendations[0].category);
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

  const handleConfirmArchitecture = async () => {
    if (!project) return;
    setActionInProgress(true);
    try {
      await api.confirmArchitecture(project.id, {
        action: "confirm",
        architect_name: architectNameInput,
        notes: notesInput,
      });
      setConfirmationStatus("Confirmed");
      setConfirmedBy(architectNameInput);
      setConfirmedAt(new Date().toISOString());
      setArchitectNotes(notesInput);
      setConfirmModalOpen(false);
    } catch (err) {
      console.error(err);
      alert("Failed to confirm architecture: " + err);
    } finally {
      setActionInProgress(false);
    }
  };

  const handleApplyOverride = async (category: string, alternativeName: string) => {
    if (!project) return;
    setActionInProgress(true);
    try {
      await api.confirmArchitecture(project.id, {
        action: "customize",
        architect_name: architectNameInput,
        overrides: { [category]: alternativeName },
        notes: `Overrode ${category} with ${alternativeName}`,
      });
      setCustomizeModalOpen(false);
      await loadData();
    } catch (err) {
      console.error(err);
      alert("Failed to apply override: " + err);
    } finally {
      setActionInProgress(false);
    }
  };

  const handleRequestRevision = async () => {
    if (!project) return;
    setActionInProgress(true);
    try {
      await api.confirmArchitecture(project.id, {
        action: "request_revision",
        architect_name: architectNameInput,
        notes: notesInput,
      });
      setConfirmationStatus("Revisions Requested");
      setConfirmedBy(architectNameInput);
      setArchitectNotes(notesInput);
      setRevisionModalOpen(false);
    } catch (err) {
      console.error(err);
      alert("Failed to submit revision request: " + err);
    } finally {
      setActionInProgress(false);
    }
  };

  const tabs = [
    { id: "evolution", label: "🏛️ Architecture Evolution: Old vs New" },
    { id: "tech_stacks", label: "⚡ Recommended Tech Stacks & Trade-Offs" },
    { id: "canvas", label: "Interactive Canvas (React Flow)" },
    { id: "high_level", label: "Target High-Level (Mermaid)" },
    { id: "component", label: "Component Graph (Mermaid)" },
    { id: "deployment", label: "Deployment Topology (Mermaid)" },
    { id: "data_flow", label: "Data Flow Pipeline (Mermaid)" },
    { id: "sequence", label: "Sequence Flow (Mermaid)" },
    { id: "components_table", label: "Service Catalog" },
    { id: "apis_table", label: "API Endpoints" },
  ];

  return (
    <div className="min-h-screen flex flex-col bg-[#080c14]">
      <Navbar projectName={project?.name} projectId={project?.id} onRefresh={loadData} />

      <main className="flex-1 p-8 space-y-6 max-w-7xl mx-auto w-full">
        {/* Top Header */}
        <div className="border-b border-[#1e293b] pb-6 space-y-3">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div className="flex items-center space-x-3">
              <div className="p-2 rounded-xl bg-cyan-500/10 border border-cyan-500/30 text-cyan-400">
                <Network className="w-5 h-5" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-white tracking-tight">Architecture Studio & Tech Stack Intelligence</h1>
                <p className="text-xs text-slate-400">
                  Evidence-driven software decomposition, legacy-to-target evolution, and human-in-the-loop change confirmation.
                </p>
              </div>
            </div>

            {/* Confirmation Status Pill */}
            <div className="flex items-center space-x-2">
              <span className="text-xs text-slate-400 font-medium">Architecture Gate:</span>
              <span
                className={`px-3 py-1 rounded-full text-xs font-bold border flex items-center space-x-1.5 ${confirmationStatus === "Confirmed"
                    ? "bg-emerald-500/15 border-emerald-500/40 text-emerald-400"
                    : confirmationStatus === "Customized"
                      ? "bg-cyan-500/15 border-cyan-500/40 text-cyan-400"
                      : confirmationStatus === "Revisions Requested"
                        ? "bg-amber-500/15 border-amber-500/40 text-amber-400"
                        : "bg-blue-500/15 border-blue-500/40 text-blue-400 animate-pulse"
                  }`}
              >
                {confirmationStatus === "Confirmed" ? (
                  <CheckCircle2 className="w-3.5 h-3.5" />
                ) : confirmationStatus === "Customized" ? (
                  <Sliders className="w-3.5 h-3.5" />
                ) : confirmationStatus === "Revisions Requested" ? (
                  <AlertTriangle className="w-3.5 h-3.5" />
                ) : (
                  <Sparkles className="w-3.5 h-3.5" />
                )}
                <span>{confirmationStatus}</span>
              </span>
            </div>
          </div>

          {/* Style Justification Card */}
          <div className="p-4 rounded-xl bg-[#0a0f1d] border border-cyan-500/30 text-xs text-slate-300 leading-relaxed shadow-lg">
            <div className="font-bold text-cyan-400 mb-1 flex items-center space-x-2">
              <Zap className="w-4 h-4" />
              <span>Target Architecture Style: {newArch?.style || "Sovereign Hybrid Architecture with Event-Driven Ledger Settlement"}</span>
            </div>
            <p>{styleDesc || newArch?.description || "Combines stateless domestic cloud edge auto-scaling with an isolated on-premises Tier-IV private datacenter for core sovereign banking ledger and HSM cryptographic keys."}</p>
          </div>
        </div>

        {/* Change Confirmation Action Banner */}
        <div
          className={`p-5 rounded-2xl border transition-all ${confirmationStatus === "Confirmed"
              ? "bg-gradient-to-r from-emerald-950/40 via-[#0a0f1d] to-[#080c14] border-emerald-500/40"
              : confirmationStatus === "Customized"
                ? "bg-gradient-to-r from-cyan-950/40 via-[#0a0f1d] to-[#080c14] border-cyan-500/40"
                : confirmationStatus === "Revisions Requested"
                  ? "bg-gradient-to-r from-amber-950/40 via-[#0a0f1d] to-[#080c14] border-amber-500/40"
                  : "bg-gradient-to-r from-blue-950/50 via-[#0a0f1d] to-[#080c14] border-blue-500/40 shadow-xl"
            }`}
        >
          <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
            <div className="space-y-1.5 max-w-3xl">
              <div className="flex items-center space-x-2">
                {confirmationStatus === "Confirmed" ? (
                  <>
                    <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                    <span className="text-sm font-bold text-emerald-400">Target Architecture Confirmed & Signed Off</span>
                  </>
                ) : confirmationStatus === "Customized" ? (
                  <>
                    <Sliders className="w-5 h-5 text-cyan-400" />
                    <span className="text-sm font-bold text-cyan-400">Architecture Active with Custom Tech Stack Overrides</span>
                  </>
                ) : confirmationStatus === "Revisions Requested" ? (
                  <>
                    <AlertTriangle className="w-5 h-5 text-amber-400" />
                    <span className="text-sm font-bold text-amber-400">Architecture Revisions Requested</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-5 h-5 text-cyan-400" />
                    <span className="text-sm font-bold text-white">Action Required: Architecture Transition Review & Confirmation Gate</span>
                  </>
                )}
              </div>
              <p className="text-xs text-slate-300 leading-relaxed">
                {confirmationStatus === "Confirmed"
                  ? `Signed off by ${confirmedBy || "Lead Architect"} on ${confirmedAt ? new Date(confirmedAt).toLocaleDateString() : "Today"}. All 4 Architecture Decision Records (ADRs) have been formally Accepted for production.`
                  : confirmationStatus === "Customized"
                    ? `Configured with custom overrides by ${confirmedBy || "Lead Architect"}. Inspect modified layers and alternatives below.`
                    : confirmationStatus === "Revisions Requested"
                      ? `Notes: "${architectNotes || "Requested structural adjustments."}" Review feedback and update specifications.`
                      : "The AI agent team has synthesized the target architecture, component breakdown, and recommended technology stack with alternatives. Review the Old vs New evolution below and formally confirm to adopt this architecture."}
              </p>
            </div>

            {/* Action Buttons */}
            <div className="flex flex-wrap items-center gap-2.5">
              <button
                onClick={() => setConfirmModalOpen(true)}
                className="px-4 py-2 rounded-xl text-xs font-bold bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white shadow-lg shadow-emerald-950/40 flex items-center space-x-1.5 transition active:scale-95"
              >
                <CheckCircle2 className="w-4 h-4" />
                <span>{confirmationStatus === "Confirmed" ? "Re-Confirm Architecture" : "Confirm & Sign-Off Architecture"}</span>
              </button>
              <button
                onClick={() => setCustomizeModalOpen(true)}
                className="px-3.5 py-2 rounded-xl text-xs font-semibold bg-[#131d33] hover:bg-[#1a2744] border border-[#2a3b5c] text-cyan-300 flex items-center space-x-1.5 transition active:scale-95"
              >
                <Sliders className="w-3.5 h-3.5" />
                <span>Customize Stack</span>
              </button>
              <button
                onClick={() => setRevisionModalOpen(true)}
                className="px-3.5 py-2 rounded-xl text-xs font-semibold bg-[#131d33] hover:bg-[#1a2744] border border-[#2a3b5c] text-amber-300 flex items-center space-x-1.5 transition active:scale-95"
              >
                <RotateCcw className="w-3.5 h-3.5" />
                <span>Request Revisions</span>
              </button>
            </div>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex flex-wrap gap-1.5 bg-[#0a0f1d] border border-[#1e293b] p-2 rounded-xl shadow-lg">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition ${activeTab === tab.id
                  ? "bg-cyan-600 text-white shadow-md font-bold"
                  : "bg-[#131d33] text-slate-400 hover:text-white hover:bg-[#1a2744]"
                }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Dynamic Tab Views */}
        <div className="min-h-[550px] space-y-6">
          {/* TAB 1: ARCHITECTURE EVOLUTION: OLD VS NEW */}
          {activeTab === "evolution" && (
            <div className="space-y-6">
              {/* Sub-view Navigation */}
              <div className="flex items-center justify-between border-b border-[#1e293b] pb-3">
                <div className="flex items-center space-x-2">
                  <History className="w-4 h-4 text-cyan-400" />
                  <span className="text-xs font-bold text-slate-200 uppercase tracking-wider">Evolutionary Comparison Modes:</span>
                </div>
                <div className="flex items-center space-x-1.5 bg-[#0f172a] p-1 rounded-lg border border-[#1e293b]">
                  <button
                    onClick={() => setEvolutionView("cards")}
                    className={`px-2.5 py-1 rounded text-xs font-medium transition ${evolutionView === "cards" ? "bg-cyan-600 text-white" : "text-slate-400 hover:text-white"
                      }`}
                  >
                    Side-by-Side Cards
                  </button>
                  <button
                    onClick={() => setEvolutionView("matrix")}
                    className={`px-2.5 py-1 rounded text-xs font-medium transition ${evolutionView === "matrix" ? "bg-cyan-600 text-white" : "text-slate-400 hover:text-white"
                      }`}
                  >
                    Metrics Delta Matrix
                  </button>
                  <button
                    onClick={() => setEvolutionView("side_by_side")}
                    className={`px-2.5 py-1 rounded text-xs font-medium transition ${evolutionView === "side_by_side" ? "bg-cyan-600 text-white" : "text-slate-400 hover:text-white"
                      }`}
                  >
                    Dual Diagrams (Split View)
                  </button>
                  <button
                    onClick={() => setEvolutionView("old_diagram")}
                    className={`px-2.5 py-1 rounded text-xs font-medium transition ${evolutionView === "old_diagram" ? "bg-cyan-600 text-white" : "text-slate-400 hover:text-white"
                      }`}
                  >
                    Old Monolith Diagram
                  </button>
                  <button
                    onClick={() => setEvolutionView("new_diagram")}
                    className={`px-2.5 py-1 rounded text-xs font-medium transition ${evolutionView === "new_diagram" ? "bg-cyan-600 text-white" : "text-slate-400 hover:text-white"
                      }`}
                  >
                    New Target Diagram
                  </button>
                </div>
              </div>

              {/* Mode 1: Cards View */}
              {evolutionView === "cards" && (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {/* OLD ARCHITECTURE CARD */}
                  <div className="bg-[#0a0f1d] border border-rose-900/40 rounded-2xl p-6 space-y-5 shadow-xl relative overflow-hidden">
                    <div className="absolute top-0 right-0 px-4 py-1.5 bg-rose-500/20 border-b border-l border-rose-500/40 rounded-bl-xl text-[11px] font-bold text-rose-400 uppercase tracking-widest">
                      Legacy Baseline (v1.x)
                    </div>

                    <div className="space-y-1">
                      <div className="flex items-center space-x-2 text-rose-400 text-xs font-bold uppercase tracking-wider">
                        <History className="w-3.5 h-3.5" />
                        <span>Baseline State</span>
                      </div>
                      <h2 className="text-lg font-bold text-white">{oldArch?.name || "SmartBank 1.0 Legacy Monolith"}</h2>
                      <div className="text-xs font-mono text-rose-300">{oldArch?.style}</div>
                    </div>

                    <p className="text-xs text-slate-300 leading-relaxed bg-[#0f172a]/60 p-3.5 rounded-xl border border-rose-950/60">
                      {oldArch?.description}
                    </p>

                    {/* Key Bottlenecks / Flaws */}
                    <div className="space-y-2">
                      <div className="text-xs font-bold text-rose-400 uppercase tracking-wider">Key Flaws & Structural Limits:</div>
                      <ul className="space-y-1.5 text-xs text-slate-300">
                        {(oldArch?.characteristics || []).map((ch, idx) => (
                          <li key={idx} className="flex items-start space-x-2">
                            <span className="text-rose-400 font-bold mt-0.5">•</span>
                            <span>{ch}</span>
                          </li>
                        ))}
                      </ul>
                    </div>

                    {/* Baseline Metrics Grid */}
                    <div className="pt-2 border-t border-[#1e293b] space-y-2">
                      <div className="text-xs font-bold text-slate-400 uppercase tracking-wider">Baseline Performance Profile:</div>
                      <div className="grid grid-cols-2 gap-2 text-xs">
                        <div className="bg-[#0f172a] p-2.5 rounded-lg border border-rose-950/80">
                          <div className="text-[10px] text-slate-400">P99 Latency</div>
                          <div className="font-mono font-bold text-rose-400">{oldArch?.metrics?.latency_p99 || "2,400 ms"}</div>
                        </div>
                        <div className="bg-[#0f172a] p-2.5 rounded-lg border border-rose-950/80">
                          <div className="text-[10px] text-slate-400">Throughput Ceiling</div>
                          <div className="font-mono font-bold text-rose-400">{oldArch?.metrics?.throughput_tps || "1,200 TPS"}</div>
                        </div>
                        <div className="bg-[#0f172a] p-2.5 rounded-lg border border-rose-950/80">
                          <div className="text-[10px] text-slate-400">Availability SLA</div>
                          <div className="font-mono font-bold text-rose-400">{oldArch?.metrics?.availability || "99.5% (~44h down)"}</div>
                        </div>
                        <div className="bg-[#0f172a] p-2.5 rounded-lg border border-rose-950/80">
                          <div className="text-[10px] text-slate-400">Disaster Recovery</div>
                          <div className="font-mono font-bold text-rose-400">{oldArch?.metrics?.rpo_rto || "RPO: 4h | RTO: 2h"}</div>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* NEW TARGET ARCHITECTURE CARD */}
                  <div className="bg-[#0a0f1d] border border-cyan-500/40 rounded-2xl p-6 space-y-5 shadow-xl relative overflow-hidden">
                    <div className="absolute top-0 right-0 px-4 py-1.5 bg-cyan-500/20 border-b border-l border-cyan-500/40 rounded-bl-xl text-[11px] font-bold text-cyan-400 uppercase tracking-widest">
                      Target Prescribed (v2.0)
                    </div>

                    <div className="space-y-1">
                      <div className="flex items-center space-x-2 text-cyan-400 text-xs font-bold uppercase tracking-wider">
                        <Sparkles className="w-3.5 h-3.5" />
                        <span>Prescribed Target State</span>
                      </div>
                      <h2 className="text-lg font-bold text-white">{newArch?.name || "SmartBank 2.0 Sovereign Hybrid Architecture"}</h2>
                      <div className="text-xs font-mono text-cyan-300">{newArch?.style}</div>
                    </div>

                    <p className="text-xs text-slate-300 leading-relaxed bg-[#0f172a]/60 p-3.5 rounded-xl border border-cyan-950/60">
                      {newArch?.description}
                    </p>

                    {/* Key Innovations */}
                    <div className="space-y-2">
                      <div className="text-xs font-bold text-cyan-400 uppercase tracking-wider">Key Architectural Innovations:</div>
                      <ul className="space-y-1.5 text-xs text-slate-300">
                        {(newArch?.characteristics || []).map((ch, idx) => (
                          <li key={idx} className="flex items-start space-x-2">
                            <span className="text-cyan-400 font-bold mt-0.5">✓</span>
                            <span>{ch}</span>
                          </li>
                        ))}
                      </ul>
                    </div>

                    {/* Target Metrics Grid */}
                    <div className="pt-2 border-t border-[#1e293b] space-y-2">
                      <div className="text-xs font-bold text-slate-400 uppercase tracking-wider">Target Performance Profile:</div>
                      <div className="grid grid-cols-2 gap-2 text-xs">
                        <div className="bg-[#0f172a] p-2.5 rounded-lg border border-cyan-950/80">
                          <div className="text-[10px] text-slate-400">P99 Latency SLA</div>
                          <div className="font-mono font-bold text-emerald-400">{newArch?.metrics?.latency_p99 || "< 180 ms"}</div>
                        </div>
                        <div className="bg-[#0f172a] p-2.5 rounded-lg border border-cyan-950/80">
                          <div className="text-[10px] text-slate-400">Throughput Scale</div>
                          <div className="font-mono font-bold text-emerald-400">{newArch?.metrics?.throughput_tps || "100,000+ TPS"}</div>
                        </div>
                        <div className="bg-[#0f172a] p-2.5 rounded-lg border border-cyan-950/80">
                          <div className="text-[10px] text-slate-400">Target Availability</div>
                          <div className="font-mono font-bold text-emerald-400">{newArch?.metrics?.availability || "99.99% (< 52m down)"}</div>
                        </div>
                        <div className="bg-[#0f172a] p-2.5 rounded-lg border border-cyan-950/80">
                          <div className="text-[10px] text-slate-400">Disaster Recovery SLA</div>
                          <div className="font-mono font-bold text-emerald-400">{newArch?.metrics?.rpo_rto || "RPO: 0 | RTO: < 15s"}</div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Mode 2: Metrics Delta Matrix */}
              {evolutionView === "matrix" && (
                <div className="bg-[#0a0f1d] border border-[#1e293b] rounded-2xl overflow-hidden shadow-xl">
                  <div className="p-4 border-b border-[#1e293b] flex items-center justify-between">
                    <div>
                      <h3 className="text-sm font-bold text-white">Architectural Evolution & Performance Delta Matrix</h3>
                      <p className="text-xs text-slate-400">Direct dimension-by-dimension comparison between Legacy Baseline and Target Prescribed Architecture.</p>
                    </div>
                  </div>
                  <div className="overflow-x-auto">
                    <table className="w-full text-left border-collapse text-xs">
                      <thead>
                        <tr className="bg-[#0f172a] border-b border-[#1e293b] text-slate-400 uppercase tracking-wider font-semibold">
                          <th className="py-3 px-4">Architectural Dimension</th>
                          <th className="py-3 px-4 text-rose-400">Legacy Baseline (Old)</th>
                          <th className="py-3 px-4 text-cyan-400">Target Prescribed (New)</th>
                          <th className="py-3 px-4 text-emerald-400">Improvement Delta</th>
                          <th className="py-3 px-4">Impact</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-[#1e293b] text-slate-200">
                        {matrix.map((row, idx) => (
                          <tr key={idx} className="hover:bg-[#11192e] transition">
                            <td className="py-3.5 px-4 font-bold text-white">{row.dimension}</td>
                            <td className="py-3.5 px-4 font-mono text-rose-300/90">{row.legacy}</td>
                            <td className="py-3.5 px-4 font-mono font-semibold text-cyan-300">{row.target}</td>
                            <td className="py-3.5 px-4 font-mono font-bold text-emerald-400">
                              <span className="flex items-center space-x-1">
                                <TrendingUp className="w-3.5 h-3.5" />
                                <span>{row.delta}</span>
                              </span>
                            </td>
                            <td className="py-3.5 px-4">
                              <span
                                className={`px-2 py-0.5 rounded text-[10px] font-bold ${row.impact === "Critical"
                                    ? "bg-rose-500/20 text-rose-300 border border-rose-500/30"
                                    : row.impact === "High"
                                      ? "bg-amber-500/20 text-amber-300 border border-amber-500/30"
                                      : "bg-blue-500/20 text-blue-300 border border-blue-500/30"
                                  }`}
                              >
                                {row.impact}
                              </span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* Mode 3: Side-by-Side Dual Diagrams */}
              {evolutionView === "side_by_side" && (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <div className="bg-[#0a0f1d] border border-rose-900/40 rounded-2xl p-4 shadow-xl space-y-3">
                    <div className="flex items-center justify-between border-b border-[#1e293b] pb-2">
                      <span className="text-xs font-bold text-rose-400 uppercase">Legacy Monolith Topology</span>
                      <span className="text-[10px] font-mono text-slate-400">Single Central Database Bottleneck</span>
                    </div>
                    <MermaidViewer chart={oldArch?.mermaid_diagram || ""} title="Old Architecture (Legacy Monolith)" />
                  </div>
                  <div className="bg-[#0a0f1d] border border-cyan-500/40 rounded-2xl p-4 shadow-xl space-y-3">
                    <div className="flex items-center justify-between border-b border-[#1e293b] pb-2">
                      <span className="text-xs font-bold text-cyan-400 uppercase">Target Sovereign Mesh Topology</span>
                      <span className="text-[10px] font-mono text-slate-400">Edge Gateway + Redis + mTLS + Core HSM</span>
                    </div>
                    <MermaidViewer chart={newArch?.mermaid_diagram || ""} title="New Architecture (Target Sovereign Hybrid)" />
                  </div>
                </div>
              )}

              {/* Mode 4: Old Monolith Diagram Only */}
              {evolutionView === "old_diagram" && (
                <div className="bg-[#0a0f1d] border border-rose-900/40 rounded-2xl p-4 shadow-xl space-y-3">
                  <div className="flex items-center justify-between border-b border-[#1e293b] pb-2">
                    <span className="text-xs font-bold text-rose-400 uppercase">Legacy Monolith Topology (Baseline)</span>
                    <span className="text-xs text-slate-400 font-mono">Synchronous tight coupling with single database SPOF</span>
                  </div>
                  <MermaidViewer chart={oldArch?.mermaid_diagram || ""} title="Old Architecture (Legacy Monolith)" />
                </div>
              )}

              {/* Mode 5: New Target Diagram Only */}
              {evolutionView === "new_diagram" && (
                <div className="bg-[#0a0f1d] border border-cyan-500/40 rounded-2xl p-4 shadow-xl space-y-3">
                  <div className="flex items-center justify-between border-b border-[#1e293b] pb-2">
                    <span className="text-xs font-bold text-cyan-400 uppercase">Target Sovereign Hybrid Topology (Prescribed)</span>
                    <span className="text-xs text-slate-400 font-mono">Decoupled edge caching, Kafka event streaming & on-prem HSM enclave</span>
                  </div>
                  <MermaidViewer chart={newArch?.mermaid_diagram || ""} title="New Architecture (Target Sovereign Hybrid)" />
                </div>
              )}
            </div>
          )}

          {/* TAB 2: RECOMMENDED TECH STACKS & TRADE-OFFS */}
          {activeTab === "tech_stacks" && (
            <div className="space-y-6">
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-[#1e293b] pb-4">
                <div>
                  <h2 className="text-base font-bold text-white flex items-center space-x-2">
                    <Zap className="w-4 h-4 text-cyan-400" />
                    <span>Recommended Technology Stack & Trade-Off Rationale</span>
                  </h2>
                  <p className="text-xs text-slate-400">
                    Each technology was selected based on strict requirements mapping, throughput targets, and data residency policies.
                  </p>
                </div>
                <button
                  onClick={() => setCustomizeModalOpen(true)}
                  className="px-3.5 py-1.5 rounded-xl text-xs font-semibold bg-cyan-600 hover:bg-cyan-500 text-white flex items-center space-x-1.5 transition"
                >
                  <Sliders className="w-3.5 h-3.5" />
                  <span>Customize Stack</span>
                </button>
              </div>

              {/* Tech Stack Cards Grid */}
              <div className="grid grid-cols-1 gap-6">
                {techStacks.map((item, idx) => {
                  const isExpanded = expandedStackIdx === idx;
                  return (
                    <div
                      key={idx}
                      className="bg-[#0a0f1d] border border-[#1e293b] hover:border-cyan-500/40 rounded-2xl p-6 space-y-4 shadow-xl transition"
                    >
                      {/* Card Header */}
                      <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 border-b border-[#1e293b] pb-4">
                        <div className="space-y-1">
                          <div className="text-[11px] font-mono text-cyan-400 font-bold uppercase tracking-wider">
                            Layer {idx + 1}: {item.category}
                          </div>
                          <div className="flex items-center space-x-3">
                            <h3 className="text-base font-bold text-white">{item.selected}</h3>
                            {item.is_overridden && (
                              <span className="px-2 py-0.5 rounded-full text-[10px] bg-amber-500/20 text-amber-300 border border-amber-500/30 font-bold">
                                Architect Override
                              </span>
                            )}
                          </div>
                        </div>

                        {/* Supported Requirements Tags */}
                        <div className="flex flex-wrap items-center gap-1.5">
                          <span className="text-[10px] text-slate-400 mr-1">Grounding:</span>
                          {(item.requirements_supported || []).map((code) => (
                            <span
                              key={code}
                              className="px-2 py-0.5 rounded-md bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 font-mono text-[10px]"
                            >
                              {code}
                            </span>
                          ))}
                        </div>
                      </div>

                      {/* Why This Stack Was Chosen */}
                      <div className="bg-[#0f172a] p-4 rounded-xl border border-cyan-950/80 space-y-1.5">
                        <div className="text-xs font-bold text-cyan-300 flex items-center space-x-1.5">
                          <CheckCircle2 className="w-3.5 h-3.5 text-cyan-400" />
                          <span>Why ArchMind AI Prescribed This Technology:</span>
                        </div>
                        <p className="text-xs text-slate-300 leading-relaxed font-sans">{item.reason_why}</p>
                      </div>

                      {/* Alternatives Considered Accordion */}
                      <div className="space-y-3">
                        <button
                          onClick={() => setExpandedStackIdx(isExpanded ? null : idx)}
                          className="flex items-center justify-between w-full py-2 px-3 rounded-lg bg-[#11192e] text-xs font-semibold text-slate-300 hover:text-white transition"
                        >
                          <div className="flex items-center space-x-2">
                            <Scale className="w-3.5 h-3.5 text-cyan-400" />
                            <span>
                              {item.alternatives?.length || 0} Alternatives Evaluated & Trade-Off Analysis
                            </span>
                          </div>
                          {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                        </button>

                        {isExpanded && (
                          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 pt-2">
                            {(item.alternatives || []).map((alt, altIdx) => (
                              <div
                                key={altIdx}
                                className="bg-[#080c14] border border-[#1e293b] rounded-xl p-4 space-y-3 flex flex-col justify-between"
                              >
                                <div className="space-y-2">
                                  <div className="flex items-center justify-between">
                                    <span className="font-bold text-white text-xs">{alt.name}</span>
                                    <span className="px-1.5 py-0.5 rounded bg-rose-500/10 text-rose-400 border border-rose-500/20 text-[9px] font-bold">
                                      Rejected
                                    </span>
                                  </div>

                                  {/* Pros */}
                                  <div className="space-y-1">
                                    <div className="text-[10px] font-bold text-emerald-400">Pros Considered:</div>
                                    <ul className="text-[11px] text-slate-400 space-y-0.5">
                                      {(alt.pros || []).map((p, pIdx) => (
                                        <li key={pIdx} className="flex items-start space-x-1">
                                          <span className="text-emerald-400 font-bold">+</span>
                                          <span>{p}</span>
                                        </li>
                                      ))}
                                    </ul>
                                  </div>

                                  {/* Cons */}
                                  <div className="space-y-1">
                                    <div className="text-[10px] font-bold text-rose-400">Cons & Risks:</div>
                                    <ul className="text-[11px] text-slate-400 space-y-0.5">
                                      {(alt.cons || []).map((c, cIdx) => (
                                        <li key={cIdx} className="flex items-start space-x-1">
                                          <span className="text-rose-400 font-bold">-</span>
                                          <span>{c}</span>
                                        </li>
                                      ))}
                                    </ul>
                                  </div>

                                  {/* Why Rejected */}
                                  <div className="p-2.5 rounded-lg bg-rose-950/20 border border-rose-900/40 text-[11px] text-rose-300">
                                    <span className="font-bold block mb-0.5">Why Rejected:</span>
                                    {alt.why_rejected}
                                  </div>

                                  {/* Trade-off */}
                                  <div className="text-[10px] text-slate-400">
                                    <span className="font-semibold text-slate-300">Trade-Off: </span>
                                    {alt.trade_offs}
                                  </div>
                                </div>

                                <button
                                  onClick={() => handleApplyOverride(item.category, alt.name)}
                                  className="mt-3 w-full py-1.5 px-3 rounded-lg text-[11px] font-semibold bg-[#131d33] hover:bg-cyan-600 hover:text-white border border-[#2a3b5c] text-cyan-300 transition active:scale-95"
                                >
                                  Swap & Adopt This Alternative
                                </button>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* TAB 3: REACT FLOW CANVAS */}
          {activeTab === "canvas" && <ReactFlowGraph components={components} />}

          {/* TAB 4: HIGH-LEVEL DIAGRAM */}
          {activeTab === "high_level" && (
            <MermaidViewer chart={diagrams.high_level || ""} title="High-Level Architecture Overview" />
          )}

          {/* TAB 5: COMPONENT GRAPH */}
          {activeTab === "component" && (
            <MermaidViewer chart={diagrams.component || ""} title="Component Inter-Service Architecture" />
          )}

          {/* TAB 6: DEPLOYMENT TOPOLOGY */}
          {activeTab === "deployment" && (
            <MermaidViewer chart={diagrams.deployment || ""} title="Multi-Tier Sovereign Hybrid Deployment" />
          )}

          {/* TAB 7: DATA FLOW PIPELINE */}
          {activeTab === "data_flow" && (
            <MermaidViewer chart={diagrams.data_flow || ""} title="End-to-End Data Flow Pipeline" />
          )}

          {/* TAB 8: SEQUENCE FLOW */}
          {activeTab === "sequence" && (
            <MermaidViewer chart={diagrams.sequence || ""} title="High-Value Fund Transfer Sequence Diagram" />
          )}

          {/* TAB 9: SERVICE CATALOG */}
          {activeTab === "components_table" && (
            <div className="bg-[#0a0f1d] border border-[#1e293b] rounded-xl overflow-hidden shadow-xl">
              <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse text-xs">
                  <thead>
                    <tr className="bg-[#0f172a] border-b border-[#1e293b] text-slate-400 uppercase tracking-wider font-semibold">
                      <th className="py-3 px-4">Code</th>
                      <th className="py-3 px-4">Service Name</th>
                      <th className="py-3 px-4">Layer</th>
                      <th className="py-3 px-4">Technology</th>
                      <th className="py-3 px-4">Deployment Target</th>
                      <th className="py-3 px-4">Scaling</th>
                      <th className="py-3 px-4">Dependencies</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#1e293b] text-slate-200">
                    {components.map((c) => (
                      <tr key={c.id || c.component_code} className="hover:bg-[#11192e] transition">
                        <td className="py-3 px-4 font-mono font-bold text-cyan-400">{c.component_code}</td>
                        <td className="py-3 px-4 font-bold text-white">{c.name}</td>
                        <td className="py-3 px-4 text-slate-300">{c.layer}</td>
                        <td className="py-3 px-4 font-mono text-[11px] text-cyan-300">{c.technology_stack}</td>
                        <td className="py-3 px-4 text-slate-400">{c.deployment_target}</td>
                        <td className="py-3 px-4 text-slate-400">{c.scaling_strategy}</td>
                        <td className="py-3 px-4">
                          <div className="flex flex-wrap gap-1">
                            {(c.dependencies || []).map((dep) => (
                              <span key={dep} className="px-1.5 py-0.5 rounded bg-slate-800 text-slate-300 font-mono text-[9px]">
                                {dep}
                              </span>
                            ))}
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* TAB 10: API ENDPOINTS */}
          {activeTab === "apis_table" && (
            <div className="bg-[#0a0f1d] border border-[#1e293b] rounded-xl overflow-hidden shadow-xl">
              <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse text-xs">
                  <thead>
                    <tr className="bg-[#0f172a] border-b border-[#1e293b] text-slate-400 uppercase tracking-wider font-semibold">
                      <th className="py-3 px-4">Component</th>
                      <th className="py-3 px-4">Method</th>
                      <th className="py-3 px-4">API Path</th>
                      <th className="py-3 px-4">Summary</th>
                      <th className="py-3 px-4">Auth Requirement</th>
                      <th className="py-3 px-4">Rate Limit</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#1e293b] text-slate-200">
                    {apis.map((a, idx) => (
                      <tr key={idx} className="hover:bg-[#11192e] transition">
                        <td className="py-3 px-4 font-mono font-bold text-cyan-400">{a.component_code}</td>
                        <td className="py-3 px-4 font-mono font-bold">
                          <span
                            className={`px-2 py-0.5 rounded text-[10px] ${a.method === "POST"
                                ? "bg-blue-500/20 text-blue-400 border border-blue-500/30"
                                : "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"
                              }`}
                          >
                            {a.method}
                          </span>
                        </td>
                        <td className="py-3 px-4 font-mono text-cyan-300">{a.path}</td>
                        <td className="py-3 px-4 text-slate-200">{a.summary}</td>
                        <td className="py-3 px-4 text-slate-400 text-[11px]">{a.auth_requirement}</td>
                        <td className="py-3 px-4 font-mono text-slate-400 text-[11px]">{a.rate_limit}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      </main>

      {/* CONFIRM ARCHITECTURE MODAL */}
      {confirmModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-200">
          <div className="bg-[#0a0f1d] border border-cyan-500/40 rounded-2xl p-6 max-w-lg w-full space-y-5 shadow-2xl relative">
            <button
              onClick={() => setConfirmModalOpen(false)}
              className="absolute top-4 right-4 text-slate-400 hover:text-white"
            >
              <X className="w-5 h-5" />
            </button>

            <div className="flex items-center space-x-3">
              <div className="p-2.5 rounded-xl bg-emerald-500/20 border border-emerald-500/40 text-emerald-400">
                <CheckCircle2 className="w-6 h-6" />
              </div>
              <div>
                <h3 className="text-base font-bold text-white">Confirm & Formally Sign-Off Architecture</h3>
                <p className="text-xs text-slate-400">Records executive architectural approval and marks ADRs as Accepted.</p>
              </div>
            </div>

            <div className="space-y-4">
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-300">Approving Architect / Lead Sign-Off Name:</label>
                <input
                  type="text"
                  value={architectNameInput}
                  onChange={(e) => setArchitectNameInput(e.target.value)}
                  className="w-full px-3.5 py-2.5 rounded-xl bg-[#080c14] border border-[#1e293b] text-xs text-white focus:outline-none focus:border-cyan-500"
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-300">Architectural Approval Directives & Notes:</label>
                <textarea
                  rows={4}
                  value={notesInput}
                  onChange={(e) => setNotesInput(e.target.value)}
                  className="w-full px-3.5 py-2.5 rounded-xl bg-[#080c14] border border-[#1e293b] text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
                />
              </div>

              <div className="p-3 rounded-xl bg-[#0f172a] border border-[#1e293b] text-[11px] text-slate-400 space-y-1">
                <div className="font-semibold text-slate-300">Consequences of Confirmation:</div>
                <div>• Advances project status to <strong className="text-emerald-400">Completed</strong>.</div>
                <div>• Formally accepts all 4 Architecture Decision Records (ADRs).</div>
                <div>• Locks target Sovereign Hybrid topology for engineering execution.</div>
              </div>
            </div>

            <div className="flex items-center justify-end space-x-3 pt-2">
              <button
                onClick={() => setConfirmModalOpen(false)}
                className="px-4 py-2 rounded-xl text-xs font-medium text-slate-400 hover:text-white"
              >
                Cancel
              </button>
              <button
                onClick={handleConfirmArchitecture}
                disabled={actionInProgress}
                className="px-5 py-2.5 rounded-xl text-xs font-bold bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white shadow-lg shadow-emerald-950/40 flex items-center space-x-1.5 transition active:scale-95 disabled:opacity-50"
              >
                <Check className="w-4 h-4" />
                <span>{actionInProgress ? "Recording Sign-Off..." : "Formally Confirm & Adopt Target Architecture"}</span>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* CUSTOMIZE STACK MODAL */}
      {customizeModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-200">
          <div className="bg-[#0a0f1d] border border-cyan-500/40 rounded-2xl p-6 max-w-xl w-full space-y-5 shadow-2xl relative">
            <button
              onClick={() => setCustomizeModalOpen(false)}
              className="absolute top-4 right-4 text-slate-400 hover:text-white"
            >
              <X className="w-5 h-5" />
            </button>

            <div className="flex items-center space-x-3">
              <div className="p-2.5 rounded-xl bg-cyan-500/20 border border-cyan-500/40 text-cyan-400">
                <Sliders className="w-6 h-6" />
              </div>
              <div>
                <h3 className="text-base font-bold text-white">Customize Architecture Technology Stack</h3>
                <p className="text-xs text-slate-400">Override default recommendations with validated alternatives.</p>
              </div>
            </div>

            <div className="space-y-4">
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-300">Select Architecture Layer / Category:</label>
                <select
                  value={selectedCategory}
                  onChange={(e) => {
                    setSelectedCategory(e.target.value);
                    const cat = techStacks.find((t) => t.category === e.target.value);
                    if (cat && cat.alternatives && cat.alternatives.length > 0) {
                      setSelectedAlternative(cat.alternatives[0].name);
                    }
                  }}
                  className="w-full px-3.5 py-2.5 rounded-xl bg-[#080c14] border border-[#1e293b] text-xs text-white focus:outline-none focus:border-cyan-500"
                >
                  {techStacks.map((t, idx) => (
                    <option key={idx} value={t.category}>
                      {t.category} (Currently: {t.selected})
                    </option>
                  ))}
                </select>
              </div>

              {/* Show Available Alternatives for Selected Category */}
              {(() => {
                const currentItem = techStacks.find((t) => t.category === selectedCategory);
                if (!currentItem || !currentItem.alternatives || currentItem.alternatives.length === 0) {
                  return <div className="text-xs text-slate-400">No alternatives available for this layer.</div>;
                }
                return (
                  <div className="space-y-2">
                    <label className="text-xs font-semibold text-slate-300">Select Alternative to Adopt:</label>
                    <div className="space-y-2 max-h-56 overflow-y-auto pr-1">
                      {currentItem.alternatives.map((alt, idx) => (
                        <div
                          key={idx}
                          onClick={() => setSelectedAlternative(alt.name)}
                          className={`p-3 rounded-xl border cursor-pointer transition ${selectedAlternative === alt.name
                              ? "bg-cyan-950/40 border-cyan-500 text-white"
                              : "bg-[#080c14] border-[#1e293b] text-slate-300 hover:border-slate-600"
                            }`}
                        >
                          <div className="flex items-center justify-between">
                            <span className="font-bold text-xs">{alt.name}</span>
                            {selectedAlternative === alt.name && (
                              <span className="text-[10px] font-bold text-cyan-400 flex items-center space-x-1">
                                <Check className="w-3.5 h-3.5" />
                                <span>Selected</span>
                              </span>
                            )}
                          </div>
                          <p className="text-[11px] text-slate-400 mt-1">{alt.why_rejected}</p>
                          <div className="text-[10px] text-slate-500 mt-1">
                            <strong>Trade-off:</strong> {alt.trade_offs}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                );
              })()}
            </div>

            <div className="flex items-center justify-end space-x-3 pt-2">
              <button
                onClick={() => setCustomizeModalOpen(false)}
                className="px-4 py-2 rounded-xl text-xs font-medium text-slate-400 hover:text-white"
              >
                Cancel
              </button>
              <button
                onClick={() => handleApplyOverride(selectedCategory, selectedAlternative)}
                disabled={!selectedAlternative || actionInProgress}
                className="px-5 py-2.5 rounded-xl text-xs font-bold bg-cyan-600 hover:bg-cyan-500 text-white shadow-lg shadow-cyan-950/40 flex items-center space-x-1.5 transition active:scale-95 disabled:opacity-50"
              >
                <Check className="w-4 h-4" />
                <span>{actionInProgress ? "Applying..." : "Apply Tech Stack Override"}</span>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* REQUEST REVISIONS MODAL */}
      {revisionModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-200">
          <div className="bg-[#0a0f1d] border border-amber-500/40 rounded-2xl p-6 max-w-lg w-full space-y-5 shadow-2xl relative">
            <button
              onClick={() => setRevisionModalOpen(false)}
              className="absolute top-4 right-4 text-slate-400 hover:text-white"
            >
              <X className="w-5 h-5" />
            </button>

            <div className="flex items-center space-x-3">
              <div className="p-2.5 rounded-xl bg-amber-500/20 border border-amber-500/40 text-amber-400">
                <RotateCcw className="w-6 h-6" />
              </div>
              <div>
                <h3 className="text-base font-bold text-white">Request Architectural Revisions</h3>
                <p className="text-xs text-slate-400">Submit architect directives for re-evaluation by the agent pipeline.</p>
              </div>
            </div>

            <div className="space-y-4">
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-300">Architect Name:</label>
                <input
                  type="text"
                  value={architectNameInput}
                  onChange={(e) => setArchitectNameInput(e.target.value)}
                  className="w-full px-3.5 py-2.5 rounded-xl bg-[#080c14] border border-[#1e293b] text-xs text-white focus:outline-none focus:border-amber-500"
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-300">Revision Directives & Feedback:</label>
                <textarea
                  rows={4}
                  value={notesInput}
                  onChange={(e) => setNotesInput(e.target.value)}
                  placeholder="e.g. Ensure ledger batch exports maintain direct COBOL mainframe flat file compatibility..."
                  className="w-full px-3.5 py-2.5 rounded-xl bg-[#080c14] border border-[#1e293b] text-xs text-slate-200 focus:outline-none focus:border-amber-500"
                />
              </div>
            </div>

            <div className="flex items-center justify-end space-x-3 pt-2">
              <button
                onClick={() => setRevisionModalOpen(false)}
                className="px-4 py-2 rounded-xl text-xs font-medium text-slate-400 hover:text-white"
              >
                Cancel
              </button>
              <button
                onClick={handleRequestRevision}
                disabled={actionInProgress}
                className="px-5 py-2.5 rounded-xl text-xs font-bold bg-amber-600 hover:bg-amber-500 text-white shadow-lg shadow-amber-950/40 flex items-center space-x-1.5 transition active:scale-95 disabled:opacity-50"
              >
                <RotateCcw className="w-4 h-4" />
                <span>{actionInProgress ? "Submitting..." : "Submit Revision Request"}</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
