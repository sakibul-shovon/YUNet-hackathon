import { Paths } from '@/features/workspace/Paths';
export const metadata = { title: 'Ebarki' };
export default async function Page({params}:{params:Promise<{locale:string}>}){const {locale}=await params;return <Paths locale={locale} />;}
