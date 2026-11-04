import { AgentHome } from '@/features/agent/AgentHome';
export const metadata = { title: 'Ebarki' };
export default async function Page({params}:{params:Promise<{locale:string}>}){const {locale}=await params;return <AgentHome locale={locale} />;}
