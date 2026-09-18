.. This file was generated with the assistance of an AI coding tool.

.. _create-railing:

Create Railing
==============

The Railing Tool adds a parametric ``IfcRailing`` following a path you draw as a
mesh (a polyline of connected edges), and generates either a panelled balustrade or a
wall-mounted handrail along that path.

Toolbar Icon
------------

The tool is grouped with the Wall tool in the Toolbar.

Accessing the Tool
-------------------

1. **From the Toolbar**: select the Railing Tool, pick or create an
   ``IfcRailingType``, then place it with :guilabel:`Add` / :kbd:`Shift` + :kbd:`A`.
2. **From the Add menu**: press :kbd:`Shift` + :kbd:`A` in the 3D viewport, choose
   :guilabel:`IFC Element`, set the IFC Class to ``IfcRailing`` (or
   ``IfcRailingType``) and set Representation to :guilabel:`Railing`.

.. note::

   The older ``mesh.add_railing`` operator has been removed. Both the toolbar tool
   and the Add menu now go through the same unified element creation flow.

Key Features
------------

Railing Types
~~~~~~~~~~~~~

The generated geometry depends on the **Railing Type**, edited from the **Railing**
panel under :menuselection:`Properties --> Scene Properties --> Geometry -->
Parametric Geometry`:

- **Frameless Panel**: a series of flat panels following the path.

  - **Height**: panel height.
  - **Thickness**: panel thickness.
  - **Spacing**: gap left between adjacent panels.

- **Wall Mounted Handrail**: a round handrail offset from a wall, on brackets.

  - **Height**: handrail height above the path.
  - **Railing Diameter**: diameter of the handrail tube.
  - **Clear Width**: clear distance between the handrail and the wall it is mounted
    on.
  - **Use Manual Supports**: when enabled, a support bracket is placed at every
    vertex of the path instead of being spaced automatically.
  - **Support Spacing**: distance between automatically placed supports (only used
    when manual supports are off).
  - **Terminal Type**: the end cap style applied at the ends of the handrail (for
    example returning to the wall or the floor).

Use the cycle icon on the panel, or :guilabel:`Cycle Railing Type`, to switch between
the two types.

Editing the Path
~~~~~~~~~~~~~~~~~

The railing follows the edges of the object's mesh. Click the path-edit icon
(:guilabel:`Edit Railing`) on the Railing panel to enter edit mode and reshape the
path with normal Blender mesh editing tools, then finish or cancel path editing from
the same panel. :guilabel:`Flip Railing Path Order` reverses the direction of the
path, which is useful to control which side the supports of a wall-mounted handrail
face.

:guilabel:`Copy Railing Parameters from Active to Selected` copies the active
railing's parameters (and path, if compatible) onto every other selected railing
object.

Removing a Railing
~~~~~~~~~~~~~~~~~~~

Use the :guilabel:`X` button on the Railing panel to remove the railing's parametric
data. This only removes the ``BBIM_Railing`` pset used to regenerate the mesh; it
does not delete the underlying IFC element.

Usage
-----

1. Select the Railing Tool from the Toolbar, or use :kbd:`Shift` + :kbd:`A` and
   choose :guilabel:`IFC Element`.
2. If this is the first railing in the project, create an ``IfcRailingType`` (or pick
   an existing one).
3. Place the railing with :guilabel:`Add` / :kbd:`Shift` + :kbd:`A`. A short default
   path is created automatically.
4. Open the Railing panel and use the path-edit icon to reshape the path to follow
   your stair, floor edge, or wall as needed.
5. Enable editing on the Railing panel, choose a Railing Type, and adjust its
   parameters.
6. Click :guilabel:`Finish Editing` to regenerate the geometry and update the
   railing's ``Pset_RailingCommon`` height property in the IFC model.

.. seealso::

   :doc:`/guides/authoring/basic_modeling/index` for general parametric modeling
   concepts shared across Bonsai's construction tools.
