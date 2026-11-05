"""Hybrid deterministic render: vector scenes in Remotion, real UI footage in FFmpeg."""
import json
import subprocess
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'out';OUT.mkdir(exist_ok=True)
TMP=ROOT/'tmp/segments';TMP.mkdir(parents=True,exist_ok=True)
QA=ROOT/'qa'
def run(cmd,log):
    print('START',log,flush=True)
    with (QA/(log+'.log')).open('w',encoding='utf-8') as f:
        result=subprocess.run(cmd,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT)
    if result.returncode:raise RuntimeError(f'{log} failed; see qa/{log}.log')
    print('DONE',log,flush=True)
def render():
    scenes=json.loads((ROOT/'scenes.json').read_text(encoding='utf-8'))
    manifest={x['name']:x for x in json.loads((ROOT/'qa/capture-manifest.json').read_text(encoding='utf-8'))}
    for name,start,end in [('intro',0,839),('engineering',5610,7199)]:
        dest=TMP/(name+'.mp4')
        if not dest.exists():
            run(['node',str(ROOT/'node_modules/@remotion/cli/remotion-cli.js'),'render','index.tsx','EbarkiMaster',str(dest),'--frames='+str(start)+'-'+str(end),'--browser-executable=C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe','--concurrency=4','--crf=17','--codec=h264','--pixel-format=yuv420p'],name)
    ordered=[TMP/'intro.mp4']
    for s in scenes:
        if s['kind']!='ui':continue
        name=s['clip'];meta=manifest[name]
        if meta['status']!='CAPTURED':raise RuntimeError('Missing real footage: '+name)
        seconds=s['end']-s['start'];active=seconds-2.5;dest=TMP/(s['id']+'.mp4')
        # Every end hold is the actual high-resolution screenshot captured after that interaction.
        filt=f"[1:v]setpts=(PTS-STARTPTS)*{active}/{meta['duration']},scale=1456:819:flags=lanczos,tpad=stop_mode=clone:stop_duration=3[ui];[0:v][ui]overlay=232:133:shortest=1[base];[2:v]scale=1456:819:flags=lanczos[still];[base][still]overlay=232:133:enable='gte(t,{active})'[out]"
        run(['ffmpeg','-y','-loop','1','-framerate','30','-i',str(ROOT/'tmp/backgrounds'/f"{s['id']}.png"),'-i',str(ROOT/'public/clips'/f'{name}.mp4'),'-loop','1','-framerate','30','-i',str(ROOT/'capture'/f'{name}-end.png'),'-filter_complex_threads','2','-filter_complex',filt,'-map','[out]','-an','-t',str(seconds),'-r','30','-c:v','libx264','-threads','4','-preset','fast','-crf','17','-pix_fmt','yuv420p',str(dest)],'scene-'+s['id'])
        ordered.append(dest)
    mux()

def mux():
    scenes=json.loads((ROOT/'scenes.json').read_text(encoding='utf-8'))
    ordered=[TMP/'intro.mp4']+[TMP/(s['id']+'.mp4') for s in scenes if s['kind']=='ui']+[TMP/'engineering.mp4']
    # Remotion writes 90kHz and FFmpeg defaults to 15,360Hz. The concat demuxer
    # requires matching stream time bases; normalize losslessly before joining.
    normalized=[]
    for p in ordered:
        dest=TMP/(p.stem+'-90k.mp4')
        run(['ffmpeg','-y','-v','error','-i',str(p),'-map','0:v:0','-an','-c:v','copy','-video_track_timescale','90000',str(dest)],'timescale-'+p.stem)
        normalized.append(dest)
    concat=TMP/'concat.txt';concat.write_text('\n'.join("file '"+p.as_posix().replace("'","'\\''")+"'" for p in normalized),encoding='utf-8')
    run(['ffmpeg','-y','-f','concat','-safe','0','-i',str(concat),'-i',str(ROOT/'audio/mix.wav'),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','256k','-ar','48000','-t','240','-movflags','+faststart',str(OUT/'ebarki-master.mp4')],'master-mux')
def captions():
    cues=json.loads((ROOT/'captions/cues.json').read_text(encoding='utf-8'))
    ass='''[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Film,Segoe UI,34,&H00FFFFFF,&H00FFFFFF,&H001C2B2C,&H001C2B2C,0,0,0,0,100,100,0,0,3,12,0,2,210,210,38,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
    def time(t):
        cs=round(t*100);return f'{cs//360000}:{cs//6000%60:02}:{cs//100%60:02}.{cs%100:02}'
    for c in cues:
        text=c['text'].replace('{','').replace('}','')
        ass+=f"Dialogue: 0,{time(c['start'])},{time(c['end'])},Film,,0,0,0,,{text}\n"
    (ROOT/'captions/ebarki.en.ass').write_text(ass,encoding='utf-8')
    run(['ffmpeg','-y','-i',str(OUT/'ebarki-master.mp4'),'-vf','ass=captions/ebarki.en.ass','-r','30','-fps_mode','cfr','-c:v','libx264','-threads','4','-preset','fast','-crf','17','-pix_fmt','yuv420p','-c:a','copy','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-movflags','+faststart',str(OUT/'ebarki-captioned.mp4')],'caption-burn')

def appendix():
    scenes=json.loads((ROOT/'appendix.json').read_text(encoding='utf-8'))
    manifest={x['name']:x for x in json.loads((ROOT/'qa/capture-manifest.json').read_text(encoding='utf-8'))}
    ordered=[]
    for s in scenes:
        name=s['clip'];meta=manifest[name]
        if meta['status']!='CAPTURED':raise RuntimeError('Missing real footage: '+name)
        seconds=s['end']-s['start'];active=seconds-2.5;dest=TMP/(s['id']+'.mp4')
        filt=f"[1:v]setpts=(PTS-STARTPTS)*{active}/{meta['duration']},scale=1456:819:flags=lanczos,tpad=stop_mode=clone:stop_duration=3[ui];[0:v][ui]overlay=232:133:shortest=1[base];[2:v]scale=1456:819:flags=lanczos[still];[base][still]overlay=232:133:enable='gte(t,{active})'[out]"
        run(['ffmpeg','-y','-loop','1','-framerate','30','-i',str(ROOT/'tmp/backgrounds'/f"{s['id']}.png"),'-i',str(ROOT/'public/clips'/f'{name}.mp4'),'-loop','1','-framerate','30','-i',str(ROOT/'capture'/f'{name}-end.png'),'-filter_complex_threads','2','-filter_complex',filt,'-map','[out]','-an','-t',str(seconds),'-r','30','-c:v','libx264','-threads','4','-preset','fast','-crf','17','-pix_fmt','yuv420p',str(dest)],'appendix-'+s['id'])
        ordered.append(dest)
    concat=TMP/'appendix-concat.txt';concat.write_text('\n'.join("file '"+p.as_posix()+"'" for p in ordered),encoding='utf-8')
    run(['ffmpeg','-y','-f','concat','-safe','0','-i',str(concat),'-i',str(ROOT/'audio/music-original.wav'),'-map','0:v:0','-map','1:a:0','-af','volume=0.55,afade=t=out:st=139:d=5','-c:v','copy','-c:a','aac','-b:a','192k','-t',str(scenes[-1]['end']),'-movflags','+faststart',str(OUT/'ebarki-coverage-reel.mp4')],'appendix-mux')
if sys.argv[1]=='render':render();captions()
elif sys.argv[1]=='captions':captions()
elif sys.argv[1]=='appendix':appendix()
elif sys.argv[1]=='mux':mux();captions()
