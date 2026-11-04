import { AgentWorkspace } from '@/features/agent/AgentWorkspace';
export const metadata = { title: 'Ebarki' };
export default async function Page({params}:{params:Promise<{locale:string}>}){const {locale}=await params;return <AgentWorkspace locale={locale} />;}
