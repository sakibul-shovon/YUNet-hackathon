'use client';

import React, { useState } from 'react';
import { Eye, Scan, CheckCircle2, ZoomIn, ZoomOut, Sparkles, Crosshair } from 'lucide-react';

export interface GroundedEntity {
  id: string;
  field: string;
  value: string;
  confidence: number;
  box: { top: number; left: number; width: number; height: number }; // percentage coords (0-100)
}

interface DocumentGroundingCanvasProps {
  documentTitle?: string;
  documentType?: string;
  imageUrl?: string;
  entities?: GroundedEntity[];
  className?: string;
}

const DEFAULT_ENTITIES: GroundedEntity[] = [
  {
    id: 'ent-1',
    field: 'Merchant / Beneficiary',
    value: 'Gadget Palace BD',
    confidence: 98,
    box: { top: 21, left: 11, width: 78, height: 6 },
  },
  {
    id: 'ent-2',
    field: 'Transaction Amount',
    value: 'BDT 3,200.00',
    confidence: 100,
    box: { top: 32, left: 11, width: 78, height: 7 },
  },
  {
    id: 'ent-3',
    field: 'Transaction ID (TrxID)',
    value: 'BL9X882KZP',
    confidence: 99,
    box: { top: 38, left: 11, width: 78, height: 6 },
  },
  {
    id: 'ent-4',
    field: 'Payment Timestamp',
    value: '15 Oct 2026, 04:30 PM',
    confidence: 95,
    box: { top: 43, left: 11, width: 78, height: 6 },
  },
  {
    id: 'ent-5',
    field: 'Status & Settlement',
    value: 'COMPLETED / SETTLED',
    confidence: 100,
    box: { top: 64, left: 11, width: 78, height: 7 },
  },
];

