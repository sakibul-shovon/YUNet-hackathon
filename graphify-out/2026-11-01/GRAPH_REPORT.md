# Graph Report - ostad hacakathon  (2026-11-01)

## Corpus Check
- 284 files · ~216,183 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 13 file(s) not represented in the graph (top: .jsonl 4, .example 1, (none) 1)

## Summary
- 2229 nodes · 5702 edges · 130 communities (81 shown, 49 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 504 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Generated
- Ast / Source Registry
- Normalization / Schemas
- Router / Export Service
- Service / Router
- Compose
- Models / Env
- Router / Service
- Package / Tailwind.Config
- Test P11 Official Watchers And Safe Releases / Service
- Service / Router
- Engine / Test P13 Security Redteam Privacy Suite
- Evidencevaultclient / Processingdetailsdrawer
- Issue Service / Issue Router
- Timeline Service / Timeline Router
- Page / Card
- Router / Domain Catalogue
- Router
- Provision Service / Test T24 Hierarchical Provisions
- Test T51 Multimodal Matrix And Pipeline / Screenshot Adapter
- Router / Service
- Models / Service
- Stt Adapter / Test P06 Multimodal Benchmark
- Security / Test T01 T02 T03 Tenancy And Auth
- Storage
- Mfs Unauthorized Charge
- Public Service Grievance
- Insurance Claim Dispute
- Defective Goods
- Ecommerce Delivery Failure
- Telecom Billing And Outage
- Service / Storage
- Intakeform / Api
- Hybrid Retriever / Test T25 Hybrid Retrieval And Rrf
- Test P12 Domain Packs And Cross Domain Coherence / Action Dag
- Main / Public Router
- Product Safety Hazard
- Admin Service / Router
- Router
- Tsconfig
- Load Test Runner / Backup Restore Drill
- Test T12 Parser Probe And Bombs / Test T13 T14 Pdf Parsing And Coordinates
- Schemas / Service
- Actionstudioclient / Actiondraftviewer
- Tasks
- Ci
- Document Parser / Service
- Draft Generator / Test T26 Draft Request
- Schemas / Router
- Runner / Metrics
- Test T21 Payment Reconciliation / Test T36 Evidence Cascading Deletion
- Test T22 Audio Transcription And Codecs / Mime Codec
- Watcher Service / Router
- Test P14 6 Judge Smoke And Capabilities
- Whywhynottraceview / Whatifdrawer
- Security / Service
- Document Ast / Seed Demo
- Conftest / Database
- Contracts / Verify I18N
- Test T10 T11 Evidence Upload / Models
- Reassessment Service / Router
- Diff Service
- Pipeline Service / Router
- Test P09 Action Studio And Filing
- Package
- Bm25 Adapter / Test T25 Hybrid Retrieval And Rrf
- E5 Adapter / Test T25 Hybrid Retrieval And Rrf
- Dataset Loader
- Router
- Test T23 Screenshot Vlm And Ocr Reconciliation
- Page / Onenextactioncard
- Generate Datasets
- Parser Probe
- Router / Schemas
- Test P10 Living Case And Decision Changes
- Config / Layout
- Citation Validator / Test T25 Hybrid Retrieval And Rrf
- Test P14 2 Judge Scenarios And Isolation
- Livingcaseactivityclient / Page
- Test T13 T14 Pdf Parsing And Coordinates
- Test T15 Evidence Preview And Privacy
- Test P08 1 Paired Jurisdictions
- Test P08 2 Issue Split Merge
- Test P08 5 Nbq And Safety Priority
- Test P06 4 Multimodal Fact Integration
- Test T49 T50 Bilingual Themes
- Route
- Test Upgrade And Deletion
- Test T19 T20 Procedural Assessment
- Production Readiness Check
- Package
- Mime Validation
- Router
- Test P04 6 E2E M1 Vertical Slice
- Test P06 6 Multimodal Downstream E2E
- Test T04 Case Crud Concurrency
- Next.Config / Next
- Test P08 4 What If Simulation
- Test P08 6 Pipeline Runs
- Test T24 Hierarchical Provisions
- Test T25 Hybrid Retrieval And Rrf
- Test T09 Review And Verification
- Postcss.Config / Postcss-Load-Config
- Test P14 6 Judge Smoke And Capabilities
- Pnpm-Workspace
- Pyproject

## God Nodes (most connected - your core abstractions)
1. `Principal` - 195 edges
2. `FactService` - 62 edges
3. `Badge()` - 46 edges
4. `EvidenceService` - 45 edges
5. `Card()` - 43 edges
6. `CardContent()` - 43 edges
7. `CardHeader()` - 42 edges
8. `CardTitle()` - 42 edges
9. `Button` - 41 edges
10. `ProceduralAssessmentEngine` - 39 edges

## Surprising Connections (you probably didn't know these)
- `run_load_test()` --indirect_call--> `client()`  [INFERRED]
  evaluation/load_tests/load_test_runner.py → services/backend/tests/conftest.py
- `seed_demo_case()` --uses--> `FactAssertion`  [INFERRED]
  scripts/seed_demo.py → services/backend/app/facts/models.py
- `seed_demo_case()` --uses--> `Principal`  [INFERRED]
  scripts/seed_demo.py → services/backend/app/identity/models.py
- `seed_demo_case()` --uses--> `Case`  [INFERRED]
  scripts/seed_demo.py → services/backend/app/cases/models.py
- `test_p04_6_e2e_m1_vertical_slice()` --calls--> `seed_demo_case()`  [EXTRACTED]
  services/backend/tests/integration/test_p04_6_e2e_m1_vertical_slice.py → scripts/seed_demo.py

## Import Cycles
- None detected.

## Communities (130 total, 49 thin omitted)

### Community 0 - "Generated"
Cohesion: 0.02
Nodes (106): ActionDAGOut, ActionNode, ApiLiveHealth, ApiPing, ApiReadyHealth, AssessmentRouteOut, AudioTranscriptOut, Body_transcribe_case_audio_api_v1_cases__case_id__audio_transcribe_post (+98 more)

### Community 1 - "Ast / Source Registry"
Cohesion: 0.06
Nodes (36): get_source_by_id(), get_source_registry(), is_private_or_restricted_ip(), is_url_allowlisted(), SourceRegistryEntry, AllNode, AnyNode, ASTNode (+28 more)

### Community 2 - "Normalization / Schemas"
Cohesion: 0.06
Nodes (18): CaseExtractor, FactProposal, FactProposalSet, TextSpan, ascii_to_bengali_digits(), bengali_to_ascii_digits(), DateValue, MoneyValue (+10 more)

### Community 3 - "Router / Export Service"
Cohesion: 0.07
Nodes (22): ComplaintDestinationOut, ComplaintDestinationService, DocumentEditRequest, EditableDocumentAST, CaseExportOut, ExportService, RasterRedactionRequest, PortalFieldDef (+14 more)

### Community 4 - "Service / Router"
Cohesion: 0.10
Nodes (15): CaseEvent, CaseSnapshot, create_case(), delete_case(), get_case(), get_case_activity(), list_cases(), update_case() (+7 more)

### Community 5 - "Compose"
Cohesion: 0.05
Nodes (48): build, depends_on, environment, ports, restart, context, dockerfile, postgres (+40 more)

### Community 6 - "Models / Env"
Cohesion: 0.10
Nodes (14): Base, FactResolution, FactReview, WebSession, do_run_migrations(), get_url(), run_async_migrations(), run_migrations_offline() (+6 more)

### Community 7 - "Router / Service"
Cohesion: 0.12
Nodes (19): OutboxMessage, Consent, DeletionRequest, auth_guest(), auth_logout(), auth_upgrade(), get_deletion_status(), get_me() (+11 more)

### Community 8 - "Package / Tailwind.Config"
Cohesion: 0.06
Nodes (41): dependencies, @claimcraft/contracts@workspace:*, clsx@^2.1.1, lucide-react@^0.474.0, next@^15.1.6, next-intl@^3.26.3, next-themes@^0.4.4, react@^19.0.0 (+33 more)

### Community 9 - "Test P11 Official Watchers And Safe Releases / Service"
Cohesion: 0.10
Nodes (12): create_access_jwt(), SourceProvision, KnowledgeService, publisher_client(), reviewer_client(), test_p11_1_official_watchers_and_manual_import_t42(), test_p11_2_section_aware_diff_and_commencement_t43(), test_p11_3_scoped_approval_and_consumer_veto_t44() (+4 more)

### Community 10 - "Service / Router"
Cohesion: 0.12
Nodes (13): extract_case_narrative(), create_case_fact(), list_case_facts(), propose_multimodal_case_fact(), review_case_fact(), FactAssertionCreate, FactAssertionOut, FactResolutionOut (+5 more)

### Community 11 - "Engine / Test P13 Security Redteam Privacy Suite"
Cohesion: 0.10
Nodes (15): AssessmentRouteOut, NextBestQuestion, ProceduralAssessmentEngine, ProceduralAssessmentOut, RouteDiffItem, select_facts(), WhatIfSimulationRequest, WhatIfSimulationResult (+7 more)

### Community 12 - "Evidencevaultclient / Processingdetailsdrawer"
Cohesion: 0.09
Nodes (25): CaseEvidencePage(), EvidenceItemRejectionBanner(), EvidenceRejectionProps, EvidenceItemData, EvidenceVaultClient(), EvidenceVaultClientProps, ReconciliationData, PipelineRun (+17 more)

### Community 13 - "Issue Service / Issue Router"
Cohesion: 0.16
Nodes (16): create_case_issue(), get_multi_issue_assessment(), list_case_issues(), merge_case_issues(), review_case_issue(), split_case_issue(), IssueCreate, IssueMergeRequest (+8 more)

### Community 14 - "Timeline Service / Timeline Router"
Cohesion: 0.14
Nodes (15): CaseReminder, ExternalReference, cancel_case_reminder(), create_case_reminder(), get_case_timeline(), list_case_reminders(), list_case_snapshots(), record_case_external_update() (+7 more)

### Community 15 - "Page / Card"
Cohesion: 0.26
Nodes (24): CaseLayout(), FactReviewPage(), CasesListPage(), fetchCases(), HelpPage(), HowItWorksPage(), LimitationsPage(), HomePage() (+16 more)

### Community 16 - "Router / Domain Catalogue"
Cohesion: 0.10
Nodes (14): DomainCapabilityEntry, DomainCatalogueResponse, DomainCatalogueService, answer_next_best_question(), apply_what_if_overrides(), check_domain_support(), get_case_assessment(), get_domain_catalogue() (+6 more)

### Community 17 - "Router"
Cohesion: 0.13
Nodes (11): complete_upload(), create_evidence_span_link(), delete_case_evidence(), get_case_evidence_item(), get_evidence_preview(), get_evidence_regions(), get_payment_reconciliation(), list_case_evidence() (+3 more)

### Community 18 - "Provision Service / Test T24 Hierarchical Provisions"
Cohesion: 0.13
Nodes (11): ProvisionService, get_provision_by_citation_handle(), get_source_provisions_tree(), lookup_provision_by_exact_section(), ProvisionLookupResult, ProvisionOut, ProvisionTreeItem, test_t24_anti_fabrication_never_invents_missing_provisions() (+3 more)

### Community 19 - "Test T51 Multimodal Matrix And Pipeline / Screenshot Adapter"
Cohesion: 0.15
Nodes (11): ChatBubbleProposal, OCRDisagreement, ScreenshotAnalysisResult, ScreenshotAdapter, test_t51_matrix_row1_english_text_only(), test_t51_matrix_row2_bangla_banglish_text_only(), test_t51_matrix_row3_voice_recording_only(), test_t51_matrix_row4_screenshot_only_preserves_uncertainty() (+3 more)

### Community 20 - "Router / Service"
Cohesion: 0.13
Nodes (6): get_scenario_manifest(), SyntheticScenarioManifest, launch_scenario(), list_scenarios(), reset_scenario(), ScenarioService

### Community 21 - "Models / Service"
Cohesion: 0.16
Nodes (4): RetrievalChunk, SourceApproval, SourceFamily, SourceVersion

### Community 22 - "Stt Adapter / Test P06 Multimodal Benchmark"
Cohesion: 0.14
Nodes (7): AudioTranscriptOut, UncertainSpan, WordTimestamp, STTAdapter, test_cascading_privacy_cleanup_t37(), test_committed_audio_samples_recall_and_timestamps(), test_provider_failure_resilience_fallback()

### Community 23 - "Security / Test T01 T02 T03 Tenancy And Auth"
Cohesion: 0.11
Nodes (8): scoped_tenant_session(), decode_and_verify_jwt(), generate_session_token(), require_role(), ActorRole, test_t01_cross_tenant_isolation(), test_t02_token_verification_and_role_escalation(), test_t03_connection_pool_tenant_context_hygiene()

### Community 25 - "Mfs Unauthorized Charge"
Cohesion: 0.08
Nodes (25): eq, allowed_actions, conditions, all, date_basis, fact, value, exclusions (+17 more)

### Community 26 - "Public Service Grievance"
Cohesion: 0.08
Nodes (25): eq, allowed_actions, conditions, all, date_basis, fact, value, exclusions (+17 more)

### Community 27 - "Insurance Claim Dispute"
Cohesion: 0.08
Nodes (25): eq, allowed_actions, conditions, all, date_basis, fact, value, exclusions (+17 more)

### Community 28 - "Defective Goods"
Cohesion: 0.08
Nodes (25): eq, allowed_actions, conditions, all, date_basis, fact, value, exclusions (+17 more)

### Community 29 - "Ecommerce Delivery Failure"
Cohesion: 0.08
Nodes (25): eq, allowed_actions, conditions, all, date_basis, fact, value, exclusions (+17 more)

### Community 30 - "Telecom Billing And Outage"
Cohesion: 0.08
Nodes (25): eq, allowed_actions, conditions, all, date_basis, fact, value, exclusions (+17 more)

### Community 32 - "Intakeform / Api"
Cohesion: 0.17
Nodes (18): FactItem, FactReviewClientProps, IntakeForm(), handleSubmit(), IntakeFormProps, VoiceNoteRecorder(), VoiceNoteRecorderProps, ScenarioLauncher() (+10 more)

### Community 33 - "Hybrid Retriever / Test T25 Hybrid Retrieval And Rrf"
Cohesion: 0.13
Nodes (5): BengaliBM25Adapter, E5EmbeddingAdapter, HybridRetriever, test_t25_channel_ablations_and_degraded_reporting(), test_t25_hybrid_retrieval_and_rrf_fusion()

### Community 34 - "Test P12 Domain Packs And Cross Domain Coherence / Action Dag"
Cohesion: 0.15
Nodes (9): ActionDAGOut, ActionDAGService, ActionNode, test_consumer(), test_p12_1_telecom_isp_domain_pack_and_stale_map(), test_p12_2_insurance_domain_pack_and_abstention(), test_p12_3_grs_pack_and_statutory_exclusions(), test_p12_4_domain_capability_catalogue_and_unsupported_fallback() (+1 more)

### Community 35 - "Main / Public Router"
Cohesion: 0.11
Nodes (7): Settings, get_capabilities(), get_technology(), api_ping(), health_live(), health_ready(), test_doctor_readiness_no_secret_leak()

### Community 36 - "Product Safety Hazard"
Cohesion: 0.08
Nodes (23): eq, allowed_actions, conditions, all, date_basis, fact, value, exclusions (+15 more)

### Community 37 - "Admin Service / Router"
Cohesion: 0.14
Nodes (3): AdminKnowledgeService, build_release(), KnowledgeReleaseOut

### Community 38 - "Router"
Cohesion: 0.12
Nodes (10): approve_candidate(), disable_release(), get_active_release(), get_candidate_diff(), get_source_health(), get_source_provision(), list_source_candidates(), promote_release() (+2 more)

### Community 39 - "Tsconfig"
Cohesion: 0.10
Nodes (20): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+12 more)

