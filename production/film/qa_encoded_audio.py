"""Measure post-encode timing against the mastered audio at five positions."""
import json
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parent
python=ROOT/'.venv/Scripts/python.exe'
if Path(sys.executable).resolve()!=python.resolve():
    raise SystemExit(subprocess.call([str(python),__file__]))
import numpy as np
import soundfile as sf
from scipy.signal import correlate, correlation_lags

decoded=ROOT/'tmp/final-decoded.wav'
subprocess.run(['ffmpeg','-y','-v','error','-i',str(ROOT/'out/ebarki-captioned.mp4'),'-vn','-ar','48000','-c:a','pcm_s16le',str(decoded)],check=True)
reference,rate=sf.read(ROOT/'audio/mix.wav',dtype='float32')
encoded,encoded_rate=sf.read(decoded,dtype='float32')
assert rate==encoded_rate==48000
reference=reference.mean(axis=1);encoded=encoded.mean(axis=1)
checks=[]
for start in [10,60,120,180,230]:
    a=reference[start*rate:(start+2)*rate];b=encoded[start*rate:(start+2)*rate]
    values=correlate(b,a,mode='full',method='fft');lags=correlation_lags(len(b),len(a),mode='full')
    valid=np.abs(lags)<=rate*.05
    lag=int(lags[valid][np.argmax(values[valid])])
    checks.append({'at_seconds':start,'encoded_audio_lag_ms':round(1000*lag/rate,4),'zero_lag_correlation':float(np.corrcoef(a,b)[0,1])})
result={'method':'Decoded final AAC versus mastered PCM, two-second cross-correlation windows, ±50ms search','checks':checks,'max_absolute_lag_ms':max(abs(x['encoded_audio_lag_ms']) for x in checks),'certifies':'No measured encoding drift at these windows; does not certify perceptual word alignment or voice performance.'}
(ROOT/'qa/encoded-audio-timing.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
