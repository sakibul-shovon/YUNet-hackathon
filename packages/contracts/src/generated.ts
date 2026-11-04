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

export interface ActionDAGOut {
  case_id: string;
  primary_action_id: string;
  nodes: unknown[];
  stage_hierarchy_explanation_en: string;
  stage_hierarchy_explanation_bn: string;
}

export interface ActionNode {
  action_id: string;
  title_en: string;
  title_bn: string;
  description_en: string;
  description_bn: string;
  action_type: string;
  status: string;
  blocking_reasons?: unknown[];
  prerequisite_actions?: unknown[];
  destination_id?: unknown;
  is_primary?: boolean;
  is_mandatory?: boolean;
}

export interface AlertCreateRequest {
  title: string;
  title_en: string;
  severity?: string;
  message: string;
  active?: boolean;
}

export interface AssessmentRouteOut {
  route_id: string;
  rule_id: string;
  issue_type: string;
  status: unknown;
  reasons: unknown[];
  allowed_actions: unknown[];
  source_dependencies: unknown[];
  statutory_citations?: unknown[];
  supported_remedies?: unknown[];
  unsupported_remedies?: unknown[];
  unsupported_remedy_warnings?: unknown[];
  condition_trace: unknown[];
}

export interface AudioTranscriptOut {
  case_id: string;
  audio_evidence_id?: unknown;
  transcript_text: string;
  language: string;
  overall_confidence: number;
  duration_seconds: number;
  words?: unknown[];
  uncertain_spans?: unknown[];
  consent_recorded?: boolean;
  created_at: string;
}

export interface AuthUserOut {
  logged_in: boolean;
  principal_id: string;
  email: string;
  full_name: string;
  phone?: unknown;
  is_demo_judge?: boolean;
  roles?: unknown[];
  access_token?: unknown;
  token_type?: string;
  demo_case_id?: unknown;
}

export interface Body_transcribe_case_audio_api_v1_audio_transcribe_post {
  audio_file: string;
  consent_granted: boolean;
  language_hint?: string;
  client_duration?: number;
  client_transcript?: string;
}

export interface Body_transcribe_case_audio_api_v1_cases__case_id__audio_transcribe_post {
  audio_file: string;
  consent_granted: boolean;
  language_hint?: string;
  client_duration?: number;
  client_transcript?: string;
}

export interface Body_transcribe_case_audio_v1_audio_transcribe_post {
  audio_file: string;
  consent_granted: boolean;
  language_hint?: string;
  client_duration?: number;
  client_transcript?: string;
}

export interface Body_transcribe_case_audio_v1_cases__case_id__audio_transcribe_post {
  audio_file: string;
  consent_granted: boolean;
  language_hint?: string;
  client_duration?: number;
  client_transcript?: string;
}