### Community 40 - "Load Test Runner / Backup Restore Drill"
Cohesion: 0.16
Nodes (6): main(), reader_task(), run_load_test(), writer_pipeline_task(), execute_drill(), request_logging_and_correlation()

### Community 41 - "Test T12 Parser Probe And Bombs / Test T13 T14 Pdf Parsing And Coordinates"
Cohesion: 0.19
Nodes (7): create_test_image(), create_test_pdf(), test_t12_encrypted_pdf_and_active_javascript_rejection(), test_t12_pdf_page_bomb_rejection(), test_t12_pixel_bomb_rejection(), test_t12_scanner_outage_stays_quarantined_and_retryable(), generate_invoice_pdf()

### Community 42 - "Schemas / Service"
Cohesion: 0.25
Nodes (11): init_upload(), EvidenceItemOut, EvidenceSpanLinkCreate, EvidenceSpanLinkOut, PaymentReconciliationResult, ReconciliationItem, UploadCompleteRequest, UploadIntentCreate (+3 more)

### Community 43 - "Actionstudioclient / Actiondraftviewer"
Cohesion: 0.13
Nodes (16): CaseActionsPage(), ActionDAG, ActionNode, ActionStudioClient(), loadPortalFields(), loadStudioData(), ComplaintDestination, DocumentSection (+8 more)

