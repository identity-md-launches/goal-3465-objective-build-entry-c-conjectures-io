#!/bin/sh
# Run from the repository root after staging the pinned offline dependencies.
set -eu
work=${1:-test/scratch/rv-exp-loads-replay}
source=eik-work/trials/rv-exp-loads/entry.c
for spec in 951:953:1 1039:1042:1 1066:1068:1 952:1067:2 3064:3117:2; do
    jobs=${spec##*:}
    range=${spec%:*}
    start=${range%:*}
    python3 eik-work/toolkit/run.py "$work" "target-$start" \
        "targetcheck-rv32im-exp-$start" targetcheck "$source" \
        --function exp --target rv32im --chunks "$range" --jobs "$jobs"
done
