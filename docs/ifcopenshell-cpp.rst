.. This file was generated with the assistance of an AI coding tool.

IfcOpenShell C++
================

The IfcOpenShell C++ core is the library that the rest of the ecosystem is
built on: IfcOpenShell-Python, the JavaScript and TypeScript bindings,
IfcConvert, IfcClash and the other utilities all use it. It is split into two
libraries:

- ``IfcParse`` reads and writes IFC-SPF files, and turns them into a typed
  object graph of generated C++ classes, one namespace per IFC schema.
- ``IfcGeom`` turns the IFC representation items of that object graph into
  geometry, using a geometry kernel such as OpenCASCADE or CGAL.

Both are consumed from your own project with
``find_package(IfcOpenShell CONFIG)``, which exports them as the
``IfcOpenShell::IfcParse``, ``IfcOpenShell::IfcGeom`` and
``IfcOpenShell::parse_schema_*`` targets. See
:doc:`ifcopenshell/installation` for how to build and install the library
itself.

Because the same core is used everywhere, IfcOpenShell is also available in
:doc:`Python <ifcopenshell-python>` and :doc:`JavaScript / TypeScript
<ifcopenshell-js>`. The :doc:`Hello, world! <ifcopenshell/hello_world>` and
:doc:`geometry processing <ifcopenshell/geometry_processing>` guides are shared
between the three languages, with a C++ tab on every snippet. The code examples
in this section cover what is specific to C++, such as schema-agnostic parsing.

Every C++ snippet in these guides is a standalone program which is built with
CMake and run as part of the documentation's test suite, see
`Building and running the examples`_ below.

.. toctree::
   :hidden:
   :maxdepth: 1
   :caption: Contents:

   Hello, world! <ifcopenshell/hello_world>
   ifcopenshell-cpp/code_examples
   Geometry processing <ifcopenshell/geometry_processing>

.. seealso::

   The machinery that all languages share is described in
   :doc:`ifcopenshell/geometry_settings`,
   :doc:`ifcopenshell/serialiser_settings` and :doc:`ifcopenshell/formats`.

.. _building-and-running-the-examples:

Building and running the examples
---------------------------------

The sources in ``docs/ifcopenshell-cpp`` are a standalone CMake project which
consumes an installed IfcOpenShell through ``find_package(IfcOpenShell
CONFIG)``, the same way any other third party consumer would:

.. code-block:: shell

    cd docs/ifcopenshell-cpp
    cmake -S . -B build -DCMAKE_PREFIX_PATH=/path/to/ifcopenshell
    cmake --build build --config RelWithDebInfo

Every example is registered as a test. The Hello, world! programs are run
against ``hello_world.ifc``, a small IFC4 model that ships with the examples,
and the code example and geometry processing programs against
``AC20-FZK-Haus.ifc``:

.. code-block:: shell

    ctest --test-dir build -C RelWithDebInfo --output-on-failure

There is also a single custom command which builds and runs all of them at
once, and which fails if any of the examples reports a failure:

.. code-block:: shell

    cmake --build build --config RelWithDebInfo --target run_examples
