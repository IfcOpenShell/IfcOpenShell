<!-- SPDX-License-Identifier: LGPL-3.0-or-later -->

# Binding generator

The generator reads the annotated C++ specifications with Clang and writes the
C API plus the WASM JavaScript and TypeScript bindings. Generated files must not
be edited directly.

Install the generator dependency from the repository root. The installed
Clang compiler and shared `libclang` library must match the Python bindings:

```sh
python -m pip install -e ".[bindgen]"
```

Configure IfcOpenShell with generation enabled, then build the code-generation
target:

```sh
cmake -S cmake -B build/capi \
  -DBUILD_IFCAPI=ON \
  -DIFCAPI_REGENERATE_BINDINGS=ON
cmake --build build/capi --target ifcopenshell_bindings_codegen
```

CMake finds the same Boost, Eigen, OpenCASCADE, CGAL, GMP, and MPFR headers used
by the configured native build and passes their include directories and active
feature definitions to the generator. The native WASM build follows the same
path after installing its pinned dependencies under `build/wasm-native`.
