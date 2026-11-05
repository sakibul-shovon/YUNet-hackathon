"""Independent ASR check of the actual voice track; retains discrepancies for review."""
import json
import re
import subprocess
import sys
from difflib import SequenceMatcher
from pathlib import Path
root=Path(__file__).resolve().parent
py=root/'.venv/Scripts/python.exe'
if Path(sys.executable).resolve()!=py.resolve():raise SystemExit(subprocess.call([str(py),__file__]))
from faster_whisper import WhisperModel
import soundfile as sf
from scipy.signal import resample_poly
model=WhisperModel('base.en',device='cpu',compute_type='int8',download_root=str(root/'tmp/models'),cpu_threads=4)
wave,rate=sf.read(root/'audio/voice.wav',dtype='float32')
wave=resample_poly(wave,16000,rate)
segments,info=model.transcribe(wave,language='en',beam_size=5,word_timestamps=True,vad_filter=True)
actual=[]
for s in segments:
 actual.extend({'word':w.word.strip(),'start':w.start,'end':w.end,'probability':w.probability} for w in s.words)
expected=json.loads((root/'captions/words.json').read_text(encoding='utf-8'))
norm=lambda x:re.sub('[^a-z]','',x.lower())
a=[norm(x['word']) for x in expected];b=[norm(x['word']) for x in actual]
matcher=SequenceMatcher(a=a,b=b,autojunk=False)
differences=[];timing=[]
for tag,i,j,k,l in matcher.get_opcodes():
 if tag!='equal':differences.append({'operation':tag,'expected':a[i:j],'recognized':b[k:l],'time':actual[k]['start'] if k<len(actual) else None})
 else:
  for x,y in zip(expected[i:j],actual[k:l]):timing.append(abs(x['start']-y['start']))
result={'method':'faster-whisper base.en independent transcription','expected_words':len(a),'recognized_words':len(b),'sequence_similarity':matcher.ratio(),'differences':differences,'matched_word_onset_mean_difference_ms':1000*sum(timing)/max(1,len(timing)),'note':'ASR comparison is an estimate, not ground-truth perceptual synchronization certification. Brand-name transcription differences require listening.','asr_words':actual}
(root/'qa/independent-audio-check.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k!='asr_words'},indent=2))
