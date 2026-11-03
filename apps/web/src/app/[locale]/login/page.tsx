import { AuthPage } from '@/features/workspace/Account';
export const metadata={title:'Ebarki'};
export default async function Page({params}:{params:Promise<{locale:string}>}){const {locale}=await params;return <AuthPage locale={locale} />;}
