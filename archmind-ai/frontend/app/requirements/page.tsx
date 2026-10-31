"use client";

import { useEffect, useState } from "react";
import { CheckSquare, Edit3, ShieldAlert, Sparkles, Filter, Check, X } from "lucide-react";
import { api } from "@/lib/api";
import { RequirementItem, Project } from "@/types";
import { Navbar } from "@/components/shared/Navbar";

export default function RequirementsPage() {
  const [project, setProject] = useState<Project | null>(null);
  const [requirements, setRequirements] = useState<RequirementItem[]>([]);
  const [typeFilter, setTypeFilter] = useState<string>("All");
  const [editingReq, setEditingReq] = useState<RequirementItem | null>(null);
  const [editTitle, setEditTitle] = useState("");
  const [editDescription, setEditDescription] = useState("");
  const [editPriority, setEditPriority] = useState("");
  const [editStatus, setEditStatus] = useState("");
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
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const openEditModal = (r: RequirementItem) => {
    setEditingReq(r);
    setEditTitle(r.title);
    setEditDescription(r.description);
    setEditPriority(r.priority);
    setEditStatus(r.approval_status);
  };

  const handleSaveEdit = async () => {
    if (!editingReq) return;
    try {
      await api.updateRequirement(editingReq.id, {
        title: editTitle,
        description: editDescription,
        priority: editPriority,
        approval_status: editStatus,
      });
      setEditingReq(null);
      await loadData();
    } catch (err) {
      console.error(err);
    }
  };

  const types = ["All", "Functional", "Non-Functional", "Technical Constraint", "Business Constraint"];

  const filtered = requirements.filter(
    (r) => typeFilter === "All" || r.req_type === typeFilter
  );

  return (
    <div className="min-h-screen flex flex-col bg-[#080c14]">
      <Navbar projectName={project?.name} projectId={project?.id} onRefresh={loadData} />

      <main className="flex-1 p-8 space-y-6 max-w-7xl mx-auto w-full">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-[#1e293b] pb-6">
          <div>
            <div className="flex items-center space-x-2">
              <CheckSquare className="w-5 h-5 text-cyan-400" />
              <h1 className="text-xl font-bold text-white tracking-tight">Requirements Intelligence & Classification</h1>
            </div>
            <p className="text-xs text-slate-400 mt-1">
              IEEE-standardized normalization. Distinguishes confirmed Facts, Inferred requirements, and Unverified Assumptions.
            </p>
          </div>
        </div>

        {/* Filter Bar */}
        <div className="flex items-center space-x-2 bg-[#0a0f1d] border border-[#1e293b] p-3 rounded-xl">
          <span className="text-xs text-slate-400 font-semibold mr-2 flex items-center">
            <Filter className="w-3.5 h-3.5 mr-1" /> Filter Type:
          </span>
          {types.map((t) => (
            <button
              key={t}
              onClick={() => setTypeFilter(t)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition ${
                typeFilter === t ? "bg-cyan-600 text-white" : "bg-[#131d33] text-slate-400 hover:text-white"
              }`}
            >
              {t}
            </button>
          ))}
        </div>

        {/* Requirements Table */}
        <div className="bg-[#0a0f1d] border border-[#1e293b] rounded-xl overflow-hidden shadow-xl">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="bg-[#0f172a] border-b border-[#1e293b] text-slate-400 uppercase tracking-wider font-semibold">
                  <th className="py-3 px-4">Code</th>
                  <th className="py-3 px-4">Title & Description</th>
                  <th className="py-3 px-4">Type</th>
                  <th className="py-3 px-4">Category</th>
                  <th className="py-3 px-4">Priority</th>
                  <th className="py-3 px-4">Evidence Citations</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#1e293b] text-slate-200">
                {filtered.map((r) => (
                  <tr key={r.id || r.req_code} className="hover:bg-[#11192e] transition">
                    <td className="py-3.5 px-4 font-mono font-bold text-cyan-400">{r.req_code}</td>
                    <td className="py-3.5 px-4 max-w-sm">
                      <div className="font-bold text-white mb-0.5">{r.title}</div>
                      <div className="text-slate-400 text-[11px] leading-relaxed line-clamp-2">{r.description}</div>
                    </td>
                    <td className="py-3.5 px-4">
                      <span className="px-2 py-0.5 rounded bg-blue-500/15 text-blue-400 border border-blue-500/30 text-[10px] font-medium">
                        {r.req_type}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-slate-300 font-sans">{r.category}</td>
                    <td className="py-3.5 px-4">
                      <span
                        className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                          r.priority === "Critical"
                            ? "bg-rose-500/20 text-rose-400 border border-rose-500/30"
                            : r.priority === "High"
                            ? "bg-amber-500/20 text-amber-400 border border-amber-500/30"
                            : "bg-blue-500/15 text-blue-300"
                        }`}
                      >
                        {r.priority}
                      </span>
                    </td>
                    <td className="py-3.5 px-4">
                      <div className="flex flex-wrap gap-1">
                        {(r.source_evidence_codes || []).map((code) => (
                          <span
                            key={code}
                            className="px-1.5 py-0.5 rounded bg-[#1e293b] text-slate-300 border border-[#334155] font-mono text-[9px]"
                          >
                            {code}
                          </span>
                        ))}
                      </div>
                    </td>
                    <td className="py-3.5 px-4">
                      <span
                        className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold ${
                          r.approval_status === "Fact"
                            ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"
                            : r.approval_status === "Assumption"
                            ? "bg-amber-500/20 text-amber-400 border border-amber-500/30"
                            : "bg-cyan-500/20 text-cyan-400 border border-cyan-500/30"
                        }`}
                      >
                        {r.approval_status}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <button
                        onClick={() => openEditModal(r)}
                        className="p-1.5 rounded-lg bg-[#1e293b] text-slate-300 hover:text-white hover:bg-slate-700 transition"
                        title="Edit Requirement"
                      >
                        <Edit3 className="w-3.5 h-3.5" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Edit Modal */}
        {editingReq && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 p-6 backdrop-blur-sm">
            <div className="bg-[#0f172a] border border-[#334155] rounded-xl w-full max-w-xl p-6 shadow-2xl space-y-4">
              <div className="flex items-center justify-between border-b border-[#1e293b] pb-3">
                <span className="text-sm font-bold text-white">Edit Requirement {editingReq.req_code}</span>
                <button
                  onClick={() => setEditingReq(null)}
                  className="p-1 text-slate-400 hover:text-white transition"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              <div className="space-y-3 text-xs">
                <div>
                  <label className="text-slate-400 block mb-1 font-semibold uppercase text-[10px]">Title</label>
                  <input
                    type="text"
                    value={editTitle}
                    onChange={(e) => setEditTitle(e.target.value)}
                    className="w-full px-3 py-2 rounded-lg bg-[#0a0f1d] border border-[#1e293b] text-white focus:outline-none focus:border-cyan-500"
                  />
                </div>

                <div>
                  <label className="text-slate-400 block mb-1 font-semibold uppercase text-[10px]">Description</label>
                  <textarea
                    rows={4}
                    value={editDescription}
                    onChange={(e) => setEditDescription(e.target.value)}
                    className="w-full px-3 py-2 rounded-lg bg-[#0a0f1d] border border-[#1e293b] text-white focus:outline-none focus:border-cyan-500"
                  />
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="text-slate-400 block mb-1 font-semibold uppercase text-[10px]">Priority</label>
                    <select
                      value={editPriority}
                      onChange={(e) => setEditPriority(e.target.value)}
                      className="w-full px-3 py-2 rounded-lg bg-[#0a0f1d] border border-[#1e293b] text-white focus:outline-none focus:border-cyan-500"
                    >
                      <option value="Critical">Critical</option>
                      <option value="High">High</option>
                      <option value="Medium">Medium</option>
                      <option value="Low">Low</option>
                    </select>
                  </div>
                  <div>
                    <label className="text-slate-400 block mb-1 font-semibold uppercase text-[10px]">Approval Status</label>
                    <select
                      value={editStatus}
                      onChange={(e) => setEditStatus(e.target.value)}
                      className="w-full px-3 py-2 rounded-lg bg-[#0a0f1d] border border-[#1e293b] text-white focus:outline-none focus:border-cyan-500"
                    >
                      <option value="Fact">Fact</option>
                      <option value="Inferred">Inferred</option>
                      <option value="Assumption">Assumption</option>
                      <option value="Clarified">Clarified</option>
                      <option value="Approved">Approved</option>
                    </select>
                  </div>
                </div>

                <div className="flex justify-end space-x-2 pt-3 border-t border-[#1e293b]">
                  <button
                    onClick={() => setEditingReq(null)}
                    className="px-3 py-1.5 rounded-lg bg-slate-800 text-slate-300 hover:text-white transition"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleSaveEdit}
                    className="flex items-center space-x-1.5 px-4 py-1.5 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white font-semibold transition"
                  >
                    <Check className="w-3.5 h-3.5" />
                    <span>Save Changes</span>
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