### Community 44 - "Tasks"
Cohesion: 0.26
Nodes (12): cmd_bootstrap(), cmd_check(), cmd_contracts(), cmd_dev(), cmd_doctor(), cmd_seed_demo(), cmd_status(), compute_sha256() (+4 more)

### Community 45 - "Ci"
Cohesion: 0.11
Nodes (18): name, runs-on, steps, jobs, foundation, name, on, pull_request (+10 more)

### Community 46 - "Document Parser / Service"
Cohesion: 0.15
Nodes (3): DocumentParser, DocumentParseResult, TextRegion

### Community 47 - "Draft Generator / Test T26 Draft Request"
Cohesion: 0.15
Nodes (5): DraftRequestGenerator, DraftRequestOut, test_t26_draft_api_endpoint_and_tenant_isolation(), test_t26_draft_generation_invariants(), test_t26_threat_and_false_claim_rejection()

### Community 48 - "Schemas / Router"
Cohesion: 0.30
Nodes (14): run_watcher_check(), CandidateDiffOut, CaseReassessmentResult, ManualImportRequest, ReleaseBuildRequest, ReleaseRollbackRequest, ReviewResultOut, ReviewSubmission (+6 more)

### Community 50 - "Test T21 Payment Reconciliation / Test T36 Evidence Cascading Deletion"
Cohesion: 0.16
Nodes (5): make_pdf_with_amount(), test_t21_duplicate_receipt_exclusion(), test_t21_payment_conflict_and_multi_receipt_resolution(), make_pdf(), test_t36_evidence_deletion_purges_files_and_invalidates_spans()

