.. This file was generated with the assistance of an AI coding tool.

JavaScript / TypeScript notes
=============================

IfcOpenShell JS/TS provides JavaScript and TypeScript bindings to the
IfcOpenShell C++ core through WebAssembly. The ``ifcopenshell`` package works
in Node.js and browsers, with modules for reading and editing IFC files,
processing geometry, and exporting geometry. Install it as described in
:doc:`ifcopenshell-js/installation`.

The :doc:`IfcOpenShell guides <ifcopenshell>` are shared between JavaScript,
Python, and C++. This page covers what only applies to JavaScript.

Examples use JavaScript ES modules and can also be used in TypeScript.
Only ``File`` and geometry ``Iterator`` implement ``Disposable``: release them
with ``dispose()`` or TypeScript ``using`` to invoke their native destructors.
Other wrappers use GC cleanup, and instance queries return ordinary JS arrays.

.. note::
   The current JS/TS bindings are a work in progress. The API is subject to change.
   The current version of the JS/TS documentation has been generated with the
   assistance of generative AI.

Geometry processing needs plugins in addition to the schema: a mapping, which
interprets IFC representations, and a geometry kernel. See
:doc:`ifcopenshell-js/installation` for loading plugins and running in the
browser.

.. seealso::

   :doc:`typescript-api` documents the JavaScript and TypeScript API in detail.
   Geometry concepts and settings are shared with the other languages, see
   :doc:`ifcopenshell/geometry_settings`.
