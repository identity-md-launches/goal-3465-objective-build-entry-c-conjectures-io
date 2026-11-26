#!/usr/bin/env python3
"""One anonymous packaging snapshot. Offline verification never calls this script."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

HERE = Path(__file__).resolve().parent
BASE = 'https://conjectures.io/v1/competitions/exact-integer-kernels/'


def main():
    out = HERE / 'public-refresh'
    out.mkdir(exist_ok=True)
    ledger = []

    def get(endpoint, filename):
        started = datetime.now(timezone.utc).isoformat()
        request = Request(BASE + endpoint, headers={'User-Agent': 'IdentityMD-delivery-evidence/1'})
        try:
            response = urlopen(request, timeout=45)
        except HTTPError as error:
            response = error
        with response:
            body = response.read(4 * 1024 * 1024)
            status = response.code
        (out / filename).write_bytes(body)
        ledger.append({'url': BASE + endpoint, 'method': 'GET', 'http_status': status,
                       'started_utc': started, 'finished_utc': datetime.now(timezone.utc).isoformat(),
                       'path': 'eik-work/delivery/public-refresh/' + filename,
                       'bytes': len(body), 'sha256': hashlib.sha256(body).hexdigest()})
        return json.loads(body)

    boards = get('boards', 'boards.json')
    references = {}
    for board in ('rv32im', 'thumbv6m', 'overall'):
        leader = get('leaderboard?board=' + board, 'leaderboard-' + board + '.json')
        references[board] = leader['reference']
        sid = leader['reference']['submission']
        get('submissions/' + str(sid), 'submission-' + str(sid) + '.json')
        get('submissions/' + str(sid) + '/source', 'source-' + str(sid) + '.json')
    snapshot = {'refreshed_utc': datetime.now(timezone.utc).isoformat(),
                'access': 'anonymous GET only', 'references': references, 'requests': ledger,
                'configuration_hash': boards['configuration_hash']}
    (out / 'snapshot.json').write_text(json.dumps(snapshot, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'references': references, 'requests': len(ledger)}, sort_keys=True))


if __name__ == '__main__':
    main()
