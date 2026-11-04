import { Access } from '@/features/agent/Access';
export const metadata={title:'Ebarki'};
export default async function Page({params}:{params:Promise<{locale:string}>}){const {locale}=await params;return <Access locale={locale} register />;}
