# Native linux/arm64 build environment

`docker/SKILL.md` and `docker/README.md` describe the `ifcos_env` harness,
which is hardcoded to `linux/amd64` (`compose.yaml` pins `platform:
linux/amd64`, and `ifcos_env`'s `ready_repo` clones the `rockylinux9-x64`
branch of `build-outputs` into `build/Linux/x86_64/...`). On Apple Silicon
that amd64 image only runs under QEMU emulation, which is very slow (a full
`-j1` build of v0.9.0 measured ~4.5 hours).

This note documents a **native arm64** build path instead. It does not
modify `Dockerfile`, `compose.yaml` or `ifcos_env` - none of that was
necessary for the image itself, and the harness script's hardcoded x64
branch/paths are left alone rather than patched blind. Everything below is
run by hand with plain `docker` commands.

## Why no Dockerfile changes were needed

`docker/Dockerfile` builds `FROM rockylinux:9`, which is a genuine
multi-arch base image, and every package it installs via `dnf` is also
available natively for aarch64. `docker buildx build --platform linux/arm64`
against the **unmodified** `Dockerfile` just works:

```bash
docker buildx build --platform linux/arm64 -f docker/Dockerfile \
    --build-arg USER_UID="$(id -u)" --build-arg USER_GID="$(id -g)" \
    -t ifcopenshell-build-env:arm64 --load docker
```

Result: `ifcopenshell-build-env:arm64`, arch `arm64`, ~393MB content
(~1.55GB on disk) - about the same size as the existing amd64
`ifcopenshell-build-env:updated` image.

## Why the dependency cache needed a different branch, not a code change

The real x86_64-only piece is not the Dockerfile, it's the **prebuilt
third-party dependency cache** that `ready_repo` clones
(`https://github.com/IfcOpenShell/build-outputs.git`, branch
`rockylinux9-x64`, unpacked to `build/Linux/x86_64/install/`). That repo
also has a `rockylinux9-arm64` branch, unpacked to
`build/Linux/aarch64/install/` - which is exactly the path
`nix/build-all.py` looks for on its own (it derives the path from
`platform.machine()`, which is `aarch64` inside an arm64 container). So the
fix is just "use the arm64 branch and let the existing build script find
it", not a code change.

Note: `build-outputs` stores the actual `.tar.gz` deps via **git-lfs** - a
plain `git clone` only gets you LFS pointer files. Run `git lfs pull` (after
`git lfs install`) inside the `build` directory before
`cache_dependencies.py unpack`, or `unpack` will fail with
`tarfile.ReadError: not a gzip file`.

## Reuse: exact commands

Requires Docker Desktop running natively on Apple Silicon (check
`docker info | grep Architecture` says `aarch64`, not under Rosetta/QEMU).

```bash
# 1. Image (only needed once - or reuse ifcopenshell-build-env:arm64 if it
#    already exists in `docker images`)
docker buildx build --platform linux/arm64 -f docker/Dockerfile \
    --build-arg USER_UID="$(id -u)" --build-arg USER_GID="$(id -g)" \
    -t ifcopenshell-build-env:arm64 --load docker

# 2. A repo checkout to bind-mount (any v0.9.0 checkout works; this repo's
#    own docker/ hardcodes x64 so don't point compose.yaml at it - just
#    bind-mount the repo root directly)
REPO=/path/to/your/ifcopenshell/checkout

# 3. Container (persistent, ccache shared across rebuilds)
docker volume create ifcopenshell-ccache-arm64
docker run -d --platform linux/arm64 --name ifcos-arm64-build \
    -v "$REPO":/__w/IfcOpenShell/IfcOpenShell \
    -v ifcopenshell-ccache-arm64:/ccache \
    -w /__w/IfcOpenShell/IfcOpenShell \
    ifcopenshell-build-env:arm64 sleep infinity

# 4. Dependencies: clone the arm64 build-outputs branch and unpack via LFS
docker exec -u builder -w /__w/IfcOpenShell/IfcOpenShell ifcos-arm64-build \
    git clone -b rockylinux9-arm64 https://github.com/IfcOpenShell/build-outputs.git build
docker exec -u builder -w /__w/IfcOpenShell/IfcOpenShell/build ifcos-arm64-build git lfs install
docker exec -u builder -w /__w/IfcOpenShell/IfcOpenShell/build ifcos-arm64-build git lfs pull
docker exec -u builder -w /__w/IfcOpenShell/IfcOpenShell/build ifcos-arm64-build \
    uv run ../nix/cache_dependencies.py unpack

# 5. Build (Python 3.13, matching Blender 5.2's bundled interpreter)
docker exec -u builder -w /__w/IfcOpenShell/IfcOpenShell \
    -e PY_TGT=py-313 -e ADD_COMMIT_SHA=1 -e BUILD_CFG=Release \
    -e CXXFLAGS=-O3 -e CFLAGS=-O3 -e IFCOS_NUM_BUILD_PROCS=2 \
    ifcos-arm64-build \
    uv run ./nix/build-all.py -v -py-313 --diskcleanup
```

