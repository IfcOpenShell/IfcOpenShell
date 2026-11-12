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

`docker/` mirrors the project's GitHub Actions build environment locally,
in a persistent, non-root container with ccache so repeat builds are fast.
See `docker/README.md` for the design rationale. Pure-Python changes don't
need any of this - only reach for it when you need a real compiled
`_ifcopenshell_wrapper*.so` or `IfcConvert` binary.

## Placement

This `docker/` folder must live as a direct child of the repo root you want
to build (sibling of `src/`, `cmake/`, etc.) - `compose.yaml` and
`ifcos_env` resolve the repo via `../` relative to wherever `docker/`
itself sits, and bind-mount it into the container. If you're setting this
up in a fresh clone, copy the whole `docker/` directory there first.

## Setup

```bash
cd docker
./ifcos_env create   # build the image (shared by name across all your clones/checkouts, so usually instant after the first time anywhere)
./ifcos_env up        # create + start the container, clone/unpack the third-party dependency cache (~10GB, one-time per container)
./ifcos_env build     # full build: all deps + IfcParse + IfcGeom + IfcConvert + the Python wrapper, for one Python version
```

`PY_TGT` and `UNIQUE_ID` live in `docker/.env` - `PY_TGT` (e.g. `py-311`)
restricts the build to one Python version instead of building five;
`UNIQUE_ID` is a hash of the folder path, recalculated on every `up`, so
each checkout gets its own container/volumes automatically.

A full first build takes ~1.5 hours (mostly compiling IfcOpenShell's own
C++, not the cached third-party deps). After that, ccache makes incremental
rebuilds of a couple of touched `.cpp` files **under a minute**.

## Container lifecycle

The container is long-lived (`sleep infinity`) so exec'd commands and
ccache state persist between builds. Commands map directly onto Docker
Compose's own container-vs-image distinction:

```bash
./ifcos_env up         # create the container if it doesn't exist, then start it (runs ready_repo too)
./ifcos_env stop       # stop the container, keep it around
./ifcos_env start      # start it back up (same container, same filesystem layer)
./ifcos_env restart    # stop, then start
./ifcos_env down       # remove the container (and its network) entirely
./ifcos_env recreate   # down, then up - a fresh container
```

Named volumes (`ccache`) and the bind-mounted repo/`build/` are unaffected
by `down`/`recreate` - only the container itself goes away, and `up`
recreates it from the image.

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
(bind-mounted, not just inside the container), owned by you (see
"Container user" below):

- `ifcopenshell/bin/IfcConvert` - the CLI binary
- `python-<version>/lib/python<X.Y>/site-packages/ifcopenshell/_ifcopenshell_wrapper*.so`
  and `ifcopenshell_wrapper.py` - the compiled wrapper + its generated
  Python glue

## Testing against a checkout (automated / AI-driven)

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

**This is the pattern to use for automated or AI-driven verification.**
Don't use `try` (below) for that - it overwrites files in a real, live
Blender installation, which isn't something an automated/AI workflow
should ever do without the human explicitly asking for it in the moment.

## Testing in Blender itself (human only)

`try` copies the built wrapper straight into your actual Blender/Bonsai
extension install, for manual in-Blender testing:

```bash
./ifcos_env try
```

It reads `BLENDER_USER_RESOURCE` from `.env` - set this to wherever
Blender's user resource folder for the Bonsai extension actually lives on
your system, which depends on your own Blender setup:

```bash
# in docker/.env
BLENDER_USER_RESOURCE=~/.config/blender/bonsai/
```

`try` figures out the built Python version from `build/.../install/`
(disambiguating with `PY_TGT` if more than one version was built) and
copies the wrapper to
`$BLENDER_USER_RESOURCE/extensions/.local/lib/python<X.Y>/site-packages/ifcopenshell/`.

## Container user

The image runs as a non-root `builder` user, UID/GID matching your host
account (passed as `--build-arg` by `create` from `id -u`/`id -g`, so it
adjusts automatically - no manual flag needed even if you're not 1000:1000).
Files the build creates under the bind mount come out owned by you, not
root. Passwordless `sudo` is available inside the container (e.g. via
`attach`) for the rare case you need root for something ad hoc.

If you're picking up an existing checkout that was previously built with
an older, root-based image, you may hit `Permission denied` the first time
you run `up`/`build` under the new image - `build/`, `.git/modules/`, the
`ccache` volume, `output/`, and `build.log` can all be left root-owned from
before. Fix it once via the container's own root (no host `sudo` needed):

```bash
docker exec -u root -w /__w/IfcOpenShell/IfcOpenShell <container-name> \
    chown -R "$(id -u)":"$(id -g)" .git/modules build output build.log /ccache
```

(`<container-name>` is `ifcopenshell-<UNIQUE_ID>` - see `docker ps -a`.)

## Other things worth knowing

- **Linux x64 only.** `compose.yaml` pins `platform: linux/amd64`; on an
  ARM host (e.g. Apple Silicon) this build isn't available.
- **The final "Package .zip archives" step of `build()` has a pre-existing
  bash syntax error**, unrelated to compilation - the actual build already
  succeeded by that point (look for `Built IfcOpenShell...` in the output),
  so this is safe to ignore if you only need the raw artifacts under
  `build/.../install/`, not packaged release zips.
- **`test_mmaped_stream` and similar `USE_MMAP`-dependent tests will fail**
  against this build - `nix/build-all.py` is invoked with `USE_MMAP=OFF`
  here. Not a bug in your code if you see it fail.
- Only the bind-mounted `<repo>/build` lives on the host filesystem your
  repo is checked out on. Anything the container writes *outside* that
  mount lives in the container's own writable layer under Docker's data
  root (commonly `/var/lib/docker`, i.e. usually your root partition) -
  keep an eye on `df -h /` if you're running several of these containers
  at once.