### Community 51 - "Test T22 Audio Transcription And Codecs / Mime Codec"
Cohesion: 0.17
Nodes (6): detect_audio_mime_from_bytes(), validate_audio_file(), make_dummy_audio_bytes(), test_t22_audio_codec_validation_and_spoof_rejection(), test_t22_audio_replay_stream_and_deletion(), test_t22_consent_enforcement_and_private_stt_transcription()

### Community 52 - "Watcher Service / Router"
Cohesion: 0.19
Nodes (4): SourceCandidate, manual_source_import(), OfficialSourceWatcher, WatcherFetchResult

### Community 53 - "Test P14 6 Judge Smoke And Capabilities"
Cohesion: 0.17
Nodes (6): judge(), test_all_eight_scenarios_e2e_launch_assessment_and_reset(), test_catalogue_contains_all_eight_scenarios_and_three_quick_starts(), test_scenario_a_whatif_capabilities(), test_scenario_h_living_case_diff_and_adversarial_isolation(), test_t54_official_destination_registry()

### Community 54 - "Whywhynottraceview / Whatifdrawer"
Cohesion: 0.17
Nodes (13): CasePathsPage(), ProcessingDetailsDrawer(), RouteDiffItem, WhatIfDrawer(), WhatIfDrawerProps, WhatIfSimulationResult, ConditionTraceItem, NextBestQuestion (+5 more)

