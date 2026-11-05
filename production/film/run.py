"""Task-runner bridge; keep the film toolchain in its own working directory."""
import subprocess
import sys
from pathlib import Path
root=Path(__file__).resolve().parent
args=sys.argv[1:]
if args[0]=='remotion':
    cmd=['node',str(root/'node_modules/@remotion/cli/remotion-cli.js'),*args[1:]]
elif args[0]=='node':cmd=['node',*args[1:]]
else:raise SystemExit('Expected remotion or node')
raise SystemExit(subprocess.call(cmd,cwd=root))
