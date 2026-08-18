<!-- SPDX-License-Identifier: LGPL-3.0-or-later -->

# Binding generator

The generator reads the annotated C++ specifications with Clang and writes the
C API plus the WASM JavaScript and TypeScript bindings. Generated files must not
be edited directly.

## How generation works

`src/ifcwrap/CMakeLists.txt` invokes `generate.py` with the include directories
and feature definitions from the configured IfcOpenShell build. The production
entry point always processes `specs/cpp/ifcparse.hpp` and
`specs/cpp/ifcgeom.hpp`.

The data flow is:

```text
C++ specs and project headers
  -> C++ spec frontend + Clang discovery
  -> merged binding model
  -> target-neutral BindingIR
  -> finalized C ABI metadata
  -> C/C++ and WASM emitters
```

The main stages are:

1. `cpp_spec_frontend.py` reads the `IFCAPI_*` source markers and adapter
   function signatures. `clang_discovery.py` and `libclang_index.py` use the
   matching `libclang` to resolve the selected C++ declarations, overloads,
   fields, and canonical types. `semantic_types.py` describes those types
   independently of an output language.
2. `pipeline.py` combines both specifications into a `MergedBindingSpec`.
   `binding_ir.py` lowers its calls and policies into `BindingIR`; `abi_ir.py`
   validates that contract and derives concrete C layouts and signatures.
3. `c_backend.py` renders `ifcopenshell_api.h`, `ifcopenshell_api.cpp`, and
   `ifcopenshell_api_internal.hpp`. For a WASM build,
   `targets/wasm/backend.py` also renders `ifcopenshell_api.mjs` and
   `ifcopenshell_api.d.ts` from the same finalized ABI metadata.
4. `generate.py` writes an artifact only when its content changed. Native
   generated C/C++ files live under `binding_generator/generated`; WASM files
   are generated in the CMake build directory.

For a new API entry, begin in the relevant C++ spec. Follow its discovery or
adapter into `pipeline.py`, inspect the result in `binding_ir.py` and
`abi_ir.py`, then follow the appropriate backend for rendering details.

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
