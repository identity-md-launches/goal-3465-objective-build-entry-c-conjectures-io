#!/bin/sh
LD_LIBRARY_PATH=$REPO/test/scratch/sysroot/usr/lib/x86_64-linux-gnu
export LD_LIBRARY_PATH
exec $REPO/test/scratch/sysroot/usr/bin/gcc --sysroot=$REPO/test/scratch/sysroot -Wl,-rpath,$REPO/test/scratch/sysroot/usr/lib/x86_64-linux-gnu "$@"
