.. This file was generated with the assistance of an AI coding tool.

IfcEdit
=======

IfcEdit is a CLI wrapper for the full ``ifcopenshell.api`` mutation API. It
exposes all editor functions — over 350 across 30+ modules — without requiring
you to write a Python script. It supports four subcommands:

- **list** — list all API modules, or all functions within a module
- **docs** — show full documentation for a function (parameters, types, descriptions)
- **run** — execute a mutation against an IFC file
- **foreach** — apply an API function to each element in a JSON array read from stdin
- **quantify** — run quantity take-off using ifc5d rules; requires the IfcOpenShell C++ geometry bindings

Installation
------------

::

    pip install ifcedit

Or install from source:

1. :doc:`Install IfcOpenShell <ifcopenshell-python/installation>`
2. `Clone the IfcOpenShell repository <https://github.com/IfcOpenShell/IfcOpenShell>`_.
3. ``cd /path/to/IfcOpenShell/src/ifcedit``
4. ``pip install .``

Usage
-----

Discover available API functions::

    $ ifcedit list
    $ ifcedit list root
    $ ifcedit list geometry

Read documentation for a function::

    $ ifcedit docs root.remove_product
    $ ifcedit docs type.assign_type

Execute a mutation (overwrites the input file by default)::

    $ ifcedit run model.ifc root.remove_product --product 42
    $ ifcedit run model.ifc type.assign_type --related_objects 10 --relating_type 20

Write to a separate output file::

    $ ifcedit run model.ifc root.create_entity -o output.ifc --ifc_class IfcWall

Dry-run to validate without modifying the file::

    $ ifcedit run model.ifc root.remove_product --dry-run --product 42

Apply an API function to each element in a JSON array from stdin (``{field}``
placeholders are substituted from each item; model is opened and saved once)::

    $ ifcquery model.ifc select 'IfcWindow' | ifcedit foreach model.ifc root.remove_product --product '{id}'
    $ ifcquery model.ifc select 'IfcDoor' | ifcedit foreach model.ifc attribute.edit_attributes \
        --product '{id}' --attributes '{"Name": "Door"}'

Write to a separate output file instead of overwriting::

    $ ifcquery model.ifc select 'IfcWall' | ifcedit foreach model.ifc root.remove_product -o output.ifc --product '{id}'

Quantity take-off (writes ``IfcElementQuantity`` psets back to the file; requires C++ geometry bindings)::

    $ ifcedit quantify list
    $ ifcedit quantify run model.ifc IFC4QtoBaseQuantities
    $ ifcedit quantify run model.ifc IFC4QtoBaseQuantities --selector IfcWall
    $ ifcedit quantify run model.ifc IFC4QtoBaseQuantities -o model_qto.ifc

Parameter types
---------------

IfcEdit automatically coerces CLI string arguments to the correct Python types
using the type hints on each API function:

.. list-table::
   :header-rows: 1

   * - Type
     - CLI input
     - Python value
   * - ``str``
     - ``"hello"``
     - ``"hello"``
   * - ``int``
     - ``"42"`` or ``"#42"``
     - ``42``
   * - ``float``
     - ``"3.14"``
     - ``3.14``
   * - ``bool``
     - ``"true"``, ``"1"``, ``"yes"``
     - ``True``
   * - ``Optional[X]``
     - ``"none"``
     - ``None``
   * - ``entity_instance``
     - ``"42"`` or ``"#42"``
     - resolved from model by step ID
   * - ``list[entity_instance]``
     - ``"5,6,7"``
     - list of resolved entities
   * - ``dict``
     - ``'{"key": "val"}'``
     - parsed JSON object
   * - ``Literal["A", "B"]``
     - ``"A"``
     - validated against allowed values

.. seealso::

   Use :doc:`IfcQuery <ifcquery>` for read-only inspection of IFC files, and
   :doc:`IfcMCP <ifcmcp>` for interactive AI-assisted editing with an in-memory
   session.
