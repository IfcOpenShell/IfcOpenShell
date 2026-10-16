IfcOpenShell
============

IfcOpenShell is an open source (LGPL-3.0-or-later) software library for
working with the Industry Foundation Classes (IFC) file format. Its core is
written in C++, and it is available in three languages:

.. list-table::
   :header-rows: 1
   :widths: 20 50 30

   * - Language
     - What it is
     - Get started
   * - Python
     - Bindings to the C++ core, plus a high level authoring API
       (``ifcopenshell.api``) and utility modules (``ifcopenshell.util``).
       All the capabilities of the C++ core are available in Python.
     - :doc:`Install <ifcopenshell-python/installation>`,
       :doc:`notes <ifcopenshell-python>`,
       `API <autoapi/index.html>`__
   * - C++
     - The core library itself: ``IfcParse`` reads and writes IFC, and
       ``IfcGeom`` processes geometry. Python, JavaScript, IfcConvert, and the
       other utilities are built on it.
     - :doc:`Compile <ifcopenshell/installation>`,
       :doc:`notes <ifcopenshell-cpp>`,
       :doc:`API <cpp-api>`
   * - JavaScript / TypeScript
     - Bindings to the C++ core through WebAssembly, for Node.js and
       browsers.
     - :doc:`Install <ifcopenshell-js/installation>`,
       :doc:`notes <ifcopenshell-js>`,
       :doc:`API <typescript-api>`

Whichever language you use, it is the same parser and the same geometry engine
underneath, so concepts, :doc:`geometry settings <ifcopenshell/geometry_settings>`
and :doc:`serialisation settings <ifcopenshell/serialiser_settings>` are shared
between C++, Python, and JavaScript. The guides in this section explain each
concept once. Every code block has a tab for each language, and switching the
tab of one code block only changes that block.

Some examples are not available in every language yet. Their tabs are greyed
out, and :doc:`ifcopenshell/parity` lists what exists in which language.

Extensive geometric support is implemented for the IFC releases IFC2x3 TC1 and
IFC4 Add2 TC1. Support for parsing is provided for IFC4x1, IFC4x2, and the
IFC4x3 release candidates.  Extending with support for arbitrary IFC schemas is
possible at compile-time when using C++ and at run-time when using Python.

.. seealso::

   It is not necessary to be a programmer to use IfcOpenShell. See
   :doc:`ifcconvert` for converting IFC models from the command line, and
   :doc:`bonsai` for a graphical application.

.. toctree::
   :hidden:
   :maxdepth: 1
   :caption: Contents:

   ifcopenshell/install
   ifcopenshell/hello_world
   ifcopenshell/code_examples
   ifcopenshell/geometry_processing
   ifcopenshell/geometry_creation
   ifcopenshell/geometry_tree
   ifcopenshell/schema_querying
   ifcopenshell-python/selector_syntax
   ifcopenshell-python/validation
   ifcopenshell/reference
   ifcopenshell/language_notes
   ifcopenshell/parity
   ifcopenshell/running_tests
