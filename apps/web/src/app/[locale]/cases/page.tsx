import { CaseDashboard } from '@/features/workspace/Cases';
export const metadata = { title: 'Ebarki' };
export default async function Page({params}:{params:Promise<{locale:string}>}){const {locale}=await params;return <CaseDashboard locale={locale} />;}
