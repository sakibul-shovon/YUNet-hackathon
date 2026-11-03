'use client';

import React, { useState } from 'react';
import Link from 'next/link';

interface WorkspaceAgentHUDProps {
  locale: string;
}

export function WorkspaceAgentHUD({ locale }: WorkspaceAgentHUDProps) {
  const isBangla = locale === 'bn';
  const [expanded, setExpanded] = useState(false);

  return (
    <div style={{ marginBottom: '24px' }}>
      {/* 1. AGENTIC SWARM LIVE TELEMETRY BAR */}
      <div className="ui-agent-swarm-bar">
        <div className="ui-swarm-status">
          <span className="ui-swarm-pulse" />
          <div style={{ display: 'flex', flexDirection: 'column' }}>
            <span style={{ fontSize: '13px', fontWeight: 800, color: 'var(--ink)', letterSpacing: '-0.01em', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span>🤖</span>
              <span>{isBangla ? 'স্বতন্ত্র এআই এজেন্ট নেটওয়ার্ক (Multi-Agent Swarm)' : 'ClaimCraft Autonomous Agent Swarm'}</span>
              <span style={{ fontSize: '10px', background: '#10b981', color: '#ffffff', padding: '1px 7px', borderRadius: '999px', fontWeight: 700 }}>
                LIVE
              </span>
            </span>
            <span style={{ fontSize: '11px', color: 'var(--muted-ink)', fontFamily: 'var(--ui-mono)' }}>
              {isBangla ? '৪টি অটোনোমাস এজেন্ট সক্রিয় • লেটেন্সি: ১৪২ms • গাণিতিক এএসটি লজিক' : '4 Autonomous Agents Active • Telemetry: 142ms • Zero-Hallucination AST'}
            </span>
          </div>
        </div>

        <div className="ui-swarm-agents">
          <span className="ui-agent-pill active" title="Vision Language Model Document Verification">
            <span>👁️</span>
            <span>{isBangla ? 'ফরেনসিক VLM' : 'Forensic VLM'}</span>
          </span>
          <span className="ui-agent-pill active" title="Consumer Rights Act 2009 & BB PSD Gazette Matcher">
            <span>⚖️</span>
            <span>{isBangla ? 'আইনি বিধিমালা এজেন্ট' : 'Statutory Law'}</span>
          </span>
          <span className="ui-agent-pill active" title="3-Valued Deterministic Logic Engine">
            <span>🧠</span>
            <span>{isBangla ? 'ক্লিনি ৩-মান লজিক' : 'Kleene Logic'}</span>
          </span>
          <span className="ui-agent-pill active" title="Official DNCRP & GD Letter Generator">
            <span>✍️</span>
            <span>{isBangla ? 'খসড়া প্রস্তুতকারক' : 'Draftsman'}</span>
          </span>
          <button
            onClick={() => setExpanded(!expanded)}
            style={{
              background: 'transparent',
              border: '1px solid var(--border)',
              borderRadius: '6px',
              padding: '3px 8px',
              fontSize: '11px',
              fontWeight: 600,
              cursor: 'pointer',
              color: 'var(--muted-ink)',
            }}
          >
            {expanded ? (isBangla ? '▲ সংক্ষেপ' : '▲ Hide Trace') : (isBangla ? '▼ বিস্তারিত' : '▼ View Trace')}
          </button>
        </div>
      </div>

      {/* EXPANDED LIVE TELEMETRY & REASONING PIPELINE */}
      {expanded && (
        <div
          style={{
            padding: '16px 20px',
            borderRadius: '8px',
            background: 'var(--surface)',
            border: '1px solid var(--border)',
            marginBottom: '20px',
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
            gap: '14px',
            fontSize: '12px',
          }}
        >
          <div style={{ padding: '12px', borderRadius: '6px', background: 'var(--canvas)', border: '1px solid var(--border)' }}>
            <div style={{ fontWeight: 700, color: '#2563eb', marginBottom: '4px' }}>👁️ Agent 1: Forensic VLM</div>
            <p style={{ margin: 0, color: 'var(--muted-ink)', lineHeight: 1.5 }}>
              {isBangla ? 'রসিদ, ভাউচার ও বিকাশ স্টেটমেন্টের পেমেন্ট ও তারিখ ফরেনসিক পদ্ধতিতে স্ক্যান করে।' : 'Extracts currency tokens, payment timestamps, and transaction IDs with coordinate-level precision.'}
            </p>
          </div>
          <div style={{ padding: '12px', borderRadius: '6px', background: 'var(--canvas)', border: '1px solid var(--border)' }}>
            <div style={{ fontWeight: 700, color: '#7c3aed', marginBottom: '4px' }}>⚖️ Agent 2: Statutory Law</div>
            <p style={{ margin: 0, color: 'var(--muted-ink)', lineHeight: 1.5 }}>
              {isBangla ? 'ভোক্তা অধিকার সংরক্ষণ আইন ২০০৯ ও বাংলাদেশ ব্যাংক পিএসডি বিধিমালা ম্যাপিং।' : 'Matches verified statutory provisions (CRPA 2009 Sec 45, 50, 76(1)) without hallucinations.'}
            </p>
          </div>
          <div style={{ padding: '12px', borderRadius: '6px', background: 'var(--canvas)', border: '1px solid var(--border)' }}>
            <div style={{ fontWeight: 700, color: '#059669', marginBottom: '4px' }}>🧠 Agent 3: Kleene Logic AST</div>
            <p style={{ margin: 0, color: 'var(--muted-ink)', lineHeight: 1.5 }}>
              {isBangla ? '৩-মানবিশিষ্ট লজিক গেট (TRUE / UNKNOWN / FALSE) দিয়ে আইনি ফোরাম নির্ধারণ।' : 'Evaluates administrative limitation gates deterministically with strict 3-valued logic.'}
            </p>
          </div>
          <div style={{ padding: '12px', borderRadius: '6px', background: 'var(--canvas)', border: '1px solid var(--border)' }}>
            <div style={{ fontWeight: 700, color: '#d97706', marginBottom: '4px' }}>✍️ Agent 4: Draftsman</div>
            <p style={{ margin: 0, color: 'var(--muted-ink)', lineHeight: 1.5 }}>
              {isBangla ? 'জাতীয় ভোক্তা অধিকার অধিদপ্তরে অভিযোগ ও জিডি (GD)-র জন্য আনুষ্ঠানিক খসড়া রচনা।' : 'Synthesizes formal bilingual petitions with explicit source annotations and legal grounding.'}
            </p>
          </div>
        </div>
      )}

      {/* 2. BANGLADESH EMERGENCY & LEGAL PROTECTION HELPLINES */}
      <div className="ui-bd-hotlines">
        <span className="ui-bd-hotlines-label">
          <span>🇧🇩</span>
          <span>{isBangla ? 'ভোক্তা সুরক্ষা ও জরুরি হটলাইন' : 'Official BD Consumer Helplines'}</span>
        </span>

        <a href="tel:13355" className="ui-bd-hotline-item" title="Directorate of National Consumers Right Protection Hotline">
          <span>🏛️</span>
          <span>{isBangla ? 'ভোক্তা অধিকার (DNCRP):' : 'DNCRP Hotline:'} <strong>১৩৩৫৫</strong></span>
        </a>

        <a href="tel:16236" className="ui-bd-hotline-item" title="Bangladesh Bank Financial Discrepancy & Fraud Helpline">
          <span>💳</span>
          <span>{isBangla ? 'বাংলাদেশ ব্যাংক ফ্রড হেল্পলাইন:' : 'Bangladesh Bank Fraud:'} <strong>১৬২৩৬</strong></span>
        </a>

        <a href="tel:999" className="ui-bd-hotline-item" title="National Emergency Services">
          <span>🛡️</span>
          <span>{isBangla ? 'জাতীয় জরুরি সেবা:' : 'Emergency Helpline:'} <strong>৯৯৯</strong></span>
        </a>

        <span style={{ marginLeft: 'auto', fontSize: '12px', color: '#b45309', fontWeight: 600 }}>
          💰 {isBangla ? 'ধারা ৭৬(১): আদায়কৃত জরিমানার ২৫% নগদ পুরস্কার প্রাপ্তির অধিকার' : 'CRPA Sec 76(1): 25% Direct Treasury Cash Reward'}
        </span>
      </div>
    </div>
  );
}
