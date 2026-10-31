"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { AlertTriangle, CheckCircle2, ArrowRight, ShieldCheck, HelpCircle, Check, X } from "lucide-react";
import { api } from "@/lib/api";
import { ConflictItem, Project } from "@/types";
import { Navbar } from "@/components/shared/Navbar";

export default function ConflictsPage() {
  const [project, setProject] = useState<Project | null>(null);
  const [conflicts, setConflicts] = useState<ConflictItem[]>([]);
  const [selectedConflict, setSelectedConflict] = useState<ConflictItem | null>(null);
  const [resolveNotes, setResolveNotes] = useState("");
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    try {
      setLoading(true);
      const projects = await api.getProjects();
      const savedId = typeof window !== "undefined" ? localStorage.getItem("archmind_active_project_id") : null;
      const active = (savedId ? projects.find(p => p.id === savedId) : null) || projects[0] || (await api.loadSmartBankDemo());
      setProject(active);

      const cList = await api.getConflicts(active.id);
      setConflicts(cList);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleResolve = async (conflictId: string) => {
    try {
      await api.resolveConflict(
        conflictId,
        resolveNotes || "Directly confirmed and resolved by Lead Architect."
      );
      setSelectedConflict(null);
      setResolveNotes("");
      await loadData();
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-[#080c14]">
      <Navbar projectName={project?.name} projectId={project?.id} onRefresh={loadData} />

      <main className="flex-1 p-8 space-y-6 max-w-7xl mx-auto w-full">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-[#1e293b] pb-6">
          <div>
            <div className="flex items-center space-x-2">
              <AlertTriangle className="w-5 h-5 text-amber-400" />
              <h1 className="text-xl font-bold text-white tracking-tight">Conflict Detective</h1>
            </div>
            <p className="text-xs text-slate-400 mt-1">
              Autonomous detection of direct contradictions, deployment incompatibilities, and missing SLAs across stakeholders.
            </p>
          </div>

          <Link
            href="/clarification"
            className="flex items-center space-x-2 px-4 py-2 rounded-lg bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500 text-white text-xs font-semibold shadow-lg shadow-cyan-600/20 transition"
          >
            <HelpCircle className="w-3.5 h-3.5" />
            <span>Open Clarification Room (HITL)</span>
          </Link>
        </div>

        {/* Conflicts Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {conflicts.map((conf) => {
            const isResolved = conf.status === "Resolved";
            return (
              <div
                key={conf.id || conf.conflict_code}
                className={`border rounded-xl p-5 flex flex-col justify-between transition-all bg-[#0a0f1d] ${
                  isResolved ? "border-emerald-500/30" : "border-amber-500/30 shadow-lg shadow-amber-500/5"
                }`}
              >
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="font-mono text-xs font-bold px-2 py-0.5 rounded bg-amber-500/20 text-amber-400 border border-amber-500/30">
                      {conf.conflict_code}
                    </span>
                    <span
                      className={`text-[10px] font-mono px-2 py-0.5 rounded-full font-bold ${
                        isResolved
                          ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"
                          : "bg-rose-500/20 text-rose-400 border border-rose-500/30"
                      }`}
                    >
                      {conf.status.toUpperCase()}
                    </span>
                  </div>

                  <div>
                    <h3 className="text-sm font-bold text-white leading-snug">{conf.conflict_type}</h3>
                    <div className="flex flex-wrap gap-1 mt-1.5">
                      {(conf.conflicting_req_codes || []).map((code) => (
                        <span
                          key={code}
                          className="px-1.5 py-0.5 rounded bg-[#1e293b] text-cyan-300 font-mono text-[9px] border border-cyan-500/30"
                        >
                          {code}
                        </span>
                      ))}
                    </div>
                  </div>

                  <p className="text-xs text-slate-300 leading-relaxed bg-[#0f172a] p-3 rounded-lg border border-[#1e293b]">
                    {conf.explanation}
                  </p>

                  <div className="space-y-1.5 text-[11px]">
                    <div className="text-slate-400">
                      <strong className="text-slate-300">Technical Impact:</strong> {conf.technical_impact}
                    </div>
                    <div className="text-slate-400">
                      <strong className="text-slate-300">Suggested Resolution:</strong> {conf.suggested_resolution}
                    </div>
                  </div>
                </div>

                <div className="pt-4 border-t border-[#1e293b] mt-4 flex items-center justify-between">
                  <span className="text-[10px] text-slate-500 font-mono">
                    Severity: <strong className="text-amber-400">{conf.severity}</strong>
                  </span>
                  {!isResolved ? (
                    <button
                      onClick={() => setSelectedConflict(conf)}
                      className="flex items-center space-x-1 px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold transition"
                    >
                      <Check className="w-3.5 h-3.5" />
                      <span>Resolve</span>
                    </button>
                  ) : (
                    <span className="flex items-center space-x-1 text-emerald-400 text-xs font-medium">
                      <CheckCircle2 className="w-3.5 h-3.5" />
                      <span>Resolved</span>
                    </span>
                  )}
                </div>
              </div>
            );
          })}
        </div>

        {/* Resolve Modal */}
        {selectedConflict && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 p-6 backdrop-blur-sm">
            <div className="bg-[#0f172a] border border-[#334155] rounded-xl w-full max-w-lg p-6 shadow-2xl space-y-4">
              <div className="flex items-center justify-between border-b border-[#1e293b] pb-3">
                <span className="text-sm font-bold text-white">Resolve {selectedConflict.conflict_code}</span>
                <button
                  onClick={() => setSelectedConflict(null)}
                  className="p-1 text-slate-400 hover:text-white transition"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              <div className="space-y-3 text-xs">
                <p className="text-slate-300 leading-relaxed bg-[#0a0f1d] p-3 rounded-lg border border-[#1e293b]">
                  {selectedConflict.explanation}
                </p>

                <div>
                  <label className="text-slate-400 block mb-1 font-semibold uppercase text-[10px]">
                    Resolution Notes & Human Justification
                  </label>
                  <textarea
                    rows={3}
                    placeholder="Enter human architect rationale..."
                    value={resolveNotes}
                    onChange={(e) => setResolveNotes(e.target.value)}
                    className="w-full px-3 py-2 rounded-lg bg-[#0a0f1d] border border-[#1e293b] text-white focus:outline-none focus:border-cyan-500"
                  />
                </div>

                <div className="flex justify-end space-x-2 pt-2">
                  <button
                    onClick={() => setSelectedConflict(null)}
                    className="px-3 py-1.5 rounded-lg bg-slate-800 text-slate-300 hover:text-white transition"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={() => handleResolve(selectedConflict.id)}
                    className="px-4 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-semibold transition"
                  >
                    Confirm Resolution
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

