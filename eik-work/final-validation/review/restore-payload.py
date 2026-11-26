import hashlib, json, pathlib, subprocess
root = pathlib.Path('test/scratch/source-review/restore/offline-runtime')
m = json.loads((root/'manifest.json').read_text())
for name in m['omitted']:
    item = m['files'][name]
    print(name, flush=True)
    path = root.parent / pathlib.Path(name).name
    subprocess.run(['curl','-fsSL','--retry','2',item['provenance'],'-o',str(path)],check=True)
    data = path.read_bytes()
    assert hashlib.sha256(data).hexdigest() == item['sha256']
    offset = 0
    for part in item['parts']:
        dest = root/part['path']
        dest.parent.mkdir(parents=True, exist_ok=True)
        chunk = data[offset:offset+part['bytes']]
        assert hashlib.sha256(chunk).hexdigest() == part['sha256']
        dest.write_bytes(chunk)
        offset += len(chunk)
    assert offset == len(data)
    print(f"verified {item['sha256']} ({offset} bytes)", flush=True)
