"""Verify actual encoded output, captions and provenance; do not infer visual acceptance."""
import hashlib
import json
import re
import subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'out';QA=ROOT/'qa';QA.mkdir(exist_ok=True)
def command(args):
    return subprocess.run(args,cwd=ROOT,capture_output=True,text=True,encoding='utf-8',errors='replace')
def probe(p):
    r=command(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(p)])
    if r.returncode:raise RuntimeError(r.stderr)
    return json.loads(r.stdout)
results={}
for name in ['ebarki-master.mp4','ebarki-captioned.mp4','ebarki-coverage-reel.mp4']:
    p=OUT/name
    if not p.exists():continue
    info=probe(p);decoded=command(['ffmpeg','-v','error','-i',str(p),'-f','null','-'])
    v=next(s for s in info['streams'] if s['codec_type']=='video')
    audio=next((s for s in info['streams'] if s['codec_type']=='audio'),None)
    results[name]={'duration_seconds':float(info['format']['duration']),'width':v['width'],'height':v['height'],'frame_rate':v['avg_frame_rate'],'frame_count':v.get('nb_frames'),'video_codec':v['codec_name'],'audio_codec':audio['codec_name'] if audio else None,'audio_sample_rate':audio.get('sample_rate') if audio else None,'bytes':p.stat().st_size,'sha256':hashlib.file_digest(p.open('rb'),'sha256').hexdigest(),'full_decode_exit':decoded.returncode,'decode_errors':decoded.stderr,'whole_film_human_review':False}
    if name=='ebarki-captioned.mp4':
        level=command(['ffmpeg','-hide_banner','-i',str(p),'-af','loudnorm=I=-16:TP=-1:LRA=9:print_format=json','-f','null','-'])
        matches=re.findall(r'\{\s*"input_i"[\s\S]*?\}',level.stderr)
        if matches:results[name]['loudness']=json.loads(matches[-1])
        black=command(['ffmpeg','-hide_banner','-i',str(p),'-vf','blackdetect=d=0.15:pix_th=0.10','-an','-f','null','-'])
        results[name]['black_intervals']=re.findall(r'black_start:[^\r\n]+',black.stderr)
        (QA/'blackdetect.log').write_text(black.stderr,encoding='utf-8')
        scene_times=[4,14,23,34,46,59,74,89,102,114,128,141,152,165,180,194,208,223,236]
        frames=OUT/'review-frames';frames.mkdir(exist_ok=True)
        for sec in scene_times:
            r=command(['ffmpeg','-y','-v','error','-ss',str(sec),'-i',str(p),'-frames:v','1',str(frames/f'{sec:03}.png')])
            if r.returncode:raise RuntimeError(r.stderr)
cues=json.loads((ROOT/'captions/cues.json').read_text(encoding='utf-8'))
results['captions']={'count':len(cues),'overlaps':sum(a['end']>b['start'] for a,b in zip(cues,cues[1:])),'negative_or_zero_duration':sum(c['end']<=c['start'] for c in cues),'max_characters_per_second':max(len(c['text'])/(c['end']-c['start']) for c in cues),'cues_over_25_cps':[i+1 for i,c in enumerate(cues) if len(c['text'])/(c['end']-c['start'])>25],'alignment':'Acoustic CTC, quantized to 30fps; ASR comparison retained separately. Human listening review not certified.'}
(QA/'media-verification.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(results,ensure_ascii=False,indent=2))
