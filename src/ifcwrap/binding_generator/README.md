<!-- SPDX-License-Identifier: LGPL-3.0-or-later -->

# Binding generator

The generator requires Python, a C++ Clang compiler with its matching shared
`libclang` library, and the Python Clang bindings declared in the repository's
`pyproject.toml`. Install it from the repository root:

```sh
python -m pip install -e ".[bindgen]"
```

Use the CMake code-generation target rather than assembling Clang arguments by
hand. Configure IfcOpenShell with `BUILD_IFCAPI=ON` and
`IFCAPI_REGENERATE_BINDINGS=ON`, then build:

```sh
cmake --build <build-directory> --target ifcopenshell_bindings_codegen
```

CMake finds the same Boost, Eigen, OpenCASCADE, CGAL, GMP, and MPFR headers used
by the configured native build and passes their include directories and active
feature definitions to the generator. The native WASM build follows the same
path after installing its pinned dependencies under `build/wasm-native`.

The module can also be invoked directly with
`python -m src.ifcwrap.binding_generator.generate`, but direct callers must
provide every required `--discovery-include-dir` and `--discovery-define`.
