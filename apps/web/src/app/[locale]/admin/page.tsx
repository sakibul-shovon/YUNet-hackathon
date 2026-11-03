import { AdminConsole } from '@/features/workspace/Admin';
export const metadata={title:'Ebarki'};
export default async function Page({params}:{params:Promise<{locale:string}>}){const {locale}=await params;return <AdminConsole locale={locale} />;}
