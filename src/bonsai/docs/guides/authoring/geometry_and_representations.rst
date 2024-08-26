Geometry and Representations
============================

Understanding IFC Elements and Geometry
---------------------------------------

In Bonsai, it's crucial to understand the relationship between IFC elements, their classification, types, and geometry.
These concepts work together but serve different purposes.

IFC Classification
^^^^^^^^^^^^^^^^^^

Every IFC element has a two-level classification:

1. IFC Class: The top level (e.g., IfcWall)
2. Predefined Type: The second level (e.g., PARTITIONING)

This classification is purely for categorization and filtering. It doesn't determine the element's geometry or appearance.

Types and Occurrences
^^^^^^^^^^^^^^^^^^^^^

IFC uses the concept of "Types" and "Occurrences":

- Types: Define common properties or materials shared by multiple elements.
- Occurrences: Individual instances of a type.

If a type has geometry associated with it, all its occurrences must have the same geometry (similar to instancing or cloning in other applications).
However, if a type has no material or geometry, it doesn't impact the geometry of its occurrences.

Representations
---------------

In IFC, unlike traditional 3D modeling:

- An object may have no geometry, one geometry, or multiple geometries.
- Each geometry is called a "Representation".
- Representations are differentiated by their "Context". A "Context" defines what the geometry is used for (e.g., 3D Body, 2D Plan, etc.).

The most common context is the 3D Body context, which represents the physical shape of the object.

Representation Types
^^^^^^^^^^^^^^^^^^^^

IFC supports various geometry types:

- Mesh-like: Facetations, tessellations, triangulations, or planar breps.
- Solid modeling: CSGs, swept solids, extrusions, lofts, etc.

In Bonsai, you can create simple mesh geometries (like a cube) and assign them to IFC elements.
However, for more complex elements like walls, slabs, or columns, other representation types are more appropriate.

Parametric Materials
^^^^^^^^^^^^^^^^^^^^

IFC standardizes certain parametric modeling techniques:

1. Material Layers: Uses an axis line and material layers to derive the body of an object by extruding layers of different thicknesses to a particular height.
2. Material Profiles: Extrudes a profile (arbitrary or parametric) along a 3D axis.

These are typically defined at the type level and inherited by occurrences.

Working with Representations in Bonsai
--------------------------------------

- Creating swept solids: Currently, the best method is to use parametric material layers (e.g., for walls) or material profiles.
- Mesh editing: For mesh-like representations, you can edit them directly in Blender's edit mode.
- Non-mesh modeling: Bonsai currently has limited tools for direct modeling of non-mesh geometries.
  Future updates will include more intuitive interfaces for this purpose.
- Deleting representations: This should be avoided as it can create invalid IFC data.
  If you delete a representation, the element should no longer be visible in the 3D view.

.. note::
  The current implementation allows low-level manipulation of IFC data, which requires a deep understanding of IFC rules.
  Users should exercise caution when manually editing representations or other low-level IFC data.

Future Developments
-------------------

The Bonsai team plans to develop more intuitive interfaces for non-mesh direct modeling tools in future versions.
This will make it easier to create and manipulate complex geometric representations without needing to understand the intricacies of IFC data structures.
