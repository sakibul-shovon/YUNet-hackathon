'use client';

import React, { useState, useEffect } from 'react';
import {
  AlertTriangle,
  ArrowRight,
  Check,
  CheckCircle2,
  Copy,
  Download,
  ExternalLink,
  FileEdit,
  FileText,
  HelpCircle,
  Info,
  Layers,
  Lock,
  PhoneCall,
  RefreshCw,
  ShieldAlert,
  ShieldCheck,
} from 'lucide-react';

import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card';

interface ActionNode {
  action_id: string;
  title_en: string;
  title_bn: string;
  description_en: string;
  description_bn: string;
  action_type: string;
  status: 'ready' | 'blocked' | 'optional' | 'completed';
  blocking_reasons: string[];
  prerequisite_actions: string[];
  destination_id?: string | null;
  is_primary: boolean;
  is_mandatory: boolean;
}

interface ActionDAG {
  case_id: string;
  primary_action_id: string;
  nodes: ActionNode[];
  stage_hierarchy_explanation_en: string;
  stage_hierarchy_explanation_bn: string;
}

interface DocumentSentence {
  sentence_id: string;
  text: string;
  statement_type: 'reviewed_fact' | 'user_allegation' | 'statutory_basis' | 'procedural_note';
  supporting_fact_id?: string | null;
  supporting_citation?: string | null;
  is_user_edited: boolean;
}

interface DocumentSection {
  section_id: string;
  section_title_en: string;
  section_title_bn: string;
  sentences: DocumentSentence[];
}

interface EditableDocumentAST {
  document_id: string;
  case_id: string;
  document_type: string;
  locale: string;
  title: string;
  counterpart_name: string;
  desired_remedy: string;
  sections: DocumentSection[];
  evidence_index: Array<{ id: string; filename: string; mime_type: string; status: string }>;
  preparation_checklist: string[];
  unsubmitted_disclaimer_en: string;
  unsubmitted_disclaimer_bn: string;
  lifecycle_state: string;
  is_filed: boolean;
  is_sent: boolean;
  created_at: string;
}

interface PortalFieldDef {
  field_key: string;
  label_en: string;
  label_bn: string;
  fact_source: string;
  required: boolean;
  prepared_value: string | null;
  transformation?: string | null;
  notes?: string | null;
}

interface PortalFieldMap {
  portal_id: string;
  portal_name_en: string;
  portal_name_bn: string;
  official_destination_url: string;
  map_version: string;
  is_stale: boolean;
  stale_reason?: string | null;
  fields: PortalFieldDef[];
  disclaimer_en: string;
  disclaimer_bn: string;
}

interface ComplaintDestination {
  destination_id: string;
  title_en: string;
  title_bn: string;
  authority_name: string;
  official_portal_url: string;
  procedure_guide_url: string;
  prerequisites_en: string[];
  prerequisites_bn: string[];
  link_health: string;
  fallback_instructions_en: string;
  fallback_instructions_bn: string;
}

interface Props {
  caseId: string;
  locale: string;
}