Artifacts land under `$REPO/build/Linux/aarch64/install/`, same layout as
the amd64 harness's `build/Linux/x86_64/install/` (see `SKILL.md`):

- `ifcopenshell/bin/IfcConvert`
- `python-3.13.6/lib/python3.13/site-packages/ifcopenshell/_ifcopenshell_wrapper*.so`
  and `ifcopenshell_wrapper.py`

## `IFCOS_NUM_BUILD_PROCS`: use 2, not `nproc`

Docker Desktop on this host exposes 12 CPUs but only **7.75GB RAM** to the
VM. A handful of `IfcOpenShell` translation units (the generated per-schema
parsers under `src/ifcparse`, and OCCT-heavy files like
`src/ifcgeom/kernels/opencascade/wire_utils.cpp`) each need well over 1GB of
RAM to compile. At `-j13` (the script's `nproc+1` default) and even at
`-j4`, `cc1plus` gets OOM-killed (`fatal error: Killed signal terminated
program cc1plus`). `-j2` built cleanly. If your Docker Desktop VM has more
RAM allocated, a higher `-j` will likely work and be faster - increase it
and watch for the same OOM signature before trusting a higher value.

## Measured build time

With dependencies already unpacked (one-time, git-lfs bound, a few
minutes) and `ccache` cold, building `v0.9.0` (commit `6f2e1aa99`) through
`IfcParse`, `IfcGeom`, `IfcConvert`, `IfcGeomServer` and the Python 3.13
wrapper at `-j2` took **~14 minutes** (848s: 11:55:20 to 12:16:08 UTC).
That's the number to compare against the ~4.5 hour amd64-under-QEMU `-j1`
baseline - roughly 19x faster, even at `-j2`.

Verified working:

```
$ IfcConvert --version
IfcOpenShell IfcConvert 0.9.0alpha0-6f2e1aa99

$ IfcConvert test/fixtures/ColumnPSetsOfSets.ifc out.obj
...
Done creating geometry (1 objects)
Conversion took 1 second
```

```python
>>> import ifcopenshell  # py3.13 wrapper, arm64
>>> f = ifcopenshell.open("ColumnPSetsOfSets.ifc")
>>> len(f.by_type("IfcProduct"))
5
```

## Constraints carried over from the shared harness

Same as `SKILL.md`: `test_mmaped_stream` and `USE_MMAP`-dependent tests
will fail (`nix/build-all.py` runs with `USE_MMAP=OFF`). The "Package .zip
archives" step isn't invoked here at all (`build-all.py` was run directly,
not through `ifcos_env build`), so there's nothing to ignore there.

Do not touch any `occt:*` / `occtdraw:*` image - unrelated to this harness,
belongs to a different maintainer's build setup.

## Known limitation: OCC-native serializers

With the default static OpenCASCADE link, the SVG (`--plan`, `--model`),
STEP and IGES serializers do not work in this build: `IfcConvert` aborts
with `Standard_NoSuchObject` or writes an empty B-rep, on any model. OBJ,
glTF, COLLADA and the Python wrapper are unaffected. This is the
per-plug-in static OCCT problem described in #9341, not something specific
to arm64.

Building with `--shared` does not resolve it here: the cached
`occt-shared-7.8.1` on the `rockylinux9-arm64` branch was compiled against
glibc 2.38 and CXXABI 1.3.15, newer than Rocky Linux 9 provides, so
`IfcGeomServer` fails to link (`undefined reference to fmod@GLIBC_2.38`).
Until #9341 lands or OCCT is rebuilt shared inside the container, use this
harness for geometry kernel, parser and Python wrapper verification only.
