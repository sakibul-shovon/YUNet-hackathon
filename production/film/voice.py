"""Local female narration, original stems and acoustic alignment (no proportional timing)."""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parent
PY=ROOT/'.venv/Scripts/python.exe'
if Path(sys.executable).resolve()!=PY.resolve():
    raise SystemExit(subprocess.call([str(PY),__file__,*sys.argv[1:]]))
import numpy as np
import requests
import soundfile as sf

ASSETS=ROOT/'audio';ASSETS.mkdir(exist_ok=True)
MODELS=ROOT/'tmp/models';MODELS.mkdir(parents=True,exist_ok=True)
scenes=json.loads((ROOT/'scenes.json').read_text(encoding='utf-8'))

def fetch(name,url):
    p=MODELS/name
    if p.exists():return p
    print('Downloading',name,flush=True)
    with requests.get(url,stream=True,timeout=90) as r:
        r.raise_for_status()
        with p.with_suffix('.part').open('wb') as f:
            for chunk in r.iter_content(1024*1024):f.write(chunk)
    p.with_suffix('.part').replace(p)
    return p

def synth():
    from kokoro_onnx import Kokoro
    base='https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.1/'
    model=Kokoro(str(fetch('kokoro-v1.0.onnx',base+'kokoro-v1.0.onnx')),str(fetch('voices-v1.0.bin',base+'voices-v1.0.bin')))
    sample='From scattered records to a clearer next step. Ebarki. Your evidence. Your next move.'
    for v in ['af_heart','af_sarah']:
        a,sr=model.create(sample,voice=v,speed=1.0,lang='en-us');sf.write(ASSETS/(v+'-sample.wav'),a,sr)
    timings=[];rate=24000;master=np.zeros(240*rate,dtype=np.float32)
    for s in scenes:
        dest=ASSETS/(s['id']+'.wav')
        if dest.exists():a,sr=sf.read(dest,dtype='float32')
        else:
            a,sr=model.create(s['voice'],voice='af_heart',speed=1.0,lang='en-us');sf.write(dest,a,sr)
        available=s['end']-s['start']-1.2
        if len(a)/sr>available:
            speed=min(1.12,(len(a)/sr)/available)
            a,sr=model.create(s['voice'],voice='af_heart',speed=speed,lang='en-us');sf.write(dest,a,sr)
        duration=len(a)/sr
        if duration>available+0.3:raise RuntimeError(f"Scene {s['id']} voice exceeds slot: {duration:.2f} > {available:.2f}")
        start=s['start']+0.6
        master[round(start*rate):round(start*rate)+len(a)]=a
        timings.append({'id':s['id'],'start':start,'end':start+duration,'text':s['voice'],'voice':'af_heart','sample_rate':sr})
        print('Voice',s['id'],round(duration,2),'s',flush=True)
    sf.write(ASSETS/'voice.wav',master,rate,subtype='PCM_24')
    text='This is a fictional demonstration recording. I paid Sample Electronics five thousand taka and another five hundred taka on October twenty fourth, twenty twenty six. The phone was promised by October twenty sixth. It has not arrived.'
    a,sr=model.create(text,voice='af_sarah',speed=0.98,lang='en-us');sf.write(ASSETS/'fictional-account.wav',a,sr)
    (ASSETS/'timings.json').write_text(json.dumps(timings,indent=2),encoding='utf-8')

