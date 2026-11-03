import { InfoPage } from '@/features/workspace/InfoPages';
export const metadata={title:'Ebarki'};
export default async function Page({params}:{params:Promise<{locale:string}>}){const {locale}=await params;return <InfoPage locale={locale} page='limitations' />;}