### Community 55 - "Security / Service"
Cohesion: 0.15
Nodes (3): get_current_principal(), hash_session_token(), verify_csrf_protection()

### Community 56 - "Document Ast / Seed Demo"
Cohesion: 0.36
Nodes (6): seed_demo_case(), _do_seed(), DocumentASTService, DocumentSectionAST, DocumentSentenceAST, Case

### Community 57 - "Conftest / Database"
Cohesion: 0.15
Nodes (4): get_db_session(), client(), db_session(), setup_test_db()

### Community 58 - "Contracts / Verify I18N"
Cohesion: 0.22
Nodes (6): export_openapi(), generate_typescript(), main(), save_state(), get_keys(), main()

### Community 59 - "Test T10 T11 Evidence Upload / Models"
Cohesion: 0.27
Nodes (6): EvidenceItem, test_t01_evidence_tenant_isolation(), test_t10_mime_spoofing_and_binary_validation(), test_t10_reused_intent_and_successful_accepted_flow(), test_t11_case_quota_reservation_limits(), test_t11_upload_token_lifespan_and_sweeper()

### Community 60 - "Reassessment Service / Router"
Cohesion: 0.20
Nodes (5): KnowledgeRelease, ReassessmentQueueService, flag_impacted_cases(), reassess_case(), ReassessmentQueueResult

