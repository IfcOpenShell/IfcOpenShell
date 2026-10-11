.. This file was generated with the assistance of an AI coding tool.

IfcQuery
========

IfcQuery is a CLI tool for querying and inspecting IFC building models. It
provides read-only subcommands for common inspection tasks, all outputting JSON
so results can be piped into other tools.

Subcommands:

- **summary** — schema version, entity counts, project metadata
- **tree** — full spatial hierarchy (IfcProject → Site → Building → Storeys → Spaces → Elements)
- **info** — deep inspection of any entity by step ID (attributes, property sets, placement matrix, type, material)
- **select** — filter elements by IFC class using the IfcOpenShell selector syntax
- **relations** — relationships for an element; use ``--traverse up`` to walk the hierarchy to IfcProject
- **clash** — geometric intersection and clearance checks; requires the IfcOpenShell C++ geometry bindings
- **validate** — schema and constraint validation; add ``--rules`` for a full EXPRESS check
- **schedule** — work schedules with nested task trees
- **cost** — cost schedules with nested cost item trees
- **schema** — IFC class documentation using the loaded model's schema version
- **contexts** — geometric representation contexts
- **materials** — material definitions (IfcMaterial, layer sets, constituent sets, profile sets)
- **plot** — generate a drawing (SVG or PNG) using ``ifcopenshell.draw``; PNG output requires ``cairosvg``
- **render** — off-screen 3D render to a PNG image; requires ``pyvista`` and the IfcOpenShell C++ geometry bindings

All subcommands accept ``--format json|text|ids`` to control output (default: ``json``):

- ``json`` — structured JSON, suitable for piping to ``jq`` or ``ifcedit foreach``
- ``text`` — indented human-readable output
- ``ids`` — comma-separated step IDs extracted from list results, suitable for piping directly into ``ifcedit run`` parameters

Installation
------------

::

    pip install ifcquery

For PNG output from ``plot``, also install ``cairosvg``::

    pip install cairosvg

For 3D rendering with ``render``, also install ``pyvista``::

    pip install pyvista

Or install from source:

1. :doc:`Install IfcOpenShell <ifcopenshell-python/installation>`
2. `Clone the IfcOpenShell repository <https://github.com/IfcOpenShell/IfcOpenShell>`_.
3. ``cd /path/to/IfcOpenShell/src/ifcquery``
4. ``pip install .``

Usage
-----

::

    $ ifcquery model.ifc summary
    $ ifcquery model.ifc tree
    $ ifcquery model.ifc info 42
    $ ifcquery model.ifc select 'IfcWall'
    $ ifcquery model.ifc relations 42
    $ ifcquery model.ifc relations 42 --traverse up
    $ ifcquery model.ifc validate
    $ ifcquery model.ifc validate --rules
    $ ifcquery model.ifc schedule
    $ ifcquery model.ifc cost
    $ ifcquery model.ifc schema IfcWall
    $ ifcquery model.ifc materials
    $ ifcquery model.ifc plot -o floorplan.svg --out-format svg --view floorplan
    $ ifcquery model.ifc plot -o floorplan.png --view floorplan
    $ ifcquery model.ifc render -o model.png
    $ ifcquery model.ifc --format ids select 'IfcWall'

Scripting with ifcedit
----------------------

``ifcquery`` and ``ifcedit`` are designed to compose. Use ``--format ids`` to
pass query results directly into ``ifcedit run`` parameters, or pipe JSON into
``ifcedit foreach`` to apply an operation to every matching element::

    # Aggregate — pass all IDs as a list parameter
    $ ifcedit run model.ifc spatial.unassign_container \
        --products "$(ifcquery model.ifc --format ids select 'IfcWall')"

    # Fan-out — one operation per element, model opened and saved once
    $ ifcquery model.ifc select 'IfcWindow' | ifcedit foreach model.ifc root.remove_product --product '{id}'

    # Render an element highlighted against everything related to it
    $ ifcquery model.ifc render -o relations.png \
        --element "$(ifcquery model.ifc --format ids relations 42)"

    # Render a clash — subject and clashing elements highlighted together
    $ ifcquery model.ifc render -o clash.png \
        --element "$(ifcquery model.ifc --format ids clash 42)"

.. seealso::

   Use :doc:`IfcEdit <ifcedit>` to make mutations to IFC files from the command
   line, and :doc:`IfcMCP <ifcmcp>` for interactive AI-assisted editing.
