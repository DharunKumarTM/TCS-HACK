"use client";

import { useEffect, useState } from "react";
import { HelpCircle, CheckCircle2, MessageSquare, Send, Sparkles, Check, ArrowRight } from "lucide-react";
import { api } from "@/lib/api";
import { ClarificationQuestion, Project } from "@/types";
import { Navbar } from "@/components/shared/Navbar";

export default function ClarificationPage() {
  const [project, setProject] = useState<Project | null>(null);
  const [questions, setQuestions] = useState<ClarificationQuestion[]>([]);
  const [selectedAnswers, setSelectedAnswers] = useState<Record<string, string>>({});
  const [customAnswers, setCustomAnswers] = useState<Record<string, string>>({});
  const [submitting, setSubmitting] = useState<Record<string, boolean>>({});
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    try {
      setLoading(true);
      const projects = await api.getProjects();
      const savedId = typeof window !== "undefined" ? localStorage.getItem("archmind_active_project_id") : null;
      const active = (savedId ? projects.find(p => p.id === savedId) : null) || projects[0] || (await api.loadSmartBankDemo());
      setProject(active);

      const qList = await api.getClarifications(active.id);
      setQuestions(qList);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleSelectOption = (questionId: string, option: string) => {
    setSelectedAnswers((prev) => ({ ...prev, [questionId]: option }));
  };

  const handleSubmitResponse = async (questionId: string) => {
    const selectedOption = selectedAnswers[questionId];
    const customAnswer = customAnswers[questionId];
    if (!selectedOption && !customAnswer) return;

    setSubmitting((prev) => ({ ...prev, [questionId]: true }));
    try {
      await api.submitClarificationResponse(questionId, selectedOption, customAnswer);
      await loadData();
    } catch (err) {
      console.error(err);
    } finally {
      setSubmitting((prev) => ({ ...prev, [questionId]: false }));
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-[#080c14]">
      <Navbar projectName={project?.name} projectId={project?.id} onRefresh={loadData} />

      <main className="flex-1 p-8 space-y-6 max-w-5xl mx-auto w-full">
        {/* Header */}
        <div className="border-b border-[#1e293b] pb-6">
          <div className="flex items-center space-x-2">
            <HelpCircle className="w-5 h-5 text-cyan-400" />
            <h1 className="text-xl font-bold text-white tracking-tight">Clarification Room (Human-In-The-Loop)</h1>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            LangGraph stateful interrupt checkpoint. Stakeholder clarifications re-evaluate contradictions and unblock architecture reasoning.
          </p>
        </div>

        {/* Questions List */}
        <div className="space-y-6">
          {questions.map((q) => {
            const isAnswered = q.status === "Answered";
            const currentSelected = selectedAnswers[q.id];

            return (
              <div
                key={q.id || q.question_code}
                className={`bg-[#0a0f1d] border rounded-xl p-6 transition shadow-lg ${
                  isAnswered ? "border-emerald-500/30" : "border-cyan-500/40"
                }`}
              >
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center space-x-2">
                    <span className="font-mono text-xs font-bold px-2 py-0.5 rounded bg-blue-500/20 text-cyan-300 border border-blue-500/30">
                      {q.question_code}
                    </span>
                    <h3 className="text-sm font-bold text-white">{q.title}</h3>
                  </div>
                  <span
                    className={`text-[10px] font-mono px-2 py-0.5 rounded-full font-bold ${
                      isAnswered
                        ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"
                        : "bg-cyan-500/20 text-cyan-400 border border-cyan-500/30 animate-pulse"
                    }`}
                  >
                    {q.status.toUpperCase()}
                  </span>
                </div>

                <p className="text-xs text-slate-200 bg-[#0f172a] p-3.5 rounded-lg border border-[#1e293b] leading-relaxed mb-4">
                  {q.question}
                </p>

                {q.context_reasoning && (
                  <div className="text-[11px] text-slate-400 italic mb-4">
                    <strong className="text-slate-300">Architectural Context:</strong> {q.context_reasoning}
                  </div>
                )}

                {/* Suggested Options */}
                <div className="space-y-2 mb-4">
                  <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block">
                    Recommended Architectural Options:
                  </span>
                  {(q.suggested_options || []).map((opt, idx) => {
                    const isPicked = currentSelected === opt;
                    return (
                      <button
                        key={idx}
                        disabled={isAnswered}
                        onClick={() => handleSelectOption(q.id, opt)}
                        className={`w-full text-left p-3 rounded-lg border text-xs transition flex items-start space-x-3 ${
                          isPicked
                            ? "bg-cyan-500/15 border-cyan-500 text-cyan-200 font-medium"
                            : "bg-[#0c1326] border-[#1e293b] text-slate-300 hover:border-slate-600"
                        } ${isAnswered ? "opacity-70 cursor-not-allowed" : ""}`}
                      >
                        <span className={`w-4 h-4 rounded-full border flex items-center justify-center shrink-0 mt-0.5 ${
                          isPicked ? "border-cyan-400 bg-cyan-400 text-black" : "border-slate-600"
                        }`}>
                          {isPicked && <Check className="w-3 h-3 stroke-[3]" />}
                        </span>
                        <span>{opt}</span>
                      </button>
                    );
                  })}
                </div>

                {/* Custom Answer Input */}
                {!isAnswered && (
                  <div className="mb-4">
                    <label className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block mb-1">
                      Or Provide Custom Architectural Directive:
                    </label>
                    <input
                      type="text"
                      placeholder="Type custom stakeholder decision..."
                      value={customAnswers[q.id] || ""}
                      onChange={(e) => setCustomAnswers({ ...customAnswers, [q.id]: e.target.value })}
                      className="w-full px-3 py-2 rounded-lg bg-[#0c1326] border border-[#1e293b] text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500"
                    />
                  </div>
                )}

                {/* Action Bar */}
                <div className="flex items-center justify-between pt-3 border-t border-[#1e293b]">
                  <div className="flex items-center space-x-1">
                    <span className="text-[10px] text-slate-500 font-mono">Related REQs:</span>
                    {(q.related_req_codes || []).map((code) => (
                      <span key={code} className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-slate-800 text-slate-300">
                        {code}
                      </span>
                    ))}
                  </div>

                  {!isAnswered ? (
                    <button
                      onClick={() => handleSubmitResponse(q.id)}
                      disabled={!currentSelected && !customAnswers[q.id]}
                      className="flex items-center space-x-1.5 px-4 py-2 rounded-lg bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500 text-white text-xs font-semibold shadow-lg shadow-cyan-600/20 transition disabled:opacity-50"
                    >
                      <Send className="w-3 h-3" />
                      <span>{submitting[q.id] ? "Submitting & Resuming..." : "Submit Clarification"}</span>
                    </button>
                  ) : (
                    <div className="flex items-center space-x-1.5 text-emerald-400 text-xs font-semibold">
                      <CheckCircle2 className="w-4 h-4" />
                      <span>Clarification Applied to Architecture</span>
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </main>
    </div>
  );
}

