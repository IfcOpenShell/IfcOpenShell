#!/bin/sh
# Side modules import libc/libc++ symbols from the main module at runtime.
export EMCC_FORCE_STDLIBS=1
exec "$@"