### Community 61 - "Diff Service"
Cohesion: 0.23
Nodes (4): CandidateImpactProposal, ParsedProvision, ProvisionDiffItem, SectionAwareDiffService

### Community 62 - "Pipeline Service / Router"
Cohesion: 0.20
Nodes (4): PipelineRunOut, PipelineRunService, PipelineStageReceipt, get_case_pipeline_runs()

### Community 63 - "Test P09 Action Studio And Filing"
Cohesion: 0.20
Nodes (6): test_p09_1_action_dag_dependency_and_non_forced_seller_notice(), test_p09_1_action_dag_financial_stage_hierarchy_t20(), test_p09_2_document_ast_and_user_edit_t26_t29(), test_p09_3_portal_field_maps_and_stale_fallback_t33(), test_p09_4_export_markdown_and_html_t27_t34(), test_p09_7_destination_registry_and_link_health_t54()

### Community 64 - "Package"
Cohesion: 0.15
Nodes (12): description, engines, node, name, packageManager, private, scripts, check:foundation (+4 more)

### Community 68 - "Router"
Cohesion: 0.20
Nodes (3): delete_audio_recording(), stream_audio_recording(), transcribe_case_audio()

### Community 69 - "Test T23 Screenshot Vlm And Ocr Reconciliation"
Cohesion: 0.30
Nodes (4): make_dummy_screenshot(), test_t23_ocr_vs_vlm_disagreement_flagged_for_user_review(), test_t23_screenshot_dark_theme_and_bubble_role_uncertainty(), test_t23_vision_api_endpoint_and_tenant_isolation()

### Community 70 - "Page / Onenextactioncard"
Cohesion: 0.35
Nodes (7): CaseOverviewPage(), IntakePage(), Badge(), BadgeProps, ActionChoice, OneNextActionCard(), OneNextActionProps

### Community 71 - "Generate Datasets"
Cohesion: 0.35
Nodes (6): build_counterfactual_pairs(), build_evidence_conflicts(), build_retrieval_queries(), build_routing_scenarios(), compute_sha256(), main()

### Community 73 - "Router / Schemas"
Cohesion: 0.31
Nodes (6): get_retriever(), hybrid_search_provisions(), validate_statutory_citations(), CitationValidationRequest, CitationValidationResponse, HybridSearchRequest

### Community 74 - "Test P10 Living Case And Decision Changes"
Cohesion: 0.29
Nodes (4): test_p10_1_user_reported_update_and_origin_tracking_t38(), test_p10_2_semantic_decision_diff_and_snapshots_t39(), test_p10_4_personal_reminders_and_cancellation_t40(), test_p10_5_stale_tab_optimistic_concurrency_t41()

### Community 75 - "Config / Layout"
Cohesion: 0.33
Nodes (4): defaultLocale, Locale, locales, config

### Community 76 - "Citation Validator / Test T25 Hybrid Retrieval And Rrf"
Cohesion: 0.24
Nodes (3): CitationValidationResult, CitationValidator, test_t28_t29_citation_validator()

### Community 77 - "Test P14 2 Judge Scenarios And Isolation"
Cohesion: 0.27
Nodes (4): judge_a(), judge_b(), test_p14_2_eight_scenarios_catalogue_and_featured_quick_starts(), test_p14_2_judge_sandbox_isolation_and_no_mutation_sharing_t52()

### Community 78 - "Livingcaseactivityclient / Page"
Cohesion: 0.28
Nodes (7): CaseActivityPage(), LivingCaseActivityClient(), loadData(), Props, Reminder, SemanticDiff, TimelineEvent

