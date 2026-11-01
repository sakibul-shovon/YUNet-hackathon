'use client';

import React, { useState, useEffect } from 'react';
import { X, Cpu, CheckCircle2, AlertCircle, Clock, Database, Layers } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';

interface PipelineStageReceipt {
  stage_name: string;
  status: string;
  provider: string;
  model_or_algorithm: string;
  duration_ms: number | null;
  details: Record<string, unknown>;
}

interface PipelineRun {
  pipeline_id: string;
  case_id: string;
  executed_at: string;
  overall_status: string;
  stages: PipelineStageReceipt[];
  technology_inventory: Record<string, string>;
}

interface ProcessingDetailsDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  caseId: string;
  locale: string;
}

export function ProcessingDetailsDrawer({
  isOpen,
  onClose,
  caseId,
  locale,
}: ProcessingDetailsDrawerProps) {
  const isBangla = locale === 'bn';
  const [loading, setLoading] = useState(false);
  const [runs, setRuns] = useState<PipelineRun[]>([]);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  useEffect(() => {
    if (!isOpen) return;
    setLoading(true);
    fetch(`/api/v1/cases/${caseId}/pipeline-runs`)
      .then((res) => {
        if (!res.ok) throw new Error('Failed to fetch pipeline runs');
        return res.json();
      })
      .then((data) => setRuns(data))
      .catch((err) => setErrorMsg(err.message))
      .finally(() => setLoading(false));
  }, [isOpen, caseId]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-end bg-black/60 backdrop-blur-xs">
      <div className="w-full max-w-2xl h-full bg-background border-l border-border p-6 overflow-y-auto flex flex-col justify-between shadow-2xl">
        <div className="space-y-6">
          {/* Header */}
          <div className="flex items-center justify-between pb-4 border-b border-border">
            <div className="flex items-center gap-2">
              <Cpu className="w-5 h-5 text-primary" />
              <h3 className="text-lg font-bold text-foreground">
                {isBangla ? 'প্রসেসিং বিবরণ ও বাস্তবায়ন প্রমাণ' : 'Processing Details & Execution Receipts'}
              </h3>
            </div>
            <button
              onClick={onClose}
              className="p-1 rounded-md text-muted-foreground hover:text-foreground hover:bg-elevated transition"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          <p className="text-xs text-muted-foreground leading-relaxed">
            {isBangla
              ? 'বাস্তব সার্ভিস রান, মডেল ভার্সন এবং রুল ইভালুয়েশন রসিদ। কোনো ভুয়ো মেট্রিক বা কৃত্রিম ফলাফল দেখানো হয় না (T53)।'
              : 'Durable execution receipts showing verified providers, model versions, and deterministic policy AST evaluations (T53).'}
          </p>

          {loading && (
            <div className="p-8 text-center text-xs text-muted-foreground animate-pulse">
              {isBangla ? 'রসিদ লোড হচ্ছে...' : 'Loading execution receipts...'}
            </div>
          )}

          {errorMsg && (
            <div className="p-3 rounded-lg bg-[var(--danger-soft)] text-[var(--danger-ink)] text-xs flex items-center gap-2">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{errorMsg}</span>
            </div>
          )}

          {runs.map((run) => (
            <div key={run.pipeline_id} className="space-y-6">
              {/* Stages List */}
              <div className="space-y-3">
                <h4 className="text-xs font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-1.5">
                  <Layers className="w-4 h-4 text-primary" />
                  <span>{isBangla ? 'পাইপলাইন ধাপসমূহ' : 'Pipeline Stages'}</span>
                </h4>
                <div className="space-y-2">
                  {run.stages.map((stage) => (
                    <div
                      key={stage.stage_name}
                      className="p-3 rounded-lg border border-border bg-surface flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs"
                    >
                      <div className="space-y-0.5">
                        <div className="flex items-center gap-2">
                          <span className="font-bold text-foreground font-mono">{stage.stage_name}</span>
                          <Badge
                            variant={
                              stage.status === 'completed'
                                ? 'brand'
                                : stage.status === 'not_applicable'
                                ? 'neutral'
                                : 'warning'
                            }
                          >
                            {stage.status}
                          </Badge>
                        </div>
                        <div className="text-muted-foreground font-mono text-[11px]">
                          {stage.provider} &bull; {stage.model_or_algorithm}
                        </div>
                      </div>
                      {stage.duration_ms !== null && (
                        <div className="flex items-center gap-1 text-muted-foreground font-mono text-[11px] shrink-0">
                          <Clock className="w-3.5 h-3.5" />
                          <span>{stage.duration_ms} ms</span>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>

              {/* Technology Stack Inventory */}
              <div className="space-y-3 pt-2">
                <h4 className="text-xs font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-1.5">
                  <Database className="w-4 h-4 text-primary" />
                  <span>{isBangla ? 'প্রযুক্তি ইনভেন্টরি' : 'Technology Inventory'}</span>
                </h4>
                <div className="p-4 rounded-xl border border-border bg-elevated/40 space-y-2 text-xs">
                  {Object.entries(run.technology_inventory).map(([k, v]) => (
                    <div key={k} className="flex flex-col sm:flex-row sm:justify-between py-1 border-b border-border/40 last:border-0 gap-1">
                      <span className="text-muted-foreground font-mono capitalize">{k.replace(/_/g, ' ')}:</span>
                      <span className="font-medium text-foreground text-right">{v}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Footer */}
        <div className="pt-4 border-t border-border flex justify-end">
          <Button variant="outline" size="sm" onClick={onClose}>
            {isBangla ? 'বন্ধ করুন' : 'Close'}
          </Button>
        </div>
      </div>
    </div>
  );
}
