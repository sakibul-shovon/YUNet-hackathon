import React from 'react';
import {AbsoluteFill, Audio, Composition, Img, OffthreadVideo, Sequence, interpolate, registerRoot, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import scenes from './scenes.json';
import cues from './captions/cues.json';
import captureMeta from './qa/capture-manifest.json';
const C={paper:'#f7f5ef',ink:'#1c2b2c',muted:'#61716f',red:'#b73e2b',teal:'#14756d',line:'#dcded6',gold:'#d29b43'};
const easing=(f:number,d=24)=>spring({frame:f,fps:30,config:{damping:24,stiffness:110},durationInFrames:d});
const Mark=({size=100,color=C.red}:{size?:number,color?:string})=><svg width={size} height={size} viewBox="0 0 100 100"><path d="M24 12H65L82 30V88H24Z M65 12V31H82 M37 51H67 M55 39L67 51L55 63" fill="none" stroke={color} strokeWidth="4" strokeLinejoin="round"/></svg>;
function Paper({label,amount,sub,x,y,rotate=0,delay=0}:{label:string,amount:string,sub:string,x:number,y:number,rotate?:number,delay?:number}){
 const f=useCurrentFrame(),p=easing(f-delay);
 return <div style={{position:'absolute',left:x,top:y,width:440,height:510,padding:44,background:'#fff',border:'1px solid '+C.line,boxShadow:'0 36px 80px #192f321c',transform:`translateY(${(1-p)*100}px) rotate(${rotate}deg)`,opacity:p}}>
 <div style={{fontSize:14,letterSpacing:3,color:C.red}}>FICTIONAL DEMONSTRATION</div><div style={{marginTop:32,fontSize:25}}>{label}</div><div style={{height:1,background:C.line,margin:'30px 0'}}/><div style={{fontFamily:'Display',fontWeight:600,fontSize:73,letterSpacing:-3}}>{amount}</div><div style={{fontSize:23,color:C.muted,marginTop:18,lineHeight:1.5}}>{sub}</div><div style={{marginTop:35,height:1,background:C.line}}/><div style={{fontSize:17,color:C.muted,marginTop:25}}>24 OCT 2026 · SAMPLE ELECTRONICS</div>
 </div>
}
function Opening({kind}:{kind:string}){
 const f=useCurrentFrame();const p=easing(f-12,35);
 if(kind==='problem')return <AbsoluteFill>
  <div style={{position:'absolute',left:145,top:150,fontSize:18,letterSpacing:5,color:C.muted}}>ONE EVERYDAY PROBLEM</div>
  <div style={{position:'absolute',left:140,top:250,fontFamily:'Display',fontSize:128,fontWeight:600,letterSpacing:-7,lineHeight:1.05,transform:`translateY(${(1-p)*40}px)`,opacity:p}}>Paid.<br/><span style={{color:C.red}}>Not delivered.</span></div>
  <div style={{position:'absolute',left:150,top:625,width:600,fontSize:30,color:C.muted,lineHeight:1.6}}>The receipt is saved.<br/>The next step is still unclear.</div>
  <Paper label="Payment record" amount="৳5,000" sub="Phone order / SAMPLE-001" x={1130} y={160} rotate={7} delay={5}/>
  <div style={{position:'absolute',left:1000,top:650,width:590,padding:28,background:C.ink,color:'#fff',borderRadius:20,transform:`translateX(${interpolate(f,[60,110],[100,0],{extrapolateLeft:'clamp',extrapolateRight:'clamp'})}px)`}}><div style={{fontSize:16,letterSpacing:3,color:'#b9cfca'}}>BUYER · 31 OCT</div><div style={{fontSize:30,marginTop:12}}>The phone has not arrived.</div></div>
 </AbsoluteFill>;
 return <AbsoluteFill><div style={{position:'absolute',top:105,left:145,fontSize:50,fontFamily:'Display',fontWeight:500}}>The story is in the details.</div><Paper label="The record" amount="৳5,000" sub="The first receipt" x={340} y={260} rotate={-5}/><Paper label="Your account" amount="৳5,500" sub="Two payments. One order." x={1080} y={240} rotate={6} delay={15}/><svg style={{position:'absolute',top:390,left:760}} width="330" height="280"><path d="M0 100 C140 0 210 230 330 130" fill="none" stroke={C.red} strokeWidth="3" strokeDasharray="8 9"/></svg><div style={{position:'absolute',top:760,left:790,color:C.red,fontSize:36,fontFamily:'Display',opacity:easing(f-80)}}>A missing piece.</div></AbsoluteFill>
}
function Brand({closing=false}:{closing?:boolean}){const f=useCurrentFrame(),p=easing(f,40);return <AbsoluteFill style={{alignItems:'center',justifyContent:'center'}}><div style={{display:'flex',gap:24,alignItems:'center',transform:`translateY(${(1-p)*60}px)`,opacity:p}}><Mark size={135}/><span style={{fontFamily:'Display',fontWeight:600,fontSize:170,letterSpacing:-10}}>Ebarki<span style={{color:C.red}}>.</span></span></div><div style={{fontSize:42,color:C.muted,marginTop:34,opacity:easing(f-28)}}>Your evidence. Your next move.</div><div style={{marginTop:75,fontSize:16,letterSpacing:3,color:C.muted,opacity:easing(f-70)}}>{closing?'MADE IN BANGLADESH · BUILT AROUND YOUR REVIEW':'CONSUMER RESOLUTION · ENGLISH + বাংলা'}</div>{closing&&<div style={{position:'absolute',bottom:156,fontSize:20,color:C.muted}}>Fictional demonstration · AI-generated narration · Preparation, not submission</div>}</AbsoluteFill>}
function Screen({scene}:{scene:any}){
 const f=useCurrentFrame();const dur=(scene.end-scene.start)*30;
 const scale=interpolate(f,[0,30,dur],[.985,1,1.025],{extrapolateRight:'clamp'});
 const clipSeconds=captureMeta.find(c=>c.name===scene.clip)?.duration||dur/30;
 const hold=75;
 return <AbsoluteFill>
 <div style={{position:'absolute',left:140,top:48,fontSize:36,fontFamily:'Display',fontWeight:500,letterSpacing:-.7}}>{scene.title}</div>
 <div style={{position:'absolute',right:140,top:60,fontSize:13,letterSpacing:3,color:C.muted}}>EBARKI / {scene.id}</div>
 <div style={{position:'absolute',left:232,top:133,width:1456,height:819,overflow:'hidden',borderRadius:16,border:'1px solid #cdd1c9',boxShadow:'0 24px 60px #23383219',transform:`scale(${scale})`,transformOrigin:'50% 40%'}}>
  {f<dur-hold?<Sequence durationInFrames={dur-hold}><OffthreadVideo src={staticFile('clips/'+scene.clip+'.mp4')} playbackRate={(clipSeconds-.12)/((dur-hold)/30)} style={{width:'100%',height:'100%',objectFit:'cover'}} muted pauseWhenBuffering/></Sequence>:<Img src={staticFile('stills/'+scene.clip+'-end.png')} style={{width:'100%',height:'100%',objectFit:'cover'}}/>}
 </div>
 <div style={{position:'absolute',left:240,top:106,fontSize:12,letterSpacing:2,color:C.muted}}>ACTUAL LOCAL APPLICATION · FICTIONAL RECORDS · EDITED DEMONSTRATION</div>
 </AbsoluteFill>
}
const Node=({x,y,title,detail,delay=0,accent=false}:{x:number,y:number,title:string,detail:string,delay?:number,accent?:boolean})=>{const p=easing(useCurrentFrame()-delay);return <div style={{position:'absolute',left:x,top:y,width:405,minHeight:155,padding:30,background:accent?'#e5f0e9':'#fff',border:'1px solid '+(accent?'#9cc5ba':C.line),borderRadius:16,opacity:p,transform:`translateY(${(1-p)*30}px)`,boxShadow:'0 15px 30px #1c2b2c09'}}><div style={{fontSize:31,fontFamily:'Display',fontWeight:600}}>{title}</div><div style={{fontSize:22,color:C.muted,lineHeight:1.35,marginTop:10}}>{detail}</div></div>};
function Architecture({id}:{id:string}){
 const f=useCurrentFrame();const paths=id==='16'?['M540 490H720','M1125 490H1300']:id==='17'?['M470 530H610V310H760','M610 530H760','M610 530V750H760','M1165 310H1330V530','M1165 750H1330V530']:['M550 440H720','M1125 440H1290','M1490 560V610H345V660'];
 return <AbsoluteFill><div style={{position:'absolute',left:140,top:80,color:C.teal,fontSize:17,letterSpacing:4}}>ENGINEERING / FOLLOW THE RECORD</div><div style={{position:'absolute',left:140,top:145,fontFamily:'Display',fontSize:64,fontWeight:500,letterSpacing:-2}}>{id==='16'?'One case. Clear boundaries.':id==='17'?'Different tools. Visible provenance.':'AI assists. Rules stay explicit.'}</div>
 <svg width="1920" height="1080" style={{position:'absolute'}}>{paths.map((d,i)=><path key={i} d={d} stroke={C.teal} strokeWidth="3" fill="none" strokeDasharray="8 9" strokeDashoffset={-f*.8} opacity={easing(f-20-i*16)}/>)}</svg>
 {id==='16'?<><Node x={145} y={410} title="Bilingual interface" detail="Next.js · React · next-intl"/><Node x={720} y={410} title="Same-origin proxy" detail="Browser → server API" delay={35}/><Node x={1300} y={410} title="Python API" detail="FastAPI · Pydantic" delay={70} accent/><div style={{position:'absolute',left:720,top:690,padding:26,width:985,border:'1px dashed #96aaa2',borderRadius:16,fontSize:28,color:C.muted,opacity:easing(f-115)}}>Owner checks · SQLAlchemy · Private evidence vault</div></>:id==='17'?<><Node x={100} y={450} title="Original records" detail="PDF · image · audio"/><Node x={760} y={230} title="Native PDF parser" detail="Text and page coordinates" delay={20}/><Node x={760} y={450} title="Consented model calls" detail="Vision · speech · wording" delay={45} accent/><Node x={760} y={670} title="Reading receipts" detail="Source identity and method" delay={70}/><Node x={1390} y={450} title="Your review" detail="Confirm · correct · exclude" delay={100} accent/><div style={{position:'absolute',left:150,top:785,color:C.muted,fontSize:22}}>No reader available? Keep the original.<br/>Manual review remains possible.</div></>:<><Node x={145} y={360} title="Reference lookup" detail="Lexical + exact references"/><Node x={720} y={360} title="Explicit conditions" detail="True · false · unknown" delay={30} accent/><Node x={1290} y={360} title="Version guard" detail="Reject stale changes" delay={60}/><Node x={145} y={660} title="Reviewed preparation" detail="Saved draft · export · handoff" delay={105} accent/><Node x={720} y={660} title="Separate public lane" detail="Community preview + moderation" delay={130}/><Node x={1290} y={660} title="Administrative record" detail="Roles · notices · source release" delay={155}/></>}
 </AbsoluteFill>
}
function Captions(){const f=useCurrentFrame();const cue=cues.find(c=>f/30>=c.start&&f/30<c.end);return cue?<div style={{position:'absolute',bottom:38,left:210,right:210,display:'flex',justifyContent:'center'}}><div style={{maxWidth:1450,background:'#182b2cf5',color:'#fff',padding:'13px 28px 15px',borderRadius:9,fontSize:34,lineHeight:1.25,textAlign:'center',boxShadow:'0 5px 20px #0002'}}>{cue.text}</div></div>:null}
function Film({captions=true}:{captions?:boolean}){
 const frame=useCurrentFrame();return <AbsoluteFill style={{background:C.paper,color:C.ink,fontFamily:'Text, Bangla, sans-serif'}}>
 <style>{`@font-face{font-family:Display;src:url('${staticFile('fonts/display-latin.woff2')}')}@font-face{font-family:Text;src:url('${staticFile('fonts/text-latin.woff2')}')}@font-face{font-family:Bangla;src:url('${staticFile('fonts/text-bengali.woff2')}')}*{box-sizing:border-box}`}</style>
 <div style={{position:'absolute',inset:0,opacity:.16,backgroundImage:'linear-gradient(#bcc2b5 1px,transparent 1px)',backgroundSize:'100% 160px'}}/>
 {scenes.map(s=><Sequence key={s.id} from={s.start*30} durationInFrames={(s.end-s.start)*30} premountFor={30}>{s.kind==='ui'?<Screen scene={s}/>:s.kind==='architecture'?<Architecture id={s.id}/>:s.kind==='reveal'||s.kind==='closing'?<Brand closing={s.kind==='closing'}/>:<Opening kind={s.kind}/>}</Sequence>)}
 <Audio src={staticFile('audio/mix.wav')}/>
 {captions&&<Captions/>}
 <div style={{position:'absolute',bottom:0,left:0,width:1920*frame/7200,height:3,background:C.red,opacity:.55}}/>
 </AbsoluteFill>
}
const Root=()=> <><Composition id="EbarkiCaptioned" component={Film} durationInFrames={7200} fps={30} width={1920} height={1080} defaultProps={{captions:true}}/><Composition id="EbarkiMaster" component={Film} durationInFrames={7200} fps={30} width={1920} height={1080} defaultProps={{captions:false}}/></>;
registerRoot(Root);
