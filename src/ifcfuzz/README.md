# ifcparse_fuzzer

A libFuzzer harness for `ifcopenshell::file`. It parses fuzzer input entirely
in-memory (no subprocess, no temp files), then walks every parsed instance
and calls `to_string()` on it. Constructing the file already tokenizes,
type-checks, and resolves every attribute of every instance, so
`to_string()` mainly adds coverage of the reserialization/formatting code
path rather than the parser itself.

Disabled by default (`BUILD_FUZZERS=OFF`); building it needs Clang, not GCC.

## Build

libFuzzer (`-fsanitize=fuzzer`) is only implemented by Clang, and it
supplies its own `main()`, so it has to be built in its own directory,
separate from any normal GCC build of IfcOpenShell - putting
`-fsanitize=fuzzer` in the global flags would break every other target,
including CMake's own compiler check. That's why `BUILD_FUZZERS` only adds
`-fsanitize=fuzzer` to this one target (see `CMakeLists.txt`); ASan/UBSan
are applied globally instead, so that `IfcParse` itself is instrumented.

```bash
mkdir -p build-fuzz && cd build-fuzz
cmake ../cmake \
  -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ \
  -DCMAKE_CXX_FLAGS="-fsanitize=address,undefined -fno-sanitize-recover=all -g -O1 -fno-omit-frame-pointer" \
  -DCMAKE_C_FLAGS="-fsanitize=address,undefined -fno-sanitize-recover=all -g -O1 -fno-omit-frame-pointer" \
  -DBUILD_FUZZERS=ON -DMINIMAL_BUILD=ON \
  -DBUILD_IFCGEOM=OFF -DBUILD_CONVERT=OFF -DWITH_OPENCASCADE=OFF \
  -DBUILD_ONLY_COMMON_SCHEMAS=ON
cmake --build . --target ifcparse_fuzzer -- -j$(nproc)
```

`-fno-sanitize-recover=all` matters: without it, most UBSan checks just log
and continue rather than aborting, so a fuzzing session would run straight
past real bugs without ever capturing them as a crash artifact.

`-DBUILD_IFCGEOM=OFF -DBUILD_CONVERT=OFF -DWITH_OPENCASCADE=OFF
-DMINIMAL_BUILD=ON` keep the build scoped to `IfcParse` (the code this
harness actually exercises) so it doesn't also have to compile/instrument
OpenCASCADE-dependent geometry code.

## Run

```bash
mkdir -p corpus  # or point at your own seed corpus of .ifc files
./src/ifcfuzz/run.sh corpus/
```

`run.sh` just sets sane sanitizer defaults and execs the binary - any
libFuzzer flag can be passed through, e.g. `-jobs=4 -workers=4` for
parallel fuzzing, or `-runs=0 <file>` to run once against a specific input.

No seed corpus or dictionary ships in this repo. Any small set of valid and
invalid `.ifc` files works as a starting corpus; a dictionary of STEP/IFC
tokens (`ISO-10303-21`, `HEADER`, common `IFCxxx` entity names, etc.) passed
via `-dict=` measurably helps the mutator get past the header boilerplate.

### Log output

`Logger` output is only wired up when the binary is run against an explicit
file argument (e.g. `-runs=1 <file>`), not during a real campaign against a
corpus directory - logging every parse warning on every execution of a
fuzzing campaign would dominate the runtime. Repro runs print
`[Warning]`/`[Error]` messages to stderr.

### Leak detection

`run.sh` sets `ASAN_OPTIONS=detect_leaks=0` by default. A leak that used to
fire on almost any malformed header (`IfcSpfLexer` allocated in
`in_memory_file_storage::read_from_stream`, not freed if header parsing
returned early or threw) has been fixed, but a second, narrower leak
remains in entity attribute parsing when a syntactically valid header is
followed by malformed entity data. libFuzzer treats a detected leak like a
crash and halts the *entire* session on the first occurrence, so leak
detection stays off by default until that one's fixed too. Run a separate,
short, deliberate pass with `ASAN_OPTIONS=detect_leaks=1` instead if you're
specifically hunting for leaks.

## Minimizing and deduplicating crashes

Not covered by `run.sh` - use libFuzzer's own flags directly:

```bash
./ifcparse_fuzzer -minimize_crash=1 -max_total_time=60 -exact_artifact_path=minimized crash-input
```

Sanitizer reports for two different bugs can look identical at a glance
(same `SUMMARY` line) if the bug is a duplicated code pattern hit from
multiple call sites - check the full symbolized stack trace, not just the
summary, before assuming two crashes are the same bug.
