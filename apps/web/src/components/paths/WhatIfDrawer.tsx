'use client';

import React, { useState } from 'react';
import { X, Sparkles, Check, AlertTriangle, ArrowRight, ShieldAlert } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { apiFetch } from '@/lib/api';

interface RouteDiffItem {
  route_id: string;
  issue_type: string;
  baseline_status: string;
  simulated_status: string;
  changed: boolean;
}

interface WhatIfSimulationResult {
  case_id: string;
  overrides: Record<string, unknown>;
  route_diff: RouteDiffItem[];
  is_material_change: boolean;
  summary_en: string;
  summary_bn: string;
}

interface WhatIfDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  caseId: string;
  locale: string;
  onApplied: () => void;
}

export function WhatIfDrawer({
  isOpen,
  onClose,
  caseId,
  locale,
  onApplied,
}: WhatIfDrawerProps) {
  const isBangla = locale === 'bn';

  // State for overrides
  const [goodsDelivered, setGoodsDelivered] = useState<boolean | null>(null);
  const [providerTicketFiled, setProviderTicketFiled] = useState<boolean | null>(null);
  const [goodsReceivedDefective, setGoodsReceivedDefective] = useState<boolean | null>(null);
  const [productHazard, setProductHazard] = useState<boolean | null>(null);

  const [loading, setLoading] = useState(false);
  const [simResult, setSimResult] = useState<WhatIfSimulationResult | null>(null);
  const [applyLoading, setApplyLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSimulate = async () => {
    setLoading(true);
    setErrorMsg(null);
    try {
      const overrides: Record<string, unknown> = {};
      if (goodsDelivered !== null) overrides.goods_delivered = goodsDelivered;
      if (providerTicketFiled !== null) overrides.provider_ticket_filed = providerTicketFiled;
      if (goodsReceivedDefective !== null) overrides.goods_received_defective = goodsReceivedDefective;
      if (productHazard !== null) overrides.product_presents_immediate_hazard = productHazard;

      const res = await apiFetch(`/api/v1/cases/${caseId}/what-if`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ overrides }),
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || 'Failed to simulate what-if scenario.');
      }

      const data = await res.json();
      setSimResult(data);
    } catch (err: unknown) {
      setErrorMsg(err instanceof Error ? err.message : 'Simulation failed');
    } finally {
      setLoading(false);
    }
  };

  const handleApply = async () => {
    if (!simResult) return;
    setApplyLoading(true);
    setErrorMsg(null);
    try {
      const res = await apiFetch(`/api/v1/cases/${caseId}/what-if/apply`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ overrides: simResult.overrides }),
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || 'Failed to apply what-if facts.');
      }

      onApplied();
      onClose();
    } catch (err: unknown) {
      setErrorMsg(err instanceof Error ? err.message : 'Apply failed');
    } finally {
      setApplyLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-end bg-black/60 backdrop-blur-xs">
      <div className="w-full max-w-xl h-full bg-background border-l border-border p-6 overflow-y-auto flex flex-col justify-between shadow-2xl">
        <div className="space-y-6">
          {/* Header */}
          <div className="flex items-center justify-between pb-4 border-b border-border">
            <div className="flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-primary" />
              <h3 className="text-lg font-bold text-foreground">
                {isBangla ? 'পরিস্থিতি সিমুলেশন (What-If)' : 'What-If Procedural Simulator'}
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
              ? 'আইনি পথের ওপর নতুন তথ্যের প্রভাব দেখুন। এই সিমুলেশন ডেটাবেসে কোনো স্থায়ী পরিবর্তন ঘটায় না (T31)।'
              : 'Test how hypothetical fact changes alter statutory eligibility without modifying your saved case memory (T31).'}
          </p>

          {/* Fact toggles */}
          <div className="space-y-4">
            <div className="p-3 rounded-lg border border-border bg-surface space-y-2">
              <label className="text-xs font-semibold text-foreground block">
                {isBangla ? 'পণ্য সরবরাহ করা হয়েছে কি?' : 'Were goods physically delivered?'}
              </label>
              <div className="flex items-center gap-2">
                <Button
                  size="sm"
                  variant={goodsDelivered === true ? 'primary' : 'outline'}
                  onClick={() => setGoodsDelivered(goodsDelivered === true ? null : true)}
                >
                  {isBangla ? 'হ্যাঁ (Yes)' : 'Yes'}
                </Button>
                <Button
                  size="sm"
                  variant={goodsDelivered === false ? 'primary' : 'outline'}
                  onClick={() => setGoodsDelivered(goodsDelivered === false ? null : false)}
                >
                  {isBangla ? 'না (No)' : 'No'}
                </Button>
              </div>
            </div>

            <div className="p-3 rounded-lg border border-border bg-surface space-y-2">
              <label className="text-xs font-semibold text-foreground block">
                {isBangla ? 'প্রোভাইডারে ফরমাল টিকিট দাখিল করা হয়েছে?' : 'Has a formal provider ticket been filed?'}
              </label>
              <div className="flex items-center gap-2">
                <Button
                  size="sm"
                  variant={providerTicketFiled === true ? 'primary' : 'outline'}
                  onClick={() => setProviderTicketFiled(providerTicketFiled === true ? null : true)}
                >
                  {isBangla ? 'হ্যাঁ (Yes)' : 'Yes'}
                </Button>
                <Button
                  size="sm"
                  variant={providerTicketFiled === false ? 'primary' : 'outline'}
                  onClick={() => setProviderTicketFiled(providerTicketFiled === false ? null : false)}
                >
                  {isBangla ? 'না (No)' : 'No'}
                </Button>
              </div>
            </div>

            <div className="p-3 rounded-lg border border-border bg-surface space-y-2">
              <label className="text-xs font-semibold text-foreground block">
                {isBangla ? 'পণ্যটি কি ত্রুটিপূর্ণ/ভাঙা ছিল?' : 'Were goods received damaged or defective?'}
              </label>
              <div className="flex items-center gap-2">
                <Button
                  size="sm"
                  variant={goodsReceivedDefective === true ? 'primary' : 'outline'}
                  onClick={() => setGoodsReceivedDefective(goodsReceivedDefective === true ? null : true)}
                >
                  {isBangla ? 'হ্যাঁ (Yes)' : 'Yes'}
                </Button>
                <Button
                  size="sm"
                  variant={goodsReceivedDefective === false ? 'primary' : 'outline'}
                  onClick={() => setGoodsReceivedDefective(goodsReceivedDefective === false ? null : false)}
                >
                  {isBangla ? 'না (No)' : 'No'}
                </Button>
              </div>
            </div>

            <div className="p-3 rounded-lg border border-border bg-surface space-y-2">
              <label className="text-xs font-semibold text-foreground block">
                {isBangla ? 'পণ্যটি কি মারাত্মক শারীরিক বিপদ সৃষ্টি করেছে?' : 'Does product pose an immediate physical hazard?'}
              </label>
              <div className="flex items-center gap-2">
                <Button
                  size="sm"
                  variant={productHazard === true ? 'danger' : 'outline'}
                  onClick={() => setProductHazard(productHazard === true ? null : true)}
                >
                  {isBangla ? 'হ্যাঁ (ঝুঁকিপূর্ণ)' : 'Yes (Hazardous)'}
                </Button>
                <Button
                  size="sm"
                  variant={productHazard === false ? 'primary' : 'outline'}
                  onClick={() => setProductHazard(productHazard === false ? null : false)}
                >
                  {isBangla ? 'না (ঝুঁকি নেই)' : 'No'}
                </Button>
              </div>
            </div>

            {/* Strict T32 Safety Prohibition Card */}
            <div className="p-3 rounded-lg bg-[var(--brand-soft)] border border-primary/20 flex items-start gap-2 text-xs">
              <ShieldAlert className="w-4 h-4 text-primary shrink-0 mt-0.5" />
              <div className="text-muted-foreground leading-normal">
                {isBangla
                  ? 'নিরাপত্তা নীতি (T32): ClaimCraft BD কখনোই OTP, PIN বা পাসওয়ার্ড চায় না বা সংরক্ষণ করে না।'
                  : 'Security Invariant (T32): ClaimCraft BD never collects or stores OTP, PIN, CVV, or passwords.'}
              </div>
            </div>
          </div>

          {errorMsg && (
            <div className="p-3 rounded-lg bg-[var(--danger-soft)] text-[var(--danger-ink)] text-xs flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 shrink-0" />
              <span>{errorMsg}</span>
            </div>
          )}

          <Button
            className="w-full gap-2"
            disabled={loading}
            onClick={handleSimulate}
          >
            <Sparkles className="w-4 h-4" />
            <span>{loading ? (isBangla ? 'সিমুলেশন চলছে...' : 'Simulating...') : (isBangla ? 'সিমুলেশন চালান' : 'Run Simulation')}</span>
          </Button>

          {/* Results Diff */}
          {simResult && (
            <div className="p-4 rounded-xl border border-primary/40 bg-surface/80 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-foreground">
                  {isBangla ? 'সিমুলেশন ফলাফল:' : 'Simulation Outcome:'}
                </span>
                <Badge variant={simResult.is_material_change ? 'brand' : 'neutral'}>
                  {simResult.is_material_change
                    ? (isBangla ? 'গুরুত্বপূর্ণ পরিবর্তন' : 'Material Change')
                    : (isBangla ? 'কোনো পরিবর্তন নেই' : 'No Route Change')}
                </Badge>
              </div>
              <p className="text-xs text-foreground/90 leading-relaxed">
                {isBangla ? simResult.summary_bn : simResult.summary_en}
              </p>

              {/* Diff list */}
              <div className="space-y-1.5 pt-2 border-t border-border/60">
                {simResult.route_diff.map((item) => (
                  <div
                    key={item.route_id}
                    className="flex items-center justify-between text-xs p-2 rounded bg-elevated/40"
                  >
                    <span className="font-mono text-muted-foreground">{item.issue_type}</span>
                    <div className="flex items-center gap-1.5">
                      <span className="text-muted-foreground">{item.baseline_status}</span>
                      <ArrowRight className="w-3 h-3 text-primary" />
                      <span className={item.changed ? 'font-bold text-primary' : 'text-muted-foreground'}>
                        {item.simulated_status}
                      </span>
                    </div>
                  </div>
                ))}
              </div>

              {simResult.is_material_change && (
                <Button
                  variant="primary"
                  size="sm"
                  className="w-full gap-2 mt-3"
                  disabled={applyLoading}
                  onClick={handleApply}
                >
                  <Check className="w-4 h-4" />
                  <span>
                    {applyLoading
                      ? (isBangla ? 'প্রয়োগ করা হচ্ছে...' : 'Applying...')
                      : (isBangla ? 'এই তথ্য কেসে প্রয়োগ করুন' : 'Apply These Facts to Case')}
                  </span>
                </Button>
              )}
            </div>
          )}
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