### Community 79 - "Test T13 T14 Pdf Parsing And Coordinates"
Cohesion: 0.33
Nodes (3): test_t13_native_pdf_critical_token_extraction(), test_t14_multicolumn_reading_order(), test_t14_rotated_page_coordinates_normalization_and_viewport_resize()

### Community 80 - "Test T15 Evidence Preview And Privacy"
Cohesion: 0.36
Nodes (3): make_sample_pdf(), test_t15_private_preview_requires_owner_and_sets_cache_headers(), test_t15_span_to_fact_linking_and_tenant_isolation()

### Community 81 - "Test P08 1 Paired Jurisdictions"
Cohesion: 0.32
Nodes (3): test_p08_1_date_limitation_and_uncertainty_t30(), test_p08_1_paired_jurisdictions_t19_t20(), test_p08_1_unsupported_remedy_checking()

### Community 82 - "Test P08 2 Issue Split Merge"
Cohesion: 0.32
Nodes (3): test_p08_2_issue_crud_and_brand_track_rejection(), test_p08_2_issue_split_and_merge(), test_p08_2_multi_issue_independent_evaluation()

### Community 83 - "Test P08 5 Nbq And Safety Priority"
Cohesion: 0.32
Nodes (3): test_p08_5_nbq_skip_preserves_unknown_t32(), test_p08_5_safety_hazard_priority_t32(), test_p08_5_strict_otp_pin_prohibition_t32()

### Community 85 - "Test T49 T50 Bilingual Themes"
Cohesion: 0.29
Nodes (4): get_all_keys(), test_t49_bilingual_message_parity(), test_t49_english_default_configuration(), test_t50_theme_default_and_tokens()

### Community 86 - "Route"
Cohesion: 0.29
Nodes (5): DELETE, GET, PATCH, POST, PUT

### Community 90 - "Production Readiness Check"
Cohesion: 0.60
Nodes (3): audit_nginx_tls(), audit_secret_leakage(), main()

### Community 91 - "Package"
Cohesion: 0.40
Nodes (4): main, name, types, version

## Knowledge Gaps
- **1 isolated node(s):** `claimcraft-backend`
  These have ≤1 connection - possible missing edges. (Counts symbols only; 939 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **49 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Principal` connect `Issue Service / Issue Router` to `Router / Export Service`, `Service / Router`, `Models / Env`, `Router / Service`, `Test P11 Official Watchers And Safe Releases / Service`, `Service / Router`, `Engine / Test P13 Security Redteam Privacy Suite`, `Timeline Service / Timeline Router`, `Router / Domain Catalogue`, `Router`, `Router / Service`, `Models / Service`, `Stt Adapter / Test P06 Multimodal Benchmark`, `Security / Test T01 T02 T03 Tenancy And Auth`, `Service / Storage`, `Test P12 Domain Packs And Cross Domain Coherence / Action Dag`, `Main / Public Router`, `Admin Service / Router`, `Router`, `Schemas / Service`, `Document Parser / Service`, `Schemas / Router`, `Watcher Service / Router`, `Test P14 6 Judge Smoke And Capabilities`, `Security / Service`, `Document Ast / Seed Demo`, `Reassessment Service / Router`, `Pipeline Service / Router`, `Router`, `Test P14 2 Judge Scenarios And Isolation`, `Router`?**
  _High betweenness centrality (0.163) - this node is a cross-community bridge._
- **Are the 105 inferred relationships involving `Principal` (e.g. with `seed_demo_case()` and `ActionDAGService`) actually correct?**
  _`Principal` has 105 INFERRED edges - model-reasoned connections that need verification._
- **What connects `claimcraft-backend` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Generated` be split into smaller, more focused modules?**
  _Cohesion score 0.018691588785046728 - nodes in this community are weakly interconnected._
- **Why does `StorageBackend` connect `Storage` to `Service / Storage`?**
  _High betweenness centrality (0.018) - this node is a cross-community bridge._
- **Are the 42 inferred relationships involving `FactService` (e.g. with `ActionDAGService` and `edit_document_ast_sentence()`) actually correct?**
  _`FactService` has 42 INFERRED edges - model-reasoned connections that need verification._
- **Should `Ast / Source Registry` be split into smaller, more focused modules?**
  _Cohesion score 0.057703081232493 - nodes in this community are weakly interconnected._