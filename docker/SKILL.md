---
name: ifcopenshell-docker-build
description: >-
  Build a real ifcopenshell_wrapper (.so + .py) and IfcConvert locally via
  the docker/ifcos_env toolchain, then wire them into a checkout for
  running C++-dependent parts of the test suite (geometry, the SWIG
  wrapper stub, the C++ parser). Use whenever a task needs to compile
  IfcOpenShell's C++ core rather than just read/patch source - e.g.
  reproducing or fixing a bug in src/ifcgeom, src/ifcparse, src/ifcwrap,
  or validating util/scripts/validate_stub.py against the actual
  generated wrapper.
---

# Building IfcOpenShell locally with docker/ifcos_env

`docker/` is a small toolchain (see `docker/README.md` for the original
author's own description and design rationale - read that first for the
*why*; this file is the practical *how*, distilled from actually driving it
end-to-end) that mirrors the project's GitHub Actions build environment
locally, with a persistent container and ccache so repeat builds are fast.
Pure-Python changes don't need any of this - only reach for it when you need
a real compiled `_ifcopenshell_wrapper*.so` or `IfcConvert` binary.

## Placement

This `docker/` folder must live as a direct child of the repo root you want
to build (sibling of `src/`, `cmake/`, etc.) - `compose.yaml` and
`ifcos_env` resolve the repo via `../` relative to wherever `docker/`
itself sits, and bind-mount it into the container. If you're setting this
up in a fresh clone, copy the whole `docker/` directory there first.

## First-time setup

```bash
cd docker
./ifcos_env create   # build the base image (shared across all your clones/checkouts by name, so usually instant after the first time anywhere)
./ifcos_env up        # start the container, clone+unpack the third-party dependency cache (~10GB, one-time per container)
./ifcos_env build     # full build: all deps + IfcParse + IfcGeom + IfcConvert + the Python wrapper, for one Python version
```

`PY_TGT` and `UNIQUE_ID` live in `docker/.env` - `PY_TGT` (e.g. `py-311`)
restricts the build to one Python version instead of building five;
`UNIQUE_ID` is a hash of the folder path, recalculated on every `up`, so
each checkout gets its own container/volumes automatically.

A full first build takes ~1.5 hours (mostly compiling IfcOpenShell's own
C++, not the cached third-party deps). After that, ccache makes incremental
rebuilds of a couple of touched `.cpp` files **under a minute**.

## Fast iteration

Pass a target to `build` to skip the parts you don't need:

```bash
./ifcos_env build IfcConvert           # only the executables (IfcConvert, IfcGeomServer) - skips the Python wrapper entirely
./ifcos_env build IfcOpenShell-Python  # only the SWIG Python wrapper - skips executables entirely
./ifcos_env build                      # no target = everything (needed the first time, or after touching shared headers)
```

Use this to keep the edit -> rebuild -> test loop fast when debugging: if
you're only touching `src/ifcgeom/`, build `IfcConvert`; if you're only
exercising the Python API, build `IfcOpenShell-Python`.

## Where the artifacts land

Build output goes to `<repo_root>/build/Linux/x86_64/install/` on the host
(bind-mounted, not just inside the container):

- `ifcopenshell/bin/IfcConvert` - the CLI binary
- `python-<version>/lib/python<X.Y>/site-packages/ifcopenshell/_ifcopenshell_wrapper*.so`
  and `ifcopenshell_wrapper.py` - the compiled wrapper + its generated
  Python glue

## Wiring the build into a checkout for testing

`_ifcopenshell_wrapper*.so` and `ifcopenshell_wrapper.py` are already
gitignored under `src/ifcopenshell-python/ifcopenshell/`, which is exactly
where a normal in-tree build would put them - copy the two files there:

```bash
SRC=build/Linux/x86_64/install/python-3.11.8/lib/python3.11/site-packages/ifcopenshell
cp "$SRC/_ifcopenshell_wrapper.cpython-311-x86_64-linux-gnu.so" src/ifcopenshell-python/ifcopenshell/
cp "$SRC/ifcopenshell_wrapper.py" src/ifcopenshell-python/ifcopenshell/
```

Then, to run the test suite against it:

```bash
export PATH="$PWD/build/Linux/x86_64/install/ifcopenshell/bin:$PATH"   # for IfcConvert-dependent tests
cd src/ifcopenshell-python/test
PYTHONPATH="$PWD/.." python3.11 -m pytest -p no:pytest-blender .
```

(`-p no:pytest-blender` avoids the pytest-blender plugin trying to find a
`blender` executable and failing collection entirely, even for non-Blender
tests.) You'll need the matching Python version's `pip install`s too
(numpy, shapely, isodate, lark, tabulate, pytest, ... - whatever the
modules under test import) since this is a bare interpreter, not the
project's pixi env.

## Known gotchas (some fixed in this copy, watch for them if you're on an
## older/different copy of this script)

- **`try` is an unimplemented stub** - it prints a message and does
  nothing. If you want the wrapper pushed straight into a Blender
  extensions folder for manual testing, do the copy yourself (see the
  README's example path) rather than relying on `try`.
- **`stop`/`down` removes the container**, it does not pause it (it's
  literally `docker compose down`). Named volumes (ccache) and the
  bind-mounted `build/` survive, so nothing is really lost - `up` just has
  to recreate the container - but don't expect `docker ps -a` to still
  show it afterwards.
- **The final "Package .zip archives" step of `build()` has a pre-existing
  bash syntax error** unrelated to compilation - the actual build already
  succeeded by that point (look for `Built IfcOpenShell...` in the output),
  so this is safe to ignore if you only need the raw artifacts under
  `build/.../install/`, not packaged release zips.
- **`ready_repo` originally cloned the third-party dependency cache one
  directory level too shallow** (`../build` instead of `build`, relative to
  the repo root), so `nix/build-all.py` would never find it and silently
  rebuild every dependency (boost, OCCT, CGAL, ...) from source - "did the
  build finish in ~1 minute, or is it grinding for 40+ minutes reconfiguring
  OCCT" is the tell. Fixed in this copy; if `up` seems to be building
  dependencies that should already be cached, check `ready_repo`'s `cd`
  targets first.
- **On a brand-new `UNIQUE_ID`/folder, `up` used to fail on the very first
  run** because `ready_repo` tried to `docker exec` into the container
  before `docker compose up -d` had created it. Also fixed in this copy
  (container creation now happens first); if you see
  `Error response from daemon: No such container` right after "Getting the
  repo ready to build...", just run `up` again.
- **Root-partition disk space**: only the bind-mounted `<repo>/build` lives
  on the host filesystem your repo is checked out on. Anything the
  container writes *outside* that mount (stray files, apt/dnf state, etc.)
  lives in the container's own writable layer under Docker's data root
  (commonly `/var/lib/docker`, i.e. usually your root partition) - keep an
  eye on `df -h /` if you're running several of these containers at once.
