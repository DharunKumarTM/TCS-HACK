"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { FileSearch, Upload, FileText, CheckCircle2, Filter, Eye, ShieldCheck, Tag, PenTool } from "lucide-react";
import { api } from "@/lib/api";
import { EvidenceItem, DocumentItem, Project } from "@/types";
import { Navbar } from "@/components/shared/Navbar";

export default function EvidencePage() {
  const [project, setProject] = useState<Project | null>(null);
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [evidenceList, setEvidenceList] = useState<EvidenceItem[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>("All");
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [selectedEvidence, setSelectedEvidence] = useState<EvidenceItem | null>(null);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);

  const loadData = async () => {
    try {
      setLoading(true);
      const projects = await api.getProjects();
      const savedId = typeof window !== "undefined" ? localStorage.getItem("archmind_active_project_id") : null;
      const active = (savedId ? projects.find(p => p.id === savedId) : null) || projects[0] || (await api.loadSmartBankDemo());
      setProject(active);

      const docs = await api.getDocuments(active.id);
      setDocuments(docs);

      const ev = await api.getEvidence(active.id);
      setEvidenceList(ev);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file || !project) return;
    setUploading(true);
    try {
      await api.uploadDocument(project.id, file);
      await loadData();
    } catch (err) {
      console.error(err);
    } finally {
      setUploading(false);
    }
  };

  const categories = ["All", "Functional", "Non-Functional", "Policy", "Constraint", "Architecture Preference"];

  const filteredEvidence = evidenceList.filter((item) => {
    const matchesCategory = selectedCategory === "All" || item.category === selectedCategory;
    const matchesSearch =
      item.statement.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.evidence_code.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.source_filename.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  return (
    <div className="min-h-screen flex flex-col bg-[#080c14]">
      <Navbar projectName={project?.name} projectId={project?.id} onRefresh={loadData} />

      <main className="flex-1 p-8 space-y-6 max-w-7xl mx-auto w-full">
        {/* Header and Upload Section */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-[#1e293b] pb-6">
          <div>
            <div className="flex items-center space-x-2">
              <FileSearch className="w-5 h-5 text-cyan-400" />
              <h1 className="text-xl font-bold text-white tracking-tight">Evidence Intelligence Workspace</h1>
            </div>
            <p className="text-xs text-slate-400 mt-1">
              Docling multi-format document parser & LlamaIndex semantic grounding. Ingested statements preserve full citation provenance.
            </p>
          </div>

          <div className="flex items-center space-x-3">
            <Link
              href="/input"
              className="flex items-center space-x-1.5 px-3.5 py-2 rounded-lg bg-[#131d33] text-cyan-300 hover:text-white border border-cyan-500/40 text-xs font-semibold shadow-md transition"
            >
              <PenTool className="w-3.5 h-3.5 text-cyan-400" />
              <span>Write / Paste Text</span>
            </Link>

            <label className="flex items-center space-x-2 px-4 py-2 rounded-lg bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500 text-white text-xs font-semibold cursor-pointer shadow-lg shadow-cyan-600/20 transition">
              <Upload className="w-3.5 h-3.5" />
              <span>{uploading ? "Ingesting..." : "Ingest Document (PDF/DOCX/MD)"}</span>
              <input type="file" onChange={handleFileUpload} className="hidden" accept=".pdf,.docx,.txt,.md,.json" />
            </label>
          </div>
        </div>

        {/* Source Documents Pill Row */}
        <div>
          <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 block mb-2">
            Ingested Evidence Sources ({documents.length})
          </span>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
            {documents.map((doc) => (
              <div
                key={doc.id}
                className="bg-[#0a0f1d] border border-[#1e293b] rounded-xl p-3 flex items-center justify-between hover:border-slate-700 transition"
              >
                <div className="flex items-center space-x-3 truncate">
                  <div className="w-8 h-8 rounded-lg bg-blue-500/10 flex items-center justify-center text-blue-400">
                    <FileText className="w-4 h-4" />
                  </div>
                  <div className="truncate">
                    <div className="text-xs font-bold text-slate-200 truncate">{doc.filename}</div>
                    <div className="text-[10px] text-slate-500 uppercase">{doc.file_type} • {(doc.file_size_bytes / 1024).toFixed(1)} KB</div>
                  </div>
                </div>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
                  INDEXED
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Filters and Search Bar */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 bg-[#0a0f1d] border border-[#1e293b] p-3 rounded-xl">
          <div className="flex flex-wrap items-center gap-1.5 w-full sm:w-auto">
            {categories.map((cat) => (
              <button
                key={cat}
                onClick={() => setSelectedCategory(cat)}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium transition ${
                  selectedCategory === cat
                    ? "bg-cyan-600 text-white shadow-sm"
                    : "bg-[#131d33] text-slate-400 hover:text-slate-200"
                }`}
              >
                {cat}
              </button>
            ))}
          </div>

          <div className="w-full sm:w-72">
            <input
              type="text"
              placeholder="Search evidence statements..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full px-3 py-1.5 rounded-lg bg-[#131d33] border border-[#1e293b] text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500"
            />
          </div>
        </div>

        {/* Extracted Evidence Table */}
        <div className="bg-[#0a0f1d] border border-[#1e293b] rounded-xl overflow-hidden shadow-xl">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="bg-[#0f172a] border-b border-[#1e293b] text-slate-400 uppercase tracking-wider font-semibold">
                  <th className="py-3 px-4">Code</th>
                  <th className="py-3 px-4">Category</th>
                  <th className="py-3 px-4">Statement</th>
                  <th className="py-3 px-4">Source Provenance</th>
                  <th className="py-3 px-4 text-center">Quality</th>
                  <th className="py-3 px-4 text-center">Confidence</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#1e293b] text-slate-200">
                {filteredEvidence.map((ev) => (
                  <tr key={ev.id || ev.evidence_code} className="hover:bg-[#11192e] transition">
                    <td className="py-3 px-4 font-mono font-bold text-cyan-400">{ev.evidence_code}</td>
                    <td className="py-3 px-4">
                      <span className="px-2 py-0.5 rounded bg-blue-500/15 text-blue-400 border border-blue-500/30 text-[10px] font-medium">
                        {ev.category}
                      </span>
                    </td>
                    <td className="py-3 px-4 font-sans text-slate-200 max-w-md truncate" title={ev.statement}>
                      {ev.statement}
                    </td>
                    <td className="py-3 px-4 text-slate-400 font-mono text-[11px] truncate max-w-xs">
                      {ev.source_filename}
                    </td>
                    <td className="py-3 px-4 text-center">
                      <span className="px-2 py-0.5 rounded bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 text-[10px] font-bold">
                        {ev.quality_grade}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-center font-mono text-cyan-300">
                      {(ev.confidence_score * 100).toFixed(0)}%
                    </td>
                    <td className="py-3 px-4 text-right">
                      <button
                        onClick={() => setSelectedEvidence(ev)}
                        className="p-1.5 rounded-lg bg-[#1e293b] text-slate-300 hover:text-white hover:bg-slate-700 transition"
                        title="View Full Excerpt"
                      >
                        <Eye className="w-3.5 h-3.5" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Verbatim Excerpt Drawer / Modal */}
        {selectedEvidence && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 p-6 backdrop-blur-sm">
            <div className="bg-[#0f172a] border border-[#334155] rounded-xl w-full max-w-2xl p-6 shadow-2xl space-y-4">
              <div className="flex items-center justify-between border-b border-[#1e293b] pb-3">
                <div className="flex items-center space-x-2">
                  <span className="text-xs font-mono font-bold px-2 py-0.5 rounded bg-cyan-500/20 text-cyan-400 border border-cyan-500/30">
                    {selectedEvidence.evidence_code}
                  </span>
                  <span className="text-sm font-bold text-white">Verbatim Source Excerpt</span>
                </div>
                <button
                  onClick={() => setSelectedEvidence(null)}
                  className="px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs transition"
                >
                  Close
                </button>
              </div>

              <div className="space-y-3 text-xs">
                <div>
                  <span className="text-slate-400 block mb-1 font-semibold uppercase text-[10px]">Normalized Statement</span>
                  <p className="bg-[#0a0f1d] p-3 rounded-lg border border-[#1e293b] text-slate-200">
                    {selectedEvidence.statement}
                  </p>
                </div>

                <div>
                  <span className="text-slate-400 block mb-1 font-semibold uppercase text-[10px]">Original Verbatim Excerpt</span>
                  <blockquote className="bg-[#070b14] p-3 rounded-lg border border-cyan-500/30 text-cyan-300 italic font-mono text-[11px] leading-relaxed">
                    {selectedEvidence.original_excerpt}
                  </blockquote>
                </div>

                <div className="grid grid-cols-2 gap-3 pt-2">
                  <div className="bg-[#0a0f1d] p-2.5 rounded-lg border border-[#1e293b]">
                    <span className="text-slate-500 text-[10px] uppercase block">Source File</span>
                    <span className="text-slate-300 font-mono text-[11px]">{selectedEvidence.source_filename}</span>
                  </div>
                  <div className="bg-[#0a0f1d] p-2.5 rounded-lg border border-[#1e293b]">
                    <span className="text-slate-500 text-[10px] uppercase block">Location Reference</span>
                    <span className="text-slate-300 font-sans text-[11px]">{selectedEvidence.location_reference || "General Section"}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

