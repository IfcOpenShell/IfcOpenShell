IfcOpenShell
============

IfcOpenShell is an open source (LGPL-3.0-or-later) software library for
working with the Industry Foundation Classes (IFC) file format. Its core is
written in C++, and it is available in three languages:

- :doc:`IfcOpenShell-Python <ifcopenshell-python>`, Python bindings to the C++
  core, with high level analysis and authoring functions on top. All the
  capabilities of the C++ core are available in Python.
- :doc:`IfcOpenShell C++ <ifcopenshell-cpp>`, the core library itself, which
  IfcOpenShell-Python, the JavaScript bindings, IfcConvert, and the other
  utilities are built on.
- :doc:`IfcOpenShell JS/TS <ifcopenshell-js>`, JavaScript and TypeScript
  bindings to the C++ core through WebAssembly, for Node.js and browsers.

Whichever language you use, it is the same parser and the same geometry engine
underneath, so concepts, :doc:`geometry settings <ifcopenshell/geometry_settings>`
and :doc:`serialisation settings <ifcopenshell/serialiser_settings>` are shared
between C++, Python, and JavaScript. The shared guides below explain each
concept once, with a C++, Python, and JavaScript tab on every code snippet.
Pick a language on any snippet, and all of them switch with it.

Extensive geometric support is implemented for the IFC releases IFC2x3 TC1 and
IFC4 Add2 TC1. Support for parsing is provided for IFC4x1, IFC4x2, and the
IFC4x3 release candidates.  Extending with support for arbitrary IFC schemas is
possible at compile-time when using C++ and at run-time when using Python.

.. seealso::

   It is not necessary to be a C++ developer to use IfcOpenShell. Please see
   other sections such as :doc:`ifcopenshell-python`, :doc:`ifcconvert`, and
   more.

.. toctree::
   :hidden:
   :maxdepth: 1
   :caption: Contents:

   ifcopenshell/hello_world
   ifcopenshell/geometry_processing
   ifcopenshell/geometry_settings
   ifcopenshell/serialiser_settings
   ifcopenshell/formats
   ifcopenshell/boolean_process
   Compiling from source <ifcopenshell/installation>
