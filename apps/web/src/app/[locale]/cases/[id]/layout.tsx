import type { ReactNode } from 'react';
import { CaseShell } from '@/features/workspace/CaseShell';
export default async function Layout({children,params}:{children:ReactNode;params:Promise<{locale:string;id:string}>}){const {locale,id}=await params;return <CaseShell locale={locale} caseId={id}>{children}</CaseShell>;}
