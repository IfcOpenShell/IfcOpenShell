.. This file was generated with the assistance of an AI coding tool.

IfcOpenShell JS/TS
==================

IfcOpenShell JS/TS provides JavaScript and TypeScript bindings to the
IfcOpenShell C++ core through WebAssembly. The ``ifcopenshell`` package works
in Node.js and browsers, with modules for reading and editing IFC files,
processing geometry, and exporting geometry.

IfcOpenShell is also available in :doc:`Python <ifcopenshell-python>` and
:doc:`C++ <ifcopenshell-cpp>`, and all three use the same C++ core. The
:doc:`Hello, world! <ifcopenshell/hello_world>` and :doc:`geometry processing
<ifcopenshell/geometry_processing>` guides are shared between the three
languages, with a JavaScript tab on every snippet. The other guides in this
section cover what is specific to JavaScript, such as installation in Node.js
and the browser, and the WebAssembly plugins.

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
   Hello, world! <ifcopenshell/hello_world>
   ifcopenshell-js/code_examples
   Geometry processing <ifcopenshell/geometry_processing>
   ifcopenshell-js/geometry_creation
   ifcopenshell-js/geometry_tree
   ifcopenshell-js/schema_querying
   ifcopenshell-js/running_tests

.. seealso::

   :doc:`typescript-api` documents the JavaScript and TypeScript API in detail.
   Geometry concepts and settings are shared with the other languages, see
   :doc:`ifcopenshell/geometry_settings`.