export interface CandidateDiffOut {
  candidate_id: string;
  family_slug: string;
  is_current_law?: boolean;
  publication_date?: unknown;
  commencement_date?: unknown;
  commencement_status: string;
  has_transitional_clauses?: boolean;
  transitional_notes?: unknown[];
  impacted_rules?: unknown[];
  impacted_domains?: unknown[];
  provision_diffs?: unknown[];
  added_count?: number;
  modified_count?: number;
  repealed_count?: number;
  unchanged_count?: number;
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

export interface CaseExportOut {
  export_id: string;
  case_id: string;
  format: string;
  document_title: string;
  content: string;
  sha256_hash: string;
  disclaimer_notice?: string;
  is_filed?: boolean;
  is_sent?: boolean;
  created_at: string;
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
  consent_status?: string;
  row_version: number;
  is_demo: boolean;
  incident_date?: unknown;
  merchant_name?: unknown;
  story_narrative?: unknown;
  created_at: string;
  updated_at: string;
}

export interface CaseOverrideRequest {
  new_status: string;
  admin_notes?: string;
}

export interface CaseReassessmentResult {
  case_id: string;
  reassessed_at: string;
  release_id: string;
  has_changed: boolean;
  prior_primary_action?: unknown;
  new_primary_action?: unknown;
  decision_diff?: Record<string, unknown>;
}

export interface CaseSnapshotOut {
  id: string;
  case_id: string;
  version: number;
  canonical_input_hash: string;
  issue_state: Record<string, unknown>;
  created_at: string;
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

export interface ChatBubbleProposal {
  bubble_id: string;
  text: string;
  speaker_role?: string;
  speaker_role_confidence?: number;
  timestamp_text?: unknown;
  normalized_box?: unknown;
}

export interface CitationValidationRequest {
  citation_handles: unknown[];
  date_context?: unknown;
  allowed_source_ids?: unknown;
}

export interface CitationValidationResponse {
  is_valid: boolean;
  valid_citations: unknown[];
  invalid_citations?: unknown[];
}

export interface CommunityCommentCreate {
  author_name?: string;
  content: string;
}

export interface CommunityCommentOut {
  id: string;
  author_name: string;
  content: string;
  created_at: string;
  is_legal_volunteer?: boolean;
}

export interface CommunityModerateRequest {
  action: string;
}

export interface CommunityPostCreate {
  title: string;
  story: string;
  category?: string;
  merchant_name?: string;
  disputed_amount_bdt?: number;
}

export interface CommunityPostOut {
  id: string;
  title: string;
  story: string;
  category: string;
  merchant_name: string;
  disputed_amount_bdt: number;
  author_name: string;
  me_too_count: number;
  created_at: string;
  has_converted_case?: boolean;
  comments_count: number;
  comments?: unknown[];
}

export interface ComplaintDestinationOut {
  destination_id: string;
  title_en: string;
  title_bn: string;
  authority_name: string;
  official_portal_url: string;
  procedure_guide_url: string;
  prerequisites_en?: unknown[];
  prerequisites_bn?: unknown[];
  link_health?: string;
  fallback_instructions_en: string;
  fallback_instructions_bn: string;
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

export interface CopilotActionSuggestion {
  id: string;
  label_en: string;
  label_bn: string;
  action_type: string;
  payload: string;
}

export interface CopilotChatRequest {
  message: string;
  locale?: string;
  case_context?: unknown;
  case_id?: unknown;
}

export interface CopilotChatResponse {
  reply_en: string;
  reply_bn: string;
  relevant_statute?: unknown;
  suggested_actions?: unknown[];
  mode?: string;
  citations?: unknown[];
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

export interface DocumentEditRequest {
  document_type: string;
  section_id: string;
  sentence_id: string;
  new_text: string;
  locale?: string;
  expected_revision?: unknown;
}

export interface DocumentParseResult {
  evidence_id: string;
  page_count: number;
  has_native_text: boolean;
  ocr_applied: boolean;
  regions?: unknown[];
  full_text?: string;
  quality_flags?: unknown[];
  page_dimensions?: unknown[];
}

export interface DocumentSectionAST {
  section_id: string;
  section_title_en: string;
  section_title_bn: string;
  sentences: unknown[];
}

export interface DocumentSentenceAST {
  sentence_id: string;
  text: string;
  statement_type: string;
  supporting_fact_id?: unknown;
  supporting_citation?: unknown;
  supporting_record?: unknown;
  is_user_edited?: boolean;
}

export interface DomainCapabilityEntry {
  domain_id: string;
  title_en: string;
  title_bn: string;
  support_status: string;
  support_depth: string;
  disclosed_routes: unknown[];
  statutory_basis: string;
  is_fully_supported: boolean;
  caveat_en?: unknown;
  caveat_bn?: unknown;
}

export interface DomainCatalogueResponse {
  jurisdiction?: string;
  domains: unknown[];
  disclaimer_en?: string;
  disclaimer_bn?: string;
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

export interface EditableDocumentAST {
  document_id: string;
  case_id: string;
  document_type: string;
  locale?: string;
  title: string;
  counterpart_name: string;
  desired_remedy: string;
  sections: unknown[];
  evidence_index?: unknown[];
  preparation_checklist?: unknown[];
  unsubmitted_disclaimer_en?: string;
  unsubmitted_disclaimer_bn?: string;
  lifecycle_state?: string;
  is_filed?: boolean;
  is_sent?: boolean;
  created_at: string;
  case_version?: number;
  revision?: number;
}

export interface EvidenceItemOut {
  id: string;
  case_id: string;
  original_filename: string;
  declared_mime_type: string;
  detected_mime_type?: unknown;
  byte_size: number;
  sha256_hash?: unknown;
  status: string;
  is_quarantined: boolean;
  rejection_reason?: unknown;
  rejection_code?: unknown;
  is_retryable?: boolean;
  guidance_en?: unknown;
  guidance_bn?: unknown;
  created_at: string;
}

export interface EvidenceSpanLinkCreate {
  assertion_id: string;
  page_number?: unknown;
  normalized_box?: unknown;
  selected_text?: unknown;
}

export interface EvidenceSpanLinkOut {
  id: string;
  assertion_id: string;
  evidence_id: string;
  source_type: string;
  page_number?: unknown;
  normalized_box?: unknown;
  selected_text?: unknown;
  created_at: string;
}

export interface ExternalUpdateCreate {
  update_type: string;
  authority_or_channel: string;
  description: string;
  reference_number?: unknown;
  outcome_status?: unknown;
  additional_facts?: Record<string, unknown>;
  expected_version: number;
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
  review_outcome?: unknown;
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

export interface HybridSearchRequest {
  query: string;
  allowed_ids?: unknown;
  date_context?: unknown;
  top_k?: number;
  dense_enabled?: boolean;
  lexical_enabled?: boolean;
}

export interface IssueCreate {
  canonical_taxonomy: string;
  desired_remedy?: unknown;
}

export interface IssueMergeRequest {
  issue_ids_to_merge: unknown[];
  target_canonical_taxonomy: string;
  target_desired_remedy?: unknown;
}

export interface IssueReviewRequest {
  user_review: string;
  desired_remedy?: unknown;
  corrected_taxonomy?: unknown;
}

export interface IssueSplitRequest {
  source_issue_id: string;
  sub_issues: unknown[];
}

export interface IssueTrackOut {
  id: string;
  case_id: string;
  canonical_taxonomy: string;
  hypothesis_state: string;
  user_review?: unknown;
  desired_remedy?: unknown;
  rejection_reason?: unknown;
  active: boolean;
  created_at: string;
  updated_at: string;
}

export interface KnowledgeReleaseOut {
  id: string;
  release_id: string;
  release_mode: string;
  manifest_hash: string;
  is_active: boolean;
  manifest_data?: Record<string, unknown>;
  created_at: string;
  promoted_at?: unknown;
}

export interface ManualImportRequest {
  family_slug: string;
  title: string;
  text_content: string;
  issuer: string;
  document_type?: string;
  official_url?: unknown;
  publication_date?: unknown;
  commencement_date?: unknown;
}

export interface MerchantComplaintSummary {
  id: string;
  date: string;
  issue_type: string;
  amount_bdt: number;
  status: string;
  summary_preview: string;
}

export interface MerchantIntelligenceOut {
  merchant_name: string;
  risk_level: string;
  complaint_count: number;
  total_disputed_bdt: number;
  common_patterns: unknown[];
  victim_count: number;
  is_known_offender: boolean;
  platform: string;
  recommended_action: string;
  recent_complaints?: unknown[];
}

export interface MerchantOverrideRequest {
  is_blacklisted: boolean;
  is_verified: boolean;
  risk_percent: number;
  admin_note: string;
}

export interface MerchantRadarLeaderboardItem {
  merchant_name: string;
  platform: string;
  category: string;
  complaint_count: number;
  total_disputed_bdt: number;
  risk_level: string;
  primary_allegation: string;
  last_reported_date: string;
}

export interface MerchantRadarResponse {
  total_tracked_merchants: number;
  total_complaints_indexed: number;
  total_disputed_amount_bdt: number;
  top_offenders: unknown[];
}

export interface MultiIssueAssessmentOut {
  case_id: string;
  issue_tracks: unknown[];
  independent_paths: unknown[];
}

export interface MultimodalFactProposal {
  field_name: string;
  field_type: string;
  raw_value: unknown;
  original_text: string;
  origin?: string;
  source_type?: string;
  locator_meta?: unknown;
}

export interface MultimodalProposalResult {
  assertion: unknown;
  source_link_id: string;
  has_conflict?: boolean;
  conflicting_assertion_id?: unknown;
  conflict_message_en?: unknown;
  conflict_message_bn?: unknown;
}

export interface NBQAnswerRequest {
  question_key: string;
  fact_field: string;
  value: unknown;
  field_type?: string;
}

export interface NBQSkipRequest {
  question_key: string;
  fact_field: string;
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

export interface OCRDisagreement {
  field_name: string;
  ocr_detected_value: unknown;
  vlm_detected_value: unknown;
  ocr_confidence: number;
  vlm_confidence: number;
  resolution_status?: string;
  guidance_en: string;
  guidance_bn: string;
}

export interface PaymentReconciliationResult {
  case_id: string;
  narrated_amount_minor_units: number;
  linked_evidence_total_minor_units: number;
  discrepancy_minor_units: number;
  is_reconciled: boolean;
  status: string;
  reconciled_items?: unknown[];
  unlinked_items?: unknown[];
  prompt_en: string;
  prompt_bn: string;
}

export interface PipelineRunOut {
  pipeline_id: string;
  case_id: string;
  executed_at: string;
  overall_status: string;
  stages: unknown[];
  technology_inventory: Record<string, unknown>;
}

export interface PipelineStageReceipt {
  stage_name: string;
  status: string;
  provider: string;
  model_or_algorithm: string;
  duration_ms?: unknown;
  details?: Record<string, unknown>;
}

export interface PortalFieldDef {
  field_key: string;
  label_en: string;
  label_bn: string;
  fact_source: string;
  required?: boolean;
  prepared_value?: unknown;
  transformation?: unknown;
  notes?: unknown;
}

export interface PortalFieldMapOut {
  portal_id: string;
  portal_name_en: string;
  portal_name_bn: string;
  official_destination_url: string;
  map_version: string;
  is_stale?: boolean;
  stale_reason?: unknown;
  fields: unknown[];
  disclaimer_en?: string;
  disclaimer_bn?: string;
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
  limitation_warning_en?: unknown;
  limitation_warning_bn?: unknown;
  days_remaining_in_limitation?: unknown;
  is_deadline_uncertain?: boolean;
}

export interface ProvisionLookupResult {
  query: string;
  normalized_query: string;
  match_found: boolean;
  provision?: unknown;
  preserves_qualification?: boolean;
  context_note_en?: string;
  context_note_bn?: string;
}

export interface ProvisionOut {
  citation_handle: string;
  source_id: string;
  provision_path: string;
  section_number: string;
  section_bn: string;
  title_en: string;
  title_bn: string;
  parent_path?: unknown;
  document_type: string;
  canonical_text_en: string;
  canonical_text_bn: string;
  qualifications_and_exceptions?: unknown[];
  key_definitions?: Record<string, unknown>;
  penalties?: unknown;
  aliases?: unknown[];
  effective_from?: unknown;
  effective_to?: unknown;
  parent_provision?: unknown;
}

export interface ProvisionTreeItem {
  provision_path: string;
  citation_handle: string;
  title_en: string;
  title_bn: string;
  section_number: string;
  children?: unknown[];
}

export interface RasterRedactionRequest {
  bounding_boxes: unknown[];
}

export interface ReassessmentQueueResult {
  release_id: string;
  impacted_cases_count: number;
  flagged_case_ids: unknown[];
  affected_rules: unknown[];
}

export interface ReconciliationItem {
  evidence_id: string;
  filename: string;
  amount_minor_units: number;
  is_duplicate?: boolean;
  is_linked?: boolean;
}

export interface ReleaseBuildRequest {
  release_id: string;
  release_mode?: string;
  source_version_ids: unknown[];
  rules?: unknown[];
  portal_maps?: unknown[];
  lexical_index_hash?: unknown;
  dense_index_model?: unknown;
}

export interface ReleaseRollbackRequest {
  target_release_id: string;
  rationale: string;
}

export interface ReminderCreate {
  reminder_title: string;
  remind_at: string;
  category?: string;
  notes?: unknown;
}

export interface ReminderOut {
  id: string;
  case_id: string;
  reminder_title: string;
  remind_at: string;
  category: string;
  notes?: unknown;
  is_completed: boolean;
  is_legal_caution?: boolean;
  disclaimer_notice?: string;
  created_at: string;
}

export interface ReplyEdit {
  draft: string;
  expected_version: number;
}

export interface ReplyInput {
  message: string;
  locale?: string;
  expected_version: number;
}

export interface ReviewInput {
  item_id: string;
  outcome: string;
  corrected_date?: unknown;
  expected_version: number;
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

export interface RouteDiffItem {
  route_id: string;
  issue_type: string;
  baseline_status: unknown;
  simulated_status: unknown;
  changed: boolean;
}

export interface RouteStatus {
}

export interface RunRequest {
  operation?: string;
  locale?: string;
  expected_version?: unknown;
}

export interface ScreenshotAnalysisResult {
  evidence_id: string;
  case_id: string;
  detected_layout: string;
  theme: string;
  authenticity_guarantee?: boolean;
  bubbles?: unknown[];
  proposed_facts?: unknown[];
  ocr_disagreements?: unknown[];
  disclaimer_en?: string;
  disclaimer_bn?: string;
  analyzed_at: string;
}

export interface SemanticDecisionDiff {
  prior_version: number;
  new_version: number;
  prior_primary_action: string;
  new_primary_action: string;
  is_decision_changed: boolean;
  changed_routes?: unknown[];
  unchanged_routes?: unknown[];
  changed_actions?: unknown[];
  unchanged_actions?: unknown[];
}

export interface SourceCandidateOut {
  id: string;
  family_id: string;
  url: string;
  status: string;
  raw_hash: string;
  origin_chain?: Record<string, unknown>;
  fetched_at: string;
}

export interface SourceHealthItem {
  source_id: string;
  title_en: string;
  title_bn: string;
  official_url: string;
  document_type: string;
  status: string;
  health_status: string;
  procedural_scope: string;
  is_authoritative_for_penalties?: boolean;
  notice?: unknown;
}

export interface SourceHealthResponse {
  active_release_id?: unknown;
  active_release_mode?: unknown;
  active_manifest_hash?: unknown;
  sources?: unknown[];
}

export interface SourceInput {
  text: string;
  label?: string;
  source_type?: string;
  evidence_id?: unknown;
  expected_version: number;
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

export interface SubIssueData {
  canonical_taxonomy: string;
  desired_remedy?: unknown;
  assigned_fact_ids?: unknown[];
}

export interface SyntheticScenarioManifest {
  scenario_id: string;
  scenario_letter: string;
  is_featured: boolean;
  title_en: string;
  title_bn: string;
  domain: string;
  inputs_en: string;
  inputs_bn: string;
  description_en: string;
  description_bn: string;
  differentiator_en: string;
  differentiator_bn: string;
  sample_story: string;
  merchant_name: string;
  initial_facts: Record<string, unknown>;
}

export interface TextRegion {
  region_id: string;
  page_number: number;
  text: string;
  normalized_box: unknown[];
  origin?: string;
  confidence?: number;
  is_critical_token?: boolean;
  critical_token_type?: unknown;
}

export interface TextSpan {
  span_id: string;
  text: string;
  start_offset: number;
  end_offset: number;
}

export interface TimelineEventOut {
  id: string;
  case_id: string;
  event_sequence: number;
  event_type: string;
  actor_type: string;
  origin: string;
  title: string;
  description: string;
  reference_number?: unknown;
  created_at: string;
  decision_diff?: unknown;
}

export interface UncertainSpan {
  span: string;
  start_time: number;
  end_time: number;
  reason: string;
  suggested_alternatives?: unknown[];
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

export interface UploadIntentCreate {
  case_id: string;
  declared_filename: string;
  declared_mime_type: string;
  declared_byte_size: number;
}

export interface UploadIntentOut {
  intent_id: string;
  case_id: string;
  upload_url: string;
  upload_token: string;
  token_expires_at: string;
  max_byte_size: number;
  storage_kind: string;
}

export interface UserLoginRequest {
  email: string;
  password: string;
}

export interface UserRegisterRequest {
  email: string;
  password: string;
  full_name: string;
  phone?: unknown;
}

export interface UserRoleUpdateRequest {
  roles: unknown[];
}

export interface ValidationError {
  loc: unknown[];
  msg: string;
  type: string;
  input?: unknown;
  ctx?: Record<string, unknown>;
}

export interface WatcherCheckRequest {
  source_id: string;
  simulate_fixture?: unknown;
}

export interface WatcherCheckResponse {
  source_id: string;
  target_url: string;
  status: string;
  change_type?: unknown;
  raw_hash?: unknown;
  clean_text_hash?: unknown;
  quarantine_reason?: unknown;
  error_message?: unknown;
  candidate_id?: unknown;
  fetched_at: string;
}

export interface WhatIfApplyRequest {
  overrides: Record<string, unknown>;
  expected_version?: unknown;
}

export interface WhatIfSimulationRequest {
  overrides: Record<string, unknown>;
}

export interface WhatIfSimulationResult {
  case_id: string;
  case_version?: unknown;
  overrides: Record<string, unknown>;
  baseline_routes: unknown[];
  simulated_routes: unknown[];
  route_diff: unknown[];
  is_material_change: boolean;
  summary_en: string;
  summary_bn: string;
}

export interface WordTimestamp {
  word: string;
  start_time: number;
  end_time: number;
  confidence?: number;
}
