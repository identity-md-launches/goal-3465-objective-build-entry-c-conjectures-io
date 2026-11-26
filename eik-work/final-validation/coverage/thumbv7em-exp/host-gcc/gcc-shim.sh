#!/bin/sh
# scratch-only host GCC shim: pinned Ubuntu gcc-13 13.3.0-6ubuntu2~24.04.1 extracted from .debs (no /usr write access)
export LD_LIBRARY_PATH=$REPO/test/scratch/gccroot/usr/lib/x86_64-linux-gnu
exec $REPO/test/scratch/gccroot/usr/bin/gcc -idirafter $REPO/test/scratch/gccroot/usr/include/x86_64-linux-gnu -idirafter $REPO/test/scratch/gccroot/usr/include -B$REPO/test/scratch/gccroot/usr/lib/x86_64-linux-gnu/ -L$REPO/test/scratch/gccroot/usr/lib/x86_64-linux-gnu -Wl,-rpath,$REPO/test/scratch/gccroot/usr/lib/x86_64-linux-gnu "$@"
