/**
 * Auto-generated ClaimCraft BD TypeScript API contracts.
 * DO NOT EDIT MANUALLY. Generated via: python scripts/tasks.py contracts
 */

export interface ApiLiveHealth {
  status: string;
  app: string;
  environment: string;
  version: string;
}

export interface ApiReadyHealth {
  status: string;
  app: string;
  environment: string;
  capabilities: {
    ai_provider: string;
    stt_provider: string;
    storage_backend: string;
  };
}

export interface ApiPing {
  message: string;
}

export interface ErrorResponse {
  error: {
    code: string;
    message: string;
    correlation_id?: string;
    details?: Record<string, unknown>;
  };
}

export interface AssessmentRouteOut {
  route_id: string;
  rule_id: string;
  issue_type: string;
  status: unknown;
  reasons: unknown[];
  allowed_actions: unknown[];
  source_dependencies: unknown[];
  condition_trace: unknown[];
}

export interface CaseCreate {
  title: string;
  jurisdiction?: string;
  locale?: string;
  desired_outcomes?: unknown[];
  incident_date?: unknown;
  merchant_name?: unknown;
  story_narrative?: unknown;
  is_demo?: boolean;
}

export interface CaseEventOut {
  id: string;
  case_id: string;
  event_sequence: number;
  event_type: string;
  actor_type: string;
  created_at: string;
  payload: Record<string, unknown>;
}

export interface CaseListOut {
  items: unknown[];
  total: number;
}

export interface CaseOut {
  id: string;
  principal_id: string;
  display_reference: string;
  title: string;
  jurisdiction: string;
  locale: string;
  desired_outcomes: unknown[];
  lifecycle_status: string;
  row_version: number;
  is_demo: boolean;
  incident_date?: unknown;
  merchant_name?: unknown;
  story_narrative?: unknown;
  created_at: string;
  updated_at: string;
}

export interface CaseUpdate {
  expected_version: number;
  title?: unknown;
  desired_outcomes?: unknown;
  merchant_name?: unknown;
  incident_date?: unknown;
  story_narrative?: unknown;
  lifecycle_status?: unknown;
}

export interface ConsentCreate {
  purpose: string;
  policy_version: string;
  processor_version?: unknown;
  affirmative_action: string;
  case_id?: unknown;
}

export interface ConsentOut {
  id: string;
  principal_id: string;
  case_id?: unknown;
  purpose: string;
  policy_version: string;
  processor_version?: unknown;
  affirmative_action: string;
  granted_at: string;
  withdrawn_at?: unknown;
}

export interface DeletionRequestCreate {
  case_id?: unknown;
  scope?: string;
  retention_acknowledged?: boolean;
}

export interface DeletionRequestOut {
  id: string;
  principal_id: string;
  case_id?: unknown;
  scope: string;
  status: string;
  requested_at: string;
  access_revoked_at?: unknown;
  completed_at?: unknown;
}

export interface DraftRequestOut {
  document_type?: string;
  locale?: string;
  subject: string;
  recipient: string;
  body_text: string;
  citations?: unknown[];
  lifecycle_state?: string;
  is_sent?: boolean;
  is_filed?: boolean;
  unsubmitted_banner_notice_en?: string;
  unsubmitted_banner_notice_bn?: string;
  created_at: string;
}

export interface FactAssertionCreate {
  field_name: string;
  field_type: string;
  raw_value: unknown;
  original_text?: unknown;
  origin?: string;
  issue_id?: unknown;
  span_start?: unknown;
  span_end?: unknown;
}

export interface FactAssertionOut {
  id: string;
  case_id: string;
  issue_id?: unknown;
  field_name: string;
  field_type: string;
  typed_value: unknown;
  original_text: string;
  origin: string;
  created_case_version: number;
  is_active: boolean;
  created_at: string;
}

export interface FactProposal {
  field_name: string;
  field_type: string;
  raw_value: unknown;
  original_text: string;
  span_ids?: unknown[];
  confidence?: number;
  uncertainty_rationale?: unknown;
}

export interface FactProposalSet {
  schema_version?: string;
  detected_domain: string;
  detected_issue: string;
  spans?: unknown[];
  proposals?: unknown[];
}

export interface FactReviewOut {
  id: string;
  assertion_id: string;
  reviewer_principal_id: string;
  review_outcome: string;
  correction_assertion_id?: unknown;
  reviewed_case_version: number;
  rationale?: unknown;
  reviewed_at: string;
}

export interface FactReviewSubmission {
  review_outcome: string;
  corrected_value?: unknown;
  corrected_original_text?: unknown;
  rationale?: unknown;
}

export interface GuestSessionResponse {
  principal_id: string;
  access_token: string;
  token_type?: string;
  expires_in?: number;
  csrf_token: string;
}

export interface HTTPValidationError {
  detail?: unknown[];
}

export interface KnowledgeReleaseOut {
  id: string;
  release_id: string;
  release_mode: string;
  manifest_hash: string;
  is_active: boolean;
  created_at: string;
  promoted_at?: unknown;
}

export interface NextBestQuestion {
  question_key: string;
  fact_field: string;
  prompt_en: string;
  prompt_bn: string;
  question_type: string;
  options?: unknown;
  priority: string;
  relevance_rationale: string;
}

export interface PrincipalOut {
  id: string;
  kind: string;
  locale: string;
  consent_revision: number;
  created_at: string;
  roles?: unknown[];
}

export interface ProceduralAssessmentOut {
  case_id: string;
  overall_status: string;
  primary_action: string;
  primary_action_title_en: string;
  primary_action_title_bn: string;
  secondary_actions: unknown[];
  routes: unknown[];
  next_best_question?: unknown;
  source_cards: unknown[];
}

export interface ReleaseBuildRequest {
  release_id: string;
  release_mode?: string;
  source_version_ids: unknown[];
  rules?: unknown[];
}

export interface ReviewResultOut {
  id: string;
  source_version_id: string;
  reviewer_name: string;
  scope: string;
  decision: string;
  approved_at: string;
}

export interface ReviewSubmission {
  scope: string;
  decision?: string;
  rationale: string;
  limitations?: unknown;
}

export interface RouteStatus {
}

export interface SourceCandidateOut {
  id: string;
  family_id: string;
  version_tag: string;
  issuer: string;
  document_type: string;
  applicability_status: string;
  clean_text_hash: string;
  created_at: string;
}

export interface SourceProvisionOut {
  id: string;
  provision_path: string;
  title: string;
  text_content: string;
  normalized_text: string;
  page_number?: unknown;
  created_at: string;
}

export interface TextSpan {
  span_id: string;
  text: string;
  start_offset: number;
  end_offset: number;
}

export interface UpgradeRequest {
  verified_user_id: string;
  verified_email: string;
  provider_access_token?: unknown;
}

export interface UpgradeResponse {
  principal_id: string;
  kind: string;
  access_token: string;
  message: string;
}

export interface ValidationError {
  loc: unknown[];
  msg: string;
  type: string;
  input?: unknown;
  ctx?: Record<string, unknown>;
}
