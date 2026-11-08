.. This file was generated with the assistance of an AI coding tool.

IfcOpenShell JS/TS
==================

IfcOpenShell JS/TS provides JavaScript and TypeScript bindings to the
IfcOpenShell C++ core through WebAssembly. The ``ifcopenshell`` package works
in Node.js and browsers, with modules for reading and editing IFC files,
processing geometry, and exporting geometry.

The guides below introduce the operations available in the current bindings.
Examples use JavaScript ES modules and can also be used in TypeScript.
Only ``File`` and geometry ``Iterator`` implement ``Disposable``: release them
with ``dispose()`` or TypeScript ``using`` to invoke their native destructors.
Other wrappers use GC cleanup, and instance queries return ordinary JS arrays.

.. note::
   The current JS/TS bindings are a work in progress. The API is subject to change.
   The current version of the JS/TS documentation has been generated with the
   assistance of generative AI.

.. toctree::
   :hidden:
   :maxdepth: 1
   :caption: Contents:

   ifcopenshell-js/installation
   ifcopenshell-js/hello_world
   ifcopenshell-js/code_examples
   ifcopenshell-js/geometry_processing
   ifcopenshell-js/geometry_creation
   ifcopenshell-js/geometry_tree
   ifcopenshell-js/schema_querying
   ifcopenshell-js/running_tests

.. seealso::

   :doc:`typescript-api` documents the JavaScript and TypeScript API in detail.
   The equivalent C++ and Python guides are in :doc:`ifcopenshell-cpp` and
   :doc:`ifcopenshell-python`. Geometry concepts and settings are shared with
   :doc:`ifcopenshell/geometry_iterator` and
   :doc:`ifcopenshell/geometry_settings`.