export function DocumentGroundingCanvas({
  documentTitle = 'bKash Transaction Statement — TrxID #BL9X882KZP',
  documentType = 'Mobile Financial Service (MFS) Proof of Payment',
  imageUrl,
  entities = DEFAULT_ENTITIES,
  className = '',
}: DocumentGroundingCanvasProps) {
  const [activeEntityId, setActiveEntityId] = useState<string | null>(null);
  const [showLaserScan, setShowLaserScan] = useState(true);

  return (
    <div
      className={`rounded-2xl border border-border bg-surface overflow-hidden shadow-xs space-y-0 ${className}`}
    >
      {/* Top Controls Header */}
      <div className="px-5 py-3.5 border-b border-border bg-surface flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-emerald-500/10 text-emerald-500 border border-emerald-500/20 flex items-center justify-center shrink-0">
            <Scan className="w-4 h-4 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h4 className="text-xs font-bold text-foreground">{documentTitle}</h4>
              <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">
                100% VLM RECONCILED
              </span>
            </div>
            <p className="text-[11px] text-muted-foreground">{documentType}</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => setShowLaserScan(!showLaserScan)}
            className={`text-[11px] px-2.5 py-1 rounded-lg border transition-colors flex items-center gap-1.5 font-medium ${
              showLaserScan
                ? 'bg-emerald-500/10 text-emerald-500 border-emerald-500/30'
                : 'bg-surface text-muted-foreground border-border hover:bg-elevated'
            }`}
          >
            <Crosshair className="w-3.5 h-3.5" />
            <span>{showLaserScan ? 'Laser Grid ON' : 'Laser Grid OFF'}</span>
          </button>
        </div>
      </div>

      {/* Dual Pane Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 min-h-[380px]">
        {/* Left Pane: Extracted Entities List */}
        <div className="lg:col-span-5 p-4 border-b lg:border-b-0 lg:border-r border-border bg-surface space-y-2.5">
          <div className="flex justify-between items-center text-[10px] uppercase font-mono tracking-wider text-muted-foreground pb-1">
            <span>Detected Semantic Tokens</span>
            <span>Confidence</span>
          </div>

          <div className="space-y-2">
            {entities.map((ent) => {
              const isHovered = activeEntityId === ent.id;
              return (
                <div
                  key={ent.id}
                  onMouseEnter={() => setActiveEntityId(ent.id)}
                  onMouseLeave={() => setActiveEntityId(null)}
                  className={`p-2.5 rounded-xl border transition-all cursor-pointer ${
                    isHovered
                      ? 'border-emerald-500 bg-emerald-500/10 shadow-xs'
                      : 'border-border/70 bg-surface/60 hover:border-border hover:bg-elevated/40'
                  }`}
                >
                  <div className="flex justify-between items-center text-xs">
                    <span className="font-semibold text-foreground truncate">{ent.field}</span>
                    <span className="font-mono text-[10px] font-bold text-emerald-600 dark:text-emerald-400">
                      {ent.confidence}%
                    </span>
                  </div>
                  <div className="text-xs font-mono font-bold text-primary mt-0.5 truncate">
                    {ent.value}
                  </div>
                </div>
              );
            })}
          </div>

          <p className="text-[10px] text-muted-foreground pt-1 italic text-center">
            ✦ Hover over any entity to spotlight exact bounding coordinates on document
          </p>
        </div>

        {/* Right Pane: Document Canvas with Interactive Overlays */}
        <div className="lg:col-span-7 p-6 bg-slate-950/20 dark:bg-slate-950/60 flex items-center justify-center relative overflow-hidden select-none">
          {/* Simulated Document Canvas Container */}
          <div className="relative w-full max-w-[340px] aspect-[1/1.35] bg-white text-slate-900 rounded-xl shadow-lg border border-slate-300/80 p-4 font-sans text-[11px] overflow-hidden">
            {/* Document Header */}
            <div className="bg-[#e2136e] -m-4 mb-3 p-3 text-white flex justify-between items-center">
              <span className="font-bold tracking-tight text-xs">bKash Statement</span>
              <span className="text-[9px] bg-white/20 px-1.5 py-0.5 rounded font-mono font-bold">
                SETTLED
              </span>
            </div>

            {/* Document Body Lines */}
            <div className="space-y-2.5 pt-1 text-slate-800">
              <div className="text-[9px] uppercase tracking-wider text-slate-500 font-bold">
                Transaction Details
              </div>

              <div className="space-y-2 text-[10.5px]">
                <div>
                  <span className="text-slate-500 block text-[9.5px]">Merchant:</span>
                  <span className="font-bold text-slate-900">Gadget Palace BD</span>
                </div>
                <div>
                  <span className="text-slate-500 block text-[9.5px]">Amount Paid:</span>
                  <span className="font-bold text-[#e2136e] text-xs">BDT 3,200.00</span>
                </div>
                <div>
                  <span className="text-slate-500 block text-[9.5px]">TrxID:</span>
                  <span className="font-mono font-bold text-slate-900">BL9X882KZP</span>
                </div>
                <div>
                  <span className="text-slate-500 block text-[9.5px]">Date & Time:</span>
                  <span className="text-slate-700">15 Oct 2026, 04:30 PM</span>
                </div>
                <div>
                  <span className="text-slate-500 block text-[9.5px]">Status:</span>
                  <span className="font-bold text-emerald-700">COMPLETED / SETTLED</span>
                </div>
              </div>
            </div>

            {/* Interactive Bounding Box Overlays */}
            {entities.map((ent) => {
              const isHovered = activeEntityId === ent.id;
              return (
                <div
                  key={ent.id}
                  style={{
                    top: `${ent.box.top}%`,
                    left: `${ent.box.left}%`,
                    width: `${ent.box.width}%`,
                    height: `${ent.box.height}%`,
                  }}
                  onMouseEnter={() => setActiveEntityId(ent.id)}
                  onMouseLeave={() => setActiveEntityId(null)}
                  className={`absolute rounded transition-all pointer-events-auto cursor-pointer ${
                    isHovered
                      ? 'ring-2 ring-emerald-500 bg-emerald-500/20 shadow-sm'
                      : showLaserScan
                      ? 'ring-1 ring-emerald-500/40 bg-emerald-500/[0.04]'
                      : 'opacity-0'
                  }`}
                >
                  {isHovered && (
                    <div className="absolute -top-5 left-0 bg-slate-900 text-emerald-400 text-[9px] font-mono font-bold px-1.5 py-0.5 rounded shadow pointer-events-none whitespace-nowrap z-20">
                      ✦ {ent.field}: {ent.confidence}% match
                    </div>
                  )}
                </div>
              );
            })}

            {/* Watermark */}
            <div className="absolute bottom-2 right-3 text-[8.5px] font-mono text-slate-400">
              Verified by ClaimCraft BD VLM
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

