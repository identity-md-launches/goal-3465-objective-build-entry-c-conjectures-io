#!/bin/sh
PATH=$REPO/test/scratch/gccdeb/root/usr/bin:/usr/bin:/bin
LD_LIBRARY_PATH=$REPO/test/scratch/gccdeb/root/usr/lib/x86_64-linux-gnu
export PATH LD_LIBRARY_PATH
exec $REPO/test/scratch/gccdeb/root/usr/bin/gcc "$@" -Wl,-rpath,$REPO/test/scratch/gccdeb/root/usr/lib/x86_64-linux-gnu
