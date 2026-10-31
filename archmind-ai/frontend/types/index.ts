export interface Project {
  id: string;
  name: string;
  description?: string;
  status: string;
  created_at: string;
  updated_at: string;
  metadata_json?: Record<string, any>;
}

export interface ProjectStats {
  project_id: string;
  project_name: string;
  status: string;
  total_documents: number;
  total_evidence: number;
  total_requirements: number;
  total_conflicts: number;
  resolved_conflicts: number;
  pending_clarifications: number;
  total_components: number;
  total_adrs: number;
  coverage_score: number;
  risk_score: number;
  validation_passed: boolean;
}

export interface DocumentItem {
  id: string;
  filename: string;
  file_type: string;
  file_size_bytes: number;
  status: string;
  created_at: string;
}

export interface EvidenceItem {
  id: string;
  evidence_code: string;
  source_filename: string;
  statement: string;
  category: string;
  original_excerpt: string;
  location_reference?: string;
  confidence_score: number;
  quality_grade: string;
  is_duplicate: boolean;
  created_at: string;
}

export interface RequirementItem {
  id: string;
  req_code: string;
  title: string;
  description: string;
  req_type: string;
  category: string;
  priority: string;
  source_evidence_codes: string[];
  confidence: number;
  verification_method: string;
  ambiguity_status: string;
  approval_status: string;
  rationale?: string;
  created_at?: string;
}

export interface ConflictItem {
  id: string;
  conflict_code: string;
  conflicting_req_codes: string[];
  conflict_type: string;
  explanation: string;
  evidence_excerpts: string[];
  severity: string;
  business_impact: string;
  technical_impact: string;
  suggested_resolution: string;
  clarification_question: string;
  confidence: number;
  status: string;
  resolution_notes?: string;
}

export interface ClarificationQuestion {
  id: string;
  question_code: string;
  title: string;
  question: string;
  context_reasoning?: string;
  related_req_codes: string[];
  suggested_options: string[];
  status: string;
  created_at?: string;
}

export interface ArchitectureComponent {
  id: string;
  component_code: string;
  name: string;
  layer: string;
  responsibility: string;
  technology_stack: string;
  deployment_target: string;
  scaling_strategy: string;
  security_controls: string[];
  related_req_codes: string[];
  dependencies: string[];
  status: string;
}

export interface APIEndpoint {
  id: string;
  component_code: string;
  method: string;
  path: string;
  summary: string;
  auth_requirement: string;
  rate_limit: string;
  related_req_codes: string[];
}

export interface DataFlow {
  id: string;
  flow_code: string;
  title: string;
  source: string;
  target: string;
  protocol: string;
  payload_type: string;
  encryption: string;
  step_sequence: number;
  description?: string;
}

export interface ADRItem {
  id: string;
  adr_code: string;
  title: string;
  status: string;
  context: string;
  problem: string;
  decision: string;
  alternatives: { option: string; trade_off: string }[];
  advantages: string[];
  disadvantages: string[];
  trade_offs: string;
  supporting_req_codes: string[];
  evidence_references: string[];
  assumptions: string[];
  consequences: string;
  confidence: number;
}

export interface TraceabilityItem {
  req_code: string;
  req_description: string;
  req_category: string;
  evidence_codes: string[];
  mapped_component_codes: string[];
  related_api_ids: string[];
  related_adr_codes: string[];
  validation_status: string;
  coverage_status: string;
  coverage_score: number;
}

export interface TraceabilityMatrixResponse {
  total_requirements: number;
  fully_covered: number;
  partially_covered: number;
  not_covered: number;
  blocked: number;
  overall_coverage_pct: number;
  items: TraceabilityItem[];
}

export interface ValidationItem {
  id?: string;
  rule_name: string;
  category: string;
  status: string;
  score: number;
  details: string;
  recommendation?: string;
  is_deterministic: boolean;
}

export interface RiskItem {
  id?: string;
  risk_code: string;
  title: string;
  category: string;
  likelihood: string;
  impact: string;
  severity: string;
  risk_score: number;
  related_req_codes: string[];
  affected_components: string[];
  mitigation_strategy: string;
}

export interface ValidationOverview {
  overall_health_score: number;
  status: string;
  passed_rules_count: number;
  warned_rules_count: number;
  failed_rules_count: number;
  validations: ValidationItem[];
  risks: RiskItem[];
}

export interface ChangeImpactResult {
  id?: string;
  target_req_code: string;
  original_description: string;
  modified_description: string;
  affected_components: string[];
  affected_apis: string[];
  affected_adrs: string[];
  infrastructure_changes: string[];
  performance_risks: string[];
  database_implications?: string;
  scaling_requirements?: string;
  new_clarification_questions: string[];
  comparison_summary: string;
  status: string;
}

export interface TechStackAlternative {
  name: string;
  pros: string[];
  cons: string[];
  why_rejected: string;
  trade_offs: string;
}

export interface TechStackItem {
  category: string;
  selected: string;
  reason_why: string;
  requirements_supported: string[];
  alternatives: TechStackAlternative[];
  is_overridden?: boolean;
  overridden_by?: string;
}

export interface ArchitectureMetrics {
  latency_p99: string;
  throughput_tps: string;
  availability: string;
  rpo_rto: string;
  security_posture: string;
  scalability_ceiling: string;
}

export interface ArchitectureEvolutionModel {
  name: string;
  style: string;
  description: string;
  characteristics: string[];
  metrics: ArchitectureMetrics;
  mermaid_diagram: string;
}

export interface ArchitectureComparison {
  project_id: string;
  old_architecture: ArchitectureEvolutionModel;
  new_architecture: ArchitectureEvolutionModel;
  comparison_matrix: {
    dimension: string;
    legacy: string;
    target: string;
    delta: string;
    impact: string;
  }[];
  tech_stack_recommendations: TechStackItem[];
  confirmation_status: string;
  confirmed_by?: string;
  confirmed_at?: string;
  architect_notes?: string;
  overrides?: Record<string, string>;
}


