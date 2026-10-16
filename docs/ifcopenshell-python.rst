Python notes
============

IfcOpenShell-Python provides Python bindings to the core IfcOpenShell C++
system, as well as high level analysis and authoring functions. All the
capabilities of the C++ core are available in Python. Install it as described
in :doc:`ifcopenshell-python/installation`.

The :doc:`IfcOpenShell guides <ifcopenshell>` are shared between Python, C++,
and JavaScript. Python has a large library written on top of the C++ core,
which the other languages do not have. This is why some Python examples are a
single line where the C++ and JavaScript versions follow the IFC relationships
by hand.

- ``ifcopenshell.api`` is the authoring API. Its functions create and edit
  IFC data the way a BIM application does, keeping relationships, owner
  history, and the rules of the schema consistent. See the
  `API reference <autoapi/ifcopenshell/api/index.html>`__, and
  :doc:`ifcopenshell/geometry_creation` and :doc:`ifcopenshell/code_examples`
  for examples.
- ``ifcopenshell.util`` holds utility modules to query IFC data, such as
  ``util.element`` for types, property sets, and containers,
  ``util.placement`` for placements, ``util.unit`` for units, and
  ``util.shape`` for geometry. See the
  `API reference <autoapi/ifcopenshell/util/index.html>`__.
- :doc:`ifcopenshell-python/selector_syntax` is a query language to filter
  elements and get their values, used by many of the utilities.
- :doc:`ifcopenshell-python/validation` validates files against the syntax
  and the schema, including the rules of the schema.
