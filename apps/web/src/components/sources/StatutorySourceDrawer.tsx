'use client';

import { useState } from 'react';
import { SourceDrawer } from '@/features/workspace/Sources';
import { useResource } from '@/features/workspace/data';
import { Button, ErrorPanel, Field, Loading, Notice, words } from '@/features/workspace/ui';

type ReferenceNode = { citation_handle: string; title_en: string; title_bn: string; children: ReferenceNode[] };
function flatten(nodes: ReferenceNode[]): ReferenceNode[] { return nodes.flatMap(node => [node, ...flatten(node.children || [])]); }

export function StatutorySourceDrawer({ locale = 'en' }: { locale?: string }) {
  const library = useResource<ReferenceNode[]>('retrieval/sources/bd_crpa_2009/provisions');
  const [search, setSearch] = useState('');
  const [citation, setCitation] = useState<string | null>(null);
  const references = flatten(library.data || []).filter(item => `${item.citation_handle} ${item.title_en} ${item.title_bn}`.toLowerCase().includes(search.toLowerCase()));
  return <div className="ui-form-stack">
    <Notice>{words(locale, 'Ebarki references link to the primary text. English wording is an unofficial summary. Check conditions and applicability before use.', 'Ebarki-র সূত্র থেকে মূল লেখা খুলতে পারবেন। English লেখা অনানুষ্ঠানিক সারাংশ। ব্যবহারের আগে শর্ত ও প্রযোজ্যতা মিলিয়ে নিন।')}</Notice>
    <Field label={words(locale, 'Find a reference', 'সূত্র খুঁজুন')}><input value={search} onChange={event => setSearch(event.target.value)} placeholder={words(locale, 'Section or title', 'ধারা বা শিরোনাম')} /></Field>
    {library.loading && <Loading locale={locale} />}
    {library.error && <ErrorPanel locale={locale} retry={library.reload} />}
    {references.map(item => <Button key={item.citation_handle} tone="secondary" onClick={() => setCitation(item.citation_handle)}>{words(locale, item.title_en, item.title_bn)} <code>{item.citation_handle}</code></Button>)}
    <SourceDrawer source={null} citation={citation} locale={locale} onClose={() => setCitation(null)} />
  </div>;
}
