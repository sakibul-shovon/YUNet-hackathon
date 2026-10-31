import { getTranslations } from 'next-intl/server';
import Link from 'next/link';
import { ArrowLeft, Cpu, Database, Scale, Code2, Shield, Layers } from 'lucide-react';
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

          <Card>
            <CardHeader className="flex flex-row items-center gap-3">
              <Database className="w-5 h-5 text-primary" />
              <CardTitle className="text-base font-bold">
                {isBangla ? 'হাইব্রিড রিট্রিভাল (Dense E5 + Lexical BM25s)' : 'Hybrid Retrieval Pipeline'}
              </CardTitle>
            </CardHeader>
            <CardContent className="text-xs text-muted-foreground space-y-2 leading-relaxed">
              <p>
                To avoid hallucinated legal advice, legal section retrieval uses Reciprocal Rank Fusion (RRF, k=60) combining local multilingual E5 embeddings (384-dimension) and Bengali-tokenized BM25s lexical index over verified release manifests.
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center gap-3">
              <Code2 className="w-5 h-5 text-primary" />
              <CardTitle className="text-base font-bold">
                {isBangla ? 'প্রযুক্তি স্ট্যাক ও ডিপেন্ডেন্সি' : 'Engineered Tech Stack'}
              </CardTitle>
            </CardHeader>
            <CardContent className="text-xs text-muted-foreground space-y-2 leading-relaxed">
              <div className="grid grid-cols-2 gap-4 pt-1 font-mono text-[11px]">
                <div>• Next.js 15 (App Router, strict TS)</div>
                <div>• FastAPI 0.162 (Modular Python 3.12+)</div>
                <div>• PostgreSQL + pgvector</div>
                <div>• Pydantic v2 & SQLAlchemy 2</div>
                <div>• Tailwind CSS 3.4 & next-intl</div>
                <div>• Google Gemini 3.8 Flash SDK</div>
              </div>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
}

