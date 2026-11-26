#!/usr/bin/env python3
"""Record the supplemental kit-core instrumentation (not a replacement evaluator)."""
from pathlib import Path
import json
import os
import subprocess
import time

root=Path(__file__).resolve().parents[3]
trial=Path(__file__).resolve().parent
work=root/'test/scratch/rv-exp-interval'
case=work/'cases/rv-exp-interval'
env=dict(os.environ)
settings={'EIK_BUILD_DIR':str(case/'build'),'PYTHONPATH':str(case/'kit'),
          'PYTHONDONTWRITEBYTECODE':'1','EIK_THREADS':'2',
          'ZIG_GLOBAL_CACHE_DIR':str(case/'build/zig-cache'),
          'ZIG_LOCAL_CACHE_DIR':str(case/'build/zig-cache'),
          'HOME':str(case/'home'),'TMPDIR':str(case/'tmp'),
          'PATH':str(root/'test/scratch/eik-dependencies/qemu/bin')+':/usr/bin:/bin'}
env.update(settings)
cmd=[str(work/'runtime/bin/python'),str(trial/'inspect-path.py')]
start=time.monotonic()
r=subprocess.run(cmd,cwd=case/'kit',env=env,capture_output=True,text=True)
def portable(s): return s.replace(str(root),'$REPO')
(trial/'inspection.stdout').write_text(portable(r.stdout))
(trial/'inspection.stderr').write_text(portable(r.stderr))
(trial/'inspection.json').write_text(json.dumps({'command':[portable(s) for s in cmd],
 'environment':{k:portable(v) for k,v in settings.items()},'cwd':portable(str(case/'kit')),
 'exit_code':r.returncode,'seconds':round(time.monotonic()-start,3)},indent=2)+'\n')
print(r.stdout,r.stderr,flush=True)
raise SystemExit(r.returncode)
