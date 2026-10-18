# IfcOpenShell C++ SDK for Linux

Extract the complete zip. You need a C++17 compiler compatible with GCC 11's
libstdc++ ABI, CMake >= 3.24, and Make or Ninja. The host must provide glibc >=
2.34 and libstdc++ >= the build compiler's version (see `build-info.json`).
Separate archives are built for x86-64 and AArch64. Python is not needed.

| Directory | Contents |
| --- | --- |
| `include/` | Public IfcOpenShell headers |
| `lib/` or `lib64/` | Shared libraries, schema/geometry/serializer plug-ins, CMake package |
| `bin/` | IfcConvert and precompiled C++ examples |
| `third-party/` | Dependency headers, libraries, and CMake packages, each in its own prefix |
| `examples/` | C++ example sources and standalone CMake project |
| `doc/html/` | Offline C++ guide and API reference; open `index.html` |
| `licenses/` | IfcOpenShell and dependency license notices |
| `share/ifcopenshell/` | CMake find modules and build recipe |

From the extracted SDK root:

```sh
cmake -S examples -B examples-build -DCMAKE_PREFIX_PATH="$PWD" -DCMAKE_BUILD_TYPE=Release
cmake --build examples-build --parallel 2
mkdir -p example-output
cd example-output
../examples-build/IfcOpenHouse
../examples-build/IfcParseExamples IfcOpenHouse.ifc
```

You can also run the binaries in `bin/`. Examples create files in the current
directory. Keep their output separate from the SDK.

For your own project use `find_package(IfcOpenShell CONFIG REQUIRED)`, then
link the `IfcOpenShell::` targets shown in `examples/CMakeLists.txt`. Set
`CMAKE_PREFIX_PATH` to the extracted SDK root; its package config locates the
included dependencies. The SDK supports IFC2X3, IFC4, and IFC4X3_ADD2, OpenCASCADE,
CGAL, Manifold, XML, RocksDB, COLLADA, and glTF. All libraries use Release mode
and the same instance-handle ABI; do not mix headers or plug-ins from other builds.

Bundled libraries use relative runtime search paths. CMake-built applications
normally get build RPATHs automatically. When deploying your own executable,
preserve the complete SDK library layout and configure its runtime search path;
schema, geometry, and serializer plug-ins are loaded dynamically. The examples
demonstrate explicit schema plug-in paths. CMake caches contain absolute paths:
reconfigure consumers after moving the SDK.

`build-info.json` records the exact compiler, source commit, and dependency
versions. IfcOpenShell source and complete build scripts are available from the
source URL there; dependency source URLs and revisions are recorded in the
included `build-all.py`. Review the bundled license notices when redistributing
this SDK or an application using it.

Maintainer: run **Build IfcOpenShell C++ SDK (Linux)** in GitHub Actions. It builds
both architectures and uploads a zip plus SHA-256 checksum for each. CI extracts
each archive under a new path, hides the original installation, rebuilds all
examples, and runs them before publishing the artifact.
Separate consumer jobs repeat these checks on native x86-64 and AArch64 runners
in clean Ubuntu containers without project dependencies or graphics development
packages.
