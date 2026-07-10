# Building an IfcOpenShell RPM on Fedora

`build-rpm.sh` builds IfcOpenShell against the system toolchain and Fedora
distribution packages, then produces an `.rpm` (and `.tar.gz`) via CPack's RPM
generator (configured in `../cmake/CMakeLists.txt`).

## Quick start

```bash
# From the repository root:
./fedora/build-rpm.sh
```

Artifacts are written to `build-fedora/assets/`. To install the result:

```bash
sudo dnf install ./build-fedora/assets/IfcOpenShell-*.rpm
```

## Options

| Variable       | Default        | Meaning                                   |
| -------------- | -------------- | ----------------------------------------- |
| `BUILD_TYPE`   | `Release`      | CMake build type                          |
| `JOBS`         | `nproc`        | Parallel build jobs                       |
| `INSTALL_DEPS` | `1`            | Install build dependencies via `dnf`      |
| arg 1          | `build-fedora` | Build directory                           |

```bash
INSTALL_DEPS=0 JOBS=8 ./fedora/build-rpm.sh /tmp/iosbuild
```

## Development packages

The script installs these via `dnf` (see the `DEPS` array). Install them
manually if you set `INSTALL_DEPS=0`:

```bash
sudo dnf install -y \
    gcc gcc-c++ make cmake git rpm-build \
    boost-devel opencascade-devel hdf5-devel zlib-devel libxml2-devel \
    cgal-devel gmp-devel mpfr-devel eigen3-devel json-devel \
    swig pcre-devel python3-devel python3-pip
```

Notes:

- `opencascade-devel` and `hdf5-devel` are in **EPEL** on RHEL/Rocky/Alma —
  enable EPEL first (`dnf install epel-release`). On Fedora they are in the
  main repositories.
- **OpenCOLLADA is not packaged for Fedora**, so COLLADA export is disabled
  (`-DCOLLADA_SUPPORT=Off`). This matches the Debian Docker CI build.
- Optional features that are **off** by default (and therefore need no extra
  packages) include USD (`USD_SUPPORT`), RocksDB (`WITH_ROCKSDB`), PROJ
  (`WITH_PROJ`) and the Qt viewer (`BUILD_QTVIEWER`). Enabling any of these
  requires the corresponding `-devel` package.
