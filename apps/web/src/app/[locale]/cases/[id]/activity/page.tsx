import { CaseActivity } from '@/features/workspace/Activity';
export const metadata = { title: 'Ebarki' };
export default async function Page({params}:{params:Promise<{locale:string}>}){const {locale}=await params;return <CaseActivity locale={locale} />;}
