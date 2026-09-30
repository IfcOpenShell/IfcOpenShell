.. This file was generated with the assistance of an AI coding tool.

IfcMCP
======

IfcMCP is an MCP (Model Context Protocol) server that exposes IfcOpenShell
query and edit tools to AI coding assistants such as Claude. It wraps
:doc:`IfcQuery <ifcquery>` and :doc:`IfcEdit <ifcedit>`, holding the IFC model
in memory across tool calls so no file I/O is required between operations.

The ``ifcmcp`` package can also be used directly as a Python library without
the MCP server layer.

Installation
------------

To use IfcMCP as an MCP server, install it together with the ``mcp`` package::

    pip install 'ifcmcp[mcp]'

If you only want to use the library directly (without an MCP client)::

    pip install ifcmcp

Or install from source:

1. :doc:`Install IfcOpenShell <ifcopenshell-python/installation>`
2. `Clone the IfcOpenShell repository <https://github.com/IfcOpenShell/IfcOpenShell>`_.
3. ``cd /path/to/IfcOpenShell/src/ifcmcp``
4. ``pip install '.[mcp]'``

Setup
-----

Add the server to your MCP client. For Claude Code::

    claude mcp add --transport stdio ifc -- ifcmcp

Or add to ``.mcp.json``:

.. code-block:: json

    {
      "mcpServers": {
        "ifc": {
          "type": "stdio",
          "command": "ifcmcp"
        }
      }
    }

Available tools
---------------

**Session tools**

- ``ifc_new(schema="IFC4")`` — create a new empty model in memory
- ``ifc_load(path)`` — open an IFC file into memory
- ``ifc_reset()`` — unload the current model, freeing all session state
- ``ifc_save(path="")`` — write model to disk; empty path overwrites the original

**Query tools**

- ``ifc_summary()`` — schema version, entity counts, project metadata
- ``ifc_tree()`` — full spatial hierarchy
- ``ifc_info(element_id)`` — deep inspection by step ID
- ``ifc_select(query)`` — filter elements by IFC class
- ``ifc_relations(element_id, traverse="")`` — relationships for an element
- ``ifc_clash(element_id, ...)`` — geometric intersection and clearance checks
- ``ifc_validate(express_rules=False)`` — schema and constraint validation
- ``ifc_schedule(max_depth=None)`` — work schedules with nested task trees
- ``ifc_cost(max_depth=None)`` — cost schedules with nested cost item trees
- ``ifc_schema(entity_type)`` — IFC class documentation
- ``ifc_contexts()`` — geometric representation contexts
- ``ifc_materials()`` — material definitions

**Drawing and rendering tools**

- ``ifc_plot(...)`` — generate a 2D drawing via ``ifcopenshell.draw`` and return it as an inline image the AI assistant can inspect; SVG always available, PNG requires ``cairosvg``
- ``ifc_render(...)`` — off-screen 3D render returned as an inline PNG image the AI assistant can inspect; requires ``pyvista`` and the IfcOpenShell C++ geometry bindings

**ShapeBuilder tools**

- ``ifc_shape_list()`` — list all available ``ShapeBuilder`` methods
- ``ifc_shape_docs(method)`` — documentation for a specific ``ShapeBuilder`` method
- ``ifc_shape(method, params="{}")`` — execute a ``ShapeBuilder`` method; entity references resolved by step ID

**Edit tools**

- ``ifc_list(module="")`` — list API modules or functions
- ``ifc_docs(function_path)`` — documentation for an API function
- ``ifc_edit(function_path, params="{}")`` — execute an ``ifcopenshell.api`` mutation
- ``ifc_quantify(rule, selector="")`` — run quantity take-off; writes ``IfcElementQuantity`` psets in-place

Typical workflow
----------------

.. code-block:: text

    ifc_load("/path/to/model.ifc")
    ifc_summary()
    ifc_tree()
    ifc_info(42)
    ifc_edit("root.remove_product", '{"product": "42"}')
    ifc_save()

.. seealso::

   :doc:`IfcQuery <ifcquery>` and :doc:`IfcEdit <ifcedit>` provide the same
   functionality as standalone CLI tools for scripting and automation.
