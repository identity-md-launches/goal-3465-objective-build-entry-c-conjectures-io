from concurrent.futures import ThreadPoolExecutor
from hashlib import sha256
import json
from pathlib import Path
import subprocess

work = Path(__file__).parent
bundle = work / 'offline-runtime'
manifest = json.loads((bundle / 'manifest.json').read_text())
def restore(name):
    item = manifest['files'][name]
    target = work / Path(name).name
    subprocess.run(['curl', '-fsSL', '--max-time', '120', item['provenance'], '-o', target], check=True)
    data = target.read_bytes()
    if sha256(data).hexdigest() != item['sha256']:
        raise ValueError(f'asset hash differs: {name}')
    offset = 0
    for part in item['parts']:
        chunk = data[offset:offset + part['bytes']]
        if sha256(chunk).hexdigest() != part['sha256']:
            raise ValueError(f'part hash differs: {name}')
        dest = bundle / part['path']
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(chunk)
        offset += len(chunk)
    print(name, item['sha256'], flush=True)
with ThreadPoolExecutor(max_workers=3) as executor:
    list(executor.map(restore, manifest['omitted']))
