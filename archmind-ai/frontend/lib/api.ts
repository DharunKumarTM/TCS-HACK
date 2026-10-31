const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${url}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options?.headers || {}),
    },
    ...options,
  });

  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`API error (${res.status}): ${errorText || res.statusText}`);
  }

  return res.json();
}

export const api = {
  // Input Analysis Module
  async analyzeInput(formData: FormData) {
    const res = await fetch(`${API_BASE}/projects/analyze-input`, {
      method: "POST",
      body: formData,
    });
    if (!res.ok) {
      const err = await res.text();
      throw new Error(`Analysis failed: ${err}`);
    }
    return res.json();
  },
  async ingestText(projectId: string, text: string, title?: string) {
    return fetchJson<any>(`/projects/${projectId}/ingest-text`, {
      method: "POST",
      body: JSON.stringify({ text, title }),
    });
  },

  // Projects
  async getProjects() {
    return fetchJson<any[]>("/projects");
  },
  async getProject(projectId: string) {
    return fetchJson<any>(`/projects/${projectId}`);
  },
  async getProjectStats(projectId: string) {
    return fetchJson<any>(`/projects/${projectId}/stats`);
  },
  async loadSmartBankDemo() {
    return fetchJson<any>("/projects/demo/smartbank", { method: "POST" });
  },
  async triggerPipeline(projectId: string, pauseForClarification: boolean = true) {
    return fetchJson<any>(`/projects/${projectId}/run-pipeline?pause_for_clarification=${pauseForClarification}`, {
      method: "POST"
    });
  },

  // Documents & Evidence
  async getDocuments(projectId: string) {
    return fetchJson<any[]>(`/projects/${projectId}/documents`);
  },
  async uploadDocument(projectId: string, file: File) {
    const formData = new FormData();
    formData.append("file", file);
    const res = await fetch(`${API_BASE}/projects/${projectId}/documents`, {
      method: "POST",
      body: formData,
    });
    if (!res.ok) throw new Error("Document upload failed");
    return res.json();
  },
  async getEvidence(projectId: string, category?: string) {
    const query = category ? `?category=${encodeURIComponent(category)}` : "";
    return fetchJson<any[]>(`/projects/${projectId}/evidence${query}`);
  },

  // Requirements
  async getRequirements(projectId: string, filter?: { type?: string; priority?: string }) {
    let query = "";
    if (filter?.type) query += `?req_type=${encodeURIComponent(filter.type)}`;
    if (filter?.priority) query += `${query ? "&" : "?"}priority=${encodeURIComponent(filter.priority)}`;
    return fetchJson<any[]>(`/projects/${projectId}/requirements${query}`);
  },
  async updateRequirement(reqId: string, payload: { title?: string; description?: string; priority?: string; approval_status?: string; ambiguity_status?: string }) {
    return fetchJson<any>(`/requirements/${reqId}`, {
      method: "PATCH",
      body: JSON.stringify(payload),
    });
  },

  // Conflicts
  async getConflicts(projectId: string, severity?: string) {
    const query = severity ? `?severity=${encodeURIComponent(severity)}` : "";
    return fetchJson<any[]>(`/projects/${projectId}/conflicts${query}`);
  },
  async resolveConflict(conflictId: string, resolutionNotes: string, status: string = "Resolved") {
    return fetchJson<any>(`/conflicts/${conflictId}/resolve`, {
      method: "POST",
      body: JSON.stringify({ resolution_notes: resolutionNotes, status }),
    });
  },

  // Clarifications
  async getClarifications(projectId: string) {
    return fetchJson<any[]>(`/projects/${projectId}/clarifications`);
  },
  async submitClarificationResponse(questionId: string, selectedOption?: string, customAnswer?: string) {
    return fetchJson<any>(`/clarifications/${questionId}/respond`, {
      method: "POST",
      body: JSON.stringify({
        selected_option: selectedOption,
        custom_answer: customAnswer,
        submitted_by: "Lead Software Architect"
      }),
    });
  },

  // Architecture & Diagrams
  async getArchitecture(projectId: string) {
    return fetchJson<any>(`/projects/${projectId}/architecture`);
  },
  async getArchitectureComparison(projectId: string) {
    return fetchJson<any>(`/projects/${projectId}/architecture/comparison`);
  },
  async confirmArchitecture(projectId: string, payload: { action: string; architect_name?: string; notes?: string; overrides?: Record<string, string> }) {
    return fetchJson<any>(`/projects/${projectId}/architecture/confirm`, {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },
  async getDiagrams(projectId: string) {
    return fetchJson<Record<string, string>>(`/projects/${projectId}/diagrams`);
  },

  // ADRs
  async getADRs(projectId: string) {
    return fetchJson<any[]>(`/projects/${projectId}/adrs`);
  },
  async updateADRStatus(adrId: string, status: string, reviewNotes?: string) {
    return fetchJson<any>(`/adrs/${adrId}`, {
      method: "PATCH",
      body: JSON.stringify({ status, review_notes: reviewNotes }),
    });
  },

  // Traceability
  async getTraceability(projectId: string) {
    return fetchJson<any>(`/projects/${projectId}/traceability`);
  },

  // Validation
  async getValidation(projectId: string) {
    return fetchJson<any>(`/projects/${projectId}/validation`);
  },

  // Change Impact
  async simulateChangeImpact(projectId: string, targetReqCode: string, modifiedDescription: string) {
    return fetchJson<any>(`/projects/${projectId}/impact-analysis`, {
      method: "POST",
      body: JSON.stringify({
        target_req_code: targetReqCode,
        modified_description: modifiedDescription
      }),
    });
  },
  async applyChangeImpact(analysisId: string) {
    return fetchJson<any>("/impact-analysis/apply", {
      method: "POST",
      body: JSON.stringify({ analysis_id: analysisId, apply_to_architecture: true }),
    });
  },

  // Reports
  async getReportMarkdown(projectId: string): Promise<string> {
    const res = await fetch(`${API_BASE}/projects/${projectId}/report`);
    if (!res.ok) throw new Error("Failed to fetch markdown report");
    return res.text();
  }
};

