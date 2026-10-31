"use client";

import { useState } from "react";
import Link from "next/link";
import { Play, Sparkles, Download, CheckCircle2, RefreshCw, FileText, PlusCircle } from "lucide-react";
import { api } from "@/lib/api";

interface NavbarProps {
  projectName?: string;
  projectId?: string;
  status?: string;
  onRefresh?: () => void;
}

export function Navbar({
  projectName = "SmartBank 2.0 - Next-Gen Digital Banking Platform",
  projectId,
  status = "Active",
  onRefresh,
}: NavbarProps) {
  const [isRunning, setIsRunning] = useState(false);
  const [isExporting, setIsExporting] = useState(false);
  const [reportModalOpen, setReportModalOpen] = useState(false);
  const [reportMarkdown, setReportMarkdown] = useState("");

  const handleRunPipeline = async () => {
    if (!projectId) return;
    setIsRunning(true);
    try {
      await api.triggerPipeline(projectId, false);
      if (onRefresh) onRefresh();
    } catch (e) {
      console.error(e);
    } finally {
      setIsRunning(false);
    }
  };

  const handleExportReport = async () => {
    if (!projectId) return;
    setIsExporting(true);
    try {
      const md = await api.getReportMarkdown(projectId);
      setReportMarkdown(md);
      setReportModalOpen(true);
    } catch (e) {
      console.error(e);
    } finally {
      setIsExporting(false);
    }
  };

  const handleDownloadFile = () => {
    const blob = new Blob([reportMarkdown], { type: "text/markdown;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `ArchMind_Architecture_Dossier_${new Date().toISOString().slice(0, 10)}.md`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <>
      <header className="h-16 bg-[#0a0f1d]/90 backdrop-blur border-b border-[#1e293b] flex items-center justify-between px-6 sticky top-0 z-20">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <span className="w-2.5 h-2.5 rounded-full bg-cyan-400"></span>
            <h2 className="text-sm font-semibold text-white tracking-tight truncate max-w-md">
              {projectName}
            </h2>
          </div>
          <span className="text-[11px] font-mono px-2 py-0.5 rounded-full bg-blue-500/15 text-blue-400 border border-blue-500/30">
            {status.toUpperCase()}
          </span>
        </div>

        <div className="flex items-center space-x-3">
          {onRefresh && (
            <button
              onClick={onRefresh}
              className="p-2 rounded-lg bg-[#131d33] text-slate-300 hover:text-white border border-[#1e293b] hover:border-slate-600 transition"
              title="Refresh Data"
            >
              <RefreshCw className="w-3.5 h-3.5" />
            </button>
          )}

          <button
            onClick={handleExportReport}
            disabled={isExporting}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-[#131d33] text-slate-200 hover:text-white border border-[#1e293b] hover:border-slate-600 text-xs font-medium transition"
          >
            <FileText className="w-3.5 h-3.5 text-cyan-400" />
            <span>{isExporting ? "Exporting..." : "Export Dossier"}</span>
          </button>

          <Link
            href="/input"
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-cyan-600/20 text-cyan-300 hover:bg-cyan-600/30 border border-cyan-500/40 text-xs font-semibold transition"
          >
            <PlusCircle className="w-3.5 h-3.5 text-cyan-400" />
            <span>+ New Input</span>
          </Link>

          <button
            onClick={handleRunPipeline}
            disabled={isRunning}
            className="flex items-center space-x-1.5 px-3.5 py-1.5 rounded-lg bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500 text-white text-xs font-semibold shadow-lg shadow-cyan-600/20 transition disabled:opacity-50"
          >
            <Play className={`w-3.5 h-3.5 fill-white ${isRunning ? "animate-spin" : ""}`} />
            <span>{isRunning ? "Orchestrating..." : "Run AI Pipeline"}</span>
          </button>
        </div>
      </header>

      {/* Report Modal */}
      {reportModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 p-6 backdrop-blur-sm">
          <div className="bg-[#0f172a] border border-[#334155] rounded-xl w-full max-w-4xl max-h-[85vh] flex flex-col shadow-2xl">
            <div className="p-4 border-b border-[#334155] flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <FileText className="w-5 h-5 text-cyan-400" />
                <h3 className="text-sm font-bold text-white">ArchMind AI – Architecture Dossier Export</h3>
              </div>
              <div className="flex items-center space-x-2">
                <button
                  onClick={handleDownloadFile}
                  className="flex items-center space-x-1.5 px-3 py-1 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-semibold transition"
                >
                  <Download className="w-3.5 h-3.5" />
                  <span>Download .md</span>
                </button>
                <button
                  onClick={() => setReportModalOpen(false)}
                  className="px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs transition"
                >
                  Close
                </button>
              </div>
            </div>
            <div className="p-6 overflow-y-auto flex-1 font-mono text-xs text-slate-300 whitespace-pre-wrap leading-relaxed select-text bg-[#090d16]">
              {reportMarkdown}
            </div>
          </div>
        </div>
      )}
    </>
  );
}

