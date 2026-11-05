"""Create labelled contact sheets from actual final encoded frames."""
import subprocess
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
raise SystemExit(subprocess.call(['node',str(ROOT/'review_frames.mjs')],cwd=ROOT))