export function ActionStudioClient({ caseId, locale }: Props) {
  const isBangla = locale === 'bn';

  const [activeTab, setActiveTab] = useState<'studio' | 'ast' | 'portal' | 'destinations'>('studio');
  const [dag, setDag] = useState<ActionDAG | null>(null);
  const [docAst, setDocAst] = useState<EditableDocumentAST | null>(null);
  const [portalMap, setPortalMap] = useState<PortalFieldMap | null>(null);
  const [destinations, setDestinations] = useState<ComplaintDestination[]>([]);
  const [selectedPortal, setSelectedPortal] = useState<string>('dncrp_ccms');

  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [editingSentence, setEditingSentence] = useState<{
    sectionId: string;
    sentenceId: string;
    text: string;
  } | null>(null);
  const [copiedKey, setCopiedKey] = useState<string | null>(null);
  const [exportNotice, setExportNotice] = useState<string | null>(null);

  useEffect(() => {
    async function loadStudioData() {
      setIsLoading(true);
      try {
        const [dagRes, astRes, destRes] = await Promise.all([
          fetch(`/api/v1/cases/${caseId}/actions/dag`),
          fetch(`/api/v1/cases/${caseId}/documents/ast?locale=${locale}`),
          fetch('/api/v1/actions/destinations'),
        ]);

        if (dagRes.ok) setDag(await dagRes.json());
        if (astRes.ok) setDocAst(await astRes.json());
        if (destRes.ok) setDestinations(await destRes.json());
      } catch (e) {
        console.error('Failed to load action studio data', e);
      } finally {
        setIsLoading(false);
      }
    }
    loadStudioData();
  }, [caseId, locale]);

  useEffect(() => {
    async function loadPortalFields() {
      try {
        const res = await fetch(`/api/v1/cases/${caseId}/portals/${selectedPortal}/fields`);
        if (res.ok) {
          setPortalMap(await res.json());
        }
      } catch (e) {
        console.error('Failed to load portal fields', e);
      }
    }
    loadPortalFields();
  }, [caseId, selectedPortal]);

  const handleCopy = (text: string, key: string) => {
    navigator.clipboard.writeText(text);
    setCopiedKey(key);
    setTimeout(() => setCopiedKey(null), 2500);
  };

  const handleSaveSentenceEdit = async () => {
    if (!editingSentence || !docAst) return;

    try {
      const res = await fetch(`/api/v1/cases/${caseId}/documents/edit`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          document_type: docAst.document_type,
          section_id: editingSentence.sectionId,
          sentence_id: editingSentence.sentenceId,
          new_text: editingSentence.text,
        }),
      });

      if (res.ok) {
        const updated = await res.json();
        setDocAst(updated);
        setEditingSentence(null);
      }
    } catch (e) {
      console.error('Failed to save sentence edit', e);
    }
  };

  const handleExport = async (format: 'markdown' | 'html') => {
    try {
      const res = await fetch(`/api/v1/cases/${caseId}/export/${format}?locale=${locale}`, {
        method: 'POST',
      });
      if (res.ok) {
        const data = await res.json();
        const blob = new Blob([data.content], {
          type: format === 'markdown' ? 'text/markdown' : 'text/html',
        });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `claimcraft-dispute-${caseId.slice(0, 8)}.${format === 'markdown' ? 'md' : 'html'}`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        setExportNotice(
          isBangla
            ? `ডকুমেন্ট ডাউনলোড সম্পন্ন হয়েছে (SHA-256: ${data.sha256_hash.slice(0, 12)}...)। মনে রাখবেন, ডাউনলোড করলে অভিযোগ জমা হয় না (T27)।`
            : `Document downloaded (SHA-256: ${data.sha256_hash.slice(0, 12)}...). Note: Downloading does not file your complaint (T27).`
        );
      }
    } catch (e) {
      console.error('Export failed', e);
    }
  };

  if (isLoading) {
    return (
      <Card className="border border-border p-8 text-center bg-surface">
        <RefreshCw className="w-8 h-8 animate-spin mx-auto text-primary mb-3" />
        <p className="text-sm font-medium text-muted-foreground">
          {isBangla ? 'অ্যাকশন স্টুডিও লোড হচ্ছে...' : 'Loading Action Studio & DAG...'}
        </p>
      </Card>
    );
  }

  const primaryNode = dag?.nodes.find((n) => n.is_primary);

  return (
    <div className="space-y-8">
      {/* 1. Header Navigation Tabs */}
      <div className="flex border-b border-border gap-2 overflow-x-auto pb-1">
        <button
          onClick={() => setActiveTab('studio')}
          className={`px-4 py-2 text-sm font-semibold border-b-2 transition-colors whitespace-nowrap cursor-pointer flex items-center gap-2 ${
            activeTab === 'studio'
              ? 'border-primary text-primary'
              : 'border-transparent text-muted-foreground hover:text-foreground'
          }`}
        >
          <Layers className="w-4 h-4" />
          <span>{isBangla ? 'অ্যাকশন শৃঙ্খলা ও পরবর্তী পদক্ষেপ' : 'Action DAG & Sequence'}</span>
        </button>

        <button
          onClick={() => setActiveTab('ast')}
          className={`px-4 py-2 text-sm font-semibold border-b-2 transition-colors whitespace-nowrap cursor-pointer flex items-center gap-2 ${
            activeTab === 'ast'
              ? 'border-primary text-primary'
              : 'border-transparent text-muted-foreground hover:text-foreground'
          }`}
        >
          <FileEdit className="w-4 h-4" />
          <span>{isBangla ? 'সম্পাদনাযোগ্য অভিযোগ AST' : 'Editable Document AST'}</span>
        </button>

        <button
          onClick={() => setActiveTab('portal')}
          className={`px-4 py-2 text-sm font-semibold border-b-2 transition-colors whitespace-nowrap cursor-pointer flex items-center gap-2 ${
            activeTab === 'portal'
              ? 'border-primary text-primary'
              : 'border-transparent text-muted-foreground hover:text-foreground'
          }`}
        >
          <Copy className="w-4 h-4" />
          <span>{isBangla ? 'পোর্টাল ফাইলিং সহযোগী' : 'Portal Filing Companion'}</span>
        </button>

        <button
          onClick={() => setActiveTab('destinations')}
          className={`px-4 py-2 text-sm font-semibold border-b-2 transition-colors whitespace-nowrap cursor-pointer flex items-center gap-2 ${
            activeTab === 'destinations'
              ? 'border-primary text-primary'
              : 'border-transparent text-muted-foreground hover:text-foreground'
          }`}
        >
          <ExternalLink className="w-4 h-4" />
          <span>{isBangla ? 'অফিশিয়াল অভিযোগ সেল' : 'Official Destinations'}</span>
        </button>
      </div>

      {/* Export Status Toast/Notice */}
      {exportNotice && (
        <div className="p-3 rounded-md bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-300 dark:border-emerald-800 text-xs text-emerald-800 dark:text-emerald-200 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 shrink-0 text-emerald-600" />
            <span>{exportNotice}</span>
          </div>
          <button
            onClick={() => setExportNotice(null)}
            className="text-xs font-bold hover:underline cursor-pointer"
          >
            ✕
          </button>
        </div>
      )}

      {/* TAB 1: STUDIO (DAG & PRIMARY ACTION HERO) */}
      {activeTab === 'studio' && (
        <div className="space-y-6">
          {/* Primary Action Hero */}
          {primaryNode && (
            <Card className="border-l-4 border-l-primary bg-gradient-to-br from-surface to-elevated/40 shadow-sm">
              <CardHeader className="pb-3 flex flex-row items-start justify-between">
                <div>
                  <Badge variant="brand" className="mb-2">
                    {isBangla ? 'সর্বাগ্রে সুপারিশকৃত পদক্ষেপ' : 'PRIMARY RECOMMENDED NEXT ACTION'}
                  </Badge>
                  <CardTitle className="text-xl md:text-2xl text-foreground font-bold">
                    {isBangla ? primaryNode.title_bn : primaryNode.title_en}
                  </CardTitle>
                </div>
                <Badge
                  variant={
                    primaryNode.status === 'ready'
                      ? 'success'
                      : primaryNode.status === 'optional'
                      ? 'warning'
                      : primaryNode.status === 'completed'
                      ? 'neutral'
                      : 'danger'
                  }
                >
                  {primaryNode.status.toUpperCase()}
                </Badge>
              </CardHeader>
              <CardContent className="space-y-4">
                <p className="text-sm text-foreground/90 leading-relaxed font-medium">
                  {isBangla ? primaryNode.description_bn : primaryNode.description_en}
                </p>

                <div className="p-3 rounded-md bg-surface border border-border/80 flex items-center justify-between">
                  <div className="text-xs text-muted-foreground flex items-center gap-1.5">
                    <Info className="w-3.5 h-3.5 text-primary" />
                    <span>
                      {primaryNode.is_mandatory
                        ? isBangla
                          ? 'বাধ্যতামূলক পদক্ষেপ'
                          : 'Mandatory Step'
                        : isBangla
                        ? 'ঐচ্ছিক পদক্ষেপ — ভোক্তা অধিদপ্তরে অভিযোগের জন্য বিক্রেতাকে নোটিশ পাঠানো বাধ্যতামূলক নয়'
                        : 'Optional Step — private seller notice does not block official DNCRP filing'}
                    </span>
                  </div>

                  <div className="flex gap-2">
                    {primaryNode.action_type === 'official_portal' && (
                      <Button
                        size="sm"
                        variant="primary"
                        onClick={() => setActiveTab('portal')}
                        className="gap-1.5 text-xs"
                      >
                        <span>{isBangla ? 'পোর্টাল ফিল্ড দেখুন' : 'Go to Portal Helper'}</span>
                        <ArrowRight className="w-3.5 h-3.5" />
                      </Button>
                    )}
                    {primaryNode.action_type === 'merchant_contact' && (
                      <Button
                        size="sm"
                        variant="primary"
                        onClick={() => setActiveTab('ast')}
                        className="gap-1.5 text-xs"
                      >
                        <span>{isBangla ? 'নোটিশ খসড়া দেখুন' : 'View Notice Draft'}</span>
                        <ArrowRight className="w-3.5 h-3.5" />
                      </Button>
                    )}
                    {primaryNode.action_type === 'hotline' && (
                      <a href="tel:16121" className="inline-flex">
                        <Button size="sm" variant="danger" className="gap-1.5 text-xs">
                          <PhoneCall className="w-3.5 h-3.5" />
                          <span>{isBangla ? '১৬১২১ হটলাইনে কল করুন' : 'Call 16121 Hotline'}</span>
                        </Button>
                      </a>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Action DAG Cards */}
          <div className="space-y-4">
            <div>
              <h3 className="text-base font-bold text-foreground">
                {isBangla ? 'বিরোধ নিষ্পত্তির পদক্ষেপসমূহ ও শৃঙ্খলা' : 'Dispute Action Hierarchy & Stage Sequence'}
              </h3>
              <p className="text-xs text-muted-foreground mt-0.5">
                {isBangla ? dag?.stage_hierarchy_explanation_bn : dag?.stage_hierarchy_explanation_en}
              </p>
            </div>

            <div className="grid gap-3 md:grid-cols-2">
              {dag?.nodes.map((node) => {
                const isBlocked = node.status === 'blocked';
                const isCompleted = node.status === 'completed';
                const isOptional = node.status === 'optional';

                return (
                  <Card
                    key={node.action_id}
                    className={`border transition-all ${
                      node.is_primary
                        ? 'border-primary/50 shadow-sm'
                        : isBlocked
                        ? 'border-red-200 dark:border-red-900/40 bg-red-50/20 dark:bg-red-950/10 opacity-80'
                        : isCompleted
                        ? 'border-emerald-200 dark:border-emerald-900/40 bg-emerald-50/20 dark:bg-emerald-950/10'
                        : 'border-border bg-surface'
                    }`}
                  >
                    <CardHeader className="pb-2 flex flex-row items-start justify-between">
                      <div className="space-y-1">
                        <div className="flex items-center gap-2">
                          <CardTitle className="text-sm font-bold text-foreground">
                            {isBangla ? node.title_bn : node.title_en}
                          </CardTitle>
                        </div>
                        <span className="text-[10px] uppercase font-bold tracking-wider text-muted-foreground">
                          {node.action_type.replace('_', ' ')}
                        </span>
                      </div>
                      <Badge
                        variant={
                          node.status === 'ready'
                            ? 'success'
                            : isOptional
                            ? 'warning'
                            : isCompleted
                            ? 'neutral'
                            : 'danger'
                        }
                      >
                        {node.status.toUpperCase()}
                      </Badge>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      <p className="text-xs text-muted-foreground leading-relaxed">
                        {isBangla ? node.description_bn : node.description_en}
                      </p>

                      {isBlocked && node.blocking_reasons.length > 0 && (
                        <div className="p-2.5 rounded bg-red-100 dark:bg-red-950/60 border border-red-200 dark:border-red-800 text-[11px] text-red-900 dark:text-red-200 space-y-1">
                          <div className="flex items-center gap-1 font-bold">
                            <Lock className="w-3.5 h-3.5 shrink-0" />
                            <span>{isBangla ? 'পূর্বশর্ত বাকি রয়েছে:' : 'Prerequisites Required:'}</span>
                          </div>
                          {node.blocking_reasons.map((r, i) => (
                            <p key={i}>{r}</p>
                          ))}
                        </div>
                      )}

                      {isOptional && (
                        <div className="p-2 rounded bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800 text-[11px] text-amber-900 dark:text-amber-200 flex items-center gap-1.5">
                          <Info className="w-3.5 h-3.5 shrink-0 text-amber-600" />
                          <span>
                            {isBangla
                              ? 'ঐচ্ছিক পদক্ষেপ — ভোক্তা অধিকার আইনে এটি ছাড়া অভিযোগ দায়ের করা যায়।'
                              : 'Optional step — not required before official CCMS filing.'}
                          </span>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          </div>
        </div>
      )}

      {/* TAB 2: EDITABLE DOCUMENT AST (T26, T29) */}
      {activeTab === 'ast' && docAst && (
        <div className="space-y-6">
          {/* Unsubmitted Disclaimer (T26) */}
          <div className="p-4 rounded-lg border-2 border-amber-400 bg-amber-50 dark:bg-amber-950/40 text-amber-900 dark:text-amber-200 text-xs font-semibold flex items-start gap-3">
            <ShieldAlert className="w-5 h-5 shrink-0 text-amber-600 mt-0.5" />
            <div>
              <p className="font-bold uppercase tracking-wider mb-1">
                {isBangla ? 'শুধুমাত্র প্রস্তুতির খসড়া — জমাকৃত নয় (T26)' : 'PREPARATION MATERIAL ONLY — NOT SUBMITTED (T26)'}
              </p>
              <p className="leading-relaxed">
                {isBangla ? docAst.unsubmitted_disclaimer_bn : docAst.unsubmitted_disclaimer_en}
              </p>
            </div>
          </div>

          {/* Export Buttons */}
          <div className="flex flex-wrap items-center justify-between gap-3 p-4 rounded-md border border-border bg-surface">
            <div>
              <h4 className="text-sm font-bold text-foreground">
                {isBangla ? 'অভিযোগ খসড়া ডাউনলোড' : 'Download Dispute Materials'}
              </h4>
              <p className="text-xs text-muted-foreground">
                {isBangla
                  ? 'ক্রিপ্টোগ্রাফিক হ্যাশযুক্ত মার্কডাউন বা এইচটিএমএল ফাইল সংরক্ষণ করুন'
                  : 'Multi-format export with SHA-256 provenance hash (T34)'}
              </p>
            </div>
            <div className="flex gap-2">
              <Button size="sm" variant="outline" onClick={() => handleExport('markdown')} className="text-xs gap-1.5">
                <Download className="w-3.5 h-3.5" />
                <span>Markdown (.md)</span>
              </Button>
              <Button size="sm" variant="outline" onClick={() => handleExport('html')} className="text-xs gap-1.5">
                <Download className="w-3.5 h-3.5" />
                <span>HTML (.html)</span>
              </Button>
            </div>
          </div>

          {/* Document AST Sections */}
          <div className="space-y-4">
            {docAst.sections.map((section) => (
              <Card key={section.section_id} className="border border-border bg-surface">
                <CardHeader className="pb-3 border-b border-border/60">
                  <CardTitle className="text-sm font-bold text-foreground">
                    {isBangla ? section.section_title_bn : section.section_title_en}
                  </CardTitle>
                </CardHeader>
                <CardContent className="pt-4 space-y-3">
                  {section.sentences.map((sent) => {
                    const isEditing =
                      editingSentence?.sectionId === section.section_id &&
                      editingSentence?.sentenceId === sent.sentence_id;

                    return (
                      <div
                        key={sent.sentence_id}
                        className={`p-3 rounded-md border transition-all ${
                          sent.is_user_edited
                            ? 'border-amber-300 dark:border-amber-800 bg-amber-50/20 dark:bg-amber-950/10'
                            : 'border-border/60 bg-elevated/30'
                        }`}
                      >
                        {isEditing ? (
                          <div className="space-y-3">
                            <textarea
                              value={editingSentence.text}
                              onChange={(e) =>
                                setEditingSentence({ ...editingSentence, text: e.target.value })
                              }
                              className="w-full text-xs font-medium p-2.5 rounded border border-border bg-surface text-foreground focus:outline-primary min-h-[70px]"
                            />
                            <div className="flex items-center justify-between text-[11px] text-amber-700 dark:text-amber-300">
                              <span className="flex items-center gap-1">
                                <AlertTriangle className="w-3.5 h-3.5 text-amber-500" />
                                {isBangla
                                  ? 'সম্পাদনা করলে বাক্যটি ব্যবহারকারীর নিজস্ব দাবি (user allegation) হিসেবে গণ্য হবে (T29)।'
                                  : 'Note: Material edits become user allegations and clear verified provenance (T29).'}
                              </span>
                              <div className="flex gap-2">
                                <Button
                                  size="sm"
                                  variant="ghost"
                                  onClick={() => setEditingSentence(null)}
                                  className="text-xs h-7 px-2"
                                >
                                  {isBangla ? 'বাতিল' : 'Cancel'}
                                </Button>
                                <Button
                                  size="sm"
                                  variant="primary"
                                  onClick={handleSaveSentenceEdit}
                                  className="text-xs h-7 px-3"
                                >
                                  {isBangla ? 'সংরক্ষণ' : 'Save'}
                                </Button>
                              </div>
                            </div>
                          </div>
                        ) : (
                          <div className="flex items-start justify-between gap-4">
                            <div className="space-y-1.5 flex-1">
                              <p className="text-xs text-foreground font-medium leading-relaxed">
                                {sent.text}
                              </p>
                              <div className="flex flex-wrap items-center gap-2">
                                <Badge
                                  variant={
                                    sent.statement_type === 'reviewed_fact'
                                      ? 'success'
                                      : sent.statement_type === 'statutory_basis'
                                      ? 'brand'
                                      : 'warning'
                                  }
                                >
                                  {sent.statement_type.replace('_', ' ')}
                                </Badge>

                                {sent.supporting_citation && (
                                  <span className="text-[10px] font-mono font-semibold text-primary">
                                    Ref: {sent.supporting_citation}
                                  </span>
                                )}

                                {sent.is_user_edited && (
                                  <span className="text-[10px] text-amber-600 dark:text-amber-400 font-semibold">
                                    (User Modified)
                                  </span>
                                )}
                              </div>
                            </div>
                            <Button
                              size="sm"
                              variant="ghost"
                              onClick={() =>
                                setEditingSentence({
                                  sectionId: section.section_id,
                                  sentenceId: sent.sentence_id,
                                  text: sent.text,
                                })
                              }
                              className="text-xs h-8 px-2 shrink-0 text-muted-foreground hover:text-foreground"
                            >
                              <FileEdit className="w-3.5 h-3.5" />
                              <span className="ml-1">{isBangla ? 'সম্পাদনা' : 'Edit'}</span>
                            </Button>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Evidence Checklist */}
          {docAst.preparation_checklist.length > 0 && (
            <Card className="border border-border bg-surface">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-bold text-foreground">
                  {isBangla ? 'দাখিল পূর্ববর্তী চেকলিস্ট' : 'Pre-Filing Verification Checklist'}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2">
                  {docAst.preparation_checklist.map((chk, i) => (
                    <li key={i} className="flex items-center gap-2 text-xs text-muted-foreground">
                      <Check className="w-4 h-4 text-emerald-600 shrink-0" />
                      <span>{chk}</span>
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          )}
        </div>
      )}

      {/* TAB 3: PORTAL FILING COMPANION (T33) */}
      {activeTab === 'portal' && portalMap && (
        <div className="space-y-6">
          {/* Security Disclaimer (T33) */}
          <div className="p-4 rounded-lg border border-border bg-elevated/40 text-xs text-muted-foreground space-y-1">
            <div className="flex items-center gap-2 font-bold text-foreground">
              <ShieldCheck className="w-4 h-4 text-primary" />
              <span>
                {isBangla
                  ? 'স্বয়ংক্রিয় পাসওয়ার্ড বা ক্যাপচা বর্জন নীতি (T33)'
                  : 'Credential-Free Quick-Copy Principle (T33)'}
              </span>
            </div>
            <p className="leading-relaxed">
              {isBangla ? portalMap.disclaimer_bn : portalMap.disclaimer_en}
            </p>
          </div>

          {/* Portal Switcher & Action */}
          <div className="flex flex-wrap items-center justify-between gap-3 p-4 rounded-md border border-border bg-surface">
            <div className="flex items-center gap-3">
              <label className="text-xs font-bold text-foreground">
                {isBangla ? 'লক্ষ্যভুক্ত সরকারি পোর্টাল:' : 'Target Portal:'}
              </label>
              <select
                value={selectedPortal}
                onChange={(e) => setSelectedPortal(e.target.value)}
                className="text-xs font-medium py-1.5 px-3 rounded border border-border bg-surface text-foreground"
              >
                <option value="dncrp_ccms">DNCRP CCMS (ccms.dncrp.com)</option>
                <option value="bb_cipc">Bangladesh Bank CIPC (cms.bb.org.bd)</option>
              </select>
            </div>

            <a
              href={portalMap.official_destination_url}
              target="_blank"
              rel="noreferrer"
              className="inline-flex"
            >
              <Button size="sm" variant="primary" className="text-xs gap-1.5">
                <span>{isBangla ? 'অফিশিয়াল পোর্টাল খুলুন' : 'Open Official Portal in New Tab'}</span>
                <ExternalLink className="w-3.5 h-3.5" />
              </Button>
            </a>
          </div>

          {/* Stale Map Warning if any */}
          {portalMap.is_stale && (
            <div className="p-3 rounded-md bg-amber-50 dark:bg-amber-950/40 border border-amber-300 dark:border-amber-800 text-xs text-amber-900 dark:text-amber-200">
              <p className="font-bold">⚠️ Stale Portal Map Fallback Active</p>
              <p>{portalMap.stale_reason}</p>
            </div>
          )}

          {/* Field Quick-Copy Grid */}
          <div className="space-y-3">
            {portalMap.fields.map((f) => {
              const val = f.prepared_value || (isBangla ? 'তথ্য পাওয়া যায়নি' : 'Value not available');
              const isCopied = copiedKey === f.field_key;

              return (
                <div
                  key={f.field_key}
                  className="p-3.5 rounded-md border border-border bg-surface flex flex-col sm:flex-row sm:items-center justify-between gap-3 hover:border-primary/40 transition-colors"
                >
                  <div className="space-y-1">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">
                      {isBangla ? f.label_bn : f.label_en}
                    </span>
                    <p className="text-xs font-mono font-bold text-foreground break-all">
                      {val}
                    </p>
                    {f.notes && (
                      <p className="text-[11px] text-primary/80 italic">{f.notes}</p>
                    )}
                  </div>

                  <Button
                    size="sm"
                    variant={isCopied ? 'secondary' : 'outline'}
                    onClick={() => handleCopy(f.prepared_value || '', f.field_key)}
                    disabled={!f.prepared_value}
                    className="text-xs gap-1.5 h-8 shrink-0 self-end sm:self-center"
                  >
                    {isCopied ? (
                      <>
                        <Check className="w-3.5 h-3.5 text-emerald-600" />
                        <span className="text-emerald-700 font-bold">
                          {isBangla ? 'কপি হয়েছে!' : 'Copied!'}
                        </span>
                      </>
                    ) : (
                      <>
                        <Copy className="w-3.5 h-3.5" />
                        <span>{isBangla ? 'কপি করুন' : 'Copy'}</span>
                      </>
                    )}
                  </Button>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* TAB 4: OFFICIAL DESTINATIONS (P09.7 & T54) */}
      {activeTab === 'destinations' && (
        <div className="space-y-6">
          <div>
            <h3 className="text-base font-bold text-foreground">
              {isBangla ? 'সরকারি অভিযোগ সেল ও যাচাইকৃত মাধ্যম' : 'Official Complaint Destinations & Verified Channels'}
            </h3>
            <p className="text-xs text-muted-foreground mt-0.5">
              {isBangla
                ? 'সরাসরি লিংক, নিয়মাবলী ও কারিগরি ত্রুটির ক্ষেত্রে বিকল্প যোগাযোগ মাধ্যম (T54)।'
                : 'Direct links, verified procedures, and link-health fallback channels (T54).'}
            </p>
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            {destinations.map((d) => {
              const isHealthy = d.link_health === 'healthy';

              return (
                <Card key={d.destination_id} className="border border-border bg-surface">
                  <CardHeader className="pb-3 flex flex-row items-start justify-between">
                    <div>
                      <CardTitle className="text-sm font-bold text-foreground">
                        {isBangla ? d.title_bn : d.title_en}
                      </CardTitle>
                      <CardDescription className="text-xs mt-0.5 font-medium">
                        {d.authority_name}
                      </CardDescription>
                    </div>
                    <Badge variant={isHealthy ? 'success' : 'warning'}>
                      {isHealthy
                        ? isBangla
                          ? 'সচল পোর্টাল'
                          : 'PORTAL HEALTHY'
                        : isBangla
                        ? 'বিকল্প মাধ্যম প্রযোজ্য'
                        : 'FALLBACK ACTIVE'}
                    </Badge>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="space-y-1.5">
                      <span className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">
                        {isBangla ? 'অভিযোগ দাখিলের পূর্বশর্ত:' : 'Filing Prerequisites:'}
                      </span>
                      <ul className="space-y-1 text-xs text-muted-foreground">
                        {(isBangla ? d.prerequisites_bn : d.prerequisites_en).map((req, i) => (
                          <li key={i} className="flex items-start gap-1.5">
                            <span className="text-primary font-bold">•</span>
                            <span>{req}</span>
                          </li>
                        ))}
                      </ul>
                    </div>

                    {!isHealthy && (
                      <div className="p-2.5 rounded bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800 text-[11px] text-amber-900 dark:text-amber-200 space-y-1">
                        <span className="font-bold flex items-center gap-1">
                          <AlertTriangle className="w-3.5 h-3.5 text-amber-600" />
                          {isBangla ? 'বিকল্প যোগাযোগের নিয়ম:' : 'Official Fallback Route:'}
                        </span>
                        <p>{isBangla ? d.fallback_instructions_bn : d.fallback_instructions_en}</p>
                      </div>
                    )}

                    <div className="pt-2 flex items-center justify-between border-t border-border/60">
                      <a
                        href={d.procedure_guide_url}
                        target="_blank"
                        rel="noreferrer"
                        className="text-xs text-muted-foreground hover:underline"
                      >
                        {isBangla ? 'অফিশিয়াল নির্দেশিকা' : 'Procedure Guide'}
                      </a>

                      <a
                        href={d.official_portal_url}
                        target="_blank"
                        rel="noreferrer"
                        className="inline-flex"
                      >
                        <Button size="sm" variant="primary" className="text-xs gap-1.5">
                          <span>{isBangla ? 'পোর্টাল ভিজিট করুন' : 'Visit Portal'}</span>
                          <ExternalLink className="w-3.5 h-3.5" />
                        </Button>
                      </a>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}

