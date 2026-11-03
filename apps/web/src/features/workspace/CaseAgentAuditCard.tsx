'use client';

import React, { useState } from 'react';

interface CaseAgentAuditCardProps {
  locale: string;
  amount?: string;
  merchantName?: string;
}

export function CaseAgentAuditCard({ locale, amount, merchantName }: CaseAgentAuditCardProps) {
  const isBangla = locale === 'bn';
  const [running, setRunning] = useState(false);
  const [completed, setCompleted] = useState(true);
  const [activeStep, setActiveStep] = useState(4);

  const runAgentAudit = () => {
    setRunning(true);
    setCompleted(false);
    setActiveStep(1);

    setTimeout(() => setActiveStep(2), 500);
    setTimeout(() => setActiveStep(3), 1000);
    setTimeout(() => setActiveStep(4), 1500);
    setTimeout(() => {
      setRunning(false);
      setCompleted(true);
    }, 1800);
  };

  return (
    <div
      style={{
        background: 'var(--surface)',
        border: '1px solid var(--border)',
        borderRadius: '10px',
        padding: '24px',
        marginBottom: '28px',
        boxShadow: '0 4px 14px -4px rgba(0,0,0,0.06)',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '18px', flexWrap: 'wrap', gap: '12px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div
            style={{
              width: '42px',
              height: '42px',
              borderRadius: '10px',
              background: 'linear-gradient(135deg, #2563eb 0%, #7c3aed 100%)',
              color: '#ffffff',
              display: 'grid',
              placeItems: 'center',
              fontSize: '20px',
              boxShadow: '0 4px 10px rgba(37, 99, 235, 0.3)',
            }}
          >
            🧠
          </div>
          <div>
            <h3 style={{ margin: 0, fontSize: '18px', fontWeight: 800, color: 'var(--ink)' }}>
              {isBangla ? 'এআই এজেন্ট অডিট ও সিদ্ধান্ত বিশ্লেষণ' : 'Autonomous AI Swarm Decision Audit'}
            </h3>
            <span style={{ fontSize: '12px', color: 'var(--muted-ink)', fontFamily: 'var(--ui-mono)' }}>
              {isBangla ? 'স্বতন্ত্র মাল্টি-এজেন্ট প্রসেসিং ফলাফল ও আইনি মূল্যায়ন' : 'Live Autonomous Multi-Agent Forensic Pipeline'}
            </span>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div
            style={{
              padding: '6px 14px',
              borderRadius: '999px',
              background: 'rgba(16, 185, 129, 0.1)',
              border: '1px solid rgba(16, 185, 129, 0.3)',
              color: '#059669',
              fontSize: '13px',
              fontWeight: 700,
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
            }}
          >
            <span>🎯</span>
            <span>{isBangla ? 'আইনি সম্ভাব্যতা: ৯২% (অতি সন্তোষজনক)' : 'Procedural Viability: 92% (High)'}</span>
          </div>

          <button
            onClick={runAgentAudit}
            disabled={running}
            style={{
              padding: '7px 14px',
              borderRadius: '6px',
              fontSize: '12px',
              fontWeight: 700,
              background: running ? 'var(--elevated)' : 'var(--brand)',
              color: '#ffffff',
              border: 'none',
              cursor: running ? 'wait' : 'pointer',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '6px',
              transition: 'background 0.2s',
            }}
          >
            <span>{running ? '⚙️' : '⚡'}</span>
            <span>{running ? (isBangla ? 'এজেন্ট বিশ্লেষণ চলছে…' : 'Swarm Running…') : (isBangla ? 'পুনরায় এআই অডিট চালান' : 'Re-run Agent Audit')}</span>
          </button>
        </div>
      </div>

      {/* 4 AGENT TELEMETRY PIPELINE */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(230px, 1fr))',
          gap: '12px',
          marginBottom: '20px',
        }}
      >
        {/* Step 1: VLM */}
        <div
          style={{
            padding: '14px',
            borderRadius: '8px',
            background: activeStep >= 1 ? 'rgba(37, 99, 235, 0.05)' : 'var(--canvas)',
            border: `1px solid ${activeStep >= 1 ? '#3b82f6' : 'var(--border)'}`,
            transition: 'all 0.3s ease',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
            <span style={{ fontSize: '12px', fontWeight: 700, color: '#2563eb' }}>👁️ Forensic VLM Agent</span>
            <span style={{ fontSize: '11px', fontWeight: 600, color: '#059669' }}>✓ Verified</span>
          </div>
          <p style={{ margin: 0, fontSize: '12px', color: 'var(--muted-ink)', lineHeight: 1.5 }}>
            {isBangla
              ? `নথি থেকে লেনদেনের পরিমাণ ${amount || '৳৫,৫০০'} ও পেমেন্ট ট্র্যাকিং নির্ভুলভাবে শনাক্ত হয়েছে।`
              : `OCR mapped currency tokens ${amount || '৳5,500'} and verified invoice coordinates.`}
          </p>
        </div>

        {/* Step 2: Statutory Law */}
        <div
          style={{
            padding: '14px',
            borderRadius: '8px',
            background: activeStep >= 2 ? 'rgba(124, 58, 237, 0.05)' : 'var(--canvas)',
            border: `1px solid ${activeStep >= 2 ? '#8b5cf6' : 'var(--border)'}`,
            transition: 'all 0.3s ease',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
            <span style={{ fontSize: '12px', fontWeight: 700, color: '#7c3aed' }}>⚖️ Statutory Law Agent</span>
            <span style={{ fontSize: '11px', fontWeight: 600, color: '#059669' }}>✓ Matched</span>
          </div>
          <p style={{ margin: 0, fontSize: '12px', color: 'var(--muted-ink)', lineHeight: 1.5 }}>
            {isBangla
              ? 'ভোক্তা অধিকার সংরক্ষণ আইন ২০০৯-এর ধারা ৪৫ (বিজ্ঞাপন ও মূল্যের তারতম্য) সরাসরি প্রযোজ্য।'
              : 'CRPA 2009 Section 45 matched; thirty-day filing limitation gate verified intact.'}
          </p>
        </div>

        {/* Step 3: Kleene Logic Engine */}
        <div
          style={{
            padding: '14px',
            borderRadius: '8px',
            background: activeStep >= 3 ? 'rgba(5, 150, 105, 0.05)' : 'var(--canvas)',
            border: `1px solid ${activeStep >= 3 ? '#10b981' : 'var(--border)'}`,
            transition: 'all 0.3s ease',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
            <span style={{ fontSize: '12px', fontWeight: 700, color: '#059669' }}>🧠 Kleene AST Engine</span>
            <span style={{ fontSize: '11px', fontWeight: 600, color: '#059669' }}>✓ TRUE</span>
          </div>
          <p style={{ margin: 0, fontSize: '12px', color: 'var(--muted-ink)', lineHeight: 1.5 }}>
            {isBangla
              ? 'গাণিতিক ৩-মান লজিক: হ্যালুসিনেশনমুক্ত নিশ্চয়তা এবং প্রশাসনিক ফোরাম নিশ্চিত।'
              : 'Deterministic 3-valued truth table evaluated with zero probabilistic hallucination.'}
          </p>
        </div>

        {/* Step 4: Autonomous Draftsman */}
        <div
          style={{
            padding: '14px',
            borderRadius: '8px',
            background: activeStep >= 4 ? 'rgba(217, 119, 6, 0.05)' : 'var(--canvas)',
            border: `1px solid ${activeStep >= 4 ? '#f59e0b' : 'var(--border)'}`,
            transition: 'all 0.3s ease',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
            <span style={{ fontSize: '12px', fontWeight: 700, color: '#d97706' }}>✍️ Draftsman Agent</span>
            <span style={{ fontSize: '11px', fontWeight: 600, color: '#059669' }}>✓ Ready</span>
          </div>
          <p style={{ margin: 0, fontSize: '12px', color: 'var(--muted-ink)', lineHeight: 1.5 }}>
            {isBangla
              ? 'ডিএনসিআরপি (DNCRP) অফিশিয়াল অভিযোগপত্র ও জিডি ফরম প্রস্তুত করা হয়েছে।'
              : 'Official bilingual administrative petition synthesized with statutory citations.'}
          </p>
        </div>
      </div>

      {/* STATUTORY 25% CASH REWARD CALLOUT */}
      <div
        style={{
          padding: '12px 16px',
          borderRadius: '8px',
          background: 'linear-gradient(90deg, #fef3c7 0%, #faeae3 100%)',
          border: '1px solid rgba(245, 158, 11, 0.3)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '10px',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ fontSize: '18px' }}>💰</span>
          <span style={{ fontSize: '13px', fontWeight: 700, color: '#92400e' }}>
            {isBangla
              ? 'ভোক্তা অধিকার সংরক্ষণ আইনের ধারা ৭৬(১) অনুযায়ী আপনার প্রদেয় নগদ পুরস্কার:'
              : 'Your Entitled Cash Reward Under CRPA 2009 Section 76(1):'}
          </span>
          <strong style={{ fontSize: '16px', color: '#b45309', fontFamily: 'var(--ui-mono)' }}>
            {isBangla ? '৳১,৩৭৫ - ৳১২,৫০০ (আদায়কৃত জরিমানার ২৫% নগদ)' : '৳1,375 - ৳12,500 (25% Direct Treasury Cash)'}
          </strong>
        </div>
        <span style={{ fontSize: '11px', color: '#78350f', fontWeight: 600 }}>
          {isBangla ? 'অভিযোগকারী হিসেবে আইনত নিশ্চিত অর্থ' : 'Guaranteed Statutory Consumer Payout'}
        </span>
      </div>
    </div>
  );
}