def align():
    import torch
    from scipy.signal import resample_poly
    from transformers import AutoProcessor,AutoModelForCTC
    torch.set_num_threads(4)
    model_id='facebook/wav2vec2-base-960h'
    proc=AutoProcessor.from_pretrained(model_id,cache_dir=str(MODELS))
    model=AutoModelForCTC.from_pretrained(model_id,cache_dir=str(MODELS)).eval()
    timings=json.loads((ASSETS/'timings.json').read_text(encoding='utf-8'))
    words=[];qa=[]
    for row in timings:
        audio,sr=sf.read(ASSETS/(row['id']+'.wav'),dtype='float32')
        audio=resample_poly(audio,16000,sr)
        inputs=proc(audio,sampling_rate=16000,return_tensors='pt')
        with torch.no_grad():logp=model(**inputs).logits.log_softmax(-1)[0].numpy()
        spoken=row['text'].split()
        normalized=[''.join(re.findall('[A-Z]',w.upper())) for w in spoken]
        target='|'.join(normalized)
        vocab=proc.tokenizer.get_vocab();blank=model.config.pad_token_id
        tokens=[vocab[ch] for ch in target]
        ext=np.full(len(tokens)*2+1,blank,dtype=np.int32);ext[1::2]=tokens
        T,S=len(logp),len(ext)
        previous=np.full(S,-1e30,dtype=np.float32);previous[0]=logp[0,blank];previous[1]=logp[0,ext[1]]
        back=np.zeros((T,S),dtype=np.int8)
        can_skip=(ext!=blank)&(ext!=np.roll(ext,2));can_skip[:2]=False
        for t in range(1,T):
            stay=previous;one=np.r_[-1e30,previous[:-1]];two=np.r_[-1e30,-1e30,previous[:-2]]
            two=np.where(can_skip,two,-1e30)
            options=np.stack([stay,one,two]);choice=np.argmax(options,axis=0)
            back[t]=choice;previous=options[choice,np.arange(S)]+logp[t,ext]
        state=S-1 if previous[-1]>=previous[-2] else S-2
        states=np.empty(T,dtype=np.int32)
        for t in range(T-1,-1,-1):states[t]=state;state-=int(back[t,state])
        step=(len(audio)/16000)/T;charoffset=0
        for display,word in zip(spoken,normalized):
            charstates=list(range(charoffset*2+1,(charoffset+len(word))*2,2))
            frames=np.flatnonzero(np.isin(states,charstates))
            if not len(frames):raise RuntimeError('Unaligned word '+display)
            start=row['start']+frames[0]*step;end=row['start']+(frames[-1]+1)*step
            score=float(np.exp(logp[frames,ext[states[frames]]]).mean())
            words.append({'word':display,'start':round(start,4),'end':round(end,4),'scene':row['id'],'acoustic_score':round(score,4),'method':'wav2vec2 CTC Viterbi forced alignment'})
            charoffset+=len(word)+1
        qa.append({'scene':row['id'],'aligned_words':len(spoken),'frames':T})
        print('Aligned',row['id'],len(spoken),flush=True)
    captions=[];buf=[]
    for i,w in enumerate(words):
        if buf and (w['scene']!=buf[-1]['scene'] or w['start']-buf[-1]['end']>0.65 or len(' '.join(x['word'] for x in buf))+len(w['word'])>68):
            captions.append(buf);buf=[]
        buf.append(w)
        if w['word'].endswith(('.', '?', '!')) or len(buf)>=10:
            captions.append(buf);buf=[]
    if buf:captions.append(buf)
    cues=[]
    for b in captions:
        cues.append({'start':round(b[0]['start']*30)/30,'end':round(b[-1]['end']*30)/30,'text':' '.join(w['word'] for w in b)})
    def stamp(t,sep):
        ms=round(t*1000);return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02}{sep}{ms%1000:03}'
    cap=ROOT/'captions';cap.mkdir(exist_ok=True)
    (cap/'words.json').write_text(json.dumps(words,indent=2),encoding='utf-8')
    (cap/'cues.json').write_text(json.dumps(cues,indent=2),encoding='utf-8')
    for ext,sep in [('srt',','),('vtt','.')]:
        body='WEBVTT\n\n' if ext=='vtt' else ''
        body+='\n\n'.join(f"{i+1}\n{stamp(c['start'],sep)} --> {stamp(c['end'],sep)}\n{c['text']}" for i,c in enumerate(cues))+'\n'
        (cap/('ebarki.en.'+ext)).write_text(body,encoding='utf-8')
    assert ' '.join(x['word'] for x in words)==' '.join(s['voice'] for s in scenes)
    assert all(cues[i]['end']<=cues[i+1]['start'] for i in range(len(cues)-1))
    (ROOT/'qa/caption-alignment.json').write_text(json.dumps({'method':'audio-derived CTC forced alignment','model':model_id,'word_count':len(words),'cues':len(cues),'text_coverage':'exact','overlaps':0,'frame_quantization_max_ms':16.67,'perceptual_sync_verified':False,'low_confidence_words':[w for w in words if w['acoustic_score']<0.2],'scenes':qa},indent=2),encoding='utf-8')

def music():
    rate=24000;duration=240;n=duration*rate;t=np.arange(n)/rate
    bed=np.zeros(n,dtype=np.float32)
    # Original restrained harmonic bed; no sampled commercial music.
    chords=[(146.83,220,293.66),(130.81,196,261.63),(164.81,246.94,329.63),(174.61,261.63,349.23)]
    for block in range(30):
        a=block*8*rate;b=min(n,a+8*rate);tt=np.arange(b-a)/rate
        envelope=np.sin(np.pi*np.minimum(tt/1.3,1)/2)*np.sin(np.pi*np.minimum((8-tt)/1.3,1)/2)
        for f in chords[block%4]:bed[a:b]+=0.014*np.sin(2*np.pi*f*tt+0.35*np.sin(2*np.pi*.13*tt))*envelope
    for start in [19,82,95,135,172,187,232]:
        a=int(start*rate);tt=np.arange(min(2*rate,n-a))/rate
        bed[a:a+len(tt)]+=0.035*np.sin(2*np.pi*587.33*tt)*np.exp(-tt*4)
    voice,sr=sf.read(ASSETS/'voice.wav',dtype='float32')
    env=np.convolve((np.abs(voice)>0.008).astype(float),np.ones(2400)/2400,mode='same')
    bed*=1-0.66*np.minimum(env*4,1)
    sf.write(ASSETS/'music-original.wav',bed,rate,subtype='PCM_24')
    mix=voice*.88+bed;sf.write(ASSETS/'mix-premaster.wav',np.stack([mix,mix],axis=1),rate,subtype='PCM_24')
    subprocess.run(['ffmpeg','-y','-i',str(ASSETS/'mix-premaster.wav'),'-af','loudnorm=I=-16:TP=-1:LRA=9','-ar','48000',str(ASSETS/'mix.wav')],check=True,capture_output=True)

{'synth':synth,'align':align,'music':music}[sys.argv[1]]()
