"use client";

import { useEffect, useState } from "react";
import { GitBranch, CheckCircle2, AlertTriangle, XCircle, ShieldCheck, Filter } from "lucide-react";
import { api } from "@/lib/api";
import { TraceabilityMatrixResponse, Project } from "@/types";
import { Navbar } from "@/components/shared/Navbar";

export default function TraceabilityPage() {
  const [project, setProject] = useState<Project | null>(null);
  const [matrix, setMatrix] = useState<TraceabilityMatrixResponse | null>(null);
  const [statusFilter, setStatusFilter] = useState<string>("All");
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    try {
      setLoading(true);
      const projects = await api.getProjects();
      const savedId = typeof window !== "undefined" ? localStorage.getItem("archmind_active_project_id") : null;
      const active = (savedId ? projects.find(p => p.id === savedId) : null) || projects[0] || (await api.loadSmartBankDemo());
      setProject(active);

      const m = await api.getTraceability(active.id);
      setMatrix(m);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const statuses = ["All", "Fully Covered", "Partially Covered", "Blocked", "Not Covered"];

  const filteredItems = (matrix?.items || []).filter(
    (item) => statusFilter === "All" || item.coverage_status === statusFilter
  );

  return (
    <div className="min-h-screen flex flex-col bg-[#080c14]">
      <Navbar projectName={project?.name} projectId={project?.id} onRefresh={loadData} />

      <main className="flex-1 p-8 space-y-6 max-w-7xl mx-auto w-full">
        {/* Header */}
        <div className="border-b border-[#1e293b] pb-6">
          <div className="flex items-center space-x-2">
            <GitBranch className="w-5 h-5 text-cyan-400" />
            <h1 className="text-xl font-bold text-white tracking-tight">Bidirectional Requirement Traceability Matrix</h1>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Evidence → Requirements → Components → APIs → ADRs → Validation. Coverage calculated strictly from verifiable mappings.
          </p>
        </div>

        {/* Coverage Summary Cards */}
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          <div className="bg-[#0a0f1d] border border-cyan-500/30 rounded-xl p-4 text-center">
            <div className="text-2xl font-bold text-cyan-400 font-mono">
              {matrix?.overall_coverage_pct || 0}%
            </div>
            <div className="text-[10px] text-slate-400 uppercase tracking-wider font-semibold mt-0.5">
              Verified Coverage
            </div>
          </div>

          <div className="bg-[#0a0f1d] border border-emerald-500/30 rounded-xl p-4 text-center">
            <div className="text-2xl font-bold text-emerald-400 font-mono">
              {matrix?.fully_covered || 0}
            </div>
            <div className="text-[10px] text-slate-400 uppercase tracking-wider font-semibold mt-0.5">
              Fully Covered
            </div>
          </div>

          <div className="bg-[#0a0f1d] border border-amber-500/30 rounded-xl p-4 text-center">
            <div className="text-2xl font-bold text-amber-400 font-mono">
              {matrix?.partially_covered || 0}
            </div>
            <div className="text-[10px] text-slate-400 uppercase tracking-wider font-semibold mt-0.5">
              Partially Covered
            </div>
          </div>

          <div className="bg-[#0a0f1d] border border-rose-500/30 rounded-xl p-4 text-center">
            <div className="text-2xl font-bold text-rose-400 font-mono">
              {matrix?.blocked || 0}
            </div>
            <div className="text-[10px] text-slate-400 uppercase tracking-wider font-semibold mt-0.5">
              Blocked by Conflicts
            </div>
          </div>

          <div className="bg-[#0a0f1d] border border-slate-700 rounded-xl p-4 text-center">
            <div className="text-2xl font-bold text-slate-400 font-mono">
              {matrix?.not_covered || 0}
            </div>
            <div className="text-[10px] text-slate-400 uppercase tracking-wider font-semibold mt-0.5">
              Not Covered
            </div>
          </div>
        </div>

        {/* Filter Bar */}
        <div className="flex items-center space-x-2 bg-[#0a0f1d] border border-[#1e293b] p-3 rounded-xl">
          <span className="text-xs text-slate-400 font-semibold mr-2 flex items-center">
            <Filter className="w-3.5 h-3.5 mr-1" /> Filter Status:
          </span>
          {statuses.map((s) => (
            <button
              key={s}
              onClick={() => setStatusFilter(s)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition ${
                statusFilter === s ? "bg-cyan-600 text-white" : "bg-[#131d33] text-slate-400 hover:text-white"
              }`}
            >
              {s}
            </button>
          ))}
        </div>

        {/* Matrix Table */}
        <div className="bg-[#0a0f1d] border border-[#1e293b] rounded-xl overflow-hidden shadow-xl">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="bg-[#0f172a] border-b border-[#1e293b] text-slate-400 uppercase tracking-wider font-semibold">
                  <th className="py-3 px-4">REQ Code</th>
                  <th className="py-3 px-4">Evidence Citations</th>
                  <th className="py-3 px-4">Requirement Specification</th>
                  <th className="py-3 px-4">Mapped Components</th>
                  <th className="py-3 px-4">Related APIs</th>
                  <th className="py-3 px-4">Related ADRs</th>
                  <th className="py-3 px-4 text-center">Coverage State</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#1e293b] text-slate-200">
                {filteredItems.map((item) => (
                  <tr key={item.req_code} className="hover:bg-[#11192e] transition">
                    <td className="py-3.5 px-4 font-mono font-bold text-cyan-400">{item.req_code}</td>
                    <td className="py-3.5 px-4">
                      <div className="flex flex-wrap gap-1">
                        {(item.evidence_codes || []).map((code) => (
                          <span key={code} className="px-1.5 py-0.5 rounded bg-[#1e293b] text-slate-300 font-mono text-[9px]">
                            {code}
                          </span>
                        ))}
                      </div>
                    </td>
                    <td className="py-3.5 px-4 max-w-sm text-slate-200">
                      <div className="line-clamp-2">{item.req_description}</div>
                      <span className="text-[10px] text-slate-500 font-sans mt-0.5 block">{item.req_category}</span>
                    </td>
                    <td className="py-3.5 px-4">
                      <div className="flex flex-wrap gap-1">
                        {(item.mapped_component_codes || []).length > 0 ? (
                          item.mapped_component_codes.map((c) => (
                            <span key={c} className="px-1.5 py-0.5 rounded bg-blue-500/20 text-cyan-300 font-mono text-[10px]">
                              {c}
                            </span>
                          ))
                        ) : (
                          <span className="text-slate-500 italic text-[11px]">Unmapped</span>
                        )}
                      </div>
                    </td>
                    <td className="py-3.5 px-4 font-mono text-[10px] text-slate-300">
                      {(item.related_api_ids || []).slice(0, 2).join(", ") || (
                        <span className="text-slate-500 italic">None</span>
                      )}
                    </td>
                    <td className="py-3.5 px-4">
                      <div className="flex flex-wrap gap-1">
                        {(item.related_adr_codes || []).map((adr) => (
                          <span key={adr} className="px-1.5 py-0.5 rounded bg-indigo-500/20 text-indigo-300 font-mono text-[10px]">
                            {adr}
                          </span>
                        ))}
                      </div>
                    </td>
                    <td className="py-3.5 px-4 text-center">
                      <span
                        className={`px-2.5 py-1 rounded-full text-[10px] font-mono font-bold ${
                          item.coverage_status === "Fully Covered"
                            ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"
                            : item.coverage_status === "Blocked"
                            ? "bg-rose-500/20 text-rose-400 border border-rose-500/30"
                            : item.coverage_status === "Partially Covered"
                            ? "bg-amber-500/20 text-amber-400 border border-amber-500/30"
                            : "bg-slate-800 text-slate-400 border border-slate-700"
                        }`}
                      >
                        {item.coverage_status.toUpperCase()}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </main>
    </div>
  );
}

