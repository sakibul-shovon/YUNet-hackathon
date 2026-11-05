"""Record actual task-runner exit codes without PowerShell stderr-redirection ambiguity."""
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
scope = sys.argv[1] if len(sys.argv) > 1 else 'foundation'
if scope not in {'foundation', 'core', 'graph'}:
    raise SystemExit('Use foundation, core or graph.')
environment = {**os.environ}
if scope == 'foundation':
    environment['EBARKI_NEXT_DIST_DIR'] = '.next-followup-verify'
if scope == 'graph':
    environment['PYTHONHASHSEED'] = '0'
    environment['GRAPHIFY_MAX_WORKERS'] = '1'
target = ROOT/'docs/qa/evidence'/f'followup-{scope}-verified.txt'
with target.open('wb') as output:
    arguments = ['graphify', 'update'] if scope == 'graph' else ['check', '--scope', scope]
    result = subprocess.run([sys.executable, str(ROOT/'scripts/tasks.py'), *arguments],
        cwd=ROOT, env=environment, stdout=output, stderr=subprocess.STDOUT)
receipt = {'product': 'Ebarki', 'scope': scope, 'exit_code': result.returncode,
           'result': 'PASS' if result.returncode == 0 else 'FAIL', 'log': target.name}
target.with_suffix('.json').write_text(json.dumps(receipt, indent=2)+'\n', encoding='utf8')
print(json.dumps(receipt))
raise SystemExit(result.returncode)
