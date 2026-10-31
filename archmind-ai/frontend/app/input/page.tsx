"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import {
  Upload,
  FileText,
  FileCode,
  PenTool,
  Sparkles,
  ArrowRight,
  CheckCircle2,
  AlertCircle,
  FileUp,
  Cpu,
  Layers,
  Shield,
  Zap,
  X
} from "lucide-react";
import { api } from "@/lib/api";
import { Navbar } from "@/components/shared/Navbar";

export default function InputModulePage() {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<"file" | "text">("text");
  const [projectName, setProjectName] = useState("");
  const [projectDescription, setProjectDescription] = useState("");
  const [textContent, setTextContent] = useState("");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [pauseForClarification, setPauseForClarification] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [activeStep, setActiveStep] = useState(0);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const samplePresets = [
    {
      title: "Healthcare Telemedicine & Remote Care",
      desc: "HIPAA compliance, real-time WebRTC, p99 < 150ms, 50,000 active video consultations",
      content: `# MedPulse 3.0 - Enterprise Telemedicine & EHR Platform

1. Patient Consultation: The platform must support real-time WebRTC video and audio consultations between licensed physicians and patients.
2. Latency Target: Media stream negotiation and end-to-end signaling latency must not exceed 150 milliseconds at the 99th percentile.
3. Concurrency: The core signaling mesh and media relay servers must sustain 50,000 active concurrent video sessions during peak hours.
4. Compliance & Privacy: All patient Electronic Health Records (EHR) and video metadata must comply strictly with HIPAA and HITECH security standards.
5. Storage & Encryption: All medical records and diagnostic images at rest must be encrypted with AES-256; TLS 1.3 enforced for data in transit.
6. Prescription Signing: Electronic prescriptions (e-Rx) must require cryptographically signed doctor certificates with multi-factor authentication.`,
    },
    {
      title: "Autonomous Fleet Telematics Mesh",
      desc: "200,000 vehicles, 40k events/sec, sub-50ms ingestion, signed OTA updates",
      content: `# FleetTrack AI - Autonomous Fleet Management Platform

1. Telemetry Ingestion: Vehicle IoT gateways must stream GPS coordinates, battery status, and sensor alerts every 100 milliseconds.
2. High Throughput: The ingestion pipeline must handle 200,000 active connected vehicles with sustained 40,000 events per second.
3. Latency SLA: Critical collision avoidance warnings and alert dispatches must be processed in under 50 milliseconds at p99.
4. Firmware Security: Vehicle Firmware Over-The-Air (FOTA) updates must be digitally signed with dual-key cryptographic certificates.
5. Time-Series Persistence: Raw telemetry data must be persisted in a partitioned append-only time-series store with automated archival.`,
    },
    {
      title: "Global E-Commerce & Flash Sale Engine",
      desc: "100,000 TPS, sub-second checkout, inventory locking, zero overselling",
      content: `# HyperShop - High-Throughput Omni-Channel Retail Platform

1. Flash Sale Checkout: The order management system shall support 100,000 transactions per second during viral flash sale events.
2. Inventory Guarantee: The inventory service must enforce distributed atomic locking to guarantee zero overselling under race conditions.
3. Latency SLA: Cart checkout and payment authorization handshake must complete in under 800 milliseconds p99.
4. Payment Security: Must comply with PCI-DSS 4.0; customer credit card tokens must be isolated in a dedicated tokenization vault.
5. Multi-Region Availability: Deliver 99.99% availability with active-active regional replication and sub-minute failover.`,
    },
  ];

  const agentSteps = [
    { title: "Ingestion & Semantic Chunking", desc: "Parsing document structure & creating vector index" },
    { title: "Evidence Intelligence Agent", desc: "Extracting statements, constraints & citation provenance" },
    { title: "Requirements Engineering Agent", desc: "IEEE normalization & classification (FR/NFR/Constraints)" },
    { title: "Conflict Intelligence Agent", desc: "Detecting contradictions, deployment clashes & missing SLAs" },
    { title: "Architecture Reasoning Agent", desc: "Decomposing components, services, APIs & formal ADRs" },
    { title: "Security Intelligence Agent", desc: "Synthesizing mTLS, encryption, IAM & audit controls" },
    { title: "Architecture Validation Agent", desc: "NetworkX DAG cycle checks & risk register scoring" },
    { title: "Traceability & Visualization", desc: "Generating React Flow canvas & 5 Mermaid.js diagrams" },
  ];

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      setErrorMsg(null);
      if (!projectName) {
        const cleanName = file.name.replace(/\.[^/.]+$/, "").replace(/[-_]/g, " ");
        setProjectName(cleanName.charAt(0).toUpperCase() + cleanName.slice(1) + " Architecture");
      }
    }
  };

  const handleSelectPreset = (preset: typeof samplePresets[0]) => {
    setTextContent(preset.content);
    setProjectName(preset.title);
    setProjectDescription(preset.desc);
    setErrorMsg(null);
  };

  const handleSubmitAnalysis = async () => {
    if (activeTab === "file" && !selectedFile) {
      setErrorMsg("Please select or upload a document file (.pdf, .docx, .txt, .md).");
      return;
    }
    if (activeTab === "text" && (!textContent || textContent.trim().length < 30)) {
      setErrorMsg("Please enter at least a few requirement sentences or choose a preset.");
      return;
    }

    setAnalyzing(true);
    setErrorMsg(null);
    setActiveStep(0);

    // Simulate agent progress indicator
    const stepInterval = setInterval(() => {
      setActiveStep((prev) => (prev < agentSteps.length - 1 ? prev + 1 : prev));
    }, 700);

    try {
      const formData = new FormData();
      formData.append("project_name", projectName || "Custom Architecture Analysis");
      formData.append("description", projectDescription || "Synthesized by ArchMind AI multi-agent orchestration");
      formData.append("input_mode", activeTab);
      formData.append("pause_for_clarification", String(pauseForClarification));

      if (activeTab === "file" && selectedFile) {
        formData.append("file", selectedFile);
      } else if (activeTab === "text") {
        formData.append("text_content", textContent);
      }

      const res = await api.analyzeInput(formData);
      if (res?.project_id && typeof window !== "undefined") {
        localStorage.setItem("archmind_active_project_id", res.project_id);
      }
      clearInterval(stepInterval);
      setActiveStep(agentSteps.length);

      // Redirect user to the synthesized architecture studio
      setTimeout(() => {
        router.push("/architecture");
      }, 1000);
    } catch (err: any) {
      clearInterval(stepInterval);
      setAnalyzing(false);
      setErrorMsg(err?.message || "Failed to analyze input. Please check backend connection.");
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-[#080c14]">
      <Navbar projectName="ArchMind AI – Project Input & Analysis Studio" />

      <main className="flex-1 p-8 space-y-8 max-w-6xl mx-auto w-full">
        {/* Header */}
        <div className="border-b border-[#1e293b] pb-6 space-y-2">
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 text-xs font-semibold">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Unified Requirements Ingestion Engine</span>
          </div>
          <h1 className="text-2xl font-extrabold text-white tracking-tight">
            Input Requirements & Synthesize Architecture
          </h1>
          <p className="text-xs text-slate-300 max-w-3xl leading-relaxed">
            Provide software requirements either by <strong>uploading documents (PDF, DOC, DOCX, TXT, MD)</strong> or by{" "}
            <strong>typing / pasting raw specification text</strong>. ArchMind AI&apos;s 8 specialized agents will extract evidence,
            normalize requirements, detect conflicts, and synthesize a complete validated architecture.
          </p>
        </div>

        {errorMsg && (
          <div className="p-4 rounded-xl bg-rose-500/15 border border-rose-500/40 text-rose-300 text-xs flex items-center space-x-3">
            <AlertCircle className="w-4 h-4 shrink-0 text-rose-400" />
            <span>{errorMsg}</span>
          </div>
        )}

        {/* Project Setup Details */}
        <div className="bg-[#0a0f1d] border border-[#1e293b] rounded-xl p-6 space-y-4 shadow-xl">
          <span className="text-xs font-bold text-slate-200 uppercase tracking-wider block">
            Step 1: Project Metadata (Optional)
          </span>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="text-[11px] font-semibold text-slate-400 uppercase block mb-1">
                Project Name
              </label>
              <input
                type="text"
                placeholder="e.g., Telemedicine Video Platform Architecture"
                value={projectName}
                onChange={(e) => setProjectName(e.target.value)}
                className="w-full px-3.5 py-2.5 rounded-lg bg-[#0f172a] border border-[#1e293b] text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-400 font-sans"
              />
            </div>

            <div>
              <label className="text-[11px] font-semibold text-slate-400 uppercase block mb-1">
                Domain / Project Description
              </label>
              <input
                type="text"
                placeholder="e.g., High-throughput microservices for patient consultations and EHR"
                value={projectDescription}
                onChange={(e) => setProjectDescription(e.target.value)}
                className="w-full px-3.5 py-2.5 rounded-lg bg-[#0f172a] border border-[#1e293b] text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-400 font-sans"
              />
            </div>
          </div>
        </div>

        {/* Step 2: Input Mode Switcher */}
        <div className="bg-[#0a0f1d] border border-[#1e293b] rounded-xl p-6 space-y-6 shadow-xl">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-[#1e293b] pb-4 gap-4">
            <div>
              <span className="text-xs font-bold text-slate-200 uppercase tracking-wider block">
                Step 2: Choose Your Input Method
              </span>
              <p className="text-[11px] text-slate-400 mt-0.5">Upload existing files or write/paste requirements directly</p>
            </div>

            {/* Mode Pills */}
            <div className="flex items-center space-x-2 bg-[#0f172a] p-1.5 rounded-xl border border-[#1e293b]">
              <button
                onClick={() => setActiveTab("file")}
                className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-xs font-semibold transition ${
                  activeTab === "file"
                    ? "bg-gradient-to-r from-blue-600 to-cyan-600 text-white shadow-md"
                    : "text-slate-400 hover:text-white"
                }`}
              >
                <Upload className="w-3.5 h-3.5" />
                <span>Upload Document (PDF / DOC / MD)</span>
              </button>

              <button
                onClick={() => setActiveTab("text")}
                className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-xs font-semibold transition ${
                  activeTab === "text"
                    ? "bg-gradient-to-r from-blue-600 to-cyan-600 text-white shadow-md"
                    : "text-slate-400 hover:text-white"
                }`}
              >
                <PenTool className="w-3.5 h-3.5" />
                <span>Write / Paste Requirements Text</span>
              </button>
            </div>
          </div>

          {/* TAB 1: FILE UPLOAD OPTION */}
          {activeTab === "file" && (
            <div className="space-y-4">
              <label className="border-2 border-dashed border-[#334155] hover:border-cyan-400/70 rounded-2xl p-10 flex flex-col items-center justify-center cursor-pointer bg-[#070b14] hover:bg-[#0c1426] transition group">
                <div className="w-14 h-14 rounded-full bg-cyan-500/10 group-hover:bg-cyan-500/20 flex items-center justify-center text-cyan-400 mb-4 transition">
                  <FileUp className="w-7 h-7" />
                </div>
                <div className="text-sm font-bold text-white mb-1">
                  Click to browse or drag & drop files here
                </div>
                <div className="text-xs text-slate-400 font-mono">
                  Supports PDF (.pdf), Microsoft Word (.doc, .docx), Markdown (.md), and Plain Text (.txt)
                </div>
                <input
                  type="file"
                  onChange={handleFileChange}
                  accept=".pdf,.doc,.docx,.txt,.md,.json"
                  className="hidden"
                />
              </label>

              {selectedFile && (
                <div className="flex items-center justify-between p-4 rounded-xl bg-[#0f172a] border border-cyan-500/30">
                  <div className="flex items-center space-x-3">
                    <FileText className="w-5 h-5 text-cyan-400" />
                    <div>
                      <div className="text-xs font-bold text-white">{selectedFile.name}</div>
                      <div className="text-[10px] text-slate-400 font-mono">
                        {(selectedFile.size / 1024).toFixed(1)} KB • {selectedFile.type || "Document"}
                      </div>
                    </div>
                  </div>
                  <button
                    onClick={() => setSelectedFile(null)}
                    className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              )}
            </div>
          )}

          {/* TAB 2: TEXT INPUT OPTION */}
          {activeTab === "text" && (
            <div className="space-y-4">
              {/* Presets Header */}
              <div className="space-y-2">
                <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 block">
                  Quick-Load Real-World Architecture Presets:
                </span>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                  {samplePresets.map((preset, idx) => (
                    <button
                      key={idx}
                      onClick={() => handleSelectPreset(preset)}
                      className="text-left p-3 rounded-xl bg-[#0f172a] hover:bg-[#131f38] border border-[#1e293b] hover:border-cyan-500/40 transition group"
                    >
                      <div className="text-xs font-bold text-white group-hover:text-cyan-300 transition">
                        {preset.title}
                      </div>
                      <div className="text-[10px] text-slate-400 mt-1 line-clamp-2">{preset.desc}</div>
                    </button>
                  ))}
                </div>
              </div>

              {/* Text Area */}
              <div className="relative">
                <textarea
                  rows={12}
                  value={textContent}
                  onChange={(e) => setTextContent(e.target.value)}
                  placeholder="Type or paste requirements, user stories, constraints, or PRD notes here...&#10;&#10;Example:&#10;1. The system shall support 50,000 active concurrent streaming users with sub-100ms latency.&#10;2. Patient medical records must comply with HIPAA regulations and remain encrypted with AES-256.&#10;3. Core ledgers must be deployed in a secure on-premises private datacenter while edge gateways run on cloud."
                  className="w-full p-4 rounded-xl bg-[#070b14] border border-[#1e293b] text-xs text-slate-200 placeholder-slate-600 focus:outline-none focus:border-cyan-400 font-mono leading-relaxed resize-y"
                />
                <div className="absolute bottom-3 right-3 text-[10px] text-slate-500 font-mono bg-[#0a0f1d] px-2 py-0.5 rounded border border-[#1e293b]">
                  {textContent.length} characters • {textContent.split(/\s+/).filter(Boolean).length} words
                </div>
              </div>
            </div>
          )}

          {/* Step 3: Execution Settings & Submit */}
          <div className="pt-4 border-t border-[#1e293b] flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <label className="flex items-center space-x-2.5 cursor-pointer text-xs text-slate-300 select-none">
              <input
                type="checkbox"
                checked={pauseForClarification}
                onChange={(e) => setPauseForClarification(e.target.checked)}
                className="w-4 h-4 rounded text-cyan-600 bg-[#0f172a] border-[#334155] focus:ring-cyan-500 focus:ring-offset-0"
              />
              <span>Pause at Clarification Room if architectural conflicts are detected (HITL Mode)</span>
            </label>

            <button
              onClick={handleSubmitAnalysis}
              disabled={analyzing}
              className="flex items-center justify-center space-x-2 px-6 py-3 rounded-xl bg-gradient-to-r from-blue-600 via-cyan-600 to-teal-500 hover:from-blue-500 hover:to-cyan-500 text-white text-xs font-bold shadow-xl shadow-cyan-600/25 transition disabled:opacity-50"
            >
              <Cpu className={`w-4 h-4 ${analyzing ? "animate-spin" : ""}`} />
              <span>{analyzing ? "AI Orchestrator Analyzing..." : "Analyze & Generate Architecture"}</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>

        {/* Live Multi-Agent Execution Modal / Overlay */}
        {analyzing && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-md p-6">
            <div className="bg-[#0f172a] border border-cyan-500/40 rounded-2xl w-full max-w-xl p-7 shadow-2xl space-y-6">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 to-cyan-500 flex items-center justify-center text-white shadow-lg shadow-cyan-500/30">
                  <Cpu className="w-5 h-5 animate-pulse" />
                </div>
                <div>
                  <h3 className="text-base font-bold text-white">LangGraph Multi-Agent Orchestration</h3>
                  <p className="text-xs text-cyan-400 font-mono">Synthesizing Architecture & Verification DAG...</p>
                </div>
              </div>

              {/* Progress bar */}
              <div className="w-full bg-[#0a0f1d] rounded-full h-2 overflow-hidden border border-[#1e293b]">
                <div
                  className="bg-gradient-to-r from-blue-500 via-cyan-400 to-teal-400 h-full transition-all duration-500"
                  style={{ width: `${Math.min(100, (activeStep / agentSteps.length) * 100)}%` }}
                />
              </div>

              {/* Steps List */}
              <div className="space-y-2.5 max-h-64 overflow-y-auto pr-1">
                {agentSteps.map((step, idx) => {
                  const isDone = idx < activeStep;
                  const isCurrent = idx === activeStep;

                  return (
                    <div
                      key={idx}
                      className={`p-2.5 rounded-lg border text-xs flex items-center justify-between transition ${
                        isCurrent
                          ? "bg-cyan-500/15 border-cyan-500/50 text-white font-semibold"
                          : isDone
                          ? "bg-[#0a0f1d] border-emerald-500/30 text-emerald-300"
                          : "bg-[#080c14] border-[#1e293b] text-slate-500"
                      }`}
                    >
                      <div className="flex items-center space-x-3">
                        <span className={`w-2 h-2 rounded-full ${
                          isCurrent ? "bg-cyan-400 animate-ping" : isDone ? "bg-emerald-400" : "bg-slate-700"
                        }`} />
                        <div>
                          <div className="text-[11px]">{step.title}</div>
                          <div className="text-[9px] text-slate-400">{step.desc}</div>
                        </div>
                      </div>

                      {isDone && <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />}
                    </div>
                  );
                })}
              </div>

              <div className="text-center text-[10px] text-slate-400 font-mono">
                Persisting structured architecture metadata to PostgreSQL relational models...
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
