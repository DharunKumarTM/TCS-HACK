"use client";

import { useEffect, useState } from "react";
import { BookOpen, CheckCircle2, XCircle, Clock, ShieldCheck, ChevronDown, ChevronUp, Check, X } from "lucide-react";
import { api } from "@/lib/api";
import { ADRItem, Project } from "@/types";
import { Navbar } from "@/components/shared/Navbar";

export default function DecisionsPage() {
  const [project, setProject] = useState<Project | null>(null);
  const [adrs, setAdrs] = useState<ADRItem[]>([]);
  const [expandedAdr, setExpandedAdr] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    try {
      setLoading(true);
      const projects = await api.getProjects();
      const savedId = typeof window !== "undefined" ? localStorage.getItem("archmind_active_project_id") : null;
      const active = (savedId ? projects.find(p => p.id === savedId) : null) || projects[0] || (await api.loadSmartBankDemo());
      setProject(active);

      const adrList = await api.getADRs(active.id);
      setAdrs(adrList);
      if (adrList.length > 0) setExpandedAdr(adrList[0].adr_code);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleUpdateStatus = async (adrId: string, newStatus: string) => {
    try {
      await api.updateADRStatus(adrId, newStatus, `Updated by Architect to ${newStatus}`);
      await loadData();
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-[#080c14]">
      <Navbar projectName={project?.name} projectId={project?.id} onRefresh={loadData} />

      <main className="flex-1 p-8 space-y-6 max-w-5xl mx-auto w-full">
        {/* Header */}
        <div className="border-b border-[#1e293b] pb-6">
          <div className="flex items-center space-x-2">
            <BookOpen className="w-5 h-5 text-cyan-400" />
            <h1 className="text-xl font-bold text-white tracking-tight">Architecture Decision Records (ADRs)</h1>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Formal architectural trade-off governance. Requires explicit human architect acceptance before moving from Proposed to Accepted.
          </p>
        </div>

        {/* ADR List */}
        <div className="space-y-4">
          {adrs.map((adr) => {
            const isExpanded = expandedAdr === adr.adr_code;
            const isAccepted = adr.status === "Accepted";
            const isProposed = adr.status === "Proposed";

            return (
              <div
                key={adr.id || adr.adr_code}
                className={`bg-[#0a0f1d] border rounded-xl overflow-hidden transition shadow-lg ${
                  isAccepted ? "border-emerald-500/40" : "border-[#1e293b]"
                }`}
              >
                {/* Header Row */}
                <div
                  onClick={() => setExpandedAdr(isExpanded ? null : adr.adr_code)}
                  className="p-5 flex items-center justify-between cursor-pointer hover:bg-[#0f172a] transition"
                >
                  <div className="flex items-center space-x-3">
                    <span className="font-mono text-xs font-bold px-2 py-0.5 rounded bg-blue-500/20 text-cyan-400 border border-blue-500/30">
                      {adr.adr_code}
                    </span>
                    <h3 className="text-sm font-bold text-white">{adr.title}</h3>
                  </div>

                  <div className="flex items-center space-x-3">
                    <span
                      className={`text-[10px] font-mono px-2 py-0.5 rounded-full font-bold ${
                        isAccepted
                          ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"
                          : isProposed
                          ? "bg-amber-500/20 text-amber-400 border border-amber-500/30"
                          : "bg-rose-500/20 text-rose-400 border border-rose-500/30"
                      }`}
                    >
                      {adr.status.toUpperCase()}
                    </span>
                    {isExpanded ? (
                      <ChevronUp className="w-4 h-4 text-slate-400" />
                    ) : (
                      <ChevronDown className="w-4 h-4 text-slate-400" />
                    )}
                  </div>
                </div>

                {/* Collapsible Details */}
                {isExpanded && (
                  <div className="p-5 border-t border-[#1e293b] space-y-4 text-xs bg-[#070b14]/60">
                    <div>
                      <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block mb-1">
                        Context & Problem Statement
                      </span>
                      <p className="text-slate-200 leading-relaxed bg-[#0a0f1d] p-3 rounded-lg border border-[#1e293b]">
                        {adr.context}
                      </p>
                    </div>

                    <div>
                      <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block mb-1">
                        Architectural Decision
                      </span>
                      <p className="text-cyan-200 leading-relaxed bg-[#0a0f1d] p-3 rounded-lg border border-cyan-500/30">
                        {adr.decision}
                      </p>
                    </div>

                    {/* Alternatives Considered */}
                    <div>
                      <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block mb-1">
                        Rejected Alternatives & Trade-Offs
                      </span>
                      <div className="space-y-1.5">
                        {(adr.alternatives || []).map((alt, idx) => (
                          <div key={idx} className="bg-[#0a0f1d] p-2.5 rounded-lg border border-[#1e293b] flex flex-col sm:flex-row sm:items-center justify-between text-[11px] gap-2">
                            <strong className="text-slate-300">{alt.option}</strong>
                            <span className="text-slate-400 italic">{alt.trade_off}</span>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Trade-Offs & Consequences */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      <div className="bg-[#0a0f1d] p-3 rounded-lg border border-[#1e293b]">
                        <span className="text-[10px] font-semibold text-slate-400 uppercase block mb-1">Key Advantages</span>
                        <ul className="list-disc list-inside space-y-1 text-slate-300 text-[11px]">
                          {(adr.advantages || []).map((adv, i) => (
                            <li key={i}>{adv}</li>
                          ))}
                        </ul>
                      </div>
                      <div className="bg-[#0a0f1d] p-3 rounded-lg border border-[#1e293b]">
                        <span className="text-[10px] font-semibold text-slate-400 uppercase block mb-1">Disadvantages / Trade-offs</span>
                        <p className="text-slate-300 text-[11px]">{adr.trade_offs}</p>
                      </div>
                    </div>

                    {/* Supporting Requirements & Actions */}
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between pt-3 border-t border-[#1e293b] gap-3">
                      <div className="flex items-center space-x-1">
                        <span className="text-[10px] text-slate-400 font-mono">Supporting REQs:</span>
                        {(adr.supporting_req_codes || []).map((c) => (
                          <span key={c} className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-blue-500/20 text-cyan-300">
                            {c}
                          </span>
                        ))}
                      </div>

                      <div className="flex items-center space-x-2">
                        {isProposed && (
                          <>
                            <button
                              onClick={() => handleUpdateStatus(adr.id, "Accepted")}
                              className="flex items-center space-x-1.5 px-3.5 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-semibold transition"
                            >
                              <Check className="w-3.5 h-3.5" />
                              <span>Accept Decision</span>
                            </button>
                            <button
                              onClick={() => handleUpdateStatus(adr.id, "Rejected")}
                              className="flex items-center space-x-1.5 px-3.5 py-1.5 rounded-lg bg-rose-600/80 hover:bg-rose-600 text-white font-semibold transition"
                            >
                              <X className="w-3.5 h-3.5" />
                              <span>Reject</span>
                            </button>
                          </>
                        )}
                        {isAccepted && (
                          <button
                            onClick={() => handleUpdateStatus(adr.id, "Superseded")}
                            className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs transition"
                          >
                            Mark Superseded
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </main>
    </div>
  );
}

