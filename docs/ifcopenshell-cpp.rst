.. This file was generated with the assistance of an AI coding tool.

C++ notes
=========

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

The :doc:`IfcOpenShell guides <ifcopenshell>` are shared between C++, Python,
and JavaScript. This page and :doc:`ifcopenshell-cpp/code_examples` cover what
only applies to C++, such as schema-agnostic parsing.

Every C++ snippet in these guides is a standalone program which is built with
CMake and run as part of the documentation's test suite, see
:ref:`building-and-running-the-examples`.

.. toctree::
   :hidden:
   :maxdepth: 1
   :caption: Contents:

   ifcopenshell-cpp/code_examples

.. seealso::

   The machinery that all languages share is described in
   :doc:`ifcopenshell/geometry_settings`,
   :doc:`ifcopenshell/serialiser_settings` and :doc:`ifcopenshell/formats`.
