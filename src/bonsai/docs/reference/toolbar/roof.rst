.. This file was generated with the assistance of an AI coding tool.

.. _create-roof:

Create Roof
===========

The Roof Tool adds a parametric ``IfcRoof`` generated from a footprint path you draw
as a mesh, producing a hip and gable roof with a constant pitch over that footprint.

.. note::

   This page documents the dedicated Roof Tool. For adding a flat roof deck as a
   ``IfcSlab`` with a ``ROOF`` predefined type instead, see
   :doc:`/guides/authoring/basic_modeling/modeling_slabs_roofs`.

Toolbar Icon
------------

The tool is grouped with the Slab and Ramp Flight tools in the Toolbar.

Accessing the Tool
-------------------

1. **From the Toolbar**: select the Roof Tool, pick or create an ``IfcRoofType``,
   then place it with :guilabel:`Add` / :kbd:`Shift` + :kbd:`A`.
2. **From the Add menu**: press :kbd:`Shift` + :kbd:`A` in the 3D viewport, choose
   :guilabel:`IFC Element`, set the IFC Class to ``IfcRoof`` (or ``IfcRoofType``) and
   set Representation to :guilabel:`Roof`.

.. note::

   The older ``mesh.add_roof`` operator has been removed. Both the toolbar tool and
   the Add menu now go through the same unified element creation flow.

Key Features
------------

Roof Parameters
~~~~~~~~~~~~~~~~

The roof's parameters are edited from the **Roof** panel under
:menuselection:`Properties --> Scene Properties --> Geometry --> Parametric
Geometry`:

- **Roof Type**: currently only ``HIP/GABLE ROOF`` is available.
- **Roof Generation Method**: ``HEIGHT`` or ``ANGLE``. Use :guilabel:`Cycle Roof
  Generation Method` to switch between them.

  - **HEIGHT** exposes a **Height** field, the maximum height of the ridge above the
    footprint.
  - **ANGLE** exposes **Slope Angle** and **Slope %** fields, which drive each other
    (editing one updates the other).

- **Roof Thickness**: thickness of the roof slab/rafters.
- **Rafter Edge Angle**: the cutting angle applied to hip rafter ends (90° is a
  standard vertical hip cut).

Editing the Footprint Path
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Like the Railing Tool, the roof is generated from the edges of the object's mesh.
Click the path-edit icon (:guilabel:`Edit Roof`) on the Roof panel to enter edit mode
and reshape the footprint with normal Blender mesh editing tools. While in edit mode,
:guilabel:`Set Gable Roof Edge Angle` can be used on selected edges to control whether
that edge of the footprint produces a hip or a gable end.

:guilabel:`Copy Roof Parameters from Active to Selected` copies the active roof's
parameters onto every other selected roof object.

Removing a Roof
~~~~~~~~~~~~~~~~

Use the :guilabel:`X` button on the Roof panel to remove the roof's parametric data.
This only removes the ``BBIM_Roof`` pset used to regenerate the mesh; it does not
delete the underlying IFC element.

Usage
-----

1. Select the Roof Tool from the Toolbar, or use :kbd:`Shift` + :kbd:`A` and choose
   :guilabel:`IFC Element`.
2. If this is the first roof in the project, create an ``IfcRoofType`` (or pick an
   existing one).
3. Place the roof with :guilabel:`Add` / :kbd:`Shift` + :kbd:`A`. A default footprint
   is created automatically.
4. Open the Roof panel and use the path-edit icon to reshape the footprint to match
   the building outline.
5. Enable editing on the Roof panel, choose a Roof Generation Method, and set the
   height (or slope), thickness and rafter edge angle.
6. Click :guilabel:`Finish Editing` to regenerate the roof geometry.

.. seealso::

   :doc:`/guides/authoring/basic_modeling/index` for general parametric modeling
   concepts shared across Bonsai's construction tools.
