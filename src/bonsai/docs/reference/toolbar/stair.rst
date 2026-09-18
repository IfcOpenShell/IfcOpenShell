.. This file was generated with the assistance of an AI coding tool.

.. _create-stair:

Create Stair
============

The Stair Flight Tool lets you add a parametric ``IfcStairFlight`` to your model and
adjust its geometry (treads, risers, width, nosing) using either the Properties editor
or on-screen dimension gizmos, without leaving the 3D viewport.

Toolbar Icon
------------

The tool is grouped with the Roof and Ramp Flight tools in the Toolbar, next to the
Slab tool.

Accessing the Tool
-------------------

There are two ways to create a stair:

1. **From the Toolbar**: select the Stair Flight Tool. If no ``IfcStairFlightType``
   exists yet in the project, the tool header shows a "Create New IfcStairFlightType"
   button. Once a type exists, pick it from the type dropdown and press
   :guilabel:`Add` (or use :kbd:`Shift` + :kbd:`A`) to place a new occurrence at the
   3D cursor.
2. **From the Add menu**: press :kbd:`Shift` + :kbd:`A` in the 3D viewport, choose
   :guilabel:`IFC Element`, set the IFC Class to ``IfcStairFlight`` (or
   ``IfcStairFlightType`` if you are defining a reusable type first) and set
   Representation to :guilabel:`Stair`.

Both paths end up calling the same parametric stair generator, so the resulting
geometry and IFC data are identical either way.

.. note::

   The older ``mesh.add_stair`` operator has been removed. Both the toolbar tool and
   the Add menu now go through the same unified element creation flow.

Key Features
------------

Stair Parameters
~~~~~~~~~~~~~~~~~

Once a stair exists, its parameters are edited from the **Stair** panel, found under
:menuselection:`Properties --> Scene Properties --> Geometry --> Parametric Geometry`.
Click the pencil icon (:guilabel:`Enable Editing`) to unlock the fields, adjust them,
then click :guilabel:`Finish Editing` to regenerate the mesh and write the values back
to the IFC model, or the cancel icon to discard the changes.

The available fields depend on the selected **Stair Type**:

- **Stair Type**: ``CONCRETE``, ``WOOD/STEEL``, or ``GENERIC``. Changes which of the
  fields below are shown.
- **Width**: the width of the stair flight.
- **Height**: the total rise of the flight.
- **Total Length Target** and its lock toggle: a target horizontal length for the
  flight. When the lock is enabled, changing the number of treads or the tread run
  keeps the total length fixed by adjusting the other value.
- **Number of Treads**: use the :kbd:`+` / :kbd:`-` gizmos in the viewport to
  increment or decrement by one, or :kbd:`Shift` + click the gizmo to type an exact
  value.
- **Tread Run**: the horizontal going of a single tread.
- **Lock First/Last Treads to Tread Run** and **Custom First / Last Treads Widths**:
  when unlocked, the first and/or last tread can use a different run than the rest of
  the flight (set either value to 0 to leave that end at the default Tread Run).
- **Nosing Length**: the overhang of the tread nosing, not counted as part of the
  tread run. Can be negative for ``WOOD/STEEL`` stairs, where it instead opens a gap
  between treads.
- **Nosing Depth**: only shown for ``CONCRETE`` and ``GENERIC`` stairs.
- **Tread Depth**: the thickness of the tread board or slab. Not shown for
  ``GENERIC`` stairs.
- **Base Slab Depth**, **Top Slab Depth**, **Has Top Nib**: only shown for
  ``CONCRETE`` stairs, controlling the underside slab thickness at the bottom and top
  of the flight and whether a top nib is generated.

Dimension Gizmos
~~~~~~~~~~~~~~~~~

While editing, the same values can be dragged directly in the 3D viewport using
labelled dimension gizmos anchored to the geometry they control (total length,
height, width, tread run, riser height, nosing, and, for concrete stairs, the base and
top slab depths).

Removing a Stair
~~~~~~~~~~~~~~~~~

Use the :guilabel:`X` button on the Stair panel to remove the stair's parametric data.
This only removes the ``BBIM_Stair`` pset used to regenerate the mesh; it does not
delete the underlying IFC element.

Usage
-----

1. Select the Stair Flight Tool from the Toolbar, or use :kbd:`Shift` + :kbd:`A` and
   choose :guilabel:`IFC Element`.
2. If this is the first stair in the project, create an ``IfcStairFlightType`` (or
   pick an existing one).
3. Place the stair with :guilabel:`Add` / :kbd:`Shift` + :kbd:`A`.
4. Open the Stair panel in :menuselection:`Scene Properties --> Geometry --> Parametric
   Geometry` and click the pencil icon to enable editing.
5. Choose a Stair Type, then adjust Width, Height, Number of Treads, Tread Run and the
   other fields relevant to that type, either from the panel or with the viewport
   gizmos.
6. Click :guilabel:`Finish Editing` to regenerate the geometry and write the stair's
   ``Pset_StairFlightCommon`` properties (number of risers, riser height, tread
   length) back to the IFC model.

.. seealso::

   :doc:`/guides/authoring/basic_modeling/index` for general parametric modeling
   concepts shared across Bonsai's construction tools.
