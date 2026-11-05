"""Install isolated, reproducible local voice/alignment tools."""
import subprocess
from pathlib import Path
root=Path(__file__).resolve().parent
venv=root/'.venv'
subprocess.run(['uv','venv','--python','3.12',str(venv)],check=True)
python=venv/'Scripts'/'python.exe'
subprocess.run(['uv','pip','install','--python',str(python),'kokoro-onnx','soundfile','numpy','requests','faster-whisper','transformers','scipy'],check=True)
subprocess.run(['uv','pip','install','--python',str(python),'torch','--index-url','https://download.pytorch.org/whl/cpu'],check=True)
with (root/'audio-requirements.lock.txt').open('w',encoding='utf-8') as out:
    subprocess.run(['uv','pip','freeze','--python',str(python)],stdout=out,check=True)
