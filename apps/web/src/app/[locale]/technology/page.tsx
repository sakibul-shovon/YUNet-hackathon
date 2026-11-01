import { getTranslations } from 'next-intl/server';
import Link from 'next/link';
import { ArrowLeft, Cpu, Database, Scale, Code2, Shield, Layers, Sparkles, ShieldCheck } from 'lucide-react';
import { Header } from '@/components/layout/Header';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';

export default async function TechnologyPage({ params }: { params: Promise<{ locale: string }> }) {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: 'landing' });
  const tNav = await getTranslations({ locale, namespace: 'nav' });

  const isBangla = locale === 'bn';

  return (
    <div className="min-h-screen flex flex-col bg-canvas text-foreground">
      <Header
        locale={locale}
        labels={{
          home: tNav('home'),
          scenarios: tNav('scenarios'),
          cases: tNav('overview'),
          startCase: t('start_cta'),
        }}
      />

      <main className="flex-1 max-w-4xl mx-auto px-4 md:px-8 py-12 w-full">
        <Link
          href={`/${locale}`}
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-muted-foreground hover:text-foreground mb-6"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>{isBangla ? 'হোমে ফিরে যান' : 'Back to home'}</span>
        </Link>

        <Badge variant="brand" className="mb-3">
          Architecture & Engineering Manifest
        </Badge>
        <h1 className="text-3xl md:text-4xl font-extrabold tracking-tight mb-4">
          {isBangla ? 'প্রযুক্তিগত কাঠামো ও বাস্তবায়ন' : 'Under the Hood: System Architecture'}
        </h1>
        <p className="text-muted-foreground text-base mb-10 leading-relaxed">
          {isBangla
            ? 'ক্লেইমক্রাফট বিডি কীভাবে জেনারেটিভ এআই এবং ডিটারমিনিস্টিক পলিসি নিয়মের সমন্বয় করে নির্ভুল ফলাফল প্রদান করে।'
            : 'How ClaimCraft BD bridges probabilistic generative models with deterministic, statutory rule execution.'}
        </p>

        <div className="space-y-6">
          {/* 1. Three Knowledge Planes */}
          <Card>
            <CardHeader className="flex flex-row items-center gap-3">
              <Layers className="w-5 h-5 text-primary" />
              <CardTitle className="text-base font-bold">
                {isBangla ? 'তিনটি জ্ঞানক্ষেত্র (Three Knowledge Planes)' : 'The Three Knowledge Planes'}
              </CardTitle>
            </CardHeader>
            <CardContent className="text-xs text-muted-foreground space-y-3 leading-relaxed">
              <p>
                <strong>1. Official Public Corpus:</strong> Immutable gazettes and regulatory provisions indexed via dense embeddings and lexical snapshots.
              </p>
              <p>
                <strong>2. Decision Knowledge AST:</strong> Reviewed YAML policy packs compiled into typed Abstract Syntax Trees executing three-valued Kleene logic.
              </p>
              <p>
                <strong>3. Private Case Memory:</strong> Encrypted, tenant-scoped storage containing original user attachments, reviewed fact assertions, and draft packages.
              </p>
            </CardContent>
          </Card>

          {/* 2. Kleene 3-Valued Logic */}
          <Card>
            <CardHeader className="flex flex-row items-center gap-3">
              <Scale className="w-5 h-5 text-primary" />
              <CardTitle className="text-base font-bold">
                {isBangla ? 'ক্লিনি ৩-মান যুক্ত পলিসি ইঞ্জিন (Kleene Three-Valued Logic)' : 'Deterministic Kleene 3-Valued Policy Engine'}
              </CardTitle>
            </CardHeader>
            <CardContent className="text-xs text-muted-foreground space-y-2 leading-relaxed">
              <p>
                Unlike generic LLMs that guess legal outcomes, ClaimCraft BD uses a deterministic AST engine with Kleene logic (`TRUE`, `FALSE`, `UNKNOWN`). An unknown fact is never coerced into false; missing facts explicitly trigger targeted Next Best Questions (NBQ) while statutory exclusions instantly block ineligible routes.
              </p>
            </CardContent>
          </Card>

          {/* 3. Ephemeral What-If Simulation */}
          <Card>
            <CardHeader className="flex flex-row items-center gap-3">
              <Sparkles className="w-5 h-5 text-primary" />
              <CardTitle className="text-base font-bold">
                {isBangla ? 'শূন্য পার্শ্বপ্রতিক্রিয়ার পরিস্থিতি সিমুলেশন (What-If Isolation — T31)' : 'Ephemeral What-If Simulation (T31 Invariant)'}
              </CardTitle>
            </CardHeader>
            <CardContent className="text-xs text-muted-foreground space-y-2 leading-relaxed">
              <p>
                Users can simulate hypothetical answers (e.g. "What if the seller claims delivery occurred?", "What if I file a bank ticket first?") entirely in-memory. The simulation has strictly zero database side effects: no rows created, no row version increments, and no persistence until the user explicitly clicks "Apply".
              </p>
            </CardContent>
          </Card>

          {/* 4. Hybrid Retrieval */}
          <Card>
            <CardHeader className="flex flex-row items-center gap-3">
              <Database className="w-5 h-5 text-primary" />
              <CardTitle className="text-base font-bold">
                {isBangla ? 'হাইব্রিড রিট্রিভাল (Dense E5 + Lexical BM25s + Exact Citations)' : 'Hybrid Retrieval Pipeline (T24 & T25)'}
              </CardTitle>
            </CardHeader>
            <CardContent className="text-xs text-muted-foreground space-y-2 leading-relaxed">
              <p>
                To eliminate statutory hallucination, legal section retrieval uses Reciprocal Rank Fusion (RRF, k=60) combining local multilingual E5 embeddings (384-dimension) and Bengali-tokenized BM25s lexical index over verified release manifests, boosted by exact Section ID lookups (`sec:45`, `ধারা ৪৫`, `sec:60`).
              </p>
            </CardContent>
          </Card>

          {/* 5. Safety & Security Invariants */}
          <Card>
            <CardHeader className="flex flex-row items-center gap-3">
              <ShieldCheck className="w-5 h-5 text-primary" />
              <CardTitle className="text-base font-bold">
                {isBangla ? 'নিরাপত্তা ও গোপনীয়তা নীতি (Security Invariants T01 & T32)' : 'Consumer Safety & Data Protection (T01 & T32)'}
              </CardTitle>
            </CardHeader>
            <CardContent className="text-xs text-muted-foreground space-y-2 leading-relaxed">
              <p>
                • <strong>Owner-Scoped Tenant Isolation (T01):</strong> Foreign cases and previews strictly return 404.<br />
                • <strong>Credential Collection Prohibition (T32):</strong> Strictly forbids asking for, collecting, or storing OTP, PIN, passwords, or CVV.<br />
                • <strong>Safety Hazard Priority:</strong> Physical product hazards automatically take absolute priority over any commercial or financial dispute.
              </p>
            </CardContent>
          </Card>

          {/* 6. Tech Stack */}
          <Card>
            <CardHeader className="flex flex-row items-center gap-3">
              <Code2 className="w-5 h-5 text-primary" />
              <CardTitle className="text-base font-bold">
                {isBangla ? 'প্রযুক্তি স্ট্যাক ও ডিপেন্ডেন্সি' : 'Engineered Tech Stack'}
              </CardTitle>
            </CardHeader>
            <CardContent className="text-xs text-muted-foreground space-y-2 leading-relaxed">
              <div className="grid grid-cols-2 gap-4 pt-1 font-mono text-[11px]">
                <div>• Next.js 16 (App Router, Strict TS)</div>
                <div>• FastAPI 0.115+ (Modular Async Python)</div>
                <div>• PostgreSQL + pgvector (Supabase)</div>
                <div>• Pydantic v2 & SQLAlchemy 2</div>
                <div>• Tailwind CSS 4 & next-intl</div>
                <div>• Google Gemini 3.8 Flash SDK</div>
              </div>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
}
