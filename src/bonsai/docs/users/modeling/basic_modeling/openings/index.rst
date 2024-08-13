Openings
========

This section covers the creation and management of openings in BlenderBIM.
Openings are crucial elements in building design, serving various purposes such as passage, ventilation, and lighting.

.. only:: builder_html and (not singlehtml)

   .. container:: toc-cards

      .. container:: card

         :doc:`door`
            Learn how to add and customize doors in your BIM model.

      .. container:: card

         :doc:`window`
            Discover the process of creating and modifying windows.

      .. container:: card

         :doc:`opening`
            Create openings without fillings for special architectural features.

Overview
--------

In the context of Building Information Modeling (BIM) and the Industry Foundation Classes (IFC)
standard, openings are represented through a combination of elements:

1. Voids: Represented by IfcOpeningElement, these are the actual cut-outs in the wall.
2. Fillings: These are the elements that occupy the voids, such as doors (IfcDoor) or windows (IfcWindow).
3. Relationships: These are abstract objects that connect fillings to voids and voids to elements in which they're created.

BlenderBIM provides tools to create and manage these elements:

- Door Creation Tool: For adding doors to walls.
- Window Creation Tool: For adding windows to walls.
- Wall Creation Tool > Void Application: For creating openings without fillings
  (currently achieved by creating a door or window and removing it
  or by using "Add Void" feature of the Create Wall tool or any element).

These tools allow you to:

- Create openings with precise dimensions and positions.
- Modify opening properties and geometries.
- Manage the relationships between walls, voids, and fillings.

The following pages provide detailed guides on working with each type of wall opening in BlenderBIM.

.. container:: global-index-toc

   .. toctree::
      :hidden:
      :caption: Wall Openings
      :maxdepth: 1

      door
      window
      opening

See Also
--------

- :doc:`../creating_walls`
