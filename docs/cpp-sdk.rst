IfcOpenShell C++ SDK
====================

The SDK contains precompiled shared libraries and plug-ins, public headers,
the dependencies used to build them, and the C++ examples. Extract the entire
archive to a writable directory. See ``README.md`` at its root for the platform,
compiler requirements, and enabled features of this build.

Build and run the examples
--------------------------

Run these commands from the extracted SDK directory. A C++17 compiler, CMake
3.24 or newer, and a build tool are required; Python is not required.

.. code-block:: sh

   cmake -S examples -B examples-build \
     -DCMAKE_PREFIX_PATH="$PWD" -DCMAKE_BUILD_TYPE=Release
   cmake --build examples-build --parallel 2
   mkdir -p example-output
   cd example-output
   ../examples-build/IfcOpenHouse
   ../examples-build/IfcParseExamples IfcOpenHouse.ifc

``IfcAdvancedHouse``, ``IfcAlignment``, and ``IfcSimplifiedAlignment`` provide
further geometry and alignment examples. The original C++ sources and their
standalone ``CMakeLists.txt`` are included in ``examples/``.

Use the libraries in your own project
-------------------------------------

Pass the SDK root as ``CMAKE_PREFIX_PATH`` when configuring your project.
The package locates its bundled dependencies automatically.

.. code-block:: cmake

   cmake_minimum_required(VERSION 3.24)
   project(MyIfcApplication LANGUAGES CXX)
   find_package(IfcOpenShell CONFIG REQUIRED)
   add_executable(my_app main.cpp)
   target_compile_features(my_app PRIVATE cxx_std_17)
   target_link_libraries(my_app PRIVATE IfcOpenShell::IfcParse)

For schema-specific code, also link a schema target such as
``IfcOpenShell::parse_schema_ifc4``. See the included examples for geometry
serialization and plug-in search paths. Keep the SDK libraries together when
running applications; copying a single library omits the schema and geometry
plug-ins loaded at runtime.

C++ API reference
-----------------

.. toctree::
   :maxdepth: 2

   output/api/library_root
